"""Precision VRT Solo — Rotas do Módulo Prescrição

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Form, Depends, UploadFile, File
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.prescricao_service import PrescricaoService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/prescricao")
async def prescricao_page(
    request: Request,
    db: Session = Depends(get_db),
):
    """Página principal do módulo prescrição."""
    service = PrescricaoService(db)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(
        request=request,
        name="prescricao.html",
        context={"permissoes": permissoes},
    )


@router.get("/prescricao/nova")
async def prescricao_nova_page(
    request: Request,
    db: Session = Depends(get_db),
):
    """Página de nova prescrição."""
    service = PrescricaoService(db)
    context = service.get_contexto_nova_page()
    return templates.TemplateResponse(
        request=request,
        name="prescricao_nova.html",
        context=context,
    )


@router.post("/prescricao/upload-geo")
async def upload_geo_prescricao(
    limite_talhao: UploadFile = File(...),
    amostras_solo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload e pré-processamento geoespacial (preview/validação)."""
    service = PrescricaoService(db)
    return service.processar_upload_geo(limite_talhao, amostras_solo)


@router.post("/prescricao/processar")
async def prescricao_processar(
    limite_talhao: UploadFile = File(...),
    amostras_solo: UploadFile = File(...),
    cliente_id: str = Form(""),
    talhao_nome: str = Form(""),
    cultura: str = Form("soja"),
    produtividade: float = Form(3.0),
    n_zonas: int = Form(4),
    metodologia: str = Form("IAC_Graos"),
    db: Session = Depends(get_db),
):
    """Executa o pipeline completo de prescrição VRT."""
    service = PrescricaoService(db)
    return service.processar_prescricao(
        limite_talhao,
        amostras_solo,
        cliente_id,
        talhao_nome,
        cultura,
        produtividade,
        n_zonas,
        metodologia,
    )


@router.get("/prescricao/resultado")
async def prescricao_resultado(
    request: Request,
    db: Session = Depends(get_db),
):
    """Página de resultado da prescrição."""
    service = PrescricaoService(db)
    context = service.get_resultado_context(request)
    return templates.TemplateResponse(
        request=request,
        name="prescricao_resultado.html",
        context=context,
    )
