"""
Precision VRT Solo — Modelo Equipamentos

Representa apenas dados de equipamentos.
Sem lógica de operação.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseModel

class Equipamentos(BaseModel):
    """
    Modelo de dados de equipamentos.
    Contém apenas atributos básicos de identificação.
    """
    
    tipo: str  # Ex: "Penetrômetro", "Drone", "GPS", "Extrator"
    fabricante: Optional[str] = None
    modelo: Optional[str] = None
    categoria: Optional[str] = None
    serie: Optional[str] = None
    data_aquisicao: Optional[datetime] = None
    status: str = "ativo"  # ativo, manutencao, inativo
    observacoes: Optional[str] = None
    
    def __init__(self, tipo: str, **kwargs):
        super().__init__(**kwargs)
        self.tipo = tipo