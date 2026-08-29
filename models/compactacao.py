"""
Precision VRT Solo — Modelo Compactação

Representa apenas dados de compactação do solo.
Sem cálculos ou validações agronômicas.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseModel
from .talhao import Talhao

class Compactacao(BaseModel):
    """
    Modelo de dados de compactação do solo.
    Contém apenas atributos básicos de medição e equipamento.
    """
    
    talhao_id: str  # Relacionamento com Talhao
    resistencia: float  # MPa ou kg/cm²
    profundidade: float  # cm
    umidade: Optional[float] = None  # %
    temperatura: Optional[float] = None  # °C
    equipamento_tipo: Optional[str] = None  # Ex: "Penetrômetro"
    equipamento_fabricante: Optional[str] = None
    equipamento_modelo: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    data_medicao: Optional[datetime] = None
    observacoes: Optional[str] = None
    
    def __init__(self, talhao_id: str, resistencia: float, profundidade: float, **kwargs):
        super().__init__(**kwargs)
        self.talhao_id = talhao_id
        self.resistencia = resistencia
        self.profundidade = profundidade