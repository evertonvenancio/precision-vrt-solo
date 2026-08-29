"""
Precision VRT Solo - Serviço do Módulo Conhecimento
Toda consulta ao banco e regra de negócio centralizada aqui.
"""
import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from core.seguranca.permissions import get_permissoes
from models.conhecimento import Artigo, CategoriaArtigo

logger = logging.getLogger(__name__)


class ConhecimentoError(Exception):
    pass


class ConhecimentoService:
    """
    Serviço central do módulo Conhecimento.
    Responsável por toda consulta ao banco e regra de negócio.
    """

    def __init__(self, db: Session):
        self.db = db

    # ──────────────────────────────────────────────────────────────
    # CONSULTAS AO BANCO (Repository Layer interno)
    # ──────────────────────────────────────────────────────────────

    def buscar_permissoes(self) -> dict:
        """Busca as permissões do usuário no banco."""
        return get_permissoes(self.db)

    # ──────────────────────────────────────────────────────────────
    # REGRAS DE NEGÓCIO
    # ──────────────────────────────────────────────────────────────

    def criar(self, tenant_id: str, categoria: CategoriaArtigo, titulo: str,
              conteudo: str, referencias: Optional[str] = None,
              chave_vinculo: Optional[str] = None) -> Artigo:
        artigo = Artigo(
            tenant_id=tenant_id,
            categoria=categoria,
            titulo=titulo,
            conteudo=conteudo,
            referencias=referencias,
            chave_vinculo=chave_vinculo
        )
        self.db.add(artigo)
        self.db.commit()
        self.db.refresh(artigo)
        return artigo

    def listar(self, tenant_id: str, categoria: Optional[CategoriaArtigo] = None,
               busca: Optional[str] = None, limit: int = 50, offset: int = 0) -> list[Artigo]:
        query = self.db.query(Artigo).filter(Artigo.tenant_id == tenant_id)
        if categoria:
            query = query.filter(Artigo.categoria == categoria)
        if busca:
            query = query.filter(Artigo.titulo.ilike(f"%{busca}%"))
        return query.offset(offset).limit(limit).all()

    def obter(self, tenant_id: str, artigo_id: str) -> Artigo:
        artigo = self.db.query(Artigo).filter(
            Artigo.tenant_id == tenant_id,
            Artigo.id == artigo_id
        ).first()
        if not artigo:
            raise ConhecimentoError("Artigo nao encontrado.")
        return artigo

    def atualizar(self, tenant_id: str, artigo_id: str, **kwargs) -> Artigo:
        artigo = self.obter(tenant_id, artigo_id)
        for key, value in kwargs.items():
            if hasattr(artigo, key) and value is not None:
                setattr(artigo, key, value)
        self.db.commit()
        self.db.refresh(artigo)
        return artigo

    def remover(self, tenant_id: str, artigo_id: str) -> bool:
        artigo = self.obter(tenant_id, artigo_id)
        self.db.delete(artigo)
        self.db.commit()
        return True
