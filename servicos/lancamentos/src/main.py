# servicos/lancamentos/src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importa o roteador da API
from src.presentation.api import router as lancamentos_router

app = FastAPI(
    title="Serviço de Lançamentos - Verity",
    description="API para controle de fluxo de caixa (Débitos e Créditos)",
    version="1.0.0"
)

# Configuração básica de CORS (permite requisições de outros domínios)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra as rotas
app.include_router(lancamentos_router)

# Healthcheck global
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "lancamentos"}