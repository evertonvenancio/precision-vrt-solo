"""
Precision VRT Solo — Modelo Usuário

Representa apenas dados de usuário.
Sem lógica de autenticação.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from .base import BaseModel

class Usuario(BaseModel):
    """
    Modelo de dados do usuário.
    Contém apenas atributos básicos de identificação.
    """
    
    login: str
    nome: str
    email: str
    perfil: str  # admin, operador, analista, etc.
    ativo: bool = True
    senha_hash: Optional[str] = None
    data_criacao: Optional[datetime] = None
    
    def __init__(self, login: str, nome: str, email: str, perfil: str, **kwargs):
        super().__init__(**kwargs)
        self.login = login
        self.nome = nome
        self.email = email
        self.perfil = perfil