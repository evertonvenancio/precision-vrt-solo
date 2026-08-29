"""
Precision VRT Solo - Multi-Tenancy Middleware
Responsável por extrair e propagar o contexto de tenant (empresa) por requisição.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Optional


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware para propagação de contexto multi-tenant.

    Extrai tenant_id de:
    1. Header X-Tenant-ID (para APIs)
    2. JWT do usuário autenticado (claim 'tenant_id')
    3. Cookie/session do usuário logado
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Extrair tenant_id do request
        tenant_id = self._extract_tenant_id(request)

        # Armazenar no state do request para uso posterior
        request.state.tenant_id = tenant_id

        # Adicionar header de resposta para debug
        response = await call_next(request)
        if tenant_id:
            response.headers["X-Tenant-ID"] = str(tenant_id)

        return response

    def _extract_tenant_id(self, request: Request) -> Optional[str]:
        """Extrai tenant_id de várias fontes possíveis."""

        # 1. Header explícito (prioridade para APIs)
        if "x-tenant-id" in request.headers:
            return request.headers["x-tenant-id"]

        # 2. Tentar extrair do JWT no cookie
        try:
            from app.web.auth import auth_service
            if auth_service:
                access_token = request.cookies.get("access_token")
                if access_token:
                    payload = auth_service.verify_token(access_token)
                    if payload and "tenant_id" in payload:
                        return str(payload["tenant_id"])
        except Exception:
            pass

        # 3. Tentar do state do usuário (se já autenticado via dependency)
        if hasattr(request.state, "user") and request.state.user:
            user = request.state.user
            if isinstance(user, dict) and "tenant_id" in user:
                return str(user["tenant_id"])

        return None


def get_tenant_id(request: Request) -> Optional[str]:
    """
    Dependency helper para obter tenant_id no contexto da requisição.
    Usado em services/endpoints que precisam do tenant.
    """
    return getattr(request.state, "tenant_id", None)


def require_tenant(request: Request) -> str:
    """
    Dependency que exige tenant_id válido.
    Levanta HTTPException se não houver tenant.
    """
    from fastapi import HTTPException, status

    tenant_id = get_tenant_id(request)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contexto de tenant não encontrado. Header X-Tenant-ID obrigatório."
        )
    return tenant_id