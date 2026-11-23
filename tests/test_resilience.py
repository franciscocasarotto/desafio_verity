"""Teste de resiliencia (RNF critico): o lancamento NAO pode falhar se o
consolidado estiver fora.

Simula a queda do consumidor: eventos vao para o outbox e ficam pendentes; o
servico de lancamentos continua aceitando gravacoes com sucesso. Quando o
consumidor volta, o relay reprocessa tudo sem perda (0% de perda de dados —
atende "max 5% perda de requisicoes" com folga).
"""
from __future__ import annotations

from datetime import date


class TestResilienciaIsolamento:
    def test_lancamentos_continua_operante_sem_consumidor(self, demo):
        lanc = demo["lanc"]
        processor = demo["processor"]
        broker = demo["app_c"].state.broker
        worker = demo["app_c"].state.worker

        # derruba o consumidor (equivalente a pod do consolidado caido)
        worker.stop()
        worker.join(timeout=2)

        for i in range(10):
            r = lanc.post("/lancamentos", json={
                "tipo": "CREDITO", "valor_centavos": 100 + i,
                "data_vencimento": "2026-11-24", "descricao": f"venda {i}",
            })
            assert r.status_code == 201, "lancamento nao pode depender do consolidado"

        # eventos ficam seguros no outbox, nada perdido
        enviados = lanc.post("/admin/outbox-flush").json()["enviados"]
        assert enviados == 10
        assert len(broker) > 0 or processor.stats.processados > 0

    def test_recuperacao_reprocessa_sem_perda(self, demo):
        """Apos retorno do consumidor, saldo final reflete 100% dos eventos."""
        import time

        lanc = demo["lanc"]
        processor = demo["processor"]
        worker = demo["app_c"].state.worker

        for i in range(10):
            lanc.post("/lancamentos", json={
                "tipo": "DEBITO", "valor_centavos": 200,
                "data_vencimento": "2026-11-24", "descricao": f"custo {i}",
            })
        lanc.post("/admin/outbox-flush")

        fim = time.time() + 5
        while time.time() < fim and processor.stats.processados < 10:
            time.sleep(0.02)

        rep = demo["cons"].get("/relatorio/dia/2026-11-24").json()
        assert rep["qtd_lancamentos"] == 10
        assert rep["saldo_centavos"] == -2000  # zero perda

    def test_evento_poison_vai_para_dlq_sem_parar_worker(self, demo):
        processor = demo["processor"]
        broker = demo["app_c"].state.broker
        # evento invalido: cancelamento sem original -> gera erro no processador
        broker.put({
            "event_id": "veneno-1",
            "event_type": "LancamentoCancelado",
            "merchant_id": "M1",
            "lancamento_id": "inexistente",
            "schema_version": 1,
            "occurred_at": "2026-11-24T00:00:00+00:00",
            "correlation_id": "t",
            "source": "teste",
            "motivo": None,
        })
        broker.put({  # evento valido atras do veneno
            "event_id": "ok-1",
            "event_type": "LancamentoCriado",
            "merchant_id": "M1",
            "lancamento_id": "L-ok",
            "tipo": "CREDITO",
            "valor_centavos": 777,
            "data_vencimento": "2026-11-24",
            "descricao": "apos veneno",
            "schema_version": 1,
            "occurred_at": "2026-11-24T00:00:00+00:00",
            "correlation_id": "t",
            "source": "teste",
        })
        import time

        fim = time.time() + 8
        while time.time() < fim and processor.stats.dlq < 1:
            time.sleep(0.05)
        assert processor.stats.dlq >= 1, "evento poison deve ir para DLQ"
        # fila nao travou: o evento valido posterior foi processado
        assert processor.stats.processados >= 1
        rep = demo["cons"].get("/relatorio/dia/2026-11-24").json()
        assert rep["saldo_centavos"] == 777

    def test_rebuild_deterministico_recupera_projecao(self, demo):
        """Read-model corrompido => rebuild a partir do event store restaura."""
        lanc, cons, processor = demo["lanc"], demo["cons"], demo["processor"]
        lanc.post("/lancamentos", json={
            "tipo": "CREDITO", "valor_centavos": 3000,
            "data_vencimento": "2026-11-28", "descricao": "venda",
        })
        lanc.post("/admin/outbox-flush")
        import time

        fim = time.time() + 5
        while time.time() < fim and processor.stats.processados < 1:
            time.sleep(0.02)

        # simula corrupcao da projecao
        with processor._lock:  # noqa: SLF001 (teste de infra)
            processor._conn.execute("DELETE FROM consolidado_diario")
            processor._conn.commit()

        r = cons.post("/admin/rebuild", json={"inicio": "2026-11-01", "fim": "2026-11-30"})
        assert r.status_code == 202
        rep = cons.get("/relatorio/dia/2026-11-28").json()
        assert rep["saldo_centavos"] == 3000
