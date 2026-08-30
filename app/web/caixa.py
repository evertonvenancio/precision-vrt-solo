"""
Precision VRT Solo - Rotas do Módulo Caixa

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.caixa_service import CaixaService

router = APIRouter()
from app.web.auth_dependencies import require_permission_web  # autenticação via cookie
from app.template_config import templates  # compartilhado - globals de RBAC



@router.get("/")
async def caixa_page(request: Request, db: Session = Depends(get_db)):
    service = CaixaService(db)
    permissoes = service.buscar_permissoes()
    contexto = service.get_contexto()
    return templates.TemplateResponse(request=request, name="caixa.html", context={**contexto, "permissoes": permissoes})
