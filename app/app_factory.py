"""
Precision VRT Solo - Factory de Aplicação
Responsabilidade: Centralizar a criação e configuração da aplicação FastAPI.
Padrão Factory para melhor organização e testabilidade.
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Importações obrigatórias - sem tratamento de erros
from core.utilitarios.startup import registrar_startup
from core.middleware.tenant import TenantMiddleware
from core.authorization.dependencies import (
    get_filtered_menu, get_user_permissions, has_permission,
    template_has_permission, template_filter_menu,
    SIDEBAR_MENU_STRUCTURE
)

def create_app() -> FastAPI:
    """
    Cria e configura a aplicação FastAPI principal.
    
    Returns:
        FastAPI: Instância configurada da aplicação
    """
    
    # Criar instância FastAPI
    app = FastAPI(
        title="Precision VRT Solo",
        description="API Principal do Sistema de Agricultura de Precisão",
        version="1.0.0"
    )

    # Middleware Multi-Tenancy
    app.add_middleware(TenantMiddleware)

    # Registrar helpers de template para RBAC na instância compartilhada
    from app.template_config import templates as shared_templates
    shared_templates.env.globals["has_permission"] = template_has_permission
    shared_templates.env.globals["filter_menu"] = template_filter_menu
    shared_templates.env.globals["SIDEBAR_MENU_STRUCTURE"] = SIDEBAR_MENU_STRUCTURE
    
    # Montar arquivos estáticos
    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    print("[OK] Static files mounted")
    
    # Incluir roteadores da API
    _include_api_routers(app)
    
    # Incluir roteadores web
    _include_web_routers(app)
    
    # Registrar startup
    registrar_startup(app)
    print("[OK] Startup registered")

    # Adicionar endpoints básicos
    _include_basic_endpoints(app)

    print("[OK] API setup complete")
    print("[SERVER] Server ready to start")
    print("[INFO] Available endpoints:")
    print("  GET / - Root endpoint")
    print("  GET /health - Health check")
    print("  /api/v1/* - API endpoints")
    print("  /web/* - Web interface endpoints")
    
    return app

def _include_api_routers(app: FastAPI) -> None:
    """Incluir todos os roteadores da API v1."""
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
    
    print("[OK] API routers included")

def _include_web_routers(app: FastAPI) -> None:
    """Incluir todos os roteadores da interface web."""
    # Carregar auth_router
    from app.web.auth import router as auth_router
    app.include_router(auth_router, prefix="/web/auth", tags=["web-auth"])
    app.include_router(auth_router, prefix="/auth", tags=["web-auth"])
    # Incluir sem prefixo para endpoints API diretos (/api/me, /logout, etc.)
    app.include_router(auth_router, tags=["web-auth"])
    print("[OK] Auth router included")
    
    # Carregar dashboard router
    from app.web.dashboard import router as dashboard_router
    app.include_router(dashboard_router, prefix="/web/dashboard", tags=["web-dashboard"])
    print("[OK] Dashboard router included")
    
    # Carregar clientes router
    from app.web.clientes import router as clientes_router
    app.include_router(clientes_router, prefix="/web/clientes", tags=["web-clientes"])
    print("[OK] Clientes router included")

    # Carregar orcamentos router
    from app.web.orcamentos import router as orcamentos_router
    app.include_router(orcamentos_router, prefix="/web/orcamentos", tags=["web-orcamentos"])
    print("[OK] Orcamentos router included")

    # Carregar vendas router
    from app.web.vendas import router as vendas_router
    app.include_router(vendas_router, prefix="/web/vendas", tags=["web-vendas"])
    print("[OK] Vendas router included")

    # Carregar nematoides router
    from app.web.nematoides import router as nematoides_router
    app.include_router(nematoides_router, prefix="/web/nematoides", tags=["web-nematoides"])
    print("[OK] Nematoides router included")

    # Carregar relatorios router
    from app.web.relatorios import router as relatorios_router
    app.include_router(relatorios_router, prefix="/web/relatorios", tags=["web-relatorios"])
    print("[OK] Relatorios router included")

    # Carregar compactacao router
    from app.web.compactacao import router as compactacao_router
    app.include_router(compactacao_router, prefix="/web/compactacao", tags=["web-compactacao"])
    print("[OK] Compactacao router included")

    # Carregar fertirrigacao router
    from app.web.fertirrigacao import router as fertirrigacao_router
    app.include_router(fertirrigacao_router, prefix="/web/fertirrigacao", tags=["web-fertirrigacao"])
    print("[OK] Fertirrigacao router included")

    # Carregar sensoriamento router
    from app.web.sensoriamento import router as sensoriamento_router
    app.include_router(sensoriamento_router, prefix="/web/sensoriamento", tags=["web-sensoriamento"])
    print("[OK] Sensoriamento router included")

    # Carregar monitoramento router
    from app.web.monitoramento import router as monitoramento_router
    app.include_router(monitoramento_router, prefix="/web/monitoramento", tags=["web-monitoramento"])
    print("[OK] Monitoramento router included")

    # Carregar financeiro router
    from app.web.financeiro import router as financeiro_router
    app.include_router(financeiro_router, prefix="/web/financeiro", tags=["web-financeiro"])
    print("[OK] Financeiro router included")

    # Carregar prescricao router
    from app.web.prescricao import router as prescricao_router
    app.include_router(prescricao_router, prefix="/web/prescricao", tags=["web-prescricao"])
    print("[OK] Prescricao router included")

    # Carregar ativos router
    from app.web.ativos import router as ativos_router
    app.include_router(ativos_router, prefix="/web/ativos", tags=["web-ativos"])
    print("[OK] Ativos router included")

    # Carregar comunicacao router
    from app.web.comunicacao import router as comunicacao_router
    app.include_router(comunicacao_router, prefix="/web/comunicacao", tags=["web-comunicacao"])
    print("[OK] Comunicacao router included")

    # Carregar auditoria router
    from app.web.auditoria import router as auditoria_router
    app.include_router(auditoria_router, prefix="/web/auditoria", tags=["web-auditoria"])
    print("[OK] Auditoria router included")

    # Carregar bulk_blend router
    from app.web.bulk_blend import router as bulk_blend_router
    app.include_router(bulk_blend_router, prefix="/web/bulk_blend", tags=["web-bulk_blend"])
    print("[OK] Bulk Blend router included")

    # Carregar caixa router
    from app.web.caixa import router as caixa_router
    app.include_router(caixa_router, prefix="/web/caixa", tags=["web-caixa"])
    print("[OK] Caixa router included")

    # Carregar clima router
    from app.web.clima import router as clima_router
    app.include_router(clima_router, prefix="/web/clima", tags=["web-clima"])
    print("[OK] Clima router included")

    # Carregar conhecimento router
    from app.web.conhecimento import router as conhecimento_router
    app.include_router(conhecimento_router, prefix="/web/conhecimento", tags=["web-conhecimento"])
    print("[OK] Conhecimento router included")

    # Carregar cruzamento router
    from app.web.cruzamento import router as cruzamento_router
    app.include_router(cruzamento_router, prefix="/web/cruzamento", tags=["web-cruzamento"])
    print("[OK] Cruzamento router included")

    # Carregar equipe router
    from app.web.equipe import router as equipe_router
    app.include_router(equipe_router, prefix="/web/equipe", tags=["web-equipe"])
    print("[OK] Equipe router included")

    # Carregar extrator router
    from app.web.extrator import router as extrator_router
    app.include_router(extrator_router, prefix="/web/extrator", tags=["web-extrator"])
    print("[OK] Extrator router included")

    # Carregar permissoes router
    from app.web.permissoes import router as permissoes_router
    app.include_router(permissoes_router, prefix="/web/permissoes", tags=["web-permissoes"])
    print("[OK] Permissoes router included")

    # Carregar tabela_precos router
    from app.web.tabela_precos import router as tabela_precos_router
    app.include_router(tabela_precos_router, prefix="/web/tabela_precos", tags=["web-tabela_precos"])
    print("[OK] Tabela Precos router included")

    # Carregar upload router
    from app.web.upload import router as upload_router
    app.include_router(upload_router, prefix="/web/upload", tags=["web-upload"])
    print("[OK] Upload router included")

    # Carregar configuracoes router
    from app.web.configuracoes import router as configuracoes_router
    app.include_router(configuracoes_router, prefix="/web/configuracoes", tags=["web-configuracoes"])
    print("[OK] Configuracoes router included")

    print("[OK] Web routers included")

def _include_basic_endpoints(app: FastAPI) -> None:
    """Incluir endpoints básicos da aplicação."""
    
    @app.get("/")
    async def root():
        return {"message": "Precision VRT Solo API is running!"}
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "message": "API is running"}
