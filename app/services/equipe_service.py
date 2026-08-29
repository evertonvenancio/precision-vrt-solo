"""
Precision VRT Solo - Serviço do Módulo Equipe
Toda consulta ao banco e regra de negócio centralizada aqui.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from core.seguranca.permissions import get_permissoes


class EquipeService:
    """
    Serviço central do módulo Equipe.
    Responsável por toda consulta ao banco e regra de negócio.
    """

    def __init__(self, db: Session):
        self.db = db

    def buscar_permissoes(self) -> dict:
        """Busca as permissões do usuário no banco."""
        return get_permissoes(self.db)

    def listar_funcionarios(self):
        """Lista funcionários da tabela funcionarios."""
        try:
            result = self.db.execute(text("SELECT id, nome_completo, cpf, cargo, salario_base, comissao_percentual, ativo FROM funcionarios WHERE ativo = 1 ORDER BY nome_completo ASC"))
            funcionarios = []
            for row in result.fetchall():
                funcionarios.append({
                    "id": row[0],
                    "nome_completo": row[1],
                    "cpf": row[2],
                    "cargo": row[3],
                    "salario_base": float(row[4]) if row[4] else 0.0,
                    "comissao_percentual": float(row[5]) if row[5] else 0.0,
                    "ativo": row[6]
                })
            return funcionarios
        except Exception as e:
            print(f"Erro ao listar funcionários: {e}")
            return []

    def get_contexto_novo_funcionario(self):
        return {"cargos": ["Agrônomo", "Consultor", "Gerente Técnico", "Assistente de Campo", "Financeiro"]}

    def get_pagina_permissoes(self):
        return {"status": "ok"}

