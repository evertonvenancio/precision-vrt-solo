"""
Precision VRT Solo - Rotas Web do Módulo Financeiro
Integração completa com Vendas e Títulos Financeiros.
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import date
import logging

from app.web.auth_dependencies import require_permission_web
from app.services.financeiro_service import FinanceiroService
from app.services.vendas_service import VendasService
from db.database import SessionLocal

router = APIRouter()
from app.template_config import templates

logger = logging.getLogger(__name__)


def _get_tenant_id(request: Request, user: dict) -> str:
    if hasattr(request.state, "tenant_id") and request.state.tenant_id:
        return str(request.state.tenant_id)
    if isinstance(user, dict) and user.get("tenant_id"):
        return str(user["tenant_id"])
    return "default"


@router.get("/contas-receber", response_class=HTMLResponse)
async def listar_contas_receber(
    request: Request,
    user: dict = Depends(require_permission_web("financeiro:read"))
):
    """Lista títulos a receber."""
    tenant_id = _get_tenant_id(request, user)
    db = SessionLocal()
    try:
        service = FinanceiroService(db, user_data=user)
        contas = service.listar_contas_receber()

        return templates.TemplateResponse(
            request=request,
            name="financeiro/contas_receber.html",
            context={
                "request": request,
                "usuario": user,
                "contas": contas,
                "titulo": "Contas a Receber",
                "hoje": date.today().isoformat(),
                "permissoes": user.get("permissions", [])
            }
        )
    finally:
        db.close()


@router.post("/baixar-titulo/{titulo_id}")
async def baixar_titulo_financeiro(
    request: Request,
    titulo_id: str,
    user: dict = Depends(require_permission_web("financeiro:write"))
):
    """Realiza a baixa de um título financeiro através do VendasService."""
    form_data = await request.form()
    dados = dict(form_data)
    usuario_id = str(user.get("id"))
    tenant_id = _get_tenant_id(request, user)

    db = SessionLocal()
    try:
        # Reutilizando a lógica de VendasService conforme orientação
        service = VendasService(db, tenant_id=tenant_id)
        service.baixar_titulo(titulo_id, dados, usuario_id=usuario_id)
        db.commit()

        return RedirectResponse(
            url="/web/financeiro/contas-receber",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao baixar título: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@router.get("/caixa", response_class=HTMLResponse)
async def resumo_caixa(
    request: Request,
    user: dict = Depends(require_permission_web("financeiro:read"))
):
    """Resumo de caixa."""
    tenant_id = _get_tenant_id(request, user)
    db = SessionLocal()
    try:
        service = FinanceiroService(db, user_data=user)
        resumo = service.obter_resumo_caixa()

        return templates.TemplateResponse(
            request=request,
            name="financeiro/caixa.html",
            context={
                "request": request,
                "usuario": user,
                "resumo": resumo,
                "titulo": "Resumo de Caixa",
                "permissoes": user.get("permissions", [])
            }
        )
    finally:
        db.close()
