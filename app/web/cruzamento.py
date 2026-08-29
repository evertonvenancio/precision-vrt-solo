"""
Precision VRT Solo - Rotas do Módulo Cruzamento

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.cruzamento_service import CruzamentoService

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/cruzamento")
async def cruzamento_page(request: Request, db: Session = Depends(get_db)):
    service = CruzamentoService(db)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(
        request=request,
        name="cruzamento.html",
        context={"permissoes": permissoes}
    )
