"""
Precision VRT Solo - Rotas do Módulo Dashboard

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from datetime import datetime

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.dashboard_service import DashboardService
from app.template_config import templates

router = APIRouter()


def get_token_from_cookie(request: Request) -> str:
    """Extrai o token JWT do cookie access_token."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    return token


@router.get("/")
async def dashboard_page(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Dashboard principal - exige permissão dashboard:read
    """
    # Extrair token do cookie
    token = get_token_from_cookie(request)

    # Verificar token e obter usuário
    from app.web.auth import auth_service
    if not auth_service:
        raise HTTPException(status_code=503, detail="Sistema de autenticação não disponível")

    payload = auth_service.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    # Obter dados do usuário
    user_data = auth_service.get_user_by_username(payload["sub"])
    if not user_data:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    # Permissão já verificada pela autenticação do cookie

    # Criar usuário autenticado com contrato
    from auth.authenticated_user import AuthenticatedUser
    from db.database import SessionLocal
    db_local = SessionLocal()
    try:
        from sqlalchemy import text
        result = db_local.execute(
            text("SELECT login, ativo FROM usuarios WHERE id = :user_id"),
            {"user_id": user_data["id"]},
        )
        additional_info = result.fetchone()
        if additional_info:
            auth_user = AuthenticatedUser.from_jwt_data(
                user_data,
                {
                    "nome": additional_info[0],
                    "email": None,
                    "ativo": additional_info[1],
                },
            )
        else:
            auth_user = AuthenticatedUser.from_jwt_data(user_data)
    finally:
        db_local.close()

    # Criar serviço com usuário autenticado
    service = DashboardService(db, auth_user.to_dict() if auth_user else None)
    permissoes = service.buscar_permissoes()
    dados = service.get_dados()

    agora = datetime.now()

    context = {
        "request": request,
        # 1. Boas-vindas
        "nome_usuario": (
            auth_user.nome
            if auth_user
            else permissoes.get("nome", user_data.get("username", "Usuário"))
        ),
        "data_atual": agora.strftime("%d/%m/%Y"),
        "hora_atual": agora.strftime("%H:%M"),

        # 2. Clientes
        "total_clientes": dados["total_clientes"],
        "total_fazendas": dados["total_fazendas"],
        "area_total_cadastrada": dados["area_total_cadastrada"],

        # 3. Operação
        "processamentos_realizados": dados["processamentos_realizados"],
        "prescricoes_geradas": dados["prescricoes_geradas"],
        "pdfs_emitidos": dados["pdfs_emitidos"],

        # 4. Módulos Técnicos
        "modulos_tecnicos": dados["modulos_tecnicos"],

        # 5. Comercial
        "orcamentos": dados["orcamentos"],
        "vendas": dados["vendas"],

        # 6. Oportunidades
        "oportunidades": dados["oportunidades"],

        # 7. Avisos
        "aniversariantes": dados["aniversariantes"],
        "notificacoes": dados["notificacoes"],
        "lembretes": dados["lembretes"],

        # 8. Clima
        "clima": dados["clima"],

        "permissoes": permissoes,
        "user_data": user_data,
        "auth_user": auth_user,
    }
    return templates.TemplateResponse(request=request, name="dashboard.html", context=context)
