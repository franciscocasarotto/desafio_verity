"""Adaptador de persistencia SQLite (dev/on-prem) com Outbox Pattern.

Producao: Azure Database for PostgreSQL Flexible Server ou Google Cloud SQL,
usando o MESMO contrato `LancamentoRepository` — basta um adaptador
asyncpg/SQLAlchemy. SQLite foi escolhido para o desafio por zero-setup e
portabilidade ("rodar localmente"), sem degradar a arquitetura (Ports & Adapters).

Outbox Pattern: o evento de dominio e gravado na MESMA transacao do lancamento;
um relay faz o publish no broker -> entrega at-least-once, sem dual-write
entre banco e fila (fonte classicade inconsistencia).
"""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import date, datetime
from typing import Sequence

from ..domain.models import Lancamento, StatusLancamento, TipoLancamento
from ..domain.ports import EventPublisher, LancamentoRepository

_SCHEMA = """
CREATE TABLE IF NOT EXISTS lancamentos (
    id TEXT PRIMARY KEY,
    merchant_id TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('DEBITO','CREDITO')),
    valor_centavos INTEGER NOT NULL CHECK (valor_centavos > 0),
    data_vencimento TEXT NOT NULL,
    descricao TEXT NOT NULL,
    status TEXT NOT NULL,
    idempotency_key TEXT,
    payload_hash TEXT NOT NULL,
    criado_em TEXT NOT NULL,
    cancelado_em TEXT,
    motivo_cancelamento TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_idemp
    ON lancamentos (merchant_id, idempotency_key)
    WHERE idempotency_key IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_merchant_data
    ON lancamentos (merchant_id, data_vencimento, status);

CREATE TABLE IF NOT EXISTS outbox_events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,
    topic TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    published_at TEXT
);
"""


class SqliteLancamentoRepository(LancamentoRepository):
    def __init__(self, db_path: str) -> None:
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        with self._lock:
            self._conn.executescript(_SCHEMA)
            self._conn.commit()

    # --- helpers ---------------------------------------------------------
    @staticmethod
    def _to_row(l: Lancamento) -> tuple:
        return (
            l.id,
            l.merchant_id,
            l.tipo.value,
            l.valor_centavos,
            l.data_vencimento.isoformat(),
            l.descricao,
            l.status.value,
            l.idempotency_key,
            l.payload_hash,
            l.criado_em.isoformat(),
            l.cancelado_em.isoformat() if l.cancelado_em else None,
            l.motivo_cancelamento,
        )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Lancamento:
        return Lancamento(
            merchant_id=row["merchant_id"],
            tipo=TipoLancamento(row["tipo"]),
            valor_centavos=row["valor_centavos"],
            data_vencimento=date.fromisoformat(row["data_vencimento"]),
            descricao=row["descricao"],
            id=row["id"],
            status=StatusLancamento(row["status"]),
            idempotency_key=row["idempotency_key"],
            payload_hash=row["payload_hash"],
            criado_em=datetime.fromisoformat(row["criado_em"]),
            cancelado_em=(
                datetime.fromisoformat(row["cancelado_em"])
                if row["cancelado_em"]
                else None
            ),
            motivo_cancelamento=row["motivo_cancelamento"],
        )

    # --- porta LancamentoRepository --------------------------------------
    def add(self, lancamento: Lancamento) -> None:
        with self._lock:
            try:
                self._conn.execute(
                    "INSERT INTO lancamentos VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    self._to_row(lancamento),
                )
                self._conn.commit()
            except sqlite3.IntegrityError as exc:
                self._conn.rollback()
                raise RuntimeError("violacao de unicidade") from exc

    def get(self, lancamento_id: str) -> Lancamento | None:
        row = self._conn.execute(
            "SELECT * FROM lancamentos WHERE id = ?", (lancamento_id,)
        ).fetchone()
        return self._from_row(row) if row else None

    def find_by_idempotency_key(
        self, merchant_id: str, key: str
    ) -> Lancamento | None:
        row = self._conn.execute(
            "SELECT * FROM lancamentos WHERE merchant_id=? AND idempotency_key=?",
            (merchant_id, key),
        ).fetchone()
        return self._from_row(row) if row else None

    def update(self, lancamento: Lancamento) -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE lancamentos SET status=?, cancelado_em=?, "
                "motivo_cancelamento=? WHERE id=?",
                (
                    lancamento.status.value,
                    lancamento.cancelado_em.isoformat()
                    if lancamento.cancelado_em
                    else None,
                    lancamento.motivo_cancelamento,
                    lancamento.id,
                ),
            )
            self._conn.commit()

    def list_by_periodo(
        self, merchant_id: str, inicio: date, fim: date, status: str | None = None
    ) -> Sequence[Lancamento]:
        sql = (
            "SELECT * FROM lancamentos WHERE merchant_id=? "
            "AND data_vencimento BETWEEN ? AND ?"
        )
        params: list = [merchant_id, inicio.isoformat(), fim.isoformat()]
        if status:
            sql += " AND status=?"
            params.append(status)
        sql += " ORDER BY data_vencimento, criado_em"
        rows = self._conn.execute(sql, params).fetchall()
        return [self._from_row(r) for r in rows]

    # --- outbox (mesma base transacional do agregado) ---------------------
    def save_outbox_event(self, topic: str, event_dict: dict) -> int:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO outbox_events (event_id, topic, payload, created_at)"
                " VALUES (?,?,?,?)",
                (
                    event_dict["event_id"],
                    topic,
                    json.dumps(event_dict),
                    datetime.now().isoformat(),
                ),
            )
            self._conn.commit()
            return int(cur.lastrowid or 0)

    def fetch_unpublished(self, limit: int = 100) -> list[tuple[int, dict]]:
        rows = self._conn.execute(
            "SELECT seq, payload FROM outbox_events WHERE published_at IS NULL"
            " ORDER BY seq LIMIT ?",
            (limit,),
        ).fetchall()
        return [(r["seq"], json.loads(r["payload"])) for r in rows]

    def mark_published(self, seq: int) -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE outbox_events SET published_at=? WHERE seq=?",
                (datetime.now().isoformat(), seq),
            )
            self._conn.commit()

    def close(self) -> None:
        self._conn.close()


class InMemoryEventPublisher(EventPublisher):
    """Fake de broker para testes/dev (substituido por Kafka/PubSub em prod)."""

    def __init__(self) -> None:
        self.published: list[dict] = []

    def publish(self, event_dict: dict) -> None:
        self.published.append(event_dict)
