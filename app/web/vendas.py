"""
Precision VRT Solo - Rotas Web do Módulo Vendas
Integração completa com RBAC e serviços reais.
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional

from core.authorization.dependencies import require_permission, get_user_permissions
from app.services.vendas_service import VendasService
from db.database import SessionLocal

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def listar_vendas(
    request: Request,
    usuario: dict = Depends(require_permission("vendas:read"))
):
    """
    Lista todas as vendas do tenant atual.
    Exige permissão: vendas:read
    """
    db = SessionLocal()
    try:
        service = VendasService(db)
        vendas = service.listar_vendas()

        return templates.TemplateResponse(
            request=request,
            name="vendas/lista.html",
            context={
                "request": request,
                "usuario": usuario,
                "vendas": vendas,
                "titulo": "Vendas",
                "permissoes": usuario.get("permissions", [])
            }
        )
    finally:
        db.close()


@router.get("/novo", response_class=HTMLResponse)
async def nova_venda(
    request: Request,
    usuario: dict = Depends(require_permission("vendas:write"))
):
    """
    Formulário para criar nova venda.
    Exige permissão: vendas:write
    """
    db = SessionLocal()
    try:
        service = VendasService(db)
        clientes = service.listar_clientes_ativos()
        orcamentos = service.listar_orcamentos_aprovados()

        return templates.TemplateResponse(
            request=request,
            name="vendas/formulario.html",
            context={
                "request": request,
                "usuario": usuario,
                "clientes": clientes,
                "orcamentos": orcamentos,
                "venda": None,
                "titulo": "Nova Venda",
                "permissoes": usuario.get("permissions", [])
            }
        )
    finally:
        db.close()


@router.get("/{venda_id}", response_class=HTMLResponse)
async def detalhar_venda(
    request: Request,
    venda_id: int,
    usuario: dict = Depends(require_permission("vendas:read"))
):
    """
    Detalhes de uma venda específica.
    Exige permissão: vendas:read
    """
    db = SessionLocal()
    try:
        service = VendasService(db)
        venda = service.buscar_por_id(venda_id)

        if not venda:
            raise HTTPException(status_code=404, detail="Venda não encontrada")

        return templates.TemplateResponse(
            request=request,
            name="vendas/detalhes.html",
            context={
                "request": request,
                "usuario": usuario,
                "venda": venda,
                "titulo": f"Venda #{venda_id}",
                "permissoes": usuario.get("permissions", [])
            }
        )
    finally:
        db.close()


@router.post("/registrar-avista")
async def registrar_venda_avista(
    request: Request,
    usuario: dict = Depends(require_permission("vendas:write"))
):
    """
    Registra uma venda à vista.
    Exige permissão: vendas:write
    """
    form_data = await request.form()
    dados = dict(form_data)

    db = SessionLocal()
    try:
        service = VendasService(db)
        venda = service.registrar_venda_avista(dados)
        db.commit()

        return RedirectResponse(
            url=f"/web/vendas/{venda.id}",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@router.post("/registrar-prazo")
async def registrar_venda_prazo(
    request: Request,
    usuario: dict = Depends(require_permission("vendas:write"))
):
    """
    Registra uma venda a prazo.
    Exige permissão: vendas:write
    """
    form_data = await request.form()
    dados = dict(form_data)

    db = SessionLocal()
    try:
        service = VendasService(db)
        venda = service.registrar_venda_prazo(dados)
        db.commit()

        return RedirectResponse(
            url=f"/web/vendas/{venda.id}",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@router.post("/{venda_id}/baixar-titulo")
async def baixar_titulo(
    request: Request,
    venda_id: int,
    titulo_id: int,
    usuario: dict = Depends(require_permission("vendas:write"))
):
    """
    Realiza a baixa de um título financeiro.
    Exige permissão: vendas:write
    """
    form_data = await request.form()
    dados = dict(form_data)

    db = SessionLocal()
    try:
        service = VendasService(db)
        service.baixar_titulo(titulo_id, dados)
        db.commit()

        return RedirectResponse(
            url=f"/web/vendas/{venda_id}",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@router.get("/{venda_id}/nf")
async def gerar_nota_fiscal(
    request: Request,
    venda_id: int,
    usuario: dict = Depends(require_permission("vendas:faturar"))
):
    """
    Gera nota fiscal da venda.
    Exige permissão: vendas:faturar
    """
    db = SessionLocal()
    try:
        service = VendasService(db)
        nf_bytes = service.gerar_nota_fiscal(venda_id)

        from fastapi.responses import StreamingResponse
        import io

        return StreamingResponse(
            io.BytesIO(nf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=nf_venda_{venda_id}.pdf"
            }
        )
    finally:
        db.close()