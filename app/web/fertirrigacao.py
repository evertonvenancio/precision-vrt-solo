"""
Precision VRT Solo - Rotas do Módulo Fertirrigação
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.fertirrigacao_service import FertirrigacaoService

router = APIRouter()
from app.web.auth_dependencies import require_permission_web  # autenticação via cookie
from app.template_config import templates  # compartilhado - globals de RBAC


@router.get("/")
async def fertirrigacao_page(
    request: Request,
    user: dict = Depends(require_permission_web("fertirrigacao:read"))
):
    """Página principal de fertirrigação."""
    return templates.TemplateResponse(
        request=request,
        name="fertirrigacao.html",
        context={
            "request": request,
            "usuario": user,
            "titulo": "Fertirrigação",
            "permissoes": user.get("permissions", [])
        }
    )


@router.get("/nova")
async def fertirrigacao_nova_page(
    request: Request,
    user: dict = Depends(require_permission_web("fertirrigacao:write"))
):
    """Página para novo cálculo de fertirrigação."""
    return templates.TemplateResponse(
        request=request,
        name="fertirrigacao_nova.html",
        context={
            "request": request,
            "usuario": user,
            "titulo": "Nova Fertirrigação",
            "permissoes": user.get("permissions", [])
        }
    )
