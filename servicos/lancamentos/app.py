"""Serviço de Lançamentos - registra débitos e créditos."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
import pika
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Serviço de Lançamentos", version="1.0.0")


class TipoLancamento(str, Enum):
    DEBITO = "DEBITO"
    CREDITO = "CREDITO"


class LancamentoCreate(BaseModel):
    tipo: TipoLancamento
    valor: Decimal = Field(..., gt=0)
    descricao: str = Field(..., min_length=3, max_length=200)
    categoria: str = Field(..., max_length=50)


class LancamentoResponse(BaseModel):
    id: str
    tipo: TipoLancamento
    valor: Decimal
    descricao: str
    categoria: str
    data: datetime


# Em produção: SQLAlchemy + PostgreSQL. Aqui uso in-memory para simplificar o demo.
db: list[dict] = []


def publicar_evento(tipo: str, payload: dict):
    """Publica evento no RabbitMQ. Falha no broker NÃO derruba o lançamento."""
    try:
        host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        conn = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        ch = conn.channel()
        ch.queue_declare(queue="lancamentos", durable=True)
        ch.basic_publish(
            exchange="",
            routing_key="lancamentos",
            body=json.dumps({"event": tipo, "data": payload}),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        conn.close()
    except Exception as e:
        # Loga mas não falha o request - o lançamento já foi persistido
        logger.warning(f"Falha ao publicar evento: {e}")


@app.get("/health")
def health():
    return {"status": "ok", "service": "lancamentos"}


@app.post("/lancamentos", response_model=LancamentoResponse, status_code=201)
def criar_lancamento(lanc: LancamentoCreate):
    novo = {
        "id": f"LANC-{uuid4().hex[:12].upper()}",
        "tipo": lanc.tipo,
        "valor": lanc.valor,
        "descricao": lanc.descricao,
        "categoria": lanc.categoria,
        "data": datetime.utcnow(),
    }
    db.append(novo)

    # Publica evento de forma desacoplada
    publicar_evento("LancamentoCriado", {
        "id": novo["id"],
        "tipo": novo["tipo"].value,
        "valor": str(novo["valor"]),
        "descricao": novo["descricao"],
        "categoria": novo["categoria"],
        "data": novo["data"].isoformat(),
    })

    return novo


@app.get("/lancamentos/{lancamento_id}")
def obter_lancamento(lancamento_id: str):
    for item in db:
        if item["id"] == lancamento_id:
            return item
    raise HTTPException(status_code=404, detail="Lançamento não encontrado")


@app.get("/lancamentos")
def listar_lancamentos():
    return db