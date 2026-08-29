"""
Precision VRT Solo - Rotas do Módulo Configuracoes

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.configuracoes_service import ConfiguracoesService

router = APIRouter()
from app.template_config import templates  # compartilhado - globals de RBAC



@router.get("/configuracoes")
async def configuracoes_page(request: Request, db: Session = Depends(get_db)):
    service = ConfiguracoesService(db)
    permissoes = service.buscar_permissoes()
    configuracoes = service.obter_configuracoes()
    return templates.TemplateResponse(
        request=request,
        name="configuracoes.html",
        context={
            "request": request,
            "permissoes": permissoes,
            "configuracoes": configuracoes,
        }
    )


@router.post("/configuracoes")
async def salvar_configuracoes(
    request: Request,
    db: Session = Depends(get_db),
    nome_empresa: str = Form(""),
    slogan: str = Form(""),
    nome_fantasia: str = Form(""),
    cnpj: str = Form(""),
    responsavel_tecnico: str = Form(""),
    crea: str = Form(""),
    email: str = Form(""),
    telefone: str = Form(""),
    nome_software: str = Form(""),
    versao: str = Form(""),
    idioma: str = Form(""),
    tema: str = Form(""),
    cidade_padrao: str = Form(""),
    estado_padrao: str = Form(""),
    auditoria_ativa: str = Form("false"),
):
    """Salva as configurações do sistema (atualização do registro único)."""
    service = ConfiguracoesService(db)
    configuracoes = service.obter_configuracoes()

    # Atualizar campos
    configuracoes.nome_empresa = nome_empresa or None
    configuracoes.slogan = slogan or None
    configuracoes.nome_fantasia = nome_fantasia or None
    configuracoes.cnpj = cnpj or None
    configuracoes.responsavel_tecnico = responsavel_tecnico or None
    configuracoes.crea = crea or None
    configuracoes.email = email or None
    configuracoes.telefone = telefone or None
    configuracoes.nome_software = nome_software or None
    configuracoes.versao = versao or None
    configuracoes.idioma = idioma or None
    configuracoes.tema = tema or None
    configuracoes.cidade_padrao = cidade_padrao or None
    configuracoes.estado_padrao = estado_padrao or None
    configuracoes.auditoria_ativa = auditoria_ativa.lower() in ("true", "on", "1", "sim")

    service.salvar(configuracoes)

    return RedirectResponse(url="/configuracoes", status_code=303)


@router.get("/api/configuracoes/clima")
async def api_configuracoes_clima(request: Request):
    """
    Endpoint para obter configurações de clima.
    """
    # Buscar cidade padrão do banco (tabela configuracoes ou similar)
    from db.database import SessionLocal
    db = SessionLocal()

    try:
        from sqlalchemy import text
        # Buscar configuração de cidade
        result = db.execute(
            text("SELECT valor FROM configuracoes WHERE chave = 'cidade_padrao' LIMIT 1")
        )
        cidade_config = result.fetchone()
        cidade = cidade_config[0] if cidade_config else "Itapetininga/SP"

        # Se houver serviço de clima funcional no projeto, usá-lo
        clima_data = None
        try:
            # Tentar usar serviço existente
            from app.services.dashboard_service import DashboardService
            service = DashboardService(db)
            clima_data = service._get_clima()
        except Exception:
            # Se não houver serviço, usar fallback
            pass

        # Se não encontrou clima via serviço, retorna null
        temperatura = None
        if clima_data and 'temp_min' in clima_data:
            temperatura = clima_data.get('temp_min')

        return {
            "cidade": cidade,
            "temperatura": temperatura
        }

    except Exception as e:
        print(f"Erro ao buscar configurações de clima: {e}")
        # Fallback caso erro
        return {
            "cidade": "Itapetininga/SP",
            "temperatura": None
        }
    finally:
        db.close()
