"""
Precision VRT Solo — Modelo Exportação

Representa apenas dados de exportação.
Não contém lógica de exportação.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseModel
from .usuario import Usuario

class Exportacao(BaseModel):
    """
    Modelo de dados de exportação.
    Contém apenas atributos básicos de formato e arquivo.
    """
    
    formato: str  # PDF, CSV, Excel, GeoJSON, etc.
    data: Optional[datetime] = None
    usuario_id: str  # Relacionamento com Usuario
    arquivo: Optional[str] = None  # Caminho para arquivo exportado
    projeto_id: Optional[str] = None  # Relacionamento com Projeto
    observacoes: Optional[str] = None
    
    def __init__(self, formato: str, usuario_id: str, **kwargs):
        super().__init__(**kwargs)
        self.formato = formato
        self.usuario_id = usuario_id