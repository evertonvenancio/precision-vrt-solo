"""
Precision VRT Solo — Rotas do Módulo Nematoides

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
"""

import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, Request, UploadFile, File, Depends, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.nematoides_service import NematoidesService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Diretórios
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/nematoides")
async def nematoides_page(request: Request, db: Session = Depends(get_db)):
    """Página principal do módulo nematoides."""
    service = NematoidesService(db)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(
        request=request,
        name="nematoides.html",
        context={"permissoes": permissoes},
    )


@router.get("/nematoides/nova")
async def nematoides_nova_page(request: Request, db: Session = Depends(get_db)):
    """Página de nova análise de nematoides."""
    service = NematoidesService(db)
    context = service.get_contexto_nova_page()
    return templates.TemplateResponse(
        request=request,
        name="nematoides_nova.html",
        context=context,
    )


@router.post("/nematoides/upload")
async def nematoides_upload_geo(
    amostras_nematoides: UploadFile = File(...),
    limite_talhao: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    """Upload e pré-processamento de amostras de nematoides."""
    try:
        # Salvar uploads
        amostras_path = UPLOAD_DIR / f"amostras_nematoides_{uuid.uuid4().hex}_{amostras_nematoides.filename}"
        with open(amostras_path, "wb") as buffer:
            shutil.copyfileobj(amostras_nematoides.file, buffer)

        limite_path = None
        if limite_talhao and limite_talhao.filename:
            limite_path = UPLOAD_DIR / f"limite_talhao_{uuid.uuid4().hex}_{limite_talhao.filename}"
            with open(limite_path, "wb") as buffer:
                shutil.copyfileobj(limite_talhao.file, buffer)

        service = NematoidesService(db)
        return service.processar_upload_geo(str(amostras_path), str(limite_path) if limite_path else None)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")


@router.post("/nematoides/processar")
async def nematoides_processar(
    limite_talhao: UploadFile = File(...),
    amostras_nematoides: UploadFile = File(...),
    cliente_id: str = Form(""),
    talhao_nome: str = Form(""),
    cultura: str = Form("soja"),
    produtividade: float = Form(3.0),
    n_zonas: int = Form(4),
    metodologia: str = Form("IAC_Graos"),
    db: Session = Depends(get_db),
):
    """Executa o pipeline completo de análise de nematoides."""
    try:
        # Salvar uploads
        limite_path = UPLOAD_DIR / f"limite_talhao_{uuid.uuid4().hex}_{limite_talhao.filename}"
        with open(limite_path, "wb") as buffer:
            shutil.copyfileobj(limite_talhao.file, buffer)

        amostras_path = UPLOAD_DIR / f"amostras_nematoides_{uuid.uuid4().hex}_{amostras_nematoides.filename}"
        with open(amostras_path, "wb") as buffer:
            shutil.copyfileobj(amostras_nematoides.file, buffer)

        service = NematoidesService(db)
        return service.processar_nematoides(
            str(amostras_path),
            str(limite_path),
            cliente_id,
            talhao_nome,
            cultura,
            produtividade,
            n_zonas,
            metodologia,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar: {str(e)}")


@router.get("/nematoides/resultado")
async def nematoides_resultado(
    request: Request,
    db: Session = Depends(get_db),
):
    """Página de resultado da análise de nematoides."""
    service = NematoidesService(db)
    context = service.get_resultado_context(request)
    return templates.TemplateResponse(
        request=request,
        name="nematoides_resultado.html",
        context=context,
    )