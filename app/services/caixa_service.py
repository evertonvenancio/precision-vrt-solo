"""
Precision VRT Solo - Serviço do Módulo Caixa
Toda consulta ao banco e regra de negócio centralizada aqui.
"""
from sqlalchemy.orm import Session

from core.seguranca.permissions import get_permissoes

# Importar função original do service existente
try:
    from app.services.caixa_service_original import get_contexto_caixa as _get_contexto_caixa_orig
except ImportError:
    def _get_contexto_caixa_orig(): return {}


class CaixaService:
    """
    Serviço central do módulo Caixa.
    Responsável por toda consulta ao banco e regra de negócio.
    """

    def __init__(self, db: Session):
        self.db = db

    def buscar_permissoes(self) -> dict:
        """Busca as permissões do usuário no banco."""
        return get_permissoes(self.db)

    def get_contexto(self):
        return _get_contexto_caixa_orig()
