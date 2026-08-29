"""
Precision VRT Solo — Modelo Arquivos

Representa apenas dados de arquivos.
Sem validações de integridade.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseModel

class Arquivos(BaseModel):
    """
    Modelo de dados de arquivos.
    Contém apenas atributos básicos de metadados.
    """
    
    nome: str
    extensao: str
    tamanho: int  # bytes
    hash_sha256: Optional[str] = None  # Hash SHA-256 para integridade
    caminho: str  # Caminho completo para arquivo
    mime_type: Optional[str] = None
    data_upload: Optional[datetime] = None
    projeto_id: Optional[str] = None  # Relacionamento com Projeto
    observacoes: Optional[str] = None
    
    def __init__(self, nome: str, extensao: str, tamanho: int, caminho: str, **kwargs):
        super().__init__(**kwargs)
        self.nome = nome
        self.extensao = extensao
        self.tamanho = tamanho
        self.caminho = caminho