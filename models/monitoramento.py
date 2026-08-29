"""
Precision VRT Solo — Modelo Monitoramento

Representa apenas dados de monitoramento.
Não contém lógica de comparação.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from .base import BaseModel
from .talhao import Talhao

class Monitoramento(BaseModel):
    """
    Modelo de dados de monitoramento.
    Contém apenas atributos básicos de imagem e observação.
    """
    
    talhao_id: str  # Relacionamento com Talhao
    imagem: Optional[str] = None  # Caminho para arquivo de imagem
    data_imagem: Optional[datetime] = None
    comparacao_com: Optional[str] = None  # Referência para comparação
    alertas: Optional[List[str]] = None  # Lista de alertas
    observacoes: Optional[str] = None
    
    def __init__(self, talhao_id: str, **kwargs):
        super().__init__(**kwargs)
        self.talhao_id = talhao_id