"""
Precision VRT Solo — Base Models

Modelo base para todos os models do sistema.
Contém apenas atributos, tipos e relacionamentos.
"""

from typing import Optional
from datetime import datetime
from uuid import uuid4

class BaseModel:
    """
    Modelo base com campos comuns para todos os models.
    Contém apenas metadados e atributos básicos.
    """
    
    id: str
    criado_em: datetime
    atualizado_em: datetime
    
    def __init__(self, id: Optional[str] = None):
        self.id = id or str(uuid4())
        self.criado_em = datetime.now()
        self.atualizado_em = datetime.now()