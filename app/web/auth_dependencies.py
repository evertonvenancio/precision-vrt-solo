"""
Precision VRT Solo - Dependências de autenticação baseadas em Cookie para rotas Web
Usadas exclusivamente por rotas SSR (Server-Side Rendering) que recebem cookies do navegador.
"""
from fastapi import Depends, HTTPException, Request, status
from typing import Optional

from app.web.auth import auth_service


def get_token_from_cookie(request: Request) -> str:
    """Extrai o token JWT do cookie access_token."""
    token = request.cookies.get("access_token")
    print(f"[DEBUG] Cookies recebidos: {request.cookies.keys()}")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")
    return token


async def get_current_user_web(request: Request) -> dict:
    """
    Obtém usuário atual a partir do cookie access_token.
    Para uso em rotas web (SSR) que recebem cookies do navegador.
    """
    if not auth_service:
        raise HTTPException(status_code=503, detail="Sistema de autenticação não disponível")

    # Extrair token do cookie
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")

    # Validar token JWT
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado")

    # Validar que usuário está ativo no banco
    try:
        from db.database import SessionLocal
        from sqlalchemy import text

        db = SessionLocal()
        result = db.execute(text('SELECT ativo, nome, email FROM usuarios WHERE id = :user_id LIMIT 1'),
                           {'user_id': user['id']})
        user_info = result.fetchone()
        db.close()

        if not user_info or not user_info[0]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário desativado no sistema")

        # Enriquecer user com dados do banco
        user["nome"] = user_info[1]
        user["email"] = user_info[2]
        user["ativo"] = user_info[0]

    except Exception as e:
        print(f"[ERROR] Erro ao verificar status do usuário: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Erro ao validar usuário")

    return user


async def get_current_user_optional(request: Request) -> Optional[dict]:
    """
    Obtém usuário atual se autenticado, senão retorna None.
    Para uso em rotas que podem ser públicas mas mostram conteúdo extra se logado.
    """
    if not auth_service:
        return None

    token = request.cookies.get("access_token")
    if not token:
        return None

    user = auth_service.get_current_user(token)
    if not user:
        return None

    try:
        from db.database import SessionLocal
        from sqlalchemy import text

        db = SessionLocal()
        result = db.execute(text('SELECT ativo, nome, email FROM usuarios WHERE id = :user_id LIMIT 1'),
                           {'user_id': user['id']})
        user_info = result.fetchone()
        db.close()

        if not user_info or not user_info[0]:
            return None

        user["nome"] = user_info[1]
        user["email"] = user_info[2]
        user["ativo"] = user_info[0]

    except Exception:
        return None

    return user


def require_permission_web(permission: str):
    """
    Dependency que exige uma permissão específica para rotas web (baseada em cookie).
    Levanta HTTPException 403 se o usuário não tiver a permissão.
    """
    async def permission_checker(request: Request):
        # Obter usuário via cookie
        user = await get_current_user_web(request)

        # Verificar permissão via service
        from core.authorization.dependencies import has_permission, get_user_permissions

        user_perms = get_user_permissions(request, user.get("permissions", []))

        if not has_permission(permission, user_perms):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão necessária: {permission}"
            )

        request.state.user = user
        request.state.user_permissions = list(user_perms)
        return user

    return permission_checker