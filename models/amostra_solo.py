"""
Precision VRT Solo — Modelo Amostra Solo

Representa apenas dados da amostra de solo.
Sem interpretação ou cálculos.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from .base import BaseModel
from .projeto import Projeto

class AmostraSolo(BaseModel):
    """
    Modelo de dados da amostra de solo.
    Contém apenas atributos básicos de coleta e localização.
    """
    
    projeto_id: str  # Relacionamento com Projeto
    ponto_identificacao: str  # Ponto de amostragem
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    profundidade_min: Optional[float] = None  # cm
    profundidade_max: Optional[float] = None  # cm
    profundidade_descricao: Optional[str] = None  # Ex: "0-20cm"
    data_coleta: Optional[datetime] = None
    laboratorio: Optional[str] = None
    metodo_coleta: Optional[str] = None
    observacoes: Optional[str] = None
    
    def __init__(self, projeto_id: str, ponto_identificacao: str, **kwargs):
        super().__init__(**kwargs)
        self.projeto_id = projeto_id
        self.ponto_identificacao = ponto_identificacao