"""
Precision VRT Solo - Rotas do Módulo Bulk Blend

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.bulk_blend_service import BulkBlendService

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/bulk-blend")
async def bulk_blend_page(request: Request, db: Session = Depends(get_db)):
    service = BulkBlendService()
    return templates.TemplateResponse(request=request, name="bulk_blend.html", context={})
