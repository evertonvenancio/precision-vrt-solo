"""
Precision VRT Solo - Sistema de Autorização e Dependências RBAC

Responsável por:
- Verificação de permissões granulares baseada em roles/permissões do usuário
- Injeção de permissões no contexto da requisição
- Helper para templates verificarem permissões dinamicamente (sidebar, botões)
"""

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional, Set
from functools import wraps


security = HTTPBearer(auto_error=False)


# Mapeamento de permissões por módulo/ação
# Usado para validação e para geração dinâmica do menu lateral
PERMISSION_MAP = {
    # Módulo: {ação: permissão_necessária}
    "dashboard": {
        "read": "dashboard:read",
        "write": "dashboard:write",
        "customize": "dashboard:customize",
    },
    "clientes": {
        "read": "clientes:read",
        "write": "clientes:write",
        "delete": "clientes:delete",
        "export": "clientes:export",
    },
    "orcamentos": {
        "read": "orcamentos:read",
        "write": "orcamentos:write",
        "delete": "orcamentos:delete",
        "aprovar": "orcamentos:aprovar",
        "export": "orcamentos:export",
    },
    "vendas": {
        "read": "vendas:read",
        "write": "vendas:write",
        "delete": "vendas:delete",
        "faturar": "vendas:faturar",
    },
    "agenda": {
        "read": "agenda:read",
        "write": "agenda:write",
        "delete": "agenda:delete",
    },
    "relatorios": {
        "read": "relatorios:read",
        "export": "relatorios:export",
        "financeiro": "relatorios:financeiro",
        "comissoes": "relatorios:comissoes",
    },
    "prescricao": {
        "read": "prescricao:read",
        "write": "prescricao:write",
        "delete": "prescricao:delete",
        "export": "prescricao:export",
        "aprovar": "prescricao:aprovar",
    },
    "compactacao": {
        "read": "compactacao:read",
        "write": "compactacao:write",
        "delete": "compactacao:delete",
    },
    "nematoides": {
        "read": "nematoides:read",
        "write": "nematoides:write",
        "delete": "nematoides:delete",
    },
    "fertirrigacao": {
        "read": "fertirrigacao:read",
        "write": "fertirrigacao:write",
        "delete": "fertirrigacao:delete",
    },
    "sensoriamento": {
        "read": "sensoriamento:read",
        "write": "sensoriamento:write",
        "delete": "sensoriamento:delete",
    },
    "monitoramento": {
        "read": "monitoramento:read",
        "write": "monitoramento:write",
        "delete": "monitoramento:delete",
    },
    "culturas": {
        "read": "culturas:read",
        "write": "culturas:write",
        "delete": "culturas:delete",
    },
    "metodologias": {
        "read": "metodologias:read",
        "write": "metodologias:write",
        "delete": "metodologias:delete",
        "versionar": "metodologias:versionar",
    },
    "bibliografia": {
        "read": "bibliografia:read",
        "write": "bibliografia:write",
        "delete": "bibliografia:delete",
    },
    "financeiro": {
        "read": "financeiro:read",
        "write": "financeiro:write",
        "delete": "financeiro:delete",
        "aprovar_pagamento": "financeiro:aprovar_pagamento",
        "concililar": "financeiro:concililar",
    },
    "patrimonio": {
        "read": "patrimonio:read",
        "write": "patrimonio:write",
        "delete": "patrimonio:delete",
    },
    "cadastros": {
        "read": "cadastros:read",
        "write": "cadastros:write",
        "delete": "cadastros:delete",
    },
    "usuarios": {
        "read": "usuarios:read",
        "write": "usuarios:write",
        "delete": "usuarios:delete",
        "permissoes": "usuarios:permissoes",
    },
    "equipes": {
        "read": "equipes:read",
        "write": "equipes:write",
        "delete": "equipes:delete",
    },
    "empresas": {
        "read": "empresas:read",
        "write": "empresas:write",
        "delete": "empresas:delete",
    },
    "produtos": {
        "read": "produtos:read",
        "write": "produtos:write",
        "delete": "produtos:delete",
    },
    "fornecedores": {
        "read": "fornecedores:read",
        "write": "fornecedores:write",
        "delete": "fornecedores:delete",
    },
    "configuracoes": {
        "read": "configuracoes:read",
        "write": "configuracoes:write",
    },
    "auditoria": {
        "read": "auditoria:read",
        "export": "auditoria:export",
    },
    "upload": {
        "read": "upload:read",
        "write": "upload:write",
        "delete": "upload:delete",
    },
}


# Estrutura do menu lateral para renderização dinâmica baseada em permissões
SIDEBAR_MENU_STRUCTURE = [
    {
        "group": "NAVEGAÇÃO",
        "items": [
            {"key": "dashboard", "label": "Dashboard", "icon": "dashboard", "perm": "dashboard:read", "url": "/web/dashboard"},
        ]
    },
    {
        "group": "RELACIONAMENTO COMERCIAL",
        "items": [
            {"key": "clientes", "label": "Clientes", "icon": "users", "perm": "clientes:read", "url": "/web/clientes"},
            {"key": "orcamentos", "label": "Orçamentos", "icon": "file-text", "perm": "orcamentos:read", "url": "/web/orcamentos"},
            {"key": "vendas", "label": "Vendas", "icon": "shopping-cart", "perm": "vendas:read", "url": "/web/vendas"},
            {"key": "agenda", "label": "Agenda", "icon": "calendar", "perm": "agenda:read", "url": "/web/agenda"},
            {"key": "relatorios", "label": "Relatórios", "icon": "bar-chart", "perm": "relatorios:read", "url": "/web/relatorios"},
        ]
    },
    {
        "group": "OPERAÇÕES AGRONÔMICAS",
        "items": [
            {"key": "prescricao", "label": "Prescrição VRT", "icon": "map", "perm": "prescricao:read", "url": "/web/prescricao"},
            {"key": "compactacao", "label": "Compactação", "icon": "layers", "perm": "compactacao:read", "url": "/web/compactacao"},
            {"key": "nematoides", "label": "Nematoides", "icon": "bug", "perm": "nematoides:read", "url": "/web/nematoides"},
            {"key": "fertirrigacao", "label": "Fertirrigação", "icon": "droplet", "perm": "fertirrigacao:read", "url": "/web/fertirrigacao"},
            {"key": "sensoriamento", "label": "Sensoriamento", "icon": "satellite", "perm": "sensoriamento:read", "url": "/web/sensoriamento"},
            {"key": "monitoramento", "label": "Monitoramento", "icon": "activity", "perm": "monitoramento:read", "url": "/web/monitoramento"},
        ]
    },
    {
        "group": "CONHECIMENTO TÉCNICO",
        "items": [
            {"key": "culturas", "label": "Culturas", "icon": "leaf", "perm": "culturas:read", "url": "/web/conhecimento/base-tecnica/culturas"},
            {"key": "metodologias", "label": "Metodologias", "icon": "book-open", "perm": "metodologias:read", "url": "/web/conhecimento/base-tecnica/metodologias"},
            {"key": "bibliografia", "label": "Bibliografia", "icon": "book", "perm": "bibliografia:read", "url": "/web/conhecimento/base-tecnica/bibliografia"},
        ]
    },
    {
        "group": "ADMINISTRAÇÃO & GESTÃO",
        "items": [
            {"key": "financeiro", "label": "Financeiro", "icon": "dollar-sign", "perm": "financeiro:read", "url": "/web/financeiro"},
            {"key": "patrimonio", "label": "Patrimônio", "icon": "truck", "perm": "patrimonio:read", "url": "/web/patrimonio"},
            {"key": "cadastros", "label": "Cadastros", "icon": "database", "perm": "cadastros:read", "url": "/web/cadastros"},
            {"key": "usuarios", "label": "Usuários", "icon": "user", "perm": "usuarios:read", "url": "/web/usuarios"},
            {"key": "equipes", "label": "Equipes", "icon": "users", "perm": "equipes:read", "url": "/web/equipes"},
            {"key": "empresas", "label": "Empresas", "icon": "building", "perm": "empresas:read", "url": "/web/empresas"},
            {"key": "produtos", "label": "Produtos", "icon": "package", "perm": "produtos:read", "url": "/web/produtos"},
            {"key": "fornecedores", "label": "Fornecedores", "icon": "truck", "perm": "fornecedores:read", "url": "/web/fornecedores"},
            {"key": "configuracoes", "label": "Configurações", "icon": "settings", "perm": "configuracoes:read", "url": "/web/configuracoes"},
            {"key": "auditoria", "label": "Auditoria", "icon": "shield", "perm": "auditoria:read", "url": "/web/auditoria"},
        ]
    },
]


def get_user_permissions(request: Request) -> Set[str]:
    """
    Extrai permissões do usuário autenticado.
    Retorna set de strings de permissão (ex: {"clientes:read", "clientes:write"}).
    """
    # Tentar obter do state (setado por auth dependency)
    if hasattr(request.state, "user_permissions"):
        return set(request.state.user_permissions)

    # Fallback: extrair do JWT no cookie
    try:
        from app.web.auth import auth_service
        if auth_service:
            access_token = request.cookies.get("access_token")
            if access_token:
                payload = auth_service.verify_token(access_token)
                if payload and "permissions" in payload:
                    return set(payload["permissions"])
    except Exception:
        pass

    return set()


def has_permission(permission: str, user_permissions: Set[str]) -> bool:
    """
    Verifica se usuário tem uma permissão específica.
    Permissão 'admin' ou 'total' concede acesso a tudo.
    """
    if "admin" in user_permissions or "total" in user_permissions or "*" in user_permissions:
        return True
    return permission in user_permissions


def require_permission(permission: str):
    """
    Dependency que exige uma permissão específica.
    Levanta HTTPException 403 se o usuário não tiver a permissão.
    """
    def permission_checker(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        # Se não há credenciais, tentar cookie
        if not credentials:
            from app.web.auth import get_token_from_cookie
            try:
                token = get_token_from_cookie(request)
                # Criar credentials fake para compatibilidade
                class FakeCredentials:
                    credentials = token
                credentials = FakeCredentials()
            except HTTPException:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Não autenticado"
                )

        # Obter usuário atual
        from app.web.auth import get_current_user
        try:
            user = get_current_user(credentials)
            request.state.user = user
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado"
            )

        # Verificar permissão
        user_perms = get_user_permissions(request)
        request.state.user_permissions = list(user_perms)

        if not has_permission(permission, user_perms):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão necessária: {permission}"
            )

        return user

    return permission_checker


def get_filtered_menu(user_permissions: Set[str]) -> List[Dict]:
    """
    Filtra a estrutura do menu lateral baseado nas permissões do usuário.
    Retorna apenas grupos/itens que o usuário tem permissão para ver.
    """
    filtered = []

    for group in SIDEBAR_MENU_STRUCTURE:
        visible_items = []
        for item in group["items"]:
            if has_permission(item["perm"], user_permissions):
                visible_items.append(item)

        if visible_items:
            filtered.append({
                "group": group["group"],
                "items": visible_items
            })

    return filtered


# Helper para uso em templates Jinja2
def template_has_permission(permission: str, user_permissions: List[str]) -> bool:
    """Helper para uso direto em templates: {% if has_permission('clientes:write', permissoes) %}"""
    return has_permission(permission, set(user_permissions))


def template_filter_menu(menu_structure: List[Dict], user_permissions: List[str]) -> List[Dict]:
    """Helper para filtrar menu em templates."""
    return get_filtered_menu(set(user_permissions))


# Permissões administrativas especiais
ADMIN_PERMISSIONS = {"admin", "total", "*"}


def is_admin(user_permissions: Set[str]) -> bool:
    """Verifica se usuário é administrador (tem acesso total)."""
    return bool(user_permissions & ADMIN_PERMISSIONS)


def get_permissions_for_module(module: str, user_permissions: Set[str]) -> Dict[str, bool]:
    """
    Retorna dicionário com todas as ações de um módulo e se o usuário tem permissão.
    Ex: get_permissions_for_module("clientes", perms) -> {"read": True, "write": False, ...}
    """
    if module not in PERMISSION_MAP:
        return {}

    result = {}
    for action, perm in PERMISSION_MAP[module].items():
        result[action] = has_permission(perm, user_permissions)
    return result