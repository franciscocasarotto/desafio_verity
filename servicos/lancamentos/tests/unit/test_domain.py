import pytest
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

from src.domain.models import (
    Lancamento, TipoLancamento, ValorInvalidoError, DataFuturaError, LancamentoError
)


class TestLancamento:
    def test_deve_criar_lancamento_valido(self):
        lanc = Lancamento(
            tipo=TipoLancamento.CREDITO,
            valor=Decimal("100.00"),
            categoria="Vendas",
            data=date.today(),
            descricao="Venda balcão"
        )
        assert lanc.valor == Decimal("100.00")
        assert lanc.valor_assinado == Decimal("100.00")

    def test_deve_rejeitar_valor_zero(self):
        with pytest.raises(ValorInvalidoError):
            Lancamento(
                tipo=TipoLancamento.DEBITO, valor=Decimal("0"),
                categoria="X", data=date.today(), descricao="Y"
            )

    def test_deve_rejeitar_data_futura(self):
        with pytest.raises(DataFuturaError):
            Lancamento(
                tipo=TipoLancamento.CREDITO, valor=Decimal("10"),
                categoria="X", data=date.today() + timedelta(days=1), descricao="Y"
            )

    def test_debito_deve_ter_valor_assinado_negativo(self):
        lanc = Lancamento(
            tipo=TipoLancamento.DEBITO, valor=Decimal("50"),
            categoria="Fornecedor", data=date.today(), descricao="Compra"
        )
        assert lanc.valor_assinado == Decimal("-50")

    def test_deve_rejeitar_descricao_vazia(self):
        with pytest.raises(LancamentoError):
            Lancamento(
                tipo=TipoLancamento.CREDITO, valor=Decimal("10"),
                categoria="X", data=date.today(), descricao="   "
            )