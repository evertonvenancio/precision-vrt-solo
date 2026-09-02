"""
Precision VRT Solo - Rotas Web do Módulo Vendas
Integração completa com RBAC, multi-tenancy e serviços reais.
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
import io
import logging
from datetime import date

from app.web.auth_dependencies import require_permission_web
from app.services.vendas_service import VendasService
from db.database import SessionLocal

router = APIRouter()
from app.template_config import templates  # compartilhado - globals de RBAC

logger = logging.getLogger(__name__)


def _get_tenant_id(request: Request, user: dict) -> str:
    """Extrai o tenant_id do request.state ou do usuário logado."""
    if hasattr(request.state, "tenant_id") and request.state.tenant_id:
        return str(request.state.tenant_id)
    if isinstance(user, dict) and user.get("tenant_id"):
        return str(user["tenant_id"])
    return "default"


def _parse_parcelas_form(form_data: dict) -> list:
    """
    Converte dados do formulário como 'parcelas[0][valor]' em uma lista de dicionários.
    """
    parcelas = {}
    for key, value in form_data.items():
        if key.startswith("parcelas["):
            try:
                # Extrai o índice e o campo: "parcelas[0][valor]" -> "0", "valor"
                parts = key.replace("parcelas[", "").replace("]", "").split("[")
                idx = int(parts[0])
                field = parts[1]

                if idx not in parcelas:
                    parcelas[idx] = {}
                parcelas[idx][field] = value
            except (IndexError, ValueError):
                continue

    # Retorna lista ordenada pelos índices
    return [parcelas[i] for i in sorted(parcelas.keys())]


@router.get("/", response_class=HTMLResponse)
async def listar_vendas(
    request: Request,
    user: dict = Depends(require_permission_web("vendas:read"))
):
    """
    Lista todas as vendas do tenant atual.
    Exige permissão: vendas:read
    """
    tenant_id = _get_tenant_id(request, user)
    db = SessionLocal()
    try:
        service = VendasService(db, tenant_id=tenant_id)
        vendas = service.listar_vendas()

        return templates.TemplateResponse(
            request=request,
            name="vendas/lista.html",
            context={
                "request": request,
                "usuario": user,
                "vendas": vendas,
                "titulo": "Vendas",
                "permissoes": user.get("permissions", [])
            }
        )
    finally:
        db.close()


@router.get("/novo", response_class=HTMLResponse)
async def nova_venda(
    request: Request,
    user: dict = Depends(require_permission_web("vendas:write"))
):
    """
    Formulário para criar nova venda.
    Exige permissão: vendas:write
    """
    tenant_id = _get_tenant_id(request, user)
    db = SessionLocal()
    try:
        service = VendasService(db, tenant_id=tenant_id)
        clientes = service.listar_clientes_ativos()
        orcamentos = service.listar_orcamentos_aprovados()

        return templates.TemplateResponse(
            request=request,
            name="vendas/formulario.html",
            context={
                "request": request,
                "usuario": user,
                "clientes": clientes,
                "orcamentos": orcamentos,
                "venda": None,
                "titulo": "Nova Venda",
                "permissoes": user.get("permissions", [])
            }
        )
    finally:
        db.close()


@router.get("/{venda_id}", response_class=HTMLResponse)
async def detalhar_venda(
    request: Request,
    venda_id: str,
    user: dict = Depends(require_permission_web("vendas:read"))
):
    """
    Detalhes de uma venda específica.
    Exige permissão: vendas:read
    """
    tenant_id = _get_tenant_id(request, user)
    db = SessionLocal()
    try:
        service = VendasService(db, tenant_id=tenant_id)
        venda = service.buscar_por_id(venda_id)

        if not venda:
            raise HTTPException(status_code=404, detail="Venda não encontrada")

        return templates.TemplateResponse(
            request=request,
            name="vendas/detalhes.html",
            context={
                "request": request,
                "usuario": user,
                "venda": venda,
                "hoje": date.today().isoformat(),
                "titulo": f"Venda #{venda_id[:8]}",
                "permissoes": user.get("permissions", [])
            }
        )
    finally:
        db.close()


@router.post("/registrar-avista")
async def registrar_venda_avista(
    request: Request,
    user: dict = Depends(require_permission_web("vendas:write"))
):
    """
    Registra uma venda à vista.
    Exige permissão: vendas:write
    """
    form_data = await request.form()
    dados = dict(form_data)
    usuario_id = str(user.get("id"))
    tenant_id = _get_tenant_id(request, user)

    db = SessionLocal()
    try:
        service = VendasService(db, tenant_id=tenant_id)
        venda = service.registrar_venda_avista(dados, usuario_id=usuario_id)
        db.commit()

        return RedirectResponse(
            url=f"/web/vendas/{venda.id}",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao registrar venda à vista: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@router.post("/registrar-prazo")
async def registrar_venda_prazo(
    request: Request,
    user: dict = Depends(require_permission_web("vendas:write"))
):
    """
    Registra uma venda a prazo.
    Exige permissão: vendas:write
    """
    form_data = await request.form()
    dados = dict(form_data)
    dados["parcelas"] = _parse_parcelas_form(dados)

    usuario_id = str(user.get("id"))
    tenant_id = _get_tenant_id(request, user)

    db = SessionLocal()
    try:
        service = VendasService(db, tenant_id=tenant_id)
        venda = service.registrar_venda_prazo(dados, usuario_id=usuario_id)
        db.commit()

        return RedirectResponse(
            url=f"/web/vendas/{venda.id}",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao registrar venda a prazo: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@router.post("/{venda_id}/baixar-titulo")
async def baixar_titulo(
    request: Request,
    venda_id: str,
    titulo_id: str,
    user: dict = Depends(require_permission_web("vendas:write"))
):
    """
    Realiza a baixa de um título financeiro.
    Exige permissão: vendas:write
    """
    form_data = await request.form()
    dados = dict(form_data)
    usuario_id = str(user.get("id"))
    tenant_id = _get_tenant_id(request, user)

    db = SessionLocal()
    try:
        service = VendasService(db, tenant_id=tenant_id)
        service.baixar_titulo(titulo_id, dados, usuario_id=usuario_id)
        db.commit()

        return RedirectResponse(
            url=f"/web/vendas/{venda_id}",
            status_code=303
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao baixar título: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@router.get("/{venda_id}/nf")
async def gerar_nota_fiscal(
    request: Request,
    venda_id: str,
    user: dict = Depends(require_permission_web("vendas:faturar"))
):
    """
    Gera nota fiscal da venda.
    Exige permissão: vendas:faturar
    """
    tenant_id = _get_tenant_id(request, user)
    db = SessionLocal()
    try:
        service = VendasService(db, tenant_id=tenant_id)
        nf_bytes = service.gerar_nota_fiscal(venda_id)

        return StreamingResponse(
            io.BytesIO(nf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=nf_venda_{venda_id[:8]}.pdf"
            }
        )
    finally:
        db.close()
