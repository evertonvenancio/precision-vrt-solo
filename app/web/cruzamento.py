"""
Precision VRT Solo - Rotas do Módulo Cruzamento

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.cruzamento_service import CruzamentoService

router = APIRouter()
from app.template_config import templates  # compartilhado - globals de RBAC



@router.get("/cruzamento")
async def cruzamento_page(request: Request, db: Session = Depends(get_db)):
    service = CruzamentoService(db)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(
        request=request,
        name="cruzamento.html",
        context={"permissoes": permissoes}
    )
