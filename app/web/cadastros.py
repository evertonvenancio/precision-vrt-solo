"""
Precision VRT Solo - Rotas do Módulo Cadastros

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.clientes_service import ClientesService

router = APIRouter()
from app.template_config import templates  # compartilhado - globals de RBAC


@router.get("/")
async def cadastros_page(request: Request, db: Session = Depends(get_db)):
    service = ClientesService(db)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(
        request=request,
        name="clientes.html",
        context={"permissoes": permissoes}
    )