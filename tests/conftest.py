"""Fixtures comuns: apps com adaptadores isolados por teste (tmp db)."""
from __future__ import annotations

import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.run_local import build_demo  # noqa: E402


@pytest.fixture()
def demo(tmp_path, monkeypatch):
    """Sobe o ambiente demo completo com bancos em arquivo temporario."""
    monkeypatch.setenv("LANCAMENTOS_DB", str(tmp_path / "l.db"))
    monkeypatch.setenv("CONSOLIDADO_DB", str(tmp_path / "c.db"))
    monkeypatch.chdir(tmp_path)
    app_l, app_c, processor, repo = build_demo()
    client_l = TestClient(app_l)
    client_c = TestClient(app_c)
    yield {
        "lanc": client_l,
        "cons": client_c,
        "processor": processor,
        "repo": repo,
        "app_l": app_l,
        "app_c": app_c,
    }
    app_c.state.worker.stop()
