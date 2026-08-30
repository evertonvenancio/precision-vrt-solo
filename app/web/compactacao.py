"""
Precision VRT Solo - Rotas do Módulo Compactação

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.compactacao_service import CompactacaoService

router = APIRouter()
from app.web.auth_dependencies import require_permission_web  # autenticação via cookie
from app.template_config import templates  # compartilhado - globals de RBAC


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/")
async def compactacao_page(request: Request, db: Session = Depends(get_db)):
    service = CompactacaoService(db)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(
        request=request,
        name="compactacao.html",
        context={"permissoes": permissoes}
    )


@router.get("/nova")
async def compactacao_nova_page(request: Request, db: Session = Depends(get_db)):
    service = CompactacaoService(db)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(
        request=request,
        name="compactacao_nova.html",
        context={"permissoes": permissoes}
    )


@router.post("/upload")
async def compactacao_upload(
    request: Request,
    db: Session = Depends(get_db),
):
    """Upload CSV de dados de compactação."""
    form = await request.form()
    arquivo_csv = form.get("arquivo_csv")
    if not arquivo_csv or not hasattr(arquivo_csv, 'filename'):
        raise HTTPException(status_code=400, detail="Arquivo CSV não fornecido")

    try:
        # Salvar upload
        caminho_csv = UPLOAD_DIR / f"compactacao_{uuid.uuid4().hex}_{arquivo_csv.filename}"
        with open(caminho_csv, "wb") as buffer:
            shutil.copyfileobj(arquivo_csv.file, buffer)

        service = CompactacaoService(db)
        return service.processar_compactacao(str(caminho_csv))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")
