"""
Precision VRT Solo - Autorização por Permissão

Responsabilidade: Validar permissões do usuário autenticado.
Não duplicar lógica de autenticação.
"""
from functools import wraps
from typing import Callable, List, Optional
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from app.web.auth import get_current_user


def require_permission(permission: str):
    """
    Decorador para exigir permissão específica.
    
    Args:
        permission: Permissão necessária (ex: "dashboard:read")
        
    Raises:
        HTTPException: 401 se não autenticado, 403 se não tiver permissão
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrair credentials da requisição
            credentials = None
            
            # Procurar credentials nos argumentos
            for arg in args:
                if isinstance(arg, Request):
                    # Se for template response, não há credentials
                    continue
                if isinstance(arg, HTTPAuthorizationCredentials):
                    credentials = arg
                    break
            
            # Se não encontrar, tentar nos kwargs
            if not credentials:
                credentials = kwargs.get('credentials')
            
            if not credentials:
                raise HTTPException(status_code=401, detail="Credenciais não fornecidas")
            
            # Obter usuário autenticado
            user = get_current_user(credentials)
            
            # Verificar permissão
            user_permissions = user.get('permissions', [])
            if permission not in user_permissions:
                raise HTTPException(status_code=403, detail=f"Permissão '{permission}' necessária")
            
            # Se tiver permissão, continuar com a função
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


class PermissionChecker:
    """
    Classe para verificar permissões em endpoints FastAPI.
    
    Uso:
        @router.get("/dashboard")
        async def dashboard(
            credentials: HTTPAuthorizationCredentials = Depends(security),
            checker: PermissionChecker = Depends()
        ):
            checker.require_permission("dashboard:read")
            # ... resto da função
    """
    
    def __init__(self, credentials: HTTPAuthorizationCredentials = Depends()):
        self.credentials = credentials
    
    def require_permission(self, permission: str):
        """
        Exige permissão específica.
        
        Args:
            permission: Permissão necessária
            
        Raises:
            HTTPException: 401 se não autenticado, 403 se não tiver permissão
        """
        user = get_current_user(self.credentials)
        
        user_permissions = user.get('permissions', [])
        if permission not in user_permissions:
            raise HTTPException(
                status_code=403, 
                detail=f"Permissão '{permission}' necessária para acessar este recurso"
            )
    
    def require_role(self, role: str):
        """
        Exige papel específico.
        
        Args:
            role: Papel necessário (ex: "admin")
            
        Raises:
            HTTPException: 401 se não autenticado, 403 se não tiver o papel
        """
        user = get_current_user(self.credentials)
        
        user_role = user.get('role')
        if user_role != role:
            raise HTTPException(
                status_code=403, 
                detail=f"Papel '{role}' necessário para acessar este recurso"
            )