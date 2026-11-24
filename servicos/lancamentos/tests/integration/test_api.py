from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_criar_lancamento_sucesso():
    r = client.post("/lancamentos", json={
        "tipo": "CREDITO", "valor": "150.00", "categoria": "Vendas",
        "data": "2026-11-24", "descricao": "Venda nº 1"
    })
    assert r.status_code == 201
    assert r.json()["valor"] == "150.00"


def test_criar_lancamento_valor_negativo():
    r = client.post("/lancamentos", json={
        "tipo": "CREDITO", "valor": "-10", "categoria": "Vendas",
        "data": "2026-11-24", "descricao": "X"
    })
    assert r.status_code == 422


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
