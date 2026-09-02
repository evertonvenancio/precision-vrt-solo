"""
Precision VRT Solo - Rotas Web do Módulo Monitoramento
Integração completa com RBAC, multi-tenancy e motor de monitoramento real.
"""

from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import shutil
from pathlib import Path
import logging

from app.web.auth_dependencies import require_permission_web
from app.services.monitoramento_service import MonitoramentoService
from db.database import SessionLocal

router = APIRouter()
from app.template_config import templates

logger = logging.getLogger(__name__)


def _get_tenant_id(request: Request, user: dict) -> str:
    """Extrai o tenant_id do request.state ou do usuário logado."""
    if hasattr(request.state, "tenant_id") and request.state.tenant_id:
        return str(request.state.tenant_id)
    if isinstance(user, dict) and user.get("tenant_id"):
        return str(user["tenant_id"])
    return "default"


@router.get("/", response_class=HTMLResponse)
async def monitoramento_page(
    request: Request,
    user: dict = Depends(require_permission_web("monitoramento:read"))
):
    """Página principal de monitoramento."""
    # TODO: Implementar listagem real de monitoramentos do tenant
    return templates.TemplateResponse(
        request=request,
        name="monitoramento.html",
        context={
            "request": request,
            "usuario": user,
            "monitoramentos": [],
            "titulo": "Monitoramento de Safras",
            "permissoes": user.get("permissions", [])
        }
    )


@router.get("/novo", response_class=HTMLResponse)
async def monitoramento_novo_page(
    request: Request,
    user: dict = Depends(require_permission_web("monitoramento:write"))
):
    """Página para novo monitoramento."""
    return templates.TemplateResponse(
        request=request,
        name="monitoramento_nova.html",
        context={
            "request": request,
            "usuario": user,
            "titulo": "Novo Monitoramento",
            "permissoes": user.get("permissions", [])
        }
    )
