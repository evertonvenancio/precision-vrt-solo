"""
Precision VRT Solo — Modelo Metodologias

Representa apenas dados de metodologia.
Nunca cálculo.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseModel

class Metodologias(BaseModel):
    """
    Modelo de dados de metodologias.
    Contém apenas atributos básicos de referência.
    """
    
    nome: str  # Nome da metodologia
    estado: str  # estado, rascunho, revisao, aprovado
    descricao: Optional[str] = None
    referencia: Optional[str] = None  # Documento de referência
    observacoes: Optional[str] = None
    
    def __init__(self, nome: str, estado: str = "rascunho", **kwargs):
        super().__init__(**kwargs)
        self.nome = nome
        self.estado = estado