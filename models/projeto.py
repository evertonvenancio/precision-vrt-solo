"""
Precision VRT Solo — Modelo Projeto

Representa apenas dados do projeto.
Sem regras agronômicas.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseModel
from .cliente import Cliente
from .propriedade import Propriedade
from .talhao import Talhao

class Projeto(BaseModel):
    """
    Modelo de dados do projeto.
    Contém apenas atributos básicos de identificação.
    """
    
    nome: str
    cliente_id: str  # Relacionamento com Cliente
    propriedade_id: str  # Relacionamento com Propriedade
    talhao_id: str  # Relacionamento com Talhao
    cultura_id: Optional[str] = None  # Relacionamento com Cultura
    safra: Optional[str] = None  # Ex: "2023/2024"
    data_inicio: Optional[datetime] = None
    data_previsao_fim: Optional[datetime] = None
    status: str = "planejado"  # planejado, em_andamento, concluido, cancelado
    observacoes: Optional[str] = None
    ativo: bool = True
    
    def __init__(self, nome: str, cliente_id: str, propriedade_id: str, talhao_id: str, **kwargs):
        super().__init__(**kwargs)
        self.nome = nome
        self.cliente_id = cliente_id
        self.propriedade_id = propriedade_id
        self.talhao_id = talhao_id