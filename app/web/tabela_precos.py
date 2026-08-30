"""
Precision VRT Solo - Rotas do Módulo Tabela de Preços

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.tabela_precos_service import TabelaPrecosService

router = APIRouter()
from app.web.auth_dependencies import require_permission_web  # autenticação via cookie
from app.template_config import templates  # compartilhado - globals de RBAC



@router.get("/cadastros/precos")
async def tabela_precos_page(request: Request, db: Session = Depends(get_db)):
    service = TabelaPrecosService(db)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(request=request, name="tabela_precos.html", context={"permissoes": permissoes})
