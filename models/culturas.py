"""
Precision VRT Solo — Modelo Culturas

Representa apenas cadastro de culturas.
Nunca metodologia.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseModel

class Culturas(BaseModel):
    """
    Modelo de dados de cadastro de culturas.
    Contém apenas atributos básicos de identificação.
    """
    
    nome: str  # Ex: "Milho", "Soja", "Café", "Cana"
    nome_cientifico: Optional[str] = None
    descricao: Optional[str] = None
    ativo: bool = True
    observacoes: Optional[str] = None
    
    def __init__(self, nome: str, **kwargs):
        super().__init__(**kwargs)
        self.nome = nome