"""
Precision VRT Solo - Serviço do Módulo Orçamentos
Toda consulta ao banco e regra de negócio centralizada aqui.
"""
from sqlalchemy.orm import Session

from core.seguranca.permissions import get_permissoes

# Importar funções originais do service existente
try:
    from services.orcamentos_service_original import (
        listar_clientes_ativos as _listar_clientes_ativos_orig,
        salvar_orcamento_stub as _salvar_orcamento_stub_orig,
    )
except ImportError:
    def _listar_clientes_ativos_orig(db): return []
    def _salvar_orcamento_stub_orig(): return None


class OrcamentosService:
    """
    Serviço central do módulo Orçamentos.
    Responsável por toda consulta ao banco e regra de negócio.
    """

    def __init__(self, db: Session):
        self.db = db

    def buscar_permissoes(self) -> dict:
        """Busca as permissões do usuário no banco."""
        return get_permissoes(self.db)

    def listar_clientes_ativos(self):
        return _listar_clientes_ativos_orig(self.db)

    def salvar_orcamento_stub(self):
        return _salvar_orcamento_stub_orig()
