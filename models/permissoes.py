"""
Precision VRT Solo — Modelo Permissões

Representa apenas dados de permissões.
Sem lógica de controle.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from .base import BaseModel
from .usuario import Usuario

class Permissoes(BaseModel):
    """
    Modelo de dados de permissões.
    Contém apenas atributos básicos de acesso.
    """
    
    usuario_id: str  # Relacionamento com Usuario
    recurso: str  # Recurso protegido
    acao: str  # Ação: read, write, delete, execute
    permissao: str  # allow, deny
    data_expiracao: Optional[datetime] = None
    
    def __init__(self, usuario_id: str, recurso: str, acao: str, permissao: str, **kwargs):
        super().__init__(**kwargs)
        self.usuario_id = usuario_id
        self.recurso = recurso
        self.acao = acao
        self.permissao = permissao