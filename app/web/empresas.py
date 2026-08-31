"""
Precision VRT Solo - Rotas do Módulo Empresa
Gestão de empresas (CNPJs) vinculadas a um cliente.

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.empresa_service import EmpresaService

from app.web.auth_dependencies import require_permission_web  # autenticação via cookie
from app.template_config import templates  # compartilhado - globals de RBAC


router = APIRouter()


# === Rotas de listagem ===

@router.get("/clientes/{cliente_id}/empresas", response_class=HTMLResponse)
async def listar_empresas(request: Request, cliente_id: str, db: Session = Depends(get_db)):
    await require_permission_web("empresas:read")(request)
    service = EmpresaService(db, user_data={"tenant_id": request.state.tenant_id if hasattr(request.state, 'tenant_id') else "default"})
    empresas = service.listar_por_cliente(cliente_id=cliente_id)
    return templates.TemplateResponse(
        request=request,
        name="empresas_lista.html",
        context={"cliente_id": cliente_id, "empresas": empresas}
    )


# === Rotas de formulário ===

@router.get("/clientes/{cliente_id}/empresas/novo", response_class=HTMLResponse)
async def formulario_nova_empresa(request: Request, cliente_id: str):
    await require_permission_web("empresas:write")(request)
    return templates.TemplateResponse(
        request=request,
        name="empresas_form.html",
        context={"cliente_id": cliente_id, "empresa": None}
    )


@router.post("/clientes/{cliente_id}/empresas/novo")
async def criar_empresa(request: Request, cliente_id: str, db: Session = Depends(get_db)):
    await require_permission_web("empresas:write")(request)
    form = await request.form()
    service = EmpresaService(db, user_data={"tenant_id": request.state.tenant_id if hasattr(request.state, 'tenant_id') else "default"})
    result = service.criar(
        cliente_id=cliente_id,
        cnpj=form["cnpj"],
        nome_fantasia=form["nome_fantasia"],
        razao_social=form["razao_social"],
    )
    return RedirectResponse(url=f"/web/clientes/{cliente_id}/empresas", status_code=302)


# === Rotas de edição ===

@router.get("/clientes/{cliente_id}/empresas/{empresa_id}/editar", response_class=HTMLResponse)
async def formulario_editar_empresa(request: Request, cliente_id: str, empresa_id: str, db: Session = Depends(get_db)):
    await require_permission_web("empresas:write")(request)
    service = EmpresaService(db, user_data={"tenant_id": request.state.tenant_id if hasattr(request.state, 'tenant_id') else "default"})
    empresa = service.obter(empresa_id=empresa_id)
    return templates.TemplateResponse(
        request=request,
        name="empresas_form.html",
        context={"cliente_id": cliente_id, "empresa": empresa}
    )


@router.post("/clientes/{cliente_id}/empresas/{empresa_id}/editar")
async def atualizar_empresa(request: Request, cliente_id: str, empresa_id: str, db: Session = Depends(get_db)):
    await require_permission_web("empresas:write")(request)
    form = await request.form()
    service = EmpresaService(db, user_data={"tenant_id": request.state.tenant_id if hasattr(request.state, 'tenant_id') else "default"})
    service.atualizar(
        empresa_id=empresa_id,
        cnpj=form["cnpj"],
        nome_fantasia=form["nome_fantasia"],
        razao_social=form["razao_social"],
    )
    return RedirectResponse(url=f"/web/clientes/{cliente_id}/empresas", status_code=302)


# === Rotas de remoção ===

@router.post("/clientes/{cliente_id}/empresas/{empresa_id}/remover")
async def remover_empresa(request: Request, cliente_id: str, empresa_id: str, db: Session = Depends(get_db)):
    await require_permission_web("empresas:write")(request)
    service = EmpresaService(db, user_data={"tenant_id": request.state.tenant_id if hasattr(request.state, 'tenant_id') else "default"})
    service.remover(empresa_id=empresa_id)
    return RedirectResponse(url=f"/web/clientes/{cliente_id}/empresas", status_code=302)