"""Domain model do servico de Lancamentos (Camada 1 - Core Business).

Regras de negocio puras, sem dependencia de framework/infra:
- Valor monetario em centavos (int) -> evita erro de ponto flutuante.
- Idempotencia por chave de idempotencia + hash do payload.
- Cancelamento e estorno logico (nunca delecao): audita e re-emite evento.
- Validacoes de invariantes (data, tipo, valor > 0).
"""
from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum


class TipoLancamento(str, Enum):
    DEBITO = "DEBITO"
    CREDITO = "CREDITO"


class StatusLancamento(str, Enum):
    ATIVO = "ATIVO"
    CANCELADO = "CANCELADO"


class DomainError(Exception):
    """Erro de regra de negocio (mapeado para HTTP 422/409 na borda)."""


class ValidationError(DomainError):
    pass


class ConflictError(DomainError):
    """Violacao de idempotencia / recurso ja existente (HTTP 409)."""


def parse_date(valor: str) -> date:
    try:
        return date.fromisoformat(valor)
    except ValueError as exc:
        raise ValidationError(f"data invalida (esperado YYYY-MM-DD): {valor}") from exc


def payload_hash(*parts: object) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(str(p).encode("utf-8"))
        h.update(b"|")
    return h.hexdigest()[:32]


@dataclass
class Lancamento:
    merchant_id: str
    tipo: TipoLancamento
    valor_centavos: int
    data_vencimento: date
    descricao: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: StatusLancamento = StatusLancamento.ATIVO
    idempotency_key: str | None = None
    payload_hash: str = field(default_factory=lambda: payload_hash(uuid.uuid4()))
    criado_em: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    cancelado_em: datetime | None = None
    motivo_cancelamento: str | None = None

    def __post_init__(self) -> None:
        if self.valor_centavos <= 0:
            raise ValidationError("valor_centavos deve ser > 0")
        if not self.merchant_id:
            raise ValidationError("merchant_id obrigatorio")
        if not self.descricao.strip():
            raise ValidationError("descricao obrigatoria")
        hoje = datetime.now(timezone.utc).date()
        # Regra de negocio: lancamento nao pode referir-se a competencia futura
        # alem de um horizonte operacional razoavel (aqui: hoje + 365 dias).
        if self.data_vencimento > hoje + __import__("datetime").timedelta(days=365):
            raise ValidationError("data_vencimento fora do horizonte permitido")
        if self.tipo == TipoLancamento.DEBITO and self.valor_centavos > 1_000_000_000_00:
            raise ValidationError("debito acima do teto antifraude (R$ 1 bi)")

    # --- Comportamentos de dominio -------------------------------------
    def valor_com_signo(self) -> int:
        """Contribuicao para o saldo: credito soma, debito subtrai."""
        return (
            self.valor_centavos
            if self.tipo == TipoLancamento.CREDITO
            else -self.valor_centavos
        )

    def cancelar(self, motivo: str | None = None) -> None:
        if self.status == StatusLancamento.CANCELADO:
            raise ConflictError("lancamento ja cancelado")
        self.status = StatusLancamento.CANCELADO
        self.cancelado_em = datetime.now(timezone.utc)
        self.motivo_cancelamento = motivo

    @property
    def esta_ativo(self) -> bool:
        return self.status == StatusLancamento.ATIVO


@dataclass
class ResultadoIdempotente:
    """Indica se a criacao foi nova ou reaproveitada pela chave de idempotencia."""

    lancamento: Lancamento
    created: bool
