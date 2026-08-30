"""
Precision VRT Solo - Rotas do Módulo Permissões

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.permissoes_service import PermissoesService

router = APIRouter()
from app.web.auth_dependencies import require_permission_web  # autenticação via cookie


@router.get("/equipe/permissoes")
async def permissoes_page(request: Request, db: Session = Depends(get_db)):
    service = PermissoesService(db)
    return HTMLResponse(
        "<div class='p-8'><h1 class='text-2xl font-bold mb-4'>Permissoes de Acesso</h1>"
        "<p class='text-gray-500 dark:text-gray-400'>Modulo em construcao. Aqui o gestor configurara os acessos.</p></div>"
    )
