import os
import json
from datetime import date
from decimal import Decimal
import redis
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/consolidado", tags=["Consolidado"])

class SaldoOut(BaseModel):
    data: date
    total_creditos: Decimal
    total_debitos: Decimal
    saldo: Decimal

# Conexão com o mesmo Redis do serviço de lançamentos
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)

@router.get("/{data}", response_model=SaldoOut)
def obter_saldo(data: date):
    data_str = data.isoformat()
    chave = f"lancamentos:{data_str}"
    
    # Busca todos os lançamentos do dia no Redis
    lancamentos_raw = redis_client.lrange(chave, 0, -1)
    
    total_creditos = Decimal("0.00")
    total_debitos = Decimal("0.00")
    
    for item in lancamentos_raw:
        lanc = json.loads(item)
        valor = Decimal(str(lanc["valor"]))
        if lanc["tipo"] == "CREDITO":
            total_creditos += valor
        else:
            total_debitos += valor
            
    return SaldoOut(
        data=data,
        total_creditos=total_creditos,
        total_debitos=total_debitos,
        saldo=total_creditos - total_debitos
    )

@router.get("/health")
def health():
    return {"status": "ok"}
