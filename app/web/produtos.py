"""
Precision VRT Solo - Rotas do Módulo Produtos
"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from app.services.clientes_service import ClientesService

router = APIRouter()
from app.web.auth_dependencies import require_permission_web  # autenticação via cookie
from app.template_config import templates

@router.get("/")
async def produtos_page(request: Request, db: Session = Depends(get_db)):
    service = ClientesService(db)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(request=request, name="tabela_precos.html", context={"permissoes": permissoes})