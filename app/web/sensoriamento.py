"""
Precision VRT Solo - Rotas do Módulo Sensoriamento
"""
from fastapi import APIRouter, Request, Depends, HTTPException

from core.authorization.dependencies import require_permission
from app.services.sensoriamento_service import SensoriamentoService

router = APIRouter()
from app.template_config import templates  # compartilhado - globals de RBAC


@router.get("/")
async def sensoriamento_page(
    request: Request,
    usuario: dict = Depends(require_permission("sensoriamento:read"))
):
    """Página principal de sensoriamento."""
    return templates.TemplateResponse(
        request=request,
        name="sensoriamento.html",
        context={
            "request": request,
            "usuario": usuario,
            "titulo": "Sensoriamento Remoto",
            "permissoes": usuario.get("permissions", [])
        }
    )


@router.get("/novo")
async def sensoriamento_novo_page(
    request: Request,
    usuario: dict = Depends(require_permission("sensoriamento:write"))
):
    """Página para novo processamento de sensoriamento."""
    return templates.TemplateResponse(
        request=request,
        name="sensoriamento_novo.html",
        context={
            "request": request,
            "usuario": usuario,
            "titulo": "Novo Sensoriamento",
            "permissoes": usuario.get("permissions", [])
        }
    )
