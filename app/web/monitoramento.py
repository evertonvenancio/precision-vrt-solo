"""
Precision VRT Solo - Rotas do Módulo Monitoramento
"""
from fastapi import APIRouter, Request, Depends, HTTPException

from core.authorization.dependencies import require_permission
from app.services.monitoramento_service import MonitoramentoService

router = APIRouter()
from app.template_config import templates  # compartilhado - globals de RBAC


@router.get("/monitoramento")
async def monitoramento_page(
    request: Request,
    usuario: dict = Depends(require_permission("monitoramento:read"))
):
    """Página principal de monitoramento."""
    return templates.TemplateResponse(
        request=request,
        name="monitoramento.html",
        context={
            "request": request,
            "usuario": usuario,
            "titulo": "Monitoramento de Safras",
            "permissoes": usuario.get("permissions", [])
        }
    )


@router.get("/monitoramento/novo")
async def monitoramento_novo_page(
    request: Request,
    usuario: dict = Depends(require_permission("monitoramento:write"))
):
    """Página para novo monitoramento."""
    return templates.TemplateResponse(
        request=request,
        name="monitoramento_novo.html",
        context={
            "request": request,
            "usuario": usuario,
            "titulo": "Novo Monitoramento",
            "permissoes": usuario.get("permissions", [])
        }
    )
