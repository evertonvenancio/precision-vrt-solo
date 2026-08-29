"""
Precision VRT Solo — Modelo Sensoriamento

Representa apenas dados de sensoriamento por satélite.
Nunca processar imagem.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseModel
from .talhao import Talhao

class Sensoriamento(BaseModel):
    """
    Modelo de dados de sensoriamento por satélite.
    Contém apenas atributos básicos de identificação e arquivo.
    """
    
    talhao_id: str  # Relacionamento com Talhao
    satelite: str  # Ex: "Sentinel-2", "Landsat-8"
    indice: str  # Ex: "NDVI", "EVI", "LAI"
    data_coleta: Optional[datetime] = None
    resolucao: Optional[float] = None  # metros
    arquivo: Optional[str] = None  # Caminho para arquivo de imagem
    arquivo_metadata: Optional[Dict[str, Any]] = None  # Metadados técnicos
    observacoes: Optional[str] = None
    
    def __init__(self, talhao_id: str, satelite: str, indice: str, **kwargs):
        super().__init__(**kwargs)
        self.talhao_id = talhao_id
        self.satelite = satelite
        self.indice = indice