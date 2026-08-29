
"""
Precision VRT Solo — Modelo de Conhecimento

Implementa modelos de dados para gestão de artigos de conhecimento e documentação técnica.
"""

from typing import Optional
from uuid import UUID
from enum import Enum

class CategoriaArtigo(Enum):
    """Categorias de artigos de conhecimento."""
    TECNICO = "tecnico"
    METODOLOGIA = "metodologia"
    AGRONOMIA = "agronomia"
    EQUIPAMENTO = "equipamento"
    PROCEDIMENTO = "procedimento"
    GUIA = "guia"
    MANUAL = "manual"
    NOTICIA = "noticia"
    REGULAMENTO = "regulamento"
    TREINAMENTO = "treinamento"
    FAQ = "faq"
    OUTRO = "outro"

class Artigo:
    """
    Representa um artigo de conhecimento.
    """
    
    def __init__(self,
                 id: UUID,
                 tenant_id: UUID,
                 categoria: CategoriaArtigo,
                 titulo: str,
                 conteudo: str,
                 referencias: Optional[str] = None,
                 chave_vinculo: Optional[str] = None):
        self.id = id
        self.tenant_id = tenant_id
        self.categoria = categoria
        self.titulo = titulo
        self.conteudo = conteudo
        self.referencias = referencias
        self.chave_vinculo = chave_vinculo
        
    def to_dict(self) -> dict:
        """
        Converte para dicionário.
        """
        return {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'categoria': self.categoria.value,
            'titulo': self.titulo,
            'conteudo': self.conteudo,
            'referencias': self.referencias,
            'chave_vinculo': self.chave_vinculo
        }

class ConhecimentoError(Exception):
    """
    Exceção personalizada para erros na camada de conhecimento.
    """
    pass
