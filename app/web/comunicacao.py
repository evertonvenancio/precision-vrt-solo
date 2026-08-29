"""
Precision VRT Solo - Rotas do Módulo Comunicação
"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from core.seguranca.permissions import get_permissoes

router = APIRouter()
from app.template_config import templates  # compartilhado - globals de RBAC



@router.get("/comunicacao")
async def comunicacao_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request=request, name="comunicacao.html", context={"permissoes": get_permissoes(db)})
