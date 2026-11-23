from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

from src.domain.models import ConsolidadoDiario
from src.application.use_cases import RecalcularConsolidadoUseCase


def test_recalcular_e_persistir():
    repo = MagicMock()
    uc = RecalcularConsolidadoUseCase(repo)
    c = uc.execute(date(2026, 11, 24), Decimal("1000"), Decimal("300"))
    assert c.saldo == Decimal("700")
    repo.save.assert_called_once_with(c)