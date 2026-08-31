"""
Precision VRT Solo - Rotas do Módulo Conhecimento
(Culturas, Metodologias, Bibliografia)

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.conhecimento_service import ConhecimentoService

router = APIRouter()
from app.web.auth_dependencies import require_permission_web  # autenticação via cookie
from app.template_config import templates  # compartilhado - globals de RBAC



# === Rotas canônicas (/base-tecnica/*) ===

@router.get("/base-tecnica/culturas")
async def culturas_base_tecnica(request: Request, db: Session = Depends(get_db)):
    service = ConhecimentoService(db)
    permissoes = service.buscar_permissoes()
    artigos = service.listar(tenant_id="default", categoria=None)
    return templates.TemplateResponse(
        request=request,
        name="base_tecnica.html",
        context={"titulo_pagina": "Culturas e Exportação de Nutrientes", "artigos": artigos, "permissoes": permissoes}
    )


@router.get("/base-tecnica/metodologias")
async def metodologias_base_tecnica(request: Request, db: Session = Depends(get_db)):
    service = ConhecimentoService(db)
    permissoes = service.buscar_permissoes()
    artigos = service.listar(tenant_id="default", categoria=None)
    return templates.TemplateResponse(
        request=request,
        name="base_tecnica.html",
        context={"titulo_pagina": "Metodologias de Cálculo", "artigos": artigos, "permissoes": permissoes}
    )


@router.get("/base-tecnica/bibliografia")
async def bibliografia_base_tecnica(request: Request, db: Session = Depends(get_db)):
    service = ConhecimentoService(db)
    permissoes = service.buscar_permissoes()
    artigos = service.listar(tenant_id="default", categoria=None)
    return templates.TemplateResponse(
        request=request,
        name="base_tecnica.html",
        context={"titulo_pagina": "Bibliografia e Referências Legais", "artigos": artigos, "permissoes": permissoes}
    )


# === Rotas legadas compatíveis com sidebar (/culturas, /metodologias, /bibliografia) ===

@router.get("/culturas")
async def culturas_page(request: Request, db: Session = Depends(get_db)):
    return RedirectResponse(url="/web/conhecimento/base-tecnica/culturas", status_code=302)


@router.get("/metodologias")
async def metodologias_page(request: Request, db: Session = Depends(get_db)):
    return RedirectResponse(url="/web/conhecimento/base-tecnica/metodologias", status_code=302)


@router.get("/bibliografia")
async def bibliografia_page(request: Request, db: Session = Depends(get_db)):
    return RedirectResponse(url="/web/conhecimento/base-tecnica/bibliografia", status_code=302)
