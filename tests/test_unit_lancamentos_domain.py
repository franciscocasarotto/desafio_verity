"""Testes unitarios do dominio de Lancamentos (regras puras, sem I/O)."""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from services.lancamentos.app.domain.models import (
    ConflictError,
    Lancamento,
    TipoLancamento,
    ValidationError,
)


def _l(**kw) -> Lancamento:
    base = dict(
        merchant_id="M1",
        tipo=TipoLancamento.CREDITO,
        valor_centavos=1000,
        data_vencimento=date.today(),
        descricao="venda balcao",
    )
    base.update(kw)
    return Lancamento(**base)


class TestInvariantes:
    def test_valor_zero_ou_negativo_e_rejeitado(self):
        with pytest.raises(ValidationError):
            _l(valor_centavos=0)
        with pytest.raises(ValidationError):
            _l(valor_centavos=-5)

    def test_descricao_vazia_rejeitada(self):
        with pytest.raises(ValidationError):
            _l(descricao="   ")

    def test_horizonte_futuro_max_365_dias(self):
        with pytest.raises(ValidationError):
            _l(data_vencimento=date.today() + timedelta(days=400))
        # dentro do horizonte ok
        _l(data_vencimento=date.today() + timedelta(days=300))

    def test_debito_acima_teto_antifraude(self):
        with pytest.raises(ValidationError):
            _l(tipo=TipoLancamento.DEBITO, valor_centavos=2_000_000_000_00)

    def test_credito_acima_teto_antifraude_liberado(self):
        l = _l(valor_centavos=2_000_000_000_00)  # creditos nao tem teto aqui
        assert l.valor_com_signo() == 2_000_000_000_00


class TestComportamento:
    def test_valor_com_signo(self):
        assert _l().valor_com_signo() == 1000
        assert _l(tipo=TipoLancamento.DEBITO).valor_com_signo() == -1000

    def test_cancelamento_transiciona_estado(self):
        l = _l()
        l.cancelar("duplicidade")
        assert not l.esta_ativo
        assert l.motivo_cancelamento == "duplicidade"
        assert l.cancelado_em is not None

    def test_cancelar_duas_vezes_conflita(self):
        l = _l()
        l.cancelar()
        with pytest.raises(ConflictError):
            l.cancelar()
