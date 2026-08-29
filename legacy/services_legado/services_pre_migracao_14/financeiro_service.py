"""
Precision VRT Solo - Serviço do Módulo Financeiro
Toda consulta ao banco e regra de negócio centralizada aqui.
Implementação REAL usando estruturas comprovadas no banco.
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from core.seguranca.permissions import get_permissoes

# Importar implementação real
from services.financeiro_service_real import FinanceiroService as FinanceiroServiceReal


class FinanceiroService:
    """
    Serviço central do módulo Financeiro.
    Responsável por toda consulta ao banco e regra de negócio.
    Implementação REAL sem mocks.
    """

    def __init__(self, db: Session, user_data: dict = None):
        self.db = db
        self.user_data = user_data or {}

    def buscar_permissoes(self) -> dict:
        """Busca as permissões do usuário no banco."""
        return get_permissoes(self.db, self.user_data)

    def listar_orcamentos(self):
        """Lista todos os orçamentos existentes no banco."""
        service_real = FinanceiroServiceReal(self.db, self.user_data)
        return service_real.listar_orcamentos()

    def listar_clientes_ativos(self):
        """Lista todos os clientes ativos no banco."""
        service_real = FinanceiroServiceReal(self.db, self.user_data)
        return service_real.listar_clientes_ativos()

    def salvar_orcamento(self, cliente_id: str, dados_orcamento: Dict[str, Any]):
        """Salva um novo orçamento no banco."""
        service_real = FinanceiroServiceReal(self.db, self.user_data)
        return service_real.salvar_orcamento(cliente_id, dados_orcamento)
