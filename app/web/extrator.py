"""
Precision VRT Solo - Rotas do Módulo Extrator

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.extrator_service import ExtratorService

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/extrator")
async def extrator_page(request: Request, db: Session = Depends(get_db)):
    service = ExtratorService(db)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(
        request=request,
        name="extrator.html",
        context={"permissoes": permissoes}
    )
