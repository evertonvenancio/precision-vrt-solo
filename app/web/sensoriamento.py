"""
Precision VRT Solo - Rotas do Módulo Sensoriamento
"""
from fastapi import APIRouter, Request, Depends, HTTPException

from app.services.sensoriamento_service import SensoriamentoService

router = APIRouter()
from app.web.auth_dependencies import require_permission_web  # autenticação via cookie
from app.template_config import templates  # compartilhado - globals de RBAC


@router.get("/")
async def sensoriamento_page(
    request: Request,
    user: dict = Depends(require_permission_web("sensoriamento:read"))
):
    """Página principal de sensoriamento."""
    return templates.TemplateResponse(
        request=request,
        name="sensoriamento.html",
        context={
            "request": request,
            "usuario": user,
            "titulo": "Sensoriamento Remoto",
            "permissoes": user.get("permissions", [])
        }
    )


@router.get("/novo")
async def sensoriamento_novo_page(
    request: Request,
    user: dict = Depends(require_permission_web("sensoriamento:write"))
):
    """Página para novo processamento de sensoriamento."""
    return templates.TemplateResponse(
        request=request,
        name="sensoriamento_novo.html",
        context={
            "request": request,
            "usuario": user,
            "titulo": "Novo Sensoriamento",
            "permissoes": user.get("permissions", [])
        }
    )
