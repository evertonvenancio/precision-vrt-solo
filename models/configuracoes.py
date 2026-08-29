"""
Precision VRT Solo — Modelo Configurações

Representa apenas persistência de configurações.
Sem validações de regras.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseModel

class Configuracoes(BaseModel):
    """
    Modelo de dados de configurações.
    Contém apenas atributos básicos de persistência.
    """
    
    chave: str  # Chave de configuração
    valor: Any  # Valor da configuração
    tipo: str = "texto"  # texto, numero, booleano, json
    descricao: Optional[str] = None
    ativo: bool = True
    
    def __init__(self, chave: str, valor: Any, **kwargs):
        super().__init__(**kwargs)
        self.chave = chave
        self.valor = valor