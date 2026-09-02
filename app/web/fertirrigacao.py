"""
Precision VRT Solo - Rotas Web do Módulo Fertirrigação
Integração completa com RBAC, multi-tenancy e motor de fertirrigação real.
"""

from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import shutil
from pathlib import Path
import logging

from app.web.auth_dependencies import require_permission_web
from app.services.fertirrigacao_service import FertirrigacaoService
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
async def fertirrigacao_page(
    request: Request,
    user: dict = Depends(require_permission_web("fertirrigacao:read"))
):
    """Página principal de fertirrigação."""
    tenant_id = _get_tenant_id(request, user)

    return templates.TemplateResponse(
        request=request,
        name="fertirrigacao.html",
        context={
            "request": request,
            "usuario": user,
            "tenant_id": tenant_id,
            "titulo": "Fertirrigação",
            "permissoes": user.get("permissions", [])
        }
    )


@router.get("/nova", response_class=HTMLResponse)
async def fertirrigacao_nova_page(
    request: Request,
    user: dict = Depends(require_permission_web("fertirrigacao:write"))
):
    """Formulário para novo cálculo de fertirrigação."""
    tenant_id = _get_tenant_id(request, user)

    return templates.TemplateResponse(
        request=request,
        name="fertirrigacao_nova.html",
        context={
            "request": request,
            "usuario": user,
            "tenant_id": tenant_id,
            "titulo": "Nova Fertirrigação",
            "permissoes": user.get("permissions", [])
        }
    )


@router.post("/processar")
async def processar_fertirrigacao(
    request: Request,
    arquivo_irrigacao: UploadFile = File(...),
    arquivo_fertilizante: UploadFile = File(None),
    cultura: str = Form(""),
    user: dict = Depends(require_permission_web("fertirrigacao:write"))
):
    """Executa o cálculo real de fertirrigação via motor existente."""
    tenant_id = _get_tenant_id(request, user)

    upload_dir = Path("uploads_temp")
    upload_dir.mkdir(exist_ok=True)

    irr_path = upload_dir / f"{tenant_id}_irrigacao_{arquivo_irrigacao.filename}"
    fert_path = None
    if arquivo_fertilizante:
        fert_path = upload_dir / f"{tenant_id}_fertilizante_{arquivo_fertilizante.filename}"

    try:
        with open(irr_path, "wb") as buffer:
            shutil.copyfileobj(arquivo_irrigacao.file, buffer)

        if arquivo_fertilizante and fert_path:
            with open(fert_path, "wb") as buffer:
                shutil.copyfileobj(arquivo_fertilizante.file, buffer)

        service = FertirrigacaoService()
        resultado = service.processar_fertirrigacao(
            arquivo_irrigacao_path=str(irr_path),
            arquivo_fertilizante_path=str(fert_path) if fert_path else None,
            cultura=cultura or None,
            configuracoes={"tenant_id": tenant_id}
        )

        if not resultado.get("success"):
            raise HTTPException(status_code=400, detail=resultado.get("error", "Erro no cálculo"))

        return RedirectResponse(url="/web/fertirrigacao", status_code=303)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no endpoint de fertirrigação: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        for f in [irr_path, fert_path]:
            if f and f.exists():
                try:
                    os.remove(f)
                except Exception:
                    pass
