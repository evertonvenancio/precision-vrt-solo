"""
Precision VRT Solo - Rotas do Módulo Caixa

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.caixa_service import CaixaService

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/financeiro/caixa")
async def caixa_page(request: Request, db: Session = Depends(get_db)):
    service = CaixaService(db)
    permissoes = service.buscar_permissoes()
    contexto = service.get_contexto()
    return templates.TemplateResponse(request=request, name="financeiro.html", context={**contexto, "permissoes": permissoes})
