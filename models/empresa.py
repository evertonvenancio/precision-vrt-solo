"""
Precision VRT Solo — Modelo Empresa

Representa um CNPJ vinculado a um Cliente.
Um Cliente pode ter múltiplas Empresas (vários CNPJs).

Persistência: tabela SQL 'empresas' (criada via migration DDL).
"""

from typing import Optional
from .base import BaseModel


class Empresa(BaseModel):
    """
    Modelo de dados de uma empresa (CNPJ) vinculada a um Cliente.
    """

    cnpj: str
    nome_fantasia: str
    razao_social: str
    cliente_id: str  # FK para clientes.id

    def __init__(self, cnpj: str, nome_fantasia: str, razao_social: str, cliente_id: str, **kwargs):
        super().__init__(**kwargs)
        self.cnpj = cnpj
        self.nome_fantasia = nome_fantasia
        self.razao_social = razao_social
        self.cliente_id = cliente_id