"""
Precision VRT Solo - Rotas do Módulo Financeiro

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.financeiro_service import FinanceiroService

router = APIRouter()
from app.web.auth_dependencies import require_permission_web  # autenticação via cookie
from app.template_config import templates  # compartilhado - globals de RBAC



@router.get("/")
async def financeiro_page(request: Request, db: Session = Depends(get_db)):
    service = FinanceiroService(db)
    permissoes = service.buscar_permissoes()
    orcamentos = service.listar_orcamentos()
    return templates.TemplateResponse(request=request, name="financeiro.html", context={"orcamentos": orcamentos, "permissoes": permissoes})


@router.get("/novo-orcamento")
async def novo_orcamento_page(request: Request, db: Session = Depends(get_db)):
    service = FinanceiroService(db)
    permissoes = service.buscar_permissoes()
    clientes = service.listar_clientes_ativos()
    return templates.TemplateResponse(request=request, name="novo_orcamento.html", context={"clientes": clientes, "permissoes": permissoes})


@router.post("/novo-orcamento")
async def salvar_orcamento(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    dados = dict(form_data)
    cliente_id = dados.get("cliente_id")

    # Converter valores numéricos
    try:
        dados["valor_total_bruto"] = float(dados.get("valor_total_bruto", 0))
    except ValueError:
        dados["valor_total_bruto"] = 0.0

    try:
        dados["desconto_percentual"] = float(dados.get("desconto_percentual", 0))
    except ValueError:
        dados["desconto_percentual"] = 0.0

    service = FinanceiroService(db, user_data={"tenant_id": "default", "permissions": ["financeiro:write"], "user_id": 1})
    resultado = service.salvar_orcamento(cliente_id, dados)

    if resultado.get("success"):
        return RedirectResponse(url="/financeiro", status_code=303)
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=resultado.get("detail", "Erro ao salvar orçamento"))


@router.get("/financeiro/caixa")
async def caixa_page(request: Request, db: Session = Depends(get_db)):
    service = FinanceiroService(db)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(request=request, name="financeiro.html", context={"permissoes": permissoes})
