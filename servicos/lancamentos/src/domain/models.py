"""Domínio puro — sem dependências de framework."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4


class TipoLancamento(str, Enum):
    DEBITO = "DEBITO"
    CREDITO = "CREDITO"


class LancamentoError(Exception):
    """Exceção base do domínio."""


class ValorInvalidoError(LancamentoError):
    pass


class DataFuturaError(LancamentoError):
    pass


@dataclass(frozen=True)
class Lancamento:
    """Entidade de domínio — imutável por design."""
    id: UUID = field(default_factory=uuid4)
    tipo: TipoLancamento = None
    valor: Decimal = None
    categoria: str = None
    data: date = None
    descricao: str = None
    criado_em: datetime = field(default_factory=datetime.utcnow)
    atualizado_em: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.valor is None or self.valor <= Decimal("0"):
            raise ValorInvalidoError(f"Valor deve ser > 0, recebido: {self.valor}")
        if self.data > date.today():
            raise DataFuturaError(f"Data não pode ser futura: {self.data}")
        if not self.descricao or not self.descricao.strip():
            raise LancamentoError("Descrição obrigatória")

    @property
    def valor_assinado(self) -> Decimal:
        """Crédito soma, débito subtrai."""
        return self.valor if self.tipo == TipoLancamento.CREDITO else -self.valor