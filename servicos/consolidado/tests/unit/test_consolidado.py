from datetime import date
from decimal import Decimal
from src.domain.models import ConsolidadoDiario


def test_saldo_calculado_corretamente():
    c = ConsolidadoDiario(
        data=date(2026, 11, 24),
        total_creditos=Decimal("1500.00"),
        total_debitos=Decimal("450.00")
    )
    assert c.saldo == Decimal("1050.00")


def test_saldo_negativo():
    c = ConsolidadoDiario(
        data=date(2026, 11, 24),
        total_creditos=Decimal("100.00"),
        total_debitos=Decimal("500.00")
    )
    assert c.saldo == Decimal("-400.00")


def test_saldo_zero():
    c = ConsolidadoDiario(
        data=date(2026, 11, 24),
        total_creditos=Decimal("100.00"),
        total_debitos=Decimal("100.00")
    )
    assert c.saldo == Decimal("0.00")