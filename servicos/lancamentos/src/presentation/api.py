# servicos/lancamentos/src/presentation/api.py
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from enum import Enum

router = APIRouter(prefix="/lancamentos", tags=["Lançamentos"])

class TipoLancamento(str, Enum):
    DEBITO = "DEBITO"
    CREDITO = "CREDITO"

class LancamentoIn(BaseModel):
    tipo: TipoLancamento
    valor: Decimal = Field(gt=0, decimal_places=2)
    categoria: str = Field(min_length=1, max_length=50)
    data: date
    descricao: str = Field(min_length=1, max_length=200)

class LancamentoOut(BaseModel):
    id: str
    tipo: TipoLancamento
    valor: Decimal
    categoria: str
    data: date
    descricao: str

# Banco de dados em memória (Mock) para o Docker rodar sem configurar SQLAlchemy agora
db_mock = []

@router.post("", response_model=LancamentoOut, status_code=201)
def criar_lancamento(body: LancamentoIn):
    # Validação de regra de negócio simples
    if body.data > date.today():
        raise HTTPException(status_code=422, detail="Data não pode ser futura")
    
    # Simula salvamento
    registro = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "tipo": body.tipo,
        "valor": body.valor,
        "categoria": body.categoria,
        "data": body.data,
        "descricao": body.descricao
    }
    db_mock.append(registro)
    return registro

@router.get("/health")
def health():
    return {"status": "ok"}