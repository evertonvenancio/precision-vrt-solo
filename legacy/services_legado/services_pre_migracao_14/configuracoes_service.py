"""
Precision VRT Solo - Serviço do Módulo Configurações

Responsabilidade: consulta ao banco e persistência de configurações.

O banco usa schema key-value (id, tenant_id, chave, valor, metodologia_padrao_id, criado_em).
O service converte entre este formato e o objeto estruturado que o frontend espera.
Arquitetura local single-user — sem multi-tenant.
"""

from __future__ import annotations

import logging
import uuid

from sqlalchemy.orm import Session

from core.seguranca.permissions import get_permissoes
from models.config import ConfigSistema

logger = logging.getLogger(__name__)


# Campos estruturados que o frontend/template espera
CAMPOS_ESTRUTURADOS = [
    "nome_empresa",
    "slogan",
    "nome_fantasia",
    "cnpj",
    "responsavel_tecnico",
    "crea",
    "email",
    "telefone",
    "nome_software",
    "versao",
    "idioma",
    "tema",
    "cidade_padrao",
    "estado_padrao",
]


class _ConfigSistemaAdapter:
    """Adapter que expõe campos estruturados a partir de registros key-value.

    O frontend/template acessa atributos diretamente (ex: config.nome_empresa).
    Este adapter lê do banco key-value e expõe como atributos de objeto.
    """

    def __init__(self, db: Session, metodologia_padrao_id: str | None = None):
        self._db = db
        self._dados: dict[str, str] = {}
        self.id = str(uuid.uuid4())  # ID sintético para compatibilidade
        self.metodologia_padrao_id = metodologia_padrao_id or "IAC_Graos"
        self._carregar()

    def _carregar(self):
        """Lê todos os registros key-value do banco para o dicionário interno."""
        registros = self._db.query(ConfigSistema).all()
        for r in registros:
            if r.chave:
                self._dados[r.chave] = r.valor or ""
        # Sincroniza metodologia_padrao_id do primeiro registro se existir
        for r in registros:
            if r.metodologia_padrao_id:
                self.metodologia_padrao_id = r.metodologia_padrao_id
                break

    def __getattr__(self, name: str):
        """Permite acesso como config.nome_empresa, config.slogan, etc."""
        if name.startswith("_"):
            raise AttributeError(name)
        return self._dados.get(name)

    def __setattr__(self, name: str, value):
        """Intercepta atribuições para armazenar no dicionário interno."""
        if name in ("_db", "_dados", "id", "metodologia_padrao_id"):
            super().__setattr__(name, value)
        else:
            if not hasattr(self, "_dados"):
                super().__setattr__(name, value)
                return
            self._dados[name] = value if value is not None else ""

    def _salvar(self):
        """Persiste o dicionário interno de volta ao banco como key-value."""
        # Remove registros antigos
        self._db.query(ConfigSistema).delete()

        # Insere novos registros
        for campo in CAMPOS_ESTRUTURADOS:
            valor = self._dados.get(campo, "")
            if valor:  # Só persiste campos preenchidos
                registro = ConfigSistema(
                    id=str(uuid.uuid4()),
                    chave=campo,
                    valor=str(valor),
                    metodologia_padrao_id=self.metodologia_padrao_id,
                )
                self._db.add(registro)

        # Sempre insere metodologia se não estiver nos campos estruturados
        if "metodologia_padrao_id" not in self._dados:
            registro = ConfigSistema(
                id=str(uuid.uuid4()),
                chave="metodologia_padrao_id",
                valor=self.metodologia_padrao_id,
            )
            self._db.add(registro)

        self._db.commit()


class ConfiguracoesService:
    """Serviço central do módulo Configurações.

    Trabalha com o schema key-value do banco SQLite existente.
    """

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Permissões (método legado — mantido para compatibilidade)
    # ------------------------------------------------------------------

    def buscar_permissoes(self) -> dict:
        """Busca as permissões do usuário no banco."""
        return get_permissoes(self.db)

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------

    def obter_configuracoes(self):
        """Retorna objeto adaptado com campos estruturados a partir do banco key-value.

        Returns:
            _ConfigSistemaAdapter com atributos acessíveis pelo template.
        """
        return _ConfigSistemaAdapter(self.db)

    # ------------------------------------------------------------------
    # Criação / Persistência
    # ------------------------------------------------------------------

    def salvar(self, configuracoes) -> None:
        """Salva alterações das configurações no banco key-value.

        Args:
            configuracoes: Instância de _ConfigSistemaAdapter com alterações.
        """
        if hasattr(configuracoes, "_salvar"):
            configuracoes._salvar()
            logger.info("Configurações salvas (key-value)")
        else:
            # Fallback para objeto padrão
            self.db.merge(configuracoes)
            self.db.commit()
            self.db.refresh(configuracoes)
            logger.info("Configurações salvas (id=%s)", getattr(configuracoes, "id", "?"))
