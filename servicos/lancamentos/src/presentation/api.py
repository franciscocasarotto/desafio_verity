"""Camada HTTP (FastAPI)."""
from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from src.domain.models import TipoLancamento, LancamentoError
from src.application.use_cases import CriarLancamentoUseCase
from src.presentation.deps import get_criar_lancamento_use_case

router = APIRouter(prefix="/lancamentos", tags=["Lançamentos"])


class LancamentoIn(BaseModel):
    tipo: TipoLancamento
    valor: Decimal = Field(gt=0, decimal_places=2)
    categoria: str = Field(min_length=1, max_length=50)
    data: date
    descricao: str = Field(min_length=1, max_length=200)


class LancamentoOut(BaseModel):
    id: UUID
    tipo: TipoLancamento
    valor: Decimal
    categoria: str
    data: date
    descricao: str


@router.post("", response_model=LancamentoOut, status_code=201)
def criar_lancamento(
    body: LancamentoIn,
    use_case: CriarLancamentoUseCase = Depends(get_criar_lancamento_use_case),
):
    try:
        lanc = use_case.execute(
            tipo=body.tipo, valor=body.valor, categoria=body.categoria,
            data=body.data, descricao=body.descricao
        )
    except LancamentoError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return LancamentoOut(
        id=lanc.id, tipo=lanc.tipo, valor=lanc.valor,
        categoria=lanc.categoria, data=lanc.data, descricao=lanc.descricao
    )


@router.get("/health")
def health():
    return {"status": "ok"}