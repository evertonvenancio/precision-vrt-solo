"""
Precision VRT Solo - Rotas Web do Módulo Orçamentos
Integração completa com RBAC e serviços reais.
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional

from app.web.auth_dependencies import require_permission_web
from app.services.orcamentos_service import OrcamentosService
from db.database import SessionLocal

router = APIRouter()
from app.template_config import templates  # compartilhado - globals de RBAC


@router.get("/", response_class=HTMLResponse)
async def listar_orcamentos(
    request: Request,
    user: dict = Depends(require_permission_web("orcamentos:read"))
):
    """
    Lista todos os orçamentos do tenant atual.
    Exige permissão: orcamentos:read
    """
    db = SessionLocal()
    try:
        service = OrcamentosService(db)
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
    db = SessionLocal()
    try:
        service = OrcamentosService(db)
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
    orcamento_id: int,
    user: dict = Depends(require_permission_web("orcamentos:read"))
):
    """
    Detalhes de um orçamento específico.
    Exige permissão: orcamentos:read
    """
    db = SessionLocal()
    try:
        service = OrcamentosService(db)
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
                "titulo": f"Orçamento #{orcamento_id}",
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
    Salva um novo orçamento ou atualiza existente.
    Exige permissão: orcamentos:write
    """
    form_data = await request.form()
    dados = dict(form_data)

    db = SessionLocal()
    try:
        service = OrcamentosService(db)
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
    orcamento_id: int,
    user: dict = Depends(require_permission_web("orcamentos:aprovar"))
):
    """
    Aprova um orçamento.
    Exige permissão: orcamentos:aprovar
    """
    db = SessionLocal()
    try:
        service = OrcamentosService(db)
        service.aprovar_orcamento(orcamento_id, user["id"])

        return RedirectResponse(
            url=f"/web/orcamentos/{orcamento_id}",
            status_code=303
        )
    finally:
        db.close()


@router.get("/{orcamento_id}/pdf")
async def gerar_pdf_orcamento(
    request: Request,
    orcamento_id: int,
    user: dict = Depends(require_permission_web("orcamentos:export"))
):
    """
    Gera PDF do orçamento.
    Exige permissão: orcamentos:export
    """
    db = SessionLocal()
    try:
        service = OrcamentosService(db)
        pdf_bytes = service.gerar_pdf(orcamento_id)

        from fastapi.responses import StreamingResponse
        import io

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=orcamento_{orcamento_id}.pdf"
            }
        )
    finally:
        db.close()
