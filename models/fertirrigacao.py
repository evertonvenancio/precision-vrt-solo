"""
Precision VRT Solo — Modelo Fertirrigação

Representa apenas dados de fertirrigação.
Sem cálculos ou recomendações agronômicas.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from .base import BaseModel
from .talhao import Talhao

class Fertirrigacao(BaseModel):
    """
    Modelo de dados de fertirrigação.
    Contém apenas atributos básicos de solução e nutrientes.
    """
    
    talhao_id: str  # Relacionamento com Talhao
    solucao_descricao: Optional[str] = None  # Descrição da solução
    nutrientes: Optional[Dict[str, float]] = None  # {nutriente: quantidade}
    concentracao: Optional[float] = None  # % ou mg/L
    condutividade_eletrica: Optional[float] = None  # dS/m
    ph: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    data_aplicacao: Optional[datetime] = None
    observacoes: Optional[str] = None
    
    def __init__(self, talhao_id: str, **kwargs):
        super().__init__(**kwargs)
        self.talhao_id = talhao_id