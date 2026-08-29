"""
Precision VRT Solo - Serviço do Módulo Cruzamento
Toda consulta ao banco e regra de negócio centralizada aqui.
"""
from sqlalchemy.orm import Session

from core.seguranca.permissions import get_permissoes


class CruzamentoService:
    """
    Serviço central do módulo Cruzamento.
    Responsável por toda consulta ao banco e regra de negócio.
    """

    def __init__(self, db: Session):
        self.db = db

    def buscar_permissoes(self) -> dict:
        """Busca as permissões do usuário no banco."""
        return get_permissoes(self.db)
