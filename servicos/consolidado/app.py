"""Serviço de Consolidado - calcula saldo diário consumindo eventos."""
from fastapi import FastAPI
from datetime import datetime
from decimal import Decimal
import pika
import json
import threading
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Serviço de Consolidado", version="1.0.0")

# Em produção: PostgreSQL + Redis. In-memory para o demo.
consolidado: dict[str, dict] = {}


def processar_evento(ch, method, properties, body):
    try:
        event = json.loads(body)
        data = event.get("data", {})
        dia = data.get("data", "")[:10] or datetime.utcnow().strftime("%Y-%m-%d")
        valor = Decimal(data.get("valor", "0"))
        tipo = data.get("tipo")

        if dia not in consolidado:
            consolidado[dia] = {
                "saldo": Decimal("0"),
                "creditos": Decimal("0"),
                "debitos": Decimal("0"),
            }

        if tipo == "CREDITO":
            consolidado[dia]["saldo"] += valor
            consolidado[dia]["creditos"] += valor
        else:
            consolidado[dia]["saldo"] -= valor
            consolidado[dia]["debitos"] += valor

        logger.info(f"Consolidado {dia} atualizado: saldo={consolidado[dia]['saldo']}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Erro ao processar evento: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def iniciar_consumidor():
    """Roda o consumer em thread separada."""
    def consumir():
        host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        try:
            conn = pika.BlockingConnection(pika.ConnectionParameters(host=host))
            ch = conn.channel()
            ch.queue_declare(queue="lancamentos", durable=True)
            ch.basic_qos(prefetch_count=50)
            ch.basic_consume(queue="lancamentos", on_message_callback=processar_evento)
            logger.info("Consumidor iniciado, aguardando mensagens...")
            ch.start_consuming()
        except Exception as e:
            logger.error(f"Consumidor falhou: {e}")

    threading.Thread(target=consumir, daemon=True).start()


@app.on_event("startup")
def startup():
    iniciar_consumidor()


@app.get("/health")
def health():
    return {"status": "ok", "service": "consolidado"}


@app.get("/consolidado/{dia}")
def consolidado_dia(dia: str):
    dados = consolidado.get(dia, {
        "saldo": Decimal("0"),
        "creditos": Decimal("0"),
        "debitos": Decimal("0"),
    })
    return {
        "dia": dia,
        "saldo": str(dados["saldo"]),
        "total_creditos": str(dados["creditos"]),
        "total_debitos": str(dados["debitos"]),
    }