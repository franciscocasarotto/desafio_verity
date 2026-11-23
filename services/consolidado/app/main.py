"""API HTTP do servico de Consolidado Diario (FastAPI).

Principio-chave (RNF): o consolidado e LIDO de um read-model proprio, alimentado
por eventos. Se ele cair, nada afeta o lancamento; se o lancamento ficar lento,
o consolidado continua servindo o ultimo estado conhecido + lag informado.

Cache-aside com TTL curto nos relatorios (dado e imutavel apos fechamento do
dia -> cache infinito para dias passados, TTL de segundos para o dia corrente).
"""
from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass

from fastapi import Depends, FastAPI, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from shared.event_schema import from_json
from shared.observability import configure_logging, new_correlation_id
from shared.security import AuthError, Principal, validate_token

from .infrastructure.event_processor import (
    ConsolidadoWorker,
    EventProcessor,
    FakeBrokerQueue,
)

SERVICE = "consolidado"
logger = configure_logging(SERVICE)


# --------------------------------------------------------------------------
@dataclass
class Settings:
    db_path: str = os.getenv("CONSOLIDADO_DB", "data/consolidado.db")
    jwt_public_key: str = os.getenv("JWT_PUBLIC_KEY_PEM", "")
    security_enabled: bool = os.getenv("SECURITY_ENABLED", "true").lower() == "true"
    cache_ttl_today_s: float = float(os.getenv("CACHE_TTL_TODAY_S", "5"))


class SimpleTTLCache:
    """Cache-aside em memoria; em prod: Redis (Azure Cache for Redis /
    Memorystore) compartilhado entre replicas."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[float, object]] = {}
        self._lock = threading.Lock()

    def get(self, key: str, ttl: float):
        with self._lock:
            hit = self._store.get(key)
            if hit and (time.time() - hit[0]) < ttl:
                return hit[1]
            return None

    def put(self, key: str, value: object) -> None:
        with self._lock:
            self._store[key] = (time.time(), value)

    def invalidate_prefix(self, prefix: str) -> None:
        with self._lock:
            for k in [k for k in self._store if k.startswith(prefix)]:
                del self._store[k]


class LancamentosReadClient:
    """Cliente HTTP resiliente para consulta ao servico de lancamentos
    (reprocessamento/reconciliacao). Timeout curto + retry limitado +
    circuit breaker simples — falha aqui NAO derruba a API de consolidado."""

    def __init__(self, base_url: str | None) -> None:
        self.base_url = base_url
        self._failures = 0
        self._open_until = 0.0

    @property
    def _circuit_open(self) -> bool:
        return time.time() < self._open_until

    def buscar_lancamentos(self, merchant_id: str, inicio: str, fim: str) -> list[dict]:
        if not self.base_url or self._circuit_open:
            return []
        import httpx

        for attempt in range(3):
            try:
                r = httpx.get(
                    f"{self.base_url}/lancamentos",
                    params={"inicio": inicio, "fim": fim},
                    headers={
                        "Authorization": f"Bearer {os.getenv('LANCAMENTOS_TOKEN', '')}",
                        "X-Correlation-Id": new_correlation_id(),
                    },
                    timeout=2.0,
                )
                r.raise_for_status()
                self._failures = 0
                return r.json().get("itens", [])
            except Exception as exc:  # noqa: BLE001
                self._failures += 1
                logger.log_event(40, "read_client_retry", attempt=attempt, error=str(exc))
                if self._failures >= 5:
                    self._open_until = time.time() + 30  # abre por 30s
                time.sleep(0.2 * (attempt + 1))
        return []


# --------------------------------------------------------------------------
class EventoIn(BaseModel):
    """Payload bruto do evento (compativel com shared.event_schema)."""

    model_config = {"extra": "allow"}


def create_app(
    processor: EventProcessor | None = None,
    broker: FakeBrokerQueue | None = None,
    settings: Settings | None = None,
) -> FastAPI:
    settings = settings or Settings()
    os.makedirs(settings.db_path and os.path.dirname(settings.db_path) or ".", exist_ok=True)
    processor = processor or EventProcessor(settings.db_path)
    broker = broker or FakeBrokerQueue()
    worker = ConsolidadoWorker(broker, processor)
    worker.start()
    cache = SimpleTTLCache()

    app = FastAPI(
        title="Servico de Consolidado Diario",
        version="1.0.0",
        description="Relatorio de saldo diario consolidado (read-model event-driven)",
    )

    @app.middleware("http")
    async def envelope(request: Request, call_next):
        new_correlation_id(request.headers.get("X-Correlation-Id"))
        start = time.perf_counter()
        response = await call_next(request)
        dur_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Correlation-Id"] = new_correlation_id(
            request.headers.get("X-Correlation-Id")
        )
        logger.log_event(
            20, "http_access", method=request.method, path=request.url.path,
            status=response.status_code, duration_ms=dur_ms,
        )
        return response

    def require_auth(required_scopes: list[str]):
        def dep(request: Request, authorization: str | None = Header(default=None)) -> Principal:
            if not settings.security_enabled:
                return Principal(
                    subject="dev",
                    merchant_id=request.headers.get("X-Merchant-Id", "M001"),
                    scopes=frozenset(required_scopes),
                )
            if not authorization or not authorization.lower().startswith("bearer "):
                raise AuthError("missing bearer token", 401)
            p = validate_token(
                authorization.split(" ", 1)[1],
                public_pem=settings.jwt_public_key,
                required_scopes=required_scopes,
            )
            mid_query = request.query_params.get("merchant_id")
            if mid_query and mid_query != p.merchant_id:
                raise AuthError("acesso negado a outro merchant", 403)
            return p

        return dep

    @app.exception_handler(AuthError)
    async def _auth_exc(_, exc: AuthError):
        return JSONResponse(status_code=exc.status_code, content={"type": "auth", "title": str(exc)})

    # ---------- ops ----------
    @app.get("/healthz", tags=["ops"])
    def healthz():
        return {"status": "UP", "service": SERVICE}

    @app.get("/readyz", tags=["ops"])
    def readyz():
        return {"status": "READY", "worker_alive": worker.is_alive()}

    @app.get("/metrics", tags=["ops"])
    def metrics():
        """Formato Prometheus-like simplificado (prod: prometheus-fastapi-instrumentator)."""
        s = processor.stats
        body = (
            "# HELP consolidado_events_total eventos processados\n"
            "# TYPE consolidado_events_total counter\n"
            f"consolidado_events_processed_total {s.processados}\n"
            f"consolidado_events_duplicate_total {s.duplicados}\n"
            f"consolidado_events_error_total {s.erros}\n"
            f"consolidado_events_dlq_total {s.dlq}\n"
            f"consolidado_queue_depth {len(broker)}\n"
        )
        return JSONResponse(content={"raw_prometheus": body.strip().splitlines()})

    # ---------- ingestao (via fila/broker no modo demo) ----------
    @app.post("/events", status_code=202, tags=["ingestao"])
    def ingestar(evento: dict, principal: Principal = Depends(require_auth(["consolidado:ingest"]))):
        """Endpoint de ingestao usado apenas pelo relay local/demo. Em prod o
        consumo e feito direto do broker (Kafka/PubSub), sem HTTP exposto."""
        ev = from_json(evento).model_dump(mode="json")
        broker.put(ev)
        cache.invalidate_prefix(f"{ev['merchant_id']}:")
        return {"status": "queued"}

    # ---------- RF-05: relatorio de saldo diario consolidado ----------
    @app.get("/relatorio/dia/{dia}", tags=["relatorio"])
    def relatorio_dia(
        dia: str,
        principal: Principal = Depends(require_auth(["consolidado:read"])),
    ):
        chave = f"{principal.merchant_id}:{dia}"
        hoje = time.strftime("%Y-%m-%d")
        ttl = settings.cache_ttl_today_s if dia == hoje else 86_400  # dia fechado: cache longo
        hit = cache.get(chave, ttl)
        if hit is not None:
            return {**hit, "_cache": "HIT"}
        dados = processor.obter_consolidado(principal.merchant_id, dia)
        if dados is None:
            dados = {
                "merchant_id": principal.merchant_id,
                "dia": dia,
                "total_creditos_centavos": 0,
                "total_debitos_centavos": 0,
                "saldo_centavos": 0,
                "qtd_lancamentos": 0,
                "atualizado_em": None,
            }
        cache.put(chave, dados)
        return {**dados, "_cache": "MISS"}

    @app.get("/relatorio/periodo", tags=["relatorio"])
    def relatorio_periodo(
        inicio: str,
        fim: str,
        principal: Principal = Depends(require_auth(["consolidado:read"])),
    ):
        itens = processor.listar_por_periodo(principal.merchant_id, inicio, fim)
        saldo_acumulado = sum(i["saldo_centavos"] for i in itens)
        return {
            "merchant_id": principal.merchant_id,
            "inicio": inicio,
            "fim": fim,
            "dias": len(itens),
            "saldo_acumulado_centavos": saldo_acumulado,
            "itens": itens,
        }

    # ---------- resiliencia operacional ----------
    @app.post("/admin/rebuild", tags=["ops"], status_code=202)
    async def rebuild(
        request: Request,
        principal: Principal = Depends(require_auth(["consolidado:admin"])),
    ):
        try:
            body = await request.json()
        except Exception:
            body = {}
        """Reprocessa o periodo a partir do event store (recupera projecao
        corrompida/perdida sem depender do servico de lancamentos)."""
        inicio = body.get("inicio", "2000-01-01")
        fim = body.get("fim", "2100-01-01")
        resultado = processor.rebuild_periodo(principal.merchant_id, inicio, fim)
        cache.invalidate_prefix(principal.merchant_id + ":")
        return {"dias_reprocessados": len(resultado)}

    app.state.processor = processor
    app.state.broker = broker
    app.state.worker = worker
    app.state.settings = settings
    return app
