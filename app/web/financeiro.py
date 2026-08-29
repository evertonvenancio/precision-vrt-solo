"""
Precision VRT Solo - Rotas do Módulo Financeiro

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.financeiro_service import FinanceiroService

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/financeiro")
async def financeiro_page(request: Request, db: Session = Depends(get_db)):
    service = FinanceiroService(db)
    permissoes = service.buscar_permissoes()
    orcamentos = service.listar_orcamentos()
    return templates.TemplateResponse(request=request, name="financeiro.html", context={"orcamentos": orcamentos, "permissoes": permissoes})


@router.get("/financeiro/novo-orcamento")
async def novo_orcamento_page(request: Request, db: Session = Depends(get_db)):
    service = FinanceiroService(db)
    permissoes = service.buscar_permissoes()
    clientes = service.listar_clientes_ativos()
    return templates.TemplateResponse(request=request, name="novo_orcamento.html", context={"clientes": clientes, "permissoes": permissoes})


@router.post("/financeiro/novo-orcamento")
async def salvar_orcamento(request: Request, db: Session = Depends(get_db)):
    service = FinanceiroService(db)
    return service.salvar_orcamento_stub()


@router.get("/financeiro/caixa")
async def caixa_page(request: Request, db: Session = Depends(get_db)):
    service = FinanceiroService(db)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(request=request, name="financeiro.html", context={"permissoes": permissoes})
