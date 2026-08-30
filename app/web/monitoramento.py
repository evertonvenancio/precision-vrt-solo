"""
Precision VRT Solo - Rotas do Módulo Monitoramento
"""
from fastapi import APIRouter, Request, Depends, HTTPException

from app.services.monitoramento_service import MonitoramentoService

router = APIRouter()
from app.web.auth_dependencies import require_permission_web  # autenticação via cookie
from app.template_config import templates  # compartilhado - globals de RBAC


@router.get("/")
async def monitoramento_page(
    request: Request,
    user: dict = Depends(require_permission_web("monitoramento:read"))
):
    """Página principal de monitoramento."""
    return templates.TemplateResponse(
        request=request,
        name="monitoramento.html",
        context={
            "request": request,
            "usuario": user,
            "titulo": "Monitoramento de Safras",
            "permissoes": user.get("permissions", [])
        }
    )


@router.get("/novo")
async def monitoramento_novo_page(
    request: Request,
    user: dict = Depends(require_permission_web("monitoramento:write"))
):
    """Página para novo monitoramento."""
    return templates.TemplateResponse(
        request=request,
        name="monitoramento_novo.html",
        context={
            "request": request,
            "usuario": user,
            "titulo": "Novo Monitoramento",
            "permissoes": user.get("permissions", [])
        }
    )
