"""
Precision VRT Solo - API Principal (Bootstrap)
"""

from pathlib import Path

# Importações obrigatórias - sem tratamento de erros
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from core.utilitarios.startup import registrar_startup

# Criar FastAPI app
app = FastAPI(
    title="Precision VRT Solo",
    description="API Principal do Sistema de Agricultura de Precisão",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção: substituir por domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("✅ FastAPI app created")

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="frontend"), name="static")
print("✅ Static files mounted")

# Incluir API routers
from api.v1.endpoints import (
    ativos, bulk_blend, clima, compactacao, comunicacao, conhecimento,
    extrator, fiscal, laudos_export, vendas, upload
)

app.include_router(ativos.router, prefix="/api/v1/ativos", tags=["ativos"])
app.include_router(bulk_blend.router, prefix="/api/v1/bulk-blend", tags=["bulk-blend"])
app.include_router(clima.router, prefix="/api/v1/clima", tags=["clima"])
app.include_router(compactacao.router, prefix="/api/v1/compactacao", tags=["compactacao"])
app.include_router(comunicacao.router, prefix="/api/v1/comunicacao", tags=["comunicacao"])
app.include_router(conhecimento.router, prefix="/api/v1/conhecimento", tags=["conhecimento"])
app.include_router(extrator.router, prefix="/api/v1/extrator", tags=["extrator"])
app.include_router(fiscal.router, prefix="/api/v1/fiscal", tags=["fiscal"])
app.include_router(laudos_export.router, prefix="/api/v1/laudos-export", tags=["laudos-export"])
app.include_router(vendas.router, prefix="/api/v1/vendas", tags=["vendas"])
app.include_router(upload.router, prefix="/api/v1/upload", tags=["upload"])

print("✅ API routers included")

# Incluir web routers
from app.web.auth import router as auth_router
from app.web.dashboard import router as dashboard_router
from app.web.clientes import router as clientes_router

app.include_router(auth_router, prefix="/web/auth", tags=["web-auth"])
app.include_router(dashboard_router, prefix="/web/dashboard", tags=["web-dashboard"])
app.include_router(clientes_router, prefix="/web/clientes", tags=["web-clientes"])

print("✅ Web routers included")

# Registrar startup
registrar_startup(app)
print("✅ Startup registered")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Precision VRT Solo API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

print("✅ API setup complete")
print("🚀 Server ready to start")
print("📝 Available endpoints:")
print("  GET / - Root endpoint")
print("  GET /health - Health check")
print("  /api/v1/* - API endpoints")
print("  /web/* - Web interface endpoints")
