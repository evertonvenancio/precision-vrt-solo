"""
Precision VRT Solo — Modelo Configurações

Representa persistência de configurações do sistema.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TipoConfig(Enum):
    """Tipos de configuração."""
    TEXTO = "texto"
    NUMERO = "numero"
    BOOLEANO = "booleano"
    JSON = "json"
    LISTA = "lista"
    DATA = "data"

class Config:
    """
    Modelo consolidado de configurações.
    """
    
    def __init__(self,
                 id: str,
                 tenant_id: str,
                 chave: str,
                 valor: Any,
                 tipo: TipoConfig = TipoConfig.TEXTO,
                 descricao: Optional[str] = None,
                 ativo: bool = True,
                 dados_adicionais: Optional[Dict[str, Any]] = None):
        self.id = id
        self.tenant_id = tenant_id
        self.chave = chave
        self.valor = valor
        self.tipo = tipo
        self.descricao = descricao
        self.ativo = ativo
        self.dados_adicionais = dados_adicionais or {}
        self.criado_em = datetime.now()
        self.atualizado_em = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte para dicionário.
        """
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'chave': self.chave,
            'valor': self.valor,
            'tipo': self.tipo.value,
            'descricao': self.descricao,
            'ativo': self.ativo,
            'dados_adicionais': self.dados_adicionais,
            'criado_em': self.criado_em.isoformat(),
            'atualizado_em': self.atualizado_em.isoformat()
        }