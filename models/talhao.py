"""
Precision VRT Solo — Modelo Talhão

Representa apenas dados do talhão.
Sem cálculos ou validações agronômicas.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from .base import BaseModel
from .propriedade import Propriedade

class Talhao(BaseModel):
    """
    Modelo de dados do talhão.
    Contém apenas atributos básicos de identificação e localização.
    """
    
    nome: str
    propriedade_id: str  # Relacionamento com Propriedade
    area: Optional[float] = None  # hectares
    geometria: Optional[str] = None  # GeoJSON ou WKT
    coordenadas_centro: Optional[str] = None  # Latitude, Longitude
    coordenadas_extremidades: Optional[List[str]] = None  # Lista de coordenadas
    sistema_cultivo: Optional[str] = None
    solo_predominante: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: bool = True
    
    def __init__(self, nome: str, propriedade_id: str, **kwargs):
        super().__init__(**kwargs)
        self.nome = nome
        self.propriedade_id = propriedade_id