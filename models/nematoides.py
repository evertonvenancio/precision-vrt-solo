"""
Precision VRT Solo — Modelo Nematoides

Representa apenas dados de análise de nematoides.
Sem cálculos ou interpretações agronômicas.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseModel
from .talhao import Talhao

class Nematoides(BaseModel):
    """
    Modelo de dados de análise de nematoides.
    Contém apenas atributos básicos de identificação e localização.
    """
    
    talhao_id: str  # Relacionamento com Talhao
    especie: str  # Espécie de nematóide
    populacao: Optional[float] = None  # Individuos/100g de solo
    profundidade: Optional[float] = None  # cm
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    data_analise: Optional[datetime] = None
    laboratorio: Optional[str] = None
    metodo_analise: Optional[str] = None
    observacoes: Optional[str] = None
    
    def __init__(self, talhao_id: str, especie: str, **kwargs):
        super().__init__(**kwargs)
        self.talhao_id = talhao_id
        self.especie = especie