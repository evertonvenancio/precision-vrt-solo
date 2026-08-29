"""
Precision VRT Solo - Serviço do Módulo Permissões
Toda consulta ao banco e regra de negócio centralizada aqui.
"""
from sqlalchemy.orm import Session


class PermissoesService:
    """
    Serviço central do módulo Permissões.
    Responsável por toda consulta ao banco e regra de negócio.
    """

    def __init__(self, db: Session):
        self.db = db
