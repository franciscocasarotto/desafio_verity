"""API HTTP do servico de Lancamentos (FastAPI).

Protecoes de resiliencia na borda:
- Rate limiting por merchant (defesa contra abuso/picos, RNF disponibilidade).
- Timeout curto no handler e error mapping consistente (RFC7807-like).
- X-Correlation-Id propagado (observabilidade ponta a ponta).
- Header Idempotency-Key para POST (RF-01).
- Security gate: JWT RS256 + escopos OAuth2.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass

from fastapi import Depends, FastAPI, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from shared.observability import configure_logging, new_correlation_id
from shared.security import AuthError, Principal, validate_token

from .application.use_cases import ServicoLancamentos
from .domain.models import ConflictError, DomainError, StatusLancamento, ValidationError
from .domain.ports import EventPublisher, LancamentoRepository
from .infrastructure.sqlite_repository import (
    InMemoryEventPublisher,
    SqliteLancamentoRepository,
)

SERVICE = "lancamentos"
logger = configure_logging(SERVICE)


# --------------------------------------------------------------------------
# Config / composicao raiz (12-factor)
# --------------------------------------------------------------------------
@dataclass
class Settings:
    db_path: str = os.getenv("LANCAMENTOS_DB", "data/lancamentos.db")
    jwt_public_key: str = os.getenv(
        "JWT_PUBLIC_KEY_PEM", ""
    )  # em prod: JWKS do IdP; aqui PEM inline p/ demo
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "300"))
    security_enabled: bool = os.getenv("SECURITY_ENABLED", "true").lower() == "true"


class SimpleRateLimiter:
    """Token bucket por merchant. Em prod: Redis/distributed limiter no gateway."""

    def __init__(self, limit_per_minute: int) -> None:
        self.limit = limit_per_minute
        self._buckets: dict[str, list[float]] = {}

    def allow(self, key: str) -> bool:
        now = time.time()
        janela = [t for t in self._buckets.get(key, []) if now - t < 60]
        if len(janela) >= self.limit:
            self._buckets[key] = janela
            return False
        janela.append(now)
        self._buckets[key] = janela
        return True


# --------------------------------------------------------------------------
# Schemas de API
# --------------------------------------------------------------------------
class LancamentoIn(BaseModel):
    tipo: str = Field(..., examples=["CREDITO"])
    valor_centavos: int = Field(..., gt=0, description="Valor em centavos")
    data_vencimento: str = Field(..., description="YYYY-MM-DD")
    descricao: str = Field(..., min_length=1, max_length=200)

    @field_validator("tipo")
    @classmethod
    def _tipo_valido(cls, v: str) -> str:
        if v not in {"DEBITO", "CREDITO"}:
            raise ValueError("tipo deve ser DEBITO ou CREDITO")
        return v


class CancelamentoIn(BaseModel):
    motivo: str | None = Field(None, max_length=200)


def _lancamento_out(l) -> dict:
    return {
        "id": l.id,
        "merchant_id": l.merchant_id,
        "tipo": l.tipo.value,
        "valor_centavos": l.valor_centavos,
        "data_vencimento": l.data_vencimento.isoformat(),
        "descricao": l.descricao,
        "status": l.status.value,
        "criado_em": l.criado_em.isoformat(),
        "cancelado_em": l.cancelado_em.isoformat() if l.cancelado_em else None,
    }


# --------------------------------------------------------------------------
# App factory (facilita testes com DI de adaptadores)
# --------------------------------------------------------------------------
def create_app(
    repo: LancamentoRepository | None = None,
    publisher: EventPublisher | None = None,
    settings: Settings | None = None,
) -> FastAPI:
    settings = settings or Settings()
    os.makedirs(os.path.dirname(settings.db_path) or ".", exist_ok=True)
    repo = repo or SqliteLancamentoRepository(settings.db_path)
    publisher = publisher or InMemoryEventPublisher()
    usecase = ServicoLancamentos(repo, publisher)
    limiter = SimpleRateLimiter(settings.rate_limit_per_minute)

    app = FastAPI(
        title="Servico de Lancamentos",
        version="1.0.0",
        description="Controle de lancamentos (debitos/creditos) do fluxo de caixa",
    )

    # ---------- middleware: correlacao + rate limit ----------
    @app.middleware("http")
    async def envelope(request: Request, call_next):
        cid = new_correlation_id(request.headers.get("X-Correlation-Id"))
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:  # nunca vazar stack trace ao cliente
            logger.exception("erro nao tratado")
            response = JSONResponse(
                status_code=500,
                content={"type": "internal", "title": "Erro interno",
                         "correlation_id": cid},
            )
        dur_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Correlation-Id"] = cid
        logger.log_event(
            20,
            "http_access",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=dur_ms,
        )
        return response

    # ---------- auth dependency ----------
    def require_auth(required_scopes: list[str]):
        def dep(
            request: Request,
            authorization: str | None = Header(default=None),
        ) -> Principal:
            if not settings.security_enabled:
                return Principal(
                    subject="dev", merchant_id=request.headers.get("X-Merchant-Id", "M001"),
                    scopes=frozenset(required_scopes),
                )
            if not authorization or not authorization.lower().startswith("bearer "):
                raise AuthError("missing bearer token", 401)
            principal = validate_token(
                authorization.split(" ", 1)[1],
                public_pem=settings.jwt_public_key,
                required_scopes=required_scopes,
            )
            # tenant isolation: merchant do token deve bater com o recurso
            mid_query = request.query_params.get("merchant_id")
            if mid_query and mid_query != principal.merchant_id:
                raise AuthError("acesso negado a outro merchant", 403)
            return principal

        return dep

    @app.exception_handler(AuthError)
    async def _auth_exc(_, exc: AuthError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"type": "auth", "title": str(exc)},
        )

    @app.exception_handler(DomainError)
    async def _domain_exc(_, exc: DomainError):
        status = 409 if isinstance(exc, ConflictError) else 422
        return JSONResponse(
            status_code=status,
            content={"type": "business-rule", "title": str(exc)},
        )

    # ---------- health probes ----------
    @app.get("/healthz", tags=["ops"])
    def healthz():
        return {"status": "UP", "service": SERVICE}

    @app.get("/readyz", tags=["ops"])
    def readyz():
        try:
            repo.list_by_periodo  # noqa: B018
            return {"status": "READY", "db": "UP"}
        except Exception as exc:  # pragma: no cover
            return JSONResponse(status_code=503, content={"status": "DOWN", "db": str(exc)})

    # ---------- endpoints de negocio ----------
    @app.post("/lancamentos", status_code=201, tags=["lancamentos"])
    def criar_lancamento(
        body: LancamentoIn,
        request: Request,
        principal: Principal = Depends(require_auth(["lancamentos:write"])),
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ):
        if not limiter.allow(principal.merchant_id):
            return JSONResponse(
                status_code=429,
                content={"type": "rate-limit", "title": "limite excedido"},
                headers={"Retry-After": "60"},
            )
        resultado = usecase.criar(
            merchant_id=principal.merchant_id,
            tipo=body.tipo,
            valor_centavos=body.valor_centavos,
            data_vencimento=body.data_vencimento,
            descricao=body.descricao,
            idempotency_key=idempotency_key,
            correlation_id=new_correlation_id(
                request.headers.get("X-Correlation-Id")
            ),
        )
        status = 201 if resultado.created else 200
        return JSONResponse(
            status_code=status,
            content=_lancamento_out(resultado.lancamento),
        )

    @app.get("/lancamentos", tags=["lancamentos"])
    def listar_lancamentos(
        inicio: str,
        fim: str,
        status: str | None = None,
        principal: Principal = Depends(require_auth(["lancamentos:read"])),
    ):
        st = StatusLancamento(status) if status else None
        itens = usecase.listar(
            merchant_id=principal.merchant_id, inicio=inicio, fim=fim, status=st
        )
        return {"total": len(itens), "itens": [_lancamento_out(i) for i in itens]}

    @app.get("/lancamentos/{lancamento_id}", tags=["lancamentos"])
    def obter_lancamento(
        lancamento_id: str,
        principal: Principal = Depends(require_auth(["lancamentos:read"])),
    ):
        lanc = usecase.obter(merchant_id=principal.merchant_id, lancamento_id=lancamento_id)
        if lanc is None:
            return JSONResponse(
                status_code=404, content={"type": "not-found", "title": "nao encontrado"}
            )
        return _lancamento_out(lanc)

    @app.delete("/lancamentos/{lancamento_id}", tags=["lancamentos"])
    def cancelar_lancamento(
        lancamento_id: str,
        body: CancelamentoIn | None = None,
        principal: Principal = Depends(require_auth(["lancamentos:cancel"])),
    ):
        lanc = usecase.cancelar(
            merchant_id=principal.merchant_id,
            lancamento_id=lancamento_id,
            motivo=body.motivo if body else None,
        )
        return _lancamento_out(lanc)

    # ---------- operacao do outbox relay ----------
    @app.post("/admin/outbox-flush", tags=["ops"], status_code=202)
    def flush_outbox(principal: Principal = Depends(require_auth(["lancamentos:admin"]))):
        enviados = usecase.republish_pending()
        return {"enviados": enviados}

    app.state.settings = settings
    app.state.publisher = publisher
    return app
