"""
Precision VRT Solo - Rotas do Módulo Fertirrigação
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db.database import get_db
from core.authorization.dependencies import require_permission
from app.services.fertirrigacao_service import FertirrigacaoService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/fertirrigacao")
async def fertirrigacao_page(
    request: Request,
    usuario: dict = Depends(require_permission("fertirrigacao:read"))
):
    """Página principal de fertirrigação."""
    return templates.TemplateResponse(
        request=request,
        name="fertirrigacao.html",
        context={
            "request": request,
            "usuario": usuario,
            "titulo": "Fertirrigação",
            "permissoes": usuario.get("permissions", [])
        }
    )


@router.get("/fertirrigacao/nova")
async def fertirrigacao_nova_page(
    request: Request,
    usuario: dict = Depends(require_permission("fertirrigacao:write"))
):
    """Página para novo cálculo de fertirrigação."""
    return templates.TemplateResponse(
        request=request,
        name="fertirrigacao_nova.html",
        context={
            "request": request,
            "usuario": usuario,
            "titulo": "Nova Fertirrigação",
            "permissoes": usuario.get("permissions", [])
        }
    )
