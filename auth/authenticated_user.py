"""
Contrato de Usuário Autenticado

Define a estrutura de dados para representar um usuário autenticado
no sistema, garantindo consistência entre serviços e endpoints.

Responsabilidade: 
- Representar identidade/contexto do usuário
- Não conter lógica de negócio
- Ser passada entre serviços para manter identidade real
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class AuthenticatedUser:
    """
    Representa um usuário autenticado no sistema.
    
    Esta estrutura garante que todos os serviços recebam a mesma
    identidade do usuário, vinda do JWT e validada no banco.
    """
    id: str  # ID único do usuário no banco
    username: str  # Username de login
    nome: str  # Nome real do usuário (se disponível)
    email: str  # Email do usuário (se disponível)
    role: str  # Papel do usuário (admin, user, etc.)
    permissions: List[str]  # Lista de permissões do usuário
    ativo: bool = True  # Status do usuário no banco
    
    @classmethod
    def from_jwt_data(cls, jwt_data: Dict[str, Any], additional_info: Dict[str, Any] = None) -> 'AuthenticatedUser':
        """
        Cria AuthenticatedUser a partir de dados do JWT + banco.
        
        Args:
            jwt_data: Dados extraídos do token JWT
            additional_info: Dados adicionais do banco (nome, email, ativo)
            
        Returns:
            Instância de AuthenticatedUser
        """
        additional_info = additional_info or {}
        
        return cls(
            id=jwt_data.get('user_id'),
            username=jwt_data.get('sub', jwt_data.get('username')),
            nome=additional_info.get('nome') or jwt_data.get('username'),
            email=additional_info.get('email'),
            role=jwt_data.get('role', 'user'),
            permissions=jwt_data.get('permissions', []),
            ativo=additional_info.get('ativo', True)
        )
    
    def has_permission(self, permission: str) -> bool:
        """
        Verifica se o usuário tem uma permissão específica.
        
        Args:
            permission: Permissão a ser verificada
            
        Returns:
            True se o usuário tem a permissão, False caso contrário
        """
        return permission in self.permissions
    
    def has_role(self, role: str) -> bool:
        """
        Verifica se o usuário tem um papel específico.
        
        Args:
            role: Papel a ser verificado
            
        Returns:
            True se o usuário tem o papel, False caso contrário
        """
        return self.role == role
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte para dicionário compatível com serviços existentes.
        
        Returns:
            Dicionário com dados do usuário
        """
        return {
            'id': self.id,
            'username': self.username,
            'nome': self.nome,
            'email': self.email,
            'role': self.role,
            'permissions': self.permissions,
            'ativo': self.ativo
        }