"""
Precision VRT Solo - Permissões
Função utilitária para carregamento de permissões de usuário.
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import text

from .seguranca import carregar_permissoes_usuario


def get_permissoes(db: Session, user_data: Dict[str, Any] = None) -> dict:
    """
    Busca as permissões do usuário.
    
    Args:
        db: Sessão do banco
        user_data: Dados do usuário autenticado (opcional)
        
    Returns:
        Dicionário com permissões do usuário
    """
    if user_data and user_data.get('user_id'):
        # Usar usuário autenticado
        return carregar_permissoes_usuario(user_data['user_id'])
    else:
        # Fallback para hardcoded (temporário)
        result = db.execute(text('SELECT id FROM usuarios WHERE login = \"admin\" LIMIT 1'))
        user = result.fetchone()
        if user:
            return carregar_permissoes_usuario(user[0])
        return {}
