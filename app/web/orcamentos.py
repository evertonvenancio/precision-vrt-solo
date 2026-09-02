"""
Precision VRT Solo - Rotas Web do Módulo Orçamentos
Integração completa com RBAC, multi-tenancy e serviços reais.
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
import io

from app.web.auth_dependencies import require_permission_web
from app.services.orcamentos_service import OrcamentosService
from db.database import SessionLocal

router = APIRouter()
from app.template_config import templates  # compartilhado - globals de RBAC


def _get_tenant_id(request: Request, user: dict) -> str:
    """Extrai o tenant_id do request.state ou do usuário logado."""
    if hasattr(request.state, "tenant_id") and request.state.tenant_id:
        return str(request.state.tenant_id)
    if isinstance(user, dict) and user.get("tenant_id"):
        return str(user["tenant_id"])
    return "default"


@router.get("/", response_class=HTMLResponse)
async def listar_orcamentos(
    request: Request,
    user: dict = Depends(require_permission_web("orcamentos:read"))
):
    """
    Lista todos os orçamentos do tenant atual.
    Exige permissão: orcamentos:read
    """
    tenant_id = _get_tenant_id(request, user)
    db = SessionLocal()
    try:
        service = OrcamentosService(db, tenant_id=tenant_id)
        orcamentos = service.listar_orcamentos()

        return templates.TemplateResponse(
            request=request,
            name="orcamentos/lista.html",
            context={
                "request": request,
                "usuario": user,
                "orcamentos": orcamentos,
                "titulo": "Orçamentos",
                "permissoes": user.get("permissions", [])
            }
        )
    finally:
        db.close()


@router.get("/novo", response_class=HTMLResponse)
async def novo_orcamento(
    request: Request,
    user: dict = Depends(require_permission_web("orcamentos:write"))
):
    """
    Formulário para criar novo orçamento.
    Exige permissão: orcamentos:write
    """
    tenant_id = _get_tenant_id(request, user)
    db = SessionLocal()
    try:
        service = OrcamentosService(db, tenant_id=tenant_id)
        clientes = service.listar_clientes_ativos()

        return templates.TemplateResponse(
            request=request,
            name="orcamentos/formulario.html",
            context={
                "request": request,
                "usuario": user,
                "clientes": clientes,
                "orcamento": None,
                "titulo": "Novo Orçamento",
                "permissoes": user.get("permissions", [])
            }
        )
    finally:
        db.close()


@router.get("/{orcamento_id}", response_class=HTMLResponse)
async def detalhar_orcamento(
    request: Request,
    orcamento_id: str,
    user: dict = Depends(require_permission_web("orcamentos:read"))
):
    """
    Detalhes de um orçamento específico.
    Exige permissão: orcamentos:read
    """
    tenant_id = _get_tenant_id(request, user)
    db = SessionLocal()
    try:
        service = OrcamentosService(db, tenant_id=tenant_id)
        orcamento = service.buscar_por_id(orcamento_id)

        if not orcamento:
            raise HTTPException(status_code=404, detail="Orçamento não encontrado")

        return templates.TemplateResponse(
            request=request,
            name="orcamentos/detalhes.html",
            context={
                "request": request,
                "usuario": user,
                "orcamento": orcamento,
                "titulo": f"Orçamento #{str(orcamento_id)[:8]}",
                "permissoes": user.get("permissions", [])
            }
        )
    finally:
        db.close()


@router.post("/salvar")
async def salvar_orcamento(
    request: Request,
    user: dict = Depends(require_permission_web("orcamentos:write"))
):
    """
    Salva um novo orçamento.
    Exige permissão: orcamentos:write
    """
    form_data = await request.form()
    dados = dict(form_data)
    dados["usuario_id"] = str(user.get("id"))

    tenant_id = _get_tenant_id(request, user)
    db = SessionLocal()
    try:
        service = OrcamentosService(db, tenant_id=tenant_id)
        resultado = service.salvar_orcamento(dados)

        return RedirectResponse(
            url=f"/web/orcamentos/{resultado['id']}",
            status_code=303
        )
    finally:
        db.close()


@router.post("/{orcamento_id}/aprovar")
async def aprovar_orcamento(
    request: Request,
    orcamento_id: str,
    user: dict = Depends(require_permission_web("orcamentos:aprovar"))
):
    """
    Aprova um orçamento.
    Exige permissão: orcamentos:aprovar
    """
    tenant_id = _get_tenant_id(request, user)
    usuario_id = str(user.get("id"))
    db = SessionLocal()
    try:
        service = OrcamentosService(db, tenant_id=tenant_id)
        service.aprovar_orcamento(orcamento_id, usuario_id)

        return RedirectResponse(
            url=f"/web/orcamentos/{orcamento_id}",
            status_code=303
        )
    finally:
        db.close()


@router.get("/{orcamento_id}/pdf")
async def gerar_pdf_orcamento(
    request: Request,
    orcamento_id: str,
    user: dict = Depends(require_permission_web("orcamentos:export"))
):
    """
    Gera PDF do orçamento.
    Exige permissão: orcamentos:export
    """
    tenant_id = _get_tenant_id(request, user)
    db = SessionLocal()
    try:
        service = OrcamentosService(db, tenant_id=tenant_id)
        pdf_bytes = service.gerar_pdf(orcamento_id)

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=orcamento_{str(orcamento_id)[:8]}.pdf"
            }
        )
    finally:
        db.close()
