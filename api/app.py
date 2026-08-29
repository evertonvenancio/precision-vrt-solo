"""
Precision VRT Solo — API FastApp

Aplicação FastAPI principal para a camada de API.
Responsável apenas por gerenciar endpoints HTTP.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import (
    prescricao_vrt,
    compactacao,
    nematoides,
    fertirrigacao,
    sensoriamento,
    monitoramento,
    exportacao,
    validacao,
    configuracoes,
    cadastros,
    financeiro,
    crm
)
from api.responses import sucesso, erro

app = FastAPI(
    title="Precision VRT Solo API",
    description="API para sistemas de agricultura de precisão",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(prescricao_vrt.router, prefix="/api/prescricao_vrt", tags=["prescricao_vrt"])
app.include_router(compactacao.router, prefix="/api/compactacao", tags=["compactacao"])
app.include_router(nematoides.router, prefix="/api/nematoides", tags=["nematoides"])
app.include_router(fertirrigacao.router, prefix="/api/fertirrigacao", tags=["fertirrigacao"])
app.include_router(sensoriamento.router, prefix="/api/sensoriamento", tags=["sensoriamento"])
app.include_router(monitoramento.router, prefix="/api/monitoramento", tags=["monitoramento"])
app.include_router(exportacao.router, prefix="/api/exportacao", tags=["exportacao"])
app.include_router(validacao.router, prefix="/api/validacao", tags=["validacao"])
app.include_router(configuracoes.router, prefix="/api/configuracoes", tags=["configuracoes"])
app.include_router(cadastros.router, prefix="/api/cadastros", tags=["cadastros"])
app.include_router(financeiro.router, prefix="/api/financeiro", tags=["financeiro"])
app.include_router(crm.router, prefix="/api/crm", tags=["crm"])

@app.get("/")
def root():
    """Endpoint raiz da API"""
    return {
        "success": True,
        "message": "Precision VRT Solo API",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """Verificação de saúde da API"""
    return {
        "success": True,
        "message": "API está operacional",
        "timestamp": "2026-08-06"
    }