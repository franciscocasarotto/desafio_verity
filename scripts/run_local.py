"""Composicao raiz do ambiente demo local.

Sobe lancamentos (porta 8001) e consolidado (porta 8002) no MESMO processo com
um broker in-memory compartilhado — mantendo a semantica de mensageria (fila,
worker, ack, retry, DLQ). A integracao e 100% assincrona: o lancamento nunca
espera nem depende da disponibilidade do consolidado (RNF principal).

Para produção os dois apps sobem como serviços separados (docker-compose/k8s)
e o broker vira Kafka (on-prem/AKS) ou Google Pub/Sub.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.security import generate_rsa_keypair  # noqa: E402


class BridgePublisher:
    """Adaptador que liga o outbox-relay do lancamentos ao broker do consolidado."""

    def __init__(self, broker) -> None:
        self.broker = broker

    def publish(self, event_dict: dict) -> None:
        self.broker.put(event_dict)


def build_demo():
    from services.consolidado.app.infrastructure.event_processor import EventProcessor
    from services.consolidado.app.main import create_app as create_consolidado
    from services.lancamentos.app.infrastructure.sqlite_repository import (
        SqliteLancamentoRepository,
    )
    from services.lancamentos.app.main import Settings as LancaSettings
    from services.lancamentos.app.main import create_app as create_lancamentos
    from services.consolidado.app.main import Settings as ConsSettings

    os.makedirs("data", exist_ok=True)
    private_pem, public_pem = generate_rsa_keypair()
    with open("data/dev_private_key.pem", "w") as f:
        f.write(private_pem)

    repo = SqliteLancamentoRepository("data/lancamentos.db")
    processor = EventProcessor("data/consolidado.db")

    app_c = create_consolidado(processor=processor, settings=ConsSettings(
        db_path="data/consolidado.db", jwt_public_key=public_pem,
        security_enabled=False,  # demo local simples; auth testada nos unit tests
    ))
    broker = app_c.state.broker

    app_l = create_lancamentos(repo=repo, publisher=BridgePublisher(broker),
                               settings=LancaSettings(
                                   db_path="data/lancamentos.db",
                                   jwt_public_key=public_pem,
                                   security_enabled=False,
                               ))
    return app_l, app_c, processor, repo


if __name__ == "__main__":
    import threading

    import uvicorn

    app_l, app_c, processor, repo = build_demo()

    t = threading.Thread(
        target=lambda: uvicorn.run(app_c, host="0.0.0.0", port=8002, log_level="warning"),
        daemon=True,
    )
    t.start()
    print("[demo] consolidado em :8002 | lancamentos em :8001 (docs em /docs)")
    uvicorn.run(app_l, host="0.0.0.0", port=8001, log_level="warning")
