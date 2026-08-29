"""
Precision VRT Solo - Serviço do Módulo Equipe
Toda consulta ao banco e regra de negócio centralizada aqui.
"""
from sqlalchemy.orm import Session

from core.seguranca.permissions import get_permissoes

# Importar funções originais do service existente
try:
    from app.services.equipe_service_original import (
        listar_funcionarios as _listar_funcionarios_orig,
        get_contexto_novo_funcionario as _get_contexto_novo_funcionario_orig,
        get_pagina_permissoes as _get_pagina_permissoes_orig,
    )
except ImportError:
    def _listar_funcionarios_orig(db): return []
    def _get_contexto_novo_funcionario_orig(): return {}
    def _get_pagina_permissoes_orig(): return {}


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
        return _listar_funcionarios_orig(self.db)

    def get_contexto_novo_funcionario(self):
        return _get_contexto_novo_funcionario_orig()

    def get_pagina_permissoes(self):
        return _get_pagina_permissoes_orig()
