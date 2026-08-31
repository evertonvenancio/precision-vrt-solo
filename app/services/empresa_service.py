"""
Precision VRT Solo - Serviço do Módulo Empresa
Toda consulta ao banco e regra de negócio centralizada aqui.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any

from core.seguranca.permissions import get_permissoes


class EmpresaService:
    """
    Serviço central do módulo Empresa.
    Responsável por toda consulta ao banco e regra de negócio.
    Permite gerenciar múltiplas empresas (CNPJs) vinculadas a um cliente.
    """

    def __init__(self, db: Session, user_data: dict = None):
        self.db = db
        self.user_data = user_data or {}

    def buscar_permissoes(self) -> dict:
        """Busca as permissões do usuário no banco."""
        return get_permissoes(self.db, self.user_data)

    def listar_por_cliente(self, cliente_id: str) -> List[Dict[str, Any]]:
        """Lista todas as empresas vinculadas a um cliente."""
        try:
            result = self.db.execute(text("""
                SELECT id, tenant_id, cliente_id, cnpj, nome_fantasia, razao_social,
                       criado_em, atualizado_em
                FROM empresas
                WHERE cliente_id = :cliente_id
                ORDER BY nome_fantasia ASC
            """), {"cliente_id": cliente_id})

            empresas = []
            for row in result.fetchall():
                empresas.append({
                    "id": row[0],
                    "tenant_id": row[1],
                    "cliente_id": row[2],
                    "cnpj": row[3],
                    "nome_fantasia": row[4],
                    "razao_social": row[5],
                    "criado_em": str(row[6]) if row[6] else None,
                    "atualizado_em": str(row[7]) if row[7] else None
                })
            return empresas
        except Exception as e:
            print(f"Erro ao listar empresas do cliente: {e}")
            return []

    def obter(self, empresa_id: str) -> Optional[Dict[str, Any]]:
        """Obtém uma empresa específica pelo ID."""
        try:
            result = self.db.execute(text("""
                SELECT id, tenant_id, cliente_id, cnpj, nome_fantasia, razao_social,
                       criado_em, atualizado_em
                FROM empresas
                WHERE id = :id
            """), {"id": empresa_id})

            row = result.fetchone()
            if row:
                return {
                    "id": row[0],
                    "tenant_id": row[1],
                    "cliente_id": row[2],
                    "cnpj": row[3],
                    "nome_fantasia": row[4],
                    "razao_social": row[5],
                    "criado_em": str(row[6]) if row[6] else None,
                    "atualizado_em": str(row[7]) if row[7] else None
                }
            return None
        except Exception as e:
            print(f"Erro ao obter empresa: {e}")
            return None

    def criar(self, cliente_id: str, cnpj: str, nome_fantasia: str, razao_social: str) -> Dict[str, Any]:
        """Cria uma nova empresa vinculada a um cliente."""
        try:
            from uuid import uuid4
            from datetime import datetime

            empresa_id = str(uuid4())
            tenant_id = self.user_data.get('tenant_id', 'default')

            self.db.execute(text("""
                INSERT INTO empresas (id, tenant_id, cliente_id, cnpj, nome_fantasia, razao_social, criado_em, atualizado_em)
                VALUES (:id, :tenant_id, :cliente_id, :cnpj, :nome_fantasia, :razao_social, :criado_em, :atualizado_em)
            """), {
                "id": empresa_id,
                "tenant_id": tenant_id,
                "cliente_id": cliente_id,
                "cnpj": cnpj,
                "nome_fantasia": nome_fantasia,
                "razao_social": razao_social,
                "criado_em": datetime.now(),
                "atualizado_em": datetime.now()
            })

            self.db.commit()
            return self.obter(empresa_id)
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao criar empresa: {e}")
            return {}

    def atualizar(self, empresa_id: str, cnpj: str, nome_fantasia: str, razao_social: str) -> Optional[Dict[str, Any]]:
        """Atualiza os dados de uma empresa existente."""
        try:
            from datetime import datetime

            self.db.execute(text("""
                UPDATE empresas
                SET cnpj = :cnpj, nome_fantasia = :nome_fantasia, razao_social = :razao_social,
                    atualizado_em = :atualizado_em
                WHERE id = :id
            """), {
                "cnpj": cnpj,
                "nome_fantasia": nome_fantasia,
                "razao_social": razao_social,
                "atualizado_em": datetime.now(),
                "id": empresa_id
            })

            self.db.commit()
            return self.obter(empresa_id)
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao atualizar empresa: {e}")
            return None

    def remover(self, empresa_id: str) -> bool:
        """Remove uma empresa pelo ID."""
        try:
            self.db.execute(text("DELETE FROM empresas WHERE id = :id"), {"id": empresa_id})
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao remover empresa: {e}")
            return False
