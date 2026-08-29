"""
Precision VRT Solo - Rotas do Módulo Clima

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.clima_service import ClimaService
from config.clima_config import clima_config

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/clima")
async def clima_page(request: Request, db: Session = Depends(get_db)):
    service = ClimaService(api_key=clima_config.api_key, config=clima_config)
    permissoes = service.buscar_permissoes(db)
    return templates.TemplateResponse(
        request=request,
        name="clima.html",
        context={"permissoes": permissoes}
    )
