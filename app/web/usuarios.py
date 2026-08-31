"""
Precision VRT Solo - Rotas do Módulo Usuários
"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from app.services.usuarios_service import UsuariosService

router = APIRouter()
from app.web.auth_dependencies import require_permission_web  # autenticação via cookie
from app.template_config import templates

@router.get("/")
async def usuarios_page(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission_web("usuarios:read"))
):
    service = UsuariosService(db, user)
    permissoes = service.buscar_permissoes()
    usuarios = service.listar_usuarios()
    return templates.TemplateResponse(
        request=request,
        name="permissoes.html",
        context={
            "usuarios": usuarios,
            "permissoes": permissoes,
            "usuario": user
        }
    )
