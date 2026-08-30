"""
Precision VRT Solo - Rotas do Módulo Agenda
"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from app.services.clientes_service import ClientesService

router = APIRouter()
from app.template_config import templates

@router.get("/")
async def agenda_page(request: Request, db: Session = Depends(get_db)):
    service = ClientesService(db)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(request=request, name="relatorios.html", context={"permissoes": permissoes})
