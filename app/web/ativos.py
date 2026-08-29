"""
Precision VRT Solo - Rotas do Módulo Ativos

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.ativos_service import AtivosService

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/ativos")
async def ativos_page(request: Request, db: Session = Depends(get_db)):
    service = AtivosService(db)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(
        request=request,
        name="ativos.html",
        context={"permissoes": permissoes}
    )


@router.get("/ativos/novo")
async def novo_ativo_page(request: Request, db: Session = Depends(get_db)):
    service = AtivosService(db)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(
        request=request,
        name="novo_ativo.html",
        context={"permissoes": permissoes}
    )
