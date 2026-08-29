"""Precision VRT Solo - Stubs de Rotas

Este arquivo contém stubs temporários para todas as rotas do sistema.
Servem como placeholders enquanto os módulos estão em desenvolvimento.
"""

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def obter_nome_rota(caminho: str) -> str:
    """Extrai nome da rota para título."""
    # Remover /web/ e substituir underscores por espaços
    nome = caminho.replace("/web/", "").replace("_", " ")
    return nome.title()


# === ROTAS TEMPORÁRIAS ===

# === ROTAS TEMPORÁRIAS ===
@router.get("/web/orcamentos")
async def orcamentos_page(request: Request):
    """Página Orcamentos - Em desenvolvimento."""
    nome_pagina = "Orcamentos"
    
    # Verificar se template existe
    template_path = "templates/orcamentos.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/vendas")
async def vendas_page(request: Request):
    """Página Vendas - Em desenvolvimento."""
    nome_pagina = "Vendas"
    
    # Verificar se template existe
    template_path = "templates/vendas.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/agenda")
async def agenda_page(request: Request):
    """Página Agenda - Em desenvolvimento."""
    nome_pagina = "Agenda"
    
    # Verificar se template existe
    template_path = "templates/agenda.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/relatorios")
async def relatorios_page(request: Request):
    """Página Relatorios - Em desenvolvimento."""
    nome_pagina = "Relatorios"
    
    # Verificar se template existe
    template_path = "templates/relatorios.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/prescricao")
async def prescricao_page(request: Request):
    """Página Prescricao - Em desenvolvimento."""
    nome_pagina = "Prescricao"
    
    # Verificar se template existe
    template_path = "templates/prescricao.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/compactacao")
async def compactacao_page(request: Request):
    """Página Compactacao - Em desenvolvimento."""
    nome_pagina = "Compactacao"
    
    # Verificar se template existe
    template_path = "templates/compactacao.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/nematoides")
async def nematoides_page(request: Request):
    """Página Nematoides - Em desenvolvimento."""
    nome_pagina = "Nematoides"
    
    # Verificar se template existe
    template_path = "templates/nematoides.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/fertirrigacao")
async def fertirrigacao_page(request: Request):
    """Página Fertirrigacao - Em desenvolvimento."""
    nome_pagina = "Fertirrigacao"
    
    # Verificar se template existe
    template_path = "templates/fertirrigacao.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/sensoriamento")
async def sensoriamento_page(request: Request):
    """Página Sensoriamento - Em desenvolvimento."""
    nome_pagina = "Sensoriamento"
    
    # Verificar se template existe
    template_path = "templates/sensoriamento.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/monitoramento")
async def monitoramento_page(request: Request):
    """Página Monitoramento - Em desenvolvimento."""
    nome_pagina = "Monitoramento"
    
    # Verificar se template existe
    template_path = "templates/monitoramento.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/culturas")
async def culturas_page(request: Request):
    """Página Culturas - Em desenvolvimento."""
    nome_pagina = "Culturas"
    
    # Verificar se template existe
    template_path = "templates/culturas.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/metodologias")
async def metodologias_page(request: Request):
    """Página Metodologias - Em desenvolvimento."""
    nome_pagina = "Metodologias"
    
    # Verificar se template existe
    template_path = "templates/metodologias.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/bibliografia")
async def bibliografia_page(request: Request):
    """Página Bibliografia - Em desenvolvimento."""
    nome_pagina = "Bibliografia"
    
    # Verificar se template existe
    template_path = "templates/bibliografia.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/financeiro")
async def financeiro_page(request: Request):
    """Página Financeiro - Em desenvolvimento."""
    nome_pagina = "Financeiro"
    
    # Verificar se template existe
    template_path = "templates/financeiro.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/patrimonio")
async def patrimonio_page(request: Request):
    """Página Patrimonio - Em desenvolvimento."""
    nome_pagina = "Patrimonio"
    
    # Verificar se template existe
    template_path = "templates/patrimonio.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/clientes")
async def clientes_page(request: Request):
    """Página Clientes - Em desenvolvimento."""
    nome_pagina = "Clientes"
    
    # Verificar se template existe
    template_path = "templates/clientes.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/usuarios")
async def usuarios_page(request: Request):
    """Página Usuarios - Em desenvolvimento."""
    nome_pagina = "Usuarios"
    
    # Verificar se template existe
    template_path = "templates/usuarios.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/equipes")
async def equipes_page(request: Request):
    """Página Equipes - Em desenvolvimento."""
    nome_pagina = "Equipes"
    
    # Verificar se template existe
    template_path = "templates/equipes.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/empresas")
async def empresas_page(request: Request):
    """Página Empresas - Em desenvolvimento."""
    nome_pagina = "Empresas"
    
    # Verificar se template existe
    template_path = "templates/empresas.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/produtos")
async def produtos_page(request: Request):
    """Página Produtos - Em desenvolvimento."""
    nome_pagina = "Produtos"
    
    # Verificar se template existe
    template_path = "templates/produtos.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/fornecedores")
async def fornecedores_page(request: Request):
    """Página Fornecedores - Em desenvolvimento."""
    nome_pagina = "Fornecedores"
    
    # Verificar se template existe
    template_path = "templates/fornecedores.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/configuracoes")
async def configuracoes_page(request: Request):
    """Página Configuracoes - Em desenvolvimento."""
    nome_pagina = "Configuracoes"
    
    # Verificar se template existe
    template_path = "templates/configuracoes.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


@router.get("/web/perfil")
async def perfil_page(request: Request):
    """Página Perfil - Em desenvolvimento."""
    nome_pagina = "Perfil"
    
    # Verificar se template existe
    template_path = "templates/perfil.html"
    
    try:
        # Tentar carregar template específico
        return templates.TemplateResponse(request=request, name=template_path, context={
            "request": request,
            "titulo": nome_pagina
        })
    except Exception:
        # Se não existir, usar em_construcao.html
        return templates.TemplateResponse(request=request, name="em_construcao.html", context={
            "request": request,
            "titulo": nome_pagina
        })


