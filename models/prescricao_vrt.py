"""
Precision VRT Solo — Modelo Prescrição VRT

Representa apenas dados de prescrição VRT.
Nunca calcular doses.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from .base import BaseModel
from .talhao import Talhao
from .culturas import Culturas
from .fertilizantes import Fertilizantes

class PrescricaoVrt(BaseModel):
    """
    Modelo de dados de prescrição VRT.
    Contém apenas atributos básicos de zonas e doses.
    """
    
    talhao_id: str  # Relacionamento com Talhao
    cultura_id: str  # Relacionamento com Culturas
    metodologia_id: Optional[str] = None  # Relacionamento com Metodologia
    zonas: Optional[Dict[str, Any]] = None  # Dicionário de zonas
    doses: Optional[Dict[str, float]] = None  # {nutriente: dose}
    fertilizantes: Optional[List[str]] = None  # Lista de fertilizantes
    data_geracao: Optional[datetime] = None
    observacoes: Optional[str] = None
    
    def __init__(self, talhao_id: str, cultura_id: str, **kwargs):
        super().__init__(**kwargs)
        self.talhao_id = talhao_id
        self.cultura_id = cultura_id