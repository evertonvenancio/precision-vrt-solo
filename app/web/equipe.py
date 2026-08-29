"""
Precision VRT Solo - Rotas do Módulo Equipe

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.equipe_service import EquipeService

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/equipe")
async def equipe_page(request: Request, db: Session = Depends(get_db)):
    service = EquipeService(db)
    permissoes = service.buscar_permissoes()
    funcionarios = service.listar_funcionarios()
    return templates.TemplateResponse(request=request, name="equipe.html", context={"funcionarios": funcionarios, "permissoes": permissoes})


@router.get("/equipe/novo-funcionario")
async def novo_funcionario_page(request: Request, db: Session = Depends(get_db)):
    service = EquipeService(db)
    permissoes = service.buscar_permissoes()
    contexto = service.get_contexto_novo_funcionario()
    return templates.TemplateResponse(request=request, name="novo_funcionario.html", context={**contexto, "permissoes": permissoes})


@router.get("/equipe/permissoes")
async def permissoes_page(request: Request, db: Session = Depends(get_db)):
    service = EquipeService(db)
    return service.get_pagina_permissoes()
