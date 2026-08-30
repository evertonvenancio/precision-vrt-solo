"""
Precision VRT Solo - Rotas do Módulo Ativos

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.ativos_service import AtivosService

router = APIRouter()
from app.web.auth_dependencies import require_permission_web  # autenticação via cookie
from app.template_config import templates  # compartilhado - globals de RBAC



@router.get("/")
async def ativos_page(request: Request, db: Session = Depends(get_db)):
    service = AtivosService(db)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(
        request=request,
        name="ativos.html",
        context={"permissoes": permissoes}
    )


@router.get("/novo")
async def novo_ativo_page(request: Request, db: Session = Depends(get_db)):
    service = AtivosService(db)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(
        request=request,
        name="novo_ativo.html",
        context={"permissoes": permissoes}
    )
