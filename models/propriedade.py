"""
Precision VRT Solo — Modelo Propriedade

Representa apenas dados da propriedade/fazenda.
Sem regras agronômicas.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseModel
from .cliente import Cliente

class Propriedade(BaseModel):
    """
    Modelo de dados da propriedade/fazenda.
    Contém apenas atributos básicos de identificação e localização.
    """
    
    nome: str
    cliente_id: str  # Relacionamento com Cliente
    matricula: Optional[str] = None
    area_total: Optional[float] = None  # hectares
    municipio: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    endereco_completo: Optional[str] = None
    contato_local: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: bool = True
    
    def __init__(self, nome: str, cliente_id: str, **kwargs):
        super().__init__(**kwargs)
        self.nome = nome
        self.cliente_id = cliente_id