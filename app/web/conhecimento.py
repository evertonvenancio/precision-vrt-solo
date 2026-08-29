"""
Precision VRT Solo - Rotas do Módulo Conhecimento
(Culturas, Metodologias, Bibliografia, Nematoides)

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.conhecimento_service import ConhecimentoService

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/base-tecnica/culturas")
async def culturas_page(request: Request, db: Session = Depends(get_db)):
    service = ConhecimentoService(db)
    permissoes = service.buscar_permissoes()
    try:
        return templates.TemplateResponse(
            request=request,
            name="base_tecnica.html",
            context={"titulo_pagina": "Culturas", "permissoes": permissoes}
        )
    except:
        return HTMLResponse(
            "<div class='p-8'><h1 class='text-2xl font-bold mb-4'>Culturas</h1>"
            "<p class='text-gray-500 dark:text-gray-400'>Modulo em construcao.</p></div>"
        )


@router.get("/base-tecnica/metodologias")
async def metodologias_page(request: Request, db: Session = Depends(get_db)):
    service = ConhecimentoService(db)
    permissoes = service.buscar_permissoes()
    try:
        return templates.TemplateResponse(
            request=request,
            name="base_tecnica.html",
            context={"titulo_pagina": "Metodologias e Formulas", "permissoes": permissoes}
        )
    except:
        return HTMLResponse(
            "<div class='p-8'><h1 class='text-2xl font-bold mb-4'>Metodologias e Formulas</h1>"
            "<p class='text-gray-500 dark:text-gray-400'>Modulo em construcao.</p></div>"
        )


@router.get("/base-tecnica/bibliografia")
async def bibliografia_page(request: Request, db: Session = Depends(get_db)):
    service = ConhecimentoService(db)
    permissoes = service.buscar_permissoes()
    try:
        return templates.TemplateResponse(
            request=request,
            name="base_tecnica.html",
            context={"titulo_pagina": "Bibliografia e Legislacao", "permissoes": permissoes}
        )
    except:
        return HTMLResponse(
            "<div class='p-8'><h1 class='text-2xl font-bold mb-4'>Bibliografia e Legislacao</h1>"
            "<p class='text-gray-500 dark:text-gray-400'>Modulo em construcao.</p></div>"
        )

