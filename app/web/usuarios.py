"""
Precision VRT Solo - Rotas do Módulo Usuários
"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from app.services.usuarios_service import UsuariosService

router = APIRouter()
from app.template_config import templates

@router.get("/")
async def usuarios_page(request: Request, db: Session = Depends(get_db)):
    service = UsuariosService(db)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(request=request, name="permissoes.html", context={"permissoes": permissoes})
