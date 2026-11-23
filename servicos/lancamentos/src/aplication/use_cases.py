"""Casos de uso — orquestram domínio + ports."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from src.domain.models import Lancamento, TipoLancamento
from src.application.ports import LancamentoRepository, EventPublisher


@dataclass
class CriarLancamentoUseCase:
    repo: LancamentoRepository
    publisher: EventPublisher

    def execute(self, tipo: TipoLancamento, valor: Decimal, categoria: str,
                data: date, descricao: str) -> Lancamento:
        lancamento = Lancamento(
            tipo=tipo, valor=valor, categoria=categoria,
            data=data, descricao=descricao
        )
        self.repo.save(lancamento)
        self.publisher.publish({
            "type": "LancamentoRegistrado",
            "operation": "CREATE",
            "payload": {
                "id": str(lancamento.id),
                "tipo": lancamento.tipo.value,
                "valor": str(lancamento.valor),
                "data": lancamento.data.isoformat(),
            }
        })
        return lancamento