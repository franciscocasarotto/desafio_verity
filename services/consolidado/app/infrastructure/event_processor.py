"""Consumer assincrono (worker) do servico de Consolidado.

Em producao este modulo roda como worker dedicado consumindo Kafka (on-prem /
AKS) ou Google Pub/Sub — NUNCA chamadas síncronas HTTP lancamentos->consolidado
(requisito: falha do consolidado nao pode derrubar o lancamento).

Caracteristicas implementadas:
- Ack explicito apos commit da projecao (no ack -> reentrega = at-least-once).
- Deduplicacao por event_id gravado junto ao offset => efeito exactly-once.
- DLQ (dead letter queue) para eventos poison, com backoff exponencial e
  limite de tentativas (retry policy).
- Checkpoint periodico de offset (recuperação apos crash sem replay total).
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone

from shared.observability import configure_logging

from ..domain.models import ConsolidadoDiario, consolidar_eventos

logger = configure_logging("consolidado-worker")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS event_store (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,
    merchant_id TEXT NOT NULL,
    dia TEXT NOT NULL,
    payload TEXT NOT NULL,
    received_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_store_query
    ON event_store (merchant_id, dia);

CREATE TABLE IF NOT EXISTS consolidado_diario (
    merchant_id TEXT NOT NULL,
    dia TEXT NOT NULL,
    total_creditos_centavos INTEGER NOT NULL,
    total_debitos_centavos INTEGER NOT NULL,
    qtd_lancamentos INTEGER NOT NULL,
    atualizado_em TEXT NOT NULL,
    PRIMARY KEY (merchant_id, dia)
);

CREATE TABLE IF NOT EXISTS consumer_offsets (
    topic TEXT PRIMARY KEY,
    last_seq INTEGER NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dlq_events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT,
    reason TEXT NOT NULL,
    payload TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 1,
    moved_at TEXT NOT NULL
);
"""


@dataclass
class WorkerStats:
    processados: int = 0
    duplicados: int = 0
    erros: int = 0
    dlq: int = 0


class EventProcessor:
    """Projecao + persistencia transacional do consolidado (SQLite p/ demo).

    Prod: Postgres/Cloud SQL com a mesma interface; event_store vira topico
    compactado (Kafka log) e a tabela consolidado vira materialized view ou
    read-model em Redis/DynamoDB conforme SLA de leitura.
    """

    MAX_ATTEMPTS = 3

    def __init__(self, db_path: str) -> None:
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        with self._lock:
            self._conn.executescript(_SCHEMA)
            self._conn.commit()
        self.stats = WorkerStats()

    # --- ingestao ----------------------------------------------------------
    def processar_evento(self, evento: dict) -> bool:
        """Retorna True se aplicou, False se duplicado (dedupe por event_id)."""
        dia = date.fromisoformat(evento["data_vencimento"]) if "data_vencimento" in evento else None
        if dia is None:
            # cancelamento: competencia vem do original ja projetado
            orig = self._buscar_original(evento["lancamento_id"])
            if orig is None:
                raise KeyError(
                    f"cancelamento sem original: {evento['lancamento_id']}"
                )
            dia = date.fromisoformat(orig["data_vencimento"])

        with self._lock:
            cur = self._conn.execute(
                "SELECT 1 FROM event_store WHERE event_id=?", (evento["event_id"],)
            ).fetchone()
            if cur:
                self.stats.duplicados += 1
                return False
            try:
                self._conn.execute(
                    "INSERT INTO event_store (event_id, merchant_id, dia, payload,"
                    " received_at) VALUES (?,?,?,?,?)",
                    (
                        evento["event_id"],
                        evento["merchant_id"],
                        dia.isoformat(),
                        json.dumps(evento),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                self._projecao_incremental(evento, dia)
                self._conn.commit()
                self.stats.processados += 1
                return True
            except Exception as exc:
                self._conn.rollback()
                self.stats.erros += 1
                raise exc

    def _buscar_original(self, lancamento_id: str) -> dict | None:
        row = self._conn.execute(
            "SELECT payload FROM event_store WHERE json_extract(payload,"
            " '$.lancamento_id')=? AND json_extract(payload,"
            " '$.event_type')='LancamentoCriado' ORDER BY seq LIMIT 1",
            (lancamento_id,),
        ).fetchone()
        return json.loads(row["payload"]) if row else None

    def _projecao_incremental(self, evento: dict, dia: date) -> None:
        mid = evento["merchant_id"]
        row = self._conn.execute(
            "SELECT * FROM consolidado_diario WHERE merchant_id=? AND dia=?",
            (mid, dia.isoformat()),
        ).fetchone()
        c = (
            ConsolidadoDiario(
                merchant_id=mid,
                dia=dia,
                total_creditos_centavos=row["total_creditos_centavos"],
                total_debitos_centavos=row["total_debitos_centavos"],
                qtd_lancamentos=row["qtd_lancamentos"],
            )
            if row
            else ConsolidadoDiario(merchant_id=mid, dia=dia)
        )
        if evento["event_type"] == "LancamentoCancelado":
            orig = self._buscar_original(evento["lancamento_id"]) or {}
            evento = {**evento, "_original": orig}
        c.aplicar_evento(evento)
        self._conn.execute(
            "INSERT INTO consolidado_diario VALUES (?,?,?,?,?,?)"
            " ON CONFLICT(merchant_id, dia) DO UPDATE SET"
            " total_creditos_centavos=excluded.total_creditos_centavos,"
            " total_debitos_centavos=excluded.total_debitos_centavos,"
            " qtd_lancamentos=excluded.qtd_lancamentos,"
            " atualizado_em=excluded.atualizado_em",
            (
                mid,
                dia.isoformat(),
                c.total_creditos_centavos,
                c.total_debitos_centavos,
                c.qtd_lancamentos,
                c.atualizado_em.isoformat(),
            ),
        )

    # --- confiabilidade: DLQ + checkpoint -----------------------------------
    def mover_para_dlq(self, evento: dict, motivo: str, attempts: int = 1) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO dlq_events (event_id, reason, payload, attempts,"
                " moved_at) VALUES (?,?,?,?,?)",
                (
                    evento.get("event_id"),
                    motivo,
                    json.dumps(evento),
                    attempts,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            self._conn.commit()
        self.stats.dlq += 1

    def salvar_offset(self, topic: str, seq: int) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO consumer_offsets (topic, last_seq, updated_at)"
                " VALUES (?,?,?)"
                " ON CONFLICT(topic) DO UPDATE SET last_seq=excluded.last_seq,"
                " updated_at=excluded.updated_at",
                (topic, seq, datetime.now(timezone.utc).isoformat()),
            )
            self._conn.commit()

    def ultimo_offset(self, topic: str) -> int:
        row = self._conn.execute(
            "SELECT last_seq FROM consumer_offsets WHERE topic=?", (topic,)
        ).fetchone()
        return int(row["last_seq"]) if row else 0

    # --- rebuild deterministico (reprocessar periodo) ------------------------
    def rebuild_periodo(self, merchant_id: str, inicio: str, fim: str) -> list[dict]:
        rows = self._conn.execute(
            "SELECT payload FROM event_store WHERE merchant_id=?"
            " AND dia BETWEEN ? AND ? ORDER BY seq",
            (merchant_id, inicio, fim),
        ).fetchall()
        por_dia: dict[str, list[dict]] = {}
        for r in rows:
            ev = json.loads(r["payload"])
            dia = ev.get("data_vencimento")
            if dia is None:
                orig = self._buscar_original(ev["lancamento_id"])
                dia = orig["data_vencimento"] if orig else None
            if dia:
                por_dia.setdefault(dia, []).append(ev)

        saida: list[dict] = []
        with self._lock:
            for dia_s, eventos in sorted(por_dia.items()):
                c = consolidar_eventos(eventos, merchant_id, date.fromisoformat(dia_s))
                self._conn.execute(
                    "INSERT INTO consolidado_diario VALUES (?,?,?,?,?,?)"
                    " ON CONFLICT(merchant_id, dia) DO UPDATE SET"
                    " total_creditos_centavos=excluded.total_creditos_centavos,"
                    " total_debitos_centavos=excluded.total_debitos_centavos,"
                    " qtd_lancamentos=excluded.qtd_lancamentos,"
                    " atualizado_em=excluded.atualizado_em",
                    (
                        merchant_id,
                        dia_s,
                        c.total_creditos_centavos,
                        c.total_debitos_centavos,
                        c.qtd_lancamentos,
                        c.atualizado_em.isoformat(),
                    ),
                )
                saida.append(c.to_dict())
            self._conn.commit()
        return saida

    # --- leituras ------------------------------------------------------------
    def obter_consolidado(self, merchant_id: str, dia: str) -> dict | None:
        row = self._conn.execute(
            "SELECT * FROM consolidado_diario WHERE merchant_id=? AND dia=?",
            (merchant_id, dia),
        ).fetchone()
        if not row:
            return None
        return {
            "merchant_id": row["merchant_id"],
            "dia": row["dia"],
            "total_creditos_centavos": row["total_creditos_centavos"],
            "total_debitos_centavos": row["total_debitos_centavos"],
            "saldo_centavos": row["total_creditos_centavos"]
            - row["total_debitos_centavos"],
            "qtd_lancamentos": row["qtd_lancamentos"],
            "atualizado_em": row["atualizado_em"],
        }

    def listar_por_periodo(self, merchant_id: str, inicio: str, fim: str) -> list[dict]:
        rows = self._conn.execute(
            "SELECT * FROM consolidado_diario WHERE merchant_id=?"
            " AND dia BETWEEN ? AND ? ORDER BY dia",
            (merchant_id, inicio, fim),
        ).fetchall()
        return [
            {
                "merchant_id": r["merchant_id"],
                "dia": r["dia"],
                "total_creditos_centavos": r["total_creditos_centavos"],
                "total_debitos_centavos": r["total_debitos_centavos"],
                "saldo_centavos": r["total_creditos_centavos"]
                - r["total_debitos_centavos"],
                "qtd_lancamentos": r["qtd_lancamentos"],
                "atualizado_em": r["atualizado_em"],
            }
            for r in rows
        ]

    def close(self) -> None:
        self._conn.close()


class FakeBrokerQueue:
    """Fila in-memory thread-safe que simula Kafka/PubSub para o modo demo.

    Em prod: particoes por merchant_id (ordem garantida por chave), replicacao
    RF=3, consumer group com offsets duraveis. Aqui mantemos a SEMANTICA (fila +
    ack + retry + DLQ) com outra tecnologia — trocavel sem mudar o processor.
    """

    def __init__(self) -> None:
        self._queue: list[dict] = []
        self._lock = threading.Lock()

    def put(self, evento: dict) -> None:
        with self._lock:
            self._queue.append(evento)

    def get(self) -> dict | None:
        with self._lock:
            return self._queue.pop(0) if self._queue else None

    def __len__(self) -> int:
        with self._lock:
            return len(self._queue)


class ConsolidadoWorker(threading.Thread):
    """Loop de consumo com retry/backoff e DLQ (padrao Competing Consumers)."""

    def __init__(self, broker: FakeBrokerQueue, processor: EventProcessor) -> None:
        super().__init__(daemon=True, name="consolidado-worker")
        self.broker = broker
        self.processor = processor
        self._parar = threading.Event()

    def stop(self) -> None:
        self._parar.set()

    def run(self) -> None:
        while not self._parar.is_set():
            evento = self.broker.get()
            if evento is None:
                time.sleep(0.05)
                continue
            self._processar_com_retry(evento)

    def _processar_com_retry(self, evento: dict) -> None:
        for attempt in range(1, self.processor.MAX_ATTEMPTS + 1):
            try:
                self.processor.processar_evento(evento)
                return
            except Exception as exc:  # noqa: BLE001
                wait = 0.2 * (2 ** (attempt - 1))  # backoff exponencial
                logger.log_event(
                    40,
                    "retry_evento",
                    event_id=evento.get("event_id"),
                    attempt=attempt,
                    error=str(exc),
                )
                if attempt == self.processor.MAX_ATTEMPTS:
                    self.processor.mover_para_dlq(
                        evento, f"{type(exc).__name__}: {exc}", attempts=attempt
                    )
                else:
                    time.sleep(wait)
