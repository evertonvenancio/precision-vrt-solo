
"""
Precision VRT Solo - Interface de Usuário (Core)

Define a interface abstrata para o modelo de Usuário.
Isola o core de dependências diretas de dados.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from enum import Enum

class StatusUsuario(Enum):
    """Status do usuário."""
    ATIVO = "ativo"
    INATIVO = "inativo"
    BLOQUEADO = "bloqueado"

class TipoUsuario(Enum):
    """Tipo de usuário."""
    ADMIN = "admin"
    GERENTE = "gerente"
    OPERADOR = "operador"
    ANALISTA = "analista"

class InterfaceUsuario(ABC):
    """
    Interface abstrata para o modelo de Usuário.
    
    Define o contrato que todas as implementações devem seguir.
    """
    
    @abstractmethod
    def get_id(self) -> int:
        """Retorna o ID do usuário."""
        pass
    
    @abstractmethod
    def get_nome(self) -> str:
        """Retorna o nome do usuário."""
        pass
    
    @abstractmethod
    def get_email(self) -> str:
        """Retorna o email do usuário."""
        pass
    
    @abstractmethod
    def get_status(self) -> StatusUsuario:
        """Retorna o status do usuário."""
        pass
    
    @abstractmethod
    def get_tipo(self) -> TipoUsuario:
        """Retorna o tipo de usuário."""
        pass
    
    @abstractmethod
    def is_ativo(self) -> bool:
        """Verifica se o usuário está ativo."""
        pass
    
    @abstractmethod
    def has_permission(self, permission: str) -> bool:
        """Verifica se o usuário tem uma permissão específica."""
        pass

__all__ = [
    'InterfaceUsuario',
    'StatusUsuario',
    'TipoUsuario'
]
