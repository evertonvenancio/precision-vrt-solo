"""
Precision VRT Solo — Modelo Cliente

Representa apenas dados cadastrais do cliente.
Sem regras comerciais ou cálculos.
"""

from typing import Optional, List
from datetime import datetime
from .base import BaseModel

class Cliente(BaseModel):
    """
    Modelo de dados do cliente.
    Contém apenas atributos de cadastro básicos.
    """
    
    nome: str
    email: str
    telefone: Optional[str] = None
    cnpj: Optional[str] = None
    cpf: Optional[str] = None
    tipo_pessoa: str = "fisica"  # fisica ou juridica
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: bool = True
    
    def __init__(self, nome: str, email: str, **kwargs):
        super().__init__(**kwargs)
        self.nome = nome
        self.email = email