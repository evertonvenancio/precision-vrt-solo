"""
Precision VRT Solo - Autenticação JWT
Implementação compatível com o sistema de relatórios.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import jwt
import os
from core.seguranca.seguranca import carregar_permissoes_usuario


# Configuração JWT (compatível comAuthService existente)
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Definição de permissões (compatível com sistema existente)
class Permission:
    """Constantes de permissão para relatórios."""
    RELATORIOS_CLIENTES = "relatorios:clientes"
    RELATORIOS_FINANCEIRO = "relatorios:financeiro"
    RELATORIOS_OPERACIONAL = "relatorios:operacional"


def get_current_user_id() -> str:
    """
    Simula obtenção do ID do usuário autenticado.
    Em um sistema real, isso viria do token JWT.
    """
    # Simular usuário autenticado (compatível com AuthService)
    return "user_authenticated"


def get_current_user_nome() -> str:
    """
    Simula obtenção do nome do usuário autenticado.
    """
    return "Usuário Teste"


def require_permission(permission: str):
    """
    Verifica se o usuário autenticado tem a permissão necessária.
    
    Args:
        permission: Permissão requerida
        
    Raises:
        HTTPException: Se o usuário não tiver a permissão
    """
    from fastapi import HTTPException, status
    
    try:
        # Simular obtenção de permissões do usuário
        user_id = get_current_user_id()
        permissoes_usuario = carregar_permissoes_usuario(user_id)
        
        # Mapear permissões de relatórios para o formato existente
        permissao_mapping = {
            Permission.RELATORIOS_CLIENTES: "view_menu_clientes",
            Permission.RELATORIOS_FINANCEIRO: "view_menu_financeiro", 
            Permission.RELATORIOS_OPERACIONAL: "view_menu_recomendacao"
        }
        
        # Verificar permissão
        permissao_sistema = permissao_mapping.get(permission, permission)
        if not permissoes_usuario.get(permissao_sistema, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada"
            )
            
    except Exception as e:
        # Se falhar a verificação, negar acesso
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada"
        )


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verifica e decodifica um token JWT.
    
    Args:
        token: Token JWT para verificar
        
    Returns:
        Dados do usuário decodificados
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.JWTError:
        return {}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT de acesso.
    
    Args:
        data: Dados para incluir no token
        expires_delta: Tempo de expiração
        
    Returns:
        Token JWT
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt