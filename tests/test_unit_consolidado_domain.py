"""Testes unitarios do dominio de Consolidado (projecao deterministica)."""
from __future__ import annotations

from datetime import date

import pytest

from services.consolidado.app.domain.models import ConsolidadoDiario, consolidar_eventos


def _criado(eid: str, tipo: str, valor: int, dia: str = "2026-11-24") -> dict:
    return {
        "event_id": eid,
        "event_type": "LancamentoCriado",
        "merchant_id": "M1",
        "lancamento_id": f"L-{eid}",
        "tipo": tipo,
        "valor_centavos": valor,
        "data_vencimento": dia,
        "descricao": "x",
    }


def _cancelado(eid: str, lanc_id: str) -> dict:
    return {
        "event_id": eid,
        "event_type": "LancamentoCancelado",
        "merchant_id": "M1",
        "lancamento_id": lanc_id,
    }


class TestProjecao:
    def test_saldo_diario_consolidado(self):
        eventos = [
            _criado("e1", "CREDITO", 5000),
            _criado("e2", "DEBITO", 2000),
            _criado("e3", "CREDITO", 1000),
        ]
        c = consolidar_eventos(eventos, "M1", date(2026, 11, 24))
        assert c.total_creditos_centavos == 6000
        assert c.total_debitos_centavos == 2000
        assert c.saldo_centavos == 4000
        assert c.qtd_lancamentos == 3

    def test_cancelamento_estorna(self):
        eventos = [
            _criado("e1", "CREDITO", 5000),
            _criado("e2", "DEBITO", 2000),
            _cancelado("e3", "L-e1"),
        ]
        c = consolidar_eventos(eventos, "M1", date(2026, 11, 24))
        assert c.total_creditos_centavos == 0
        assert c.saldo_centavos == -2000
        assert c.qtd_lancamentos == 1

    def test_reprocessamento_deterministico(self):
        """Rebuild a partir dos mesmos eventos => mesmo resultado (auditoria)."""
        eventos = [_criado("e1", "CREDITO", 700), _criado("e2", "DEBITO", 300)]
        a = consolidar_eventos(eventos, "M1", date(2026, 11, 24))
        b = consolidar_eventos(list(reversed(eventos)), "M1", date(2026, 11, 24))
        assert a.saldo_centavos == b.saldo_centavos == 400

    def test_evento_desconhecido_gera_erro(self):
        with pytest.raises(ValueError):
            ConsolidadoDiario("M1", date(2026, 11, 24)).aplicar_evento(
                {"event_type": "NadaHaver"}
            )
