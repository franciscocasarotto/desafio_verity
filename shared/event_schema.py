"""Contrato de eventos entre os servicos (Event Schema = fronteira integrada).

Versionamento por `schema_version` + topic naming com sufixo de versao
(lancamentos.v1) permite evolucao sem quebrar consumidores (Compatibilidade:
adicionar campos opcionais e retro/nano-compativel).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EventType(str, Enum):
    LANCAMENTO_CRIADO = "LancamentoCriado"
    LANCAMENTO_CANCELADO = "LancamentoCancelado"


class EventoBase(BaseModel):
    """Envelope CloudEvents-like (simplificado) para todos os eventos."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    schema_version: int = 1
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    merchant_id: str
    correlation_id: str = "-"
    source: str = "lancamentos-service"


class LancamentoCriado(EventoBase):
    event_type: EventType = EventType.LANCAMENTO_CRIADO
    lancamento_id: str
    tipo: str  # DEBITO | CREDITO
    valor_centavos: int
    data_vencimento: str  # YYYY-MM-DD (data de competencia do caixa)
    descricao: str


class LancamentoCancelado(EventoBase):
    event_type: EventType = EventType.LANCAMENTO_CANCELADO
    lancamento_id: str
    motivo: str | None = None


def to_json(event: EventoBase) -> str:
    import json

    return event.model_dump_json()


def from_json(payload: str | dict[str, Any]) -> EventoBase:
    data = payload if isinstance(payload, dict) else __import__("json").loads(payload)
    et = data.get("event_type")
    if et == EventType.LANCAMENTO_CRIADO.value or et == "LancamentoCriado":
        return LancamentoCriado.model_validate(data)
    if et == EventType.LANCAMENTO_CANCELADO.value or et == "LancamentoCancelado":
        return LancamentoCancelado.model_validate(data)
    raise ValueError(f"evento desconhecido: {et}")
