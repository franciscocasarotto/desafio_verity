"""Testes de integracao vertical: lancamento -> evento -> consolidado.

Valida o fluxo de ponta a ponta do requisito de negocio com os dois servicos
reais (FastAPI TestClient + worker + SQLite), incluindo idempotencia e o
cancelamento com estorno no relatorio diario.
"""
from __future__ import annotations

import time


def _espera_processar(processor, esperado: int, timeout: float = 5.0) -> None:
    fim = time.time() + timeout
    while time.time() < fim:
        if processor.stats.processados >= esperado:
            return
        time.sleep(0.02)
    raise AssertionError(
        f"timeout aguardando processamento ({processor.stats.processados}/{esperado})"
    )


class TestFluxoPontaAPonta:
    def test_criar_lancamentos_e_consolidar_saldo_diario(self, demo):
        lanc, cons, processor = demo["lanc"], demo["cons"], demo["processor"]
        dia = "2026-11-24"

        r1 = lanc.post("/lancamentos", json={
            "tipo": "CREDITO", "valor_centavos": 5000,
            "data_vencimento": dia, "descricao": "venda dia",
        }, headers={"Idempotency-Key": "k1"})
        assert r1.status_code == 201

        r2 = lanc.post("/lancamentos", json={
            "tipo": "DEBITO", "valor_centavos": 1800,
            "data_vencimento": dia, "descricao": "fornecedor",
        })
        assert r2.status_code == 201

        # outbox relay -> broker -> worker
        lanc.post("/admin/outbox-flush")
        _espera_processar(processor, 2)

        rep = cons.get(f"/relatorio/dia/{dia}").json()
        assert rep["total_creditos_centavos"] == 5000
        assert rep["total_debitos_centavos"] == 1800
        assert rep["saldo_centavos"] == 3200
        assert rep["qtd_lancamentos"] == 2

    def test_idempotencia_repeticao_nao_duplica(self, demo):
        lanc, cons, processor = demo["lanc"], demo["cons"], demo["processor"]
        corpo = {
            "tipo": "CREDITO", "valor_centavos": 900,
            "data_vencimento": "2026-11-25", "descricao": "mesma venda",
        }
        a = lanc.post("/lancamentos", json=corpo, headers={"Idempotency-Key": "dupla"})
        b = lanc.post("/lancamentos", json=corpo, headers={"Idempotency-Key": "dupla"})
        assert a.status_code == 201 and b.status_code == 200
        assert a.json()["id"] == b.json()["id"]

        lanc.post("/admin/outbox-flush")
        _espera_processar(processor, 1)
        rep = cons.get("/relatorio/dia/2026-11-25").json()
        assert rep["qtd_lancamentos"] == 1
        assert rep["saldo_centavos"] == 900

    def test_idempotency_key_com_payload_diferente_409(self, demo):
        lanc = demo["lanc"]
        lanc.post("/lancamentos", json={
            "tipo": "CREDITO", "valor_centavos": 100,
            "data_vencimento": "2026-11-26", "descricao": "a",
        }, headers={"Idempotency-Key": "k-conf"})
        r = lanc.post("/lancamentos", json={
            "tipo": "CREDITO", "valor_centavos": 999,
            "data_vencimento": "2026-11-26", "descricao": "b",
        }, headers={"Idempotency-Key": "k-conf"})
        assert r.status_code == 409

    def test_cancelamento_estorna_no_relatorio(self, demo):
        lanc, cons, processor = demo["lanc"], demo["cons"], demo["processor"]
        dia = "2026-11-27"
        criado = lanc.post("/lancamentos", json={
            "tipo": "DEBITO", "valor_centavos": 2500,
            "data_vencimento": dia, "descricao": "aluguel",
        }).json()
        lanc.post("/admin/outbox-flush")
        _espera_processar(processor, 1)

        d = lanc.request(
            "DELETE", f"/lancamentos/{criado['id']}", json={"motivo": "pago em dobro"}
        )
        assert d.status_code == 200 and d.json()["status"] == "CANCELADO"

        lanc.post("/admin/outbox-flush")
        _espera_processar(processor, 2)

        rep = cons.get(f"/relatorio/dia/{dia}").json()
        assert rep["saldo_centavos"] == 0
        assert rep["qtd_lancamentos"] == 0

    def test_relatorio_periodo_acumulado(self, demo):
        lanc, cons, processor = demo["lanc"], demo["cons"], demo["processor"]
        lanc.post("/lancamentos", json={
            "tipo": "CREDITO", "valor_centavos": 1000,
            "data_vencimento": "2026-12-01", "descricao": "d1",
        })
        lanc.post("/lancamentos", json={
            "tipo": "DEBITO", "valor_centavos": 400,
            "data_vencimento": "2026-12-02", "descricao": "d2",
        })
        lanc.post("/admin/outbox-flush")
        _espera_processar(processor, 2)
        rep = cons.get("/relatorio/periodo?inicio=2026-12-01&fim=2026-12-31").json()
        assert rep["dias"] == 2
        assert rep["saldo_acumulado_centavos"] == 600

    def test_validacoes_de_api(self, demo):
        lanc = demo["lanc"]
        assert lanc.post("/lancamentos", json={
            "tipo": "OUTRO", "valor_centavos": 10,
            "data_vencimento": "2026-11-24", "descricao": "x",
        }).status_code == 422
        assert lanc.post("/lancamentos", json={
            "tipo": "CREDITO", "valor_centavos": -1,
            "data_vencimento": "2026-11-24", "descricao": "x",
        }).status_code == 422  # validacao pydantic (gt=0)
        assert lanc.get("/lancamentos/nao-existe").status_code == 404

    def test_health_e_metrics(self, demo):
        assert demo["lanc"].get("/healthz").json()["status"] == "UP"
        assert demo["cons"].get("/readyz").json()["worker_alive"] is True
        m = demo["cons"].get("/metrics").json()["raw_prometheus"]
        assert any("consolidado_events_processed_total" in linha for linha in m)
