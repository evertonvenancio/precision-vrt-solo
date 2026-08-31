"""
Precision VRT Solo - Serviço do Módulo Usuários
Toda consulta ao banco e regra de negócio centralizada aqui.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any

from core.seguranca.permissions import get_permissoes


class UsuariosService:
    """
    Serviço central do módulo Usuários.
    Responsável por toda consulta ao banco e regra de negócio.
    """

    def __init__(self, db: Session, user_data: dict = None):
        self.db = db
        self.user_data = user_data or {}

    def buscar_permissoes(self) -> dict:
        """Busca as permissões do usuário no banco."""
        return get_permissoes(self.db, self.user_data)

    def listar_usuarios(self) -> List[Dict[str, Any]]:
        """Lista todos os usuários ativos do banco."""
        try:
            result = self.db.execute(text("""
                SELECT id, login, ativo, criado_em
                FROM usuarios
                WHERE ativo = 1
                ORDER BY login ASC
            """))

            usuarios = []
            for row in result.fetchall():
                usuarios.append({
                    "id": row[0],
                    "login": row[1],
                    "nome": row[1],
                    "email": None,
                    "perfil": "admin" if row[1] == "admin" else "usuario",
                    "ativo": row[2],
                    "criado_em": str(row[3]) if row[3] else None
                })
            return usuarios
        except Exception as e:
            print(f"Erro ao listar usuários: {e}")
            return []