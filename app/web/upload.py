"""Precision VRT Solo — Rotas do Módulo Upload

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Form, Depends, UploadFile, File
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.upload_service import UploadService

router = APIRouter()
from app.web.auth_dependencies import require_permission_web  # autenticação via cookie
from app.template_config import templates  # compartilhado - globals de RBAC


@router.get("/upload")
async def upload_page(request: Request, db: Session = Depends(get_db)):
    """Página de upload de arquivos"""
    return templates.TemplateResponse("upload.html", {"request": request})


@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Processar upload de arquivo"""
    try:
        upload_service = UploadService()
        resultado = await upload_service.processar_arquivo(file)
        
        return templates.TemplateResponse(
            "upload_resultado.html", 
            {"request": request, "resultado": resultado}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "upload.html", 
            {"request": request, "error": str(e)}
        )


@router.get("/upload/tipos-suportados")
async def get_tipos_suportados():
    """Retornar tipos de arquivos suportados"""
    return {
        "tipos": ["CSV", "XLSX", "SHP", "GeoJSON", "TIFF", "ZIP", "ISOXML"],
        "descricao": "Formatos suportados para upload e processamento"
    }
