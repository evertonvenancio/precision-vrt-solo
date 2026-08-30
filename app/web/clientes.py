"""
Precision VRT Solo - Rotas do Módulo Clientes

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.clientes_service import ClientesService
from app.web.auth_dependencies import require_permission_web

router = APIRouter()
from app.template_config import templates  # compartilhado - globals de RBAC


@router.get("/")
async def clientes_page(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission_web("clientes:read"))
):
    """
    Lista de clientes - exige permissão clientes:read
    """
    service = ClientesService(db, user)
    permissoes = service.buscar_permissoes()
    clientes = service.listar()
    return templates.TemplateResponse(request=request, name="clientes.html", context={
        "clientes": clientes,
        "permissoes": permissoes,
        "usuario": user
    })


@router.get("/novo")
async def novo_cliente_page(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission_web("clientes:write"))
):
    """
    Novo cliente - exige permissão clientes:write
    """
    service = ClientesService(db, user)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(request=request, name="novo_cliente.html", context={
        "cliente": None,
        "permissoes": permissoes,
        "usuario": user
    })


@router.post("/novo")
async def salvar_cliente(
    request: Request,
    nome: str = Form(...),
    cpf_cnpj: str = Form(...),
    telefone: str = Form(...),
    email: str = Form(...),
    cidade: str = Form(...),
    estado: str = Form(...),
    area_total_hectares: float = Form(0),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission_web("clientes:write"))
):
    """
    Salvar novo cliente - exige permissão clientes:write
    """
    service = ClientesService(db, user)
    result = service.criar(nome, cpf_cnpj, telefone, email, cidade, estado, area_total_hectares)
    if result and isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"success": True, "message": "Cliente criado com sucesso", "client_id": result}


@router.get("/{cliente_id}/editar")
async def editar_cliente_page(
    cliente_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission_web("clientes:write"))
):
    """
    Editar cliente - exige permissão clientes:write
    """
    service = ClientesService(db, user)
    permissoes = service.buscar_permissoes()
    cliente = service.obter(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return templates.TemplateResponse(request=request, name="novo_cliente.html", context={
        "cliente": cliente,
        "permissoes": permissoes,
        "usuario": user
    })


@router.post("/{cliente_id}/editar")
async def processar_edicao_cliente(
    cliente_id: str,
    request: Request,
    nome: str = Form(...),
    cpf_cnpj: str = Form(...),
    telefone: str = Form(...),
    email: str = Form(...),
    cidade: str = Form(...),
    estado: str = Form(...),
    area_total_hectares: float = Form(0),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission_web("clientes:write"))
):
    """
    Processar edição de cliente - exige permissão clientes:write
    """
    service = ClientesService(db, user)
    result = service.atualizar(cliente_id, nome, cpf_cnpj, telefone, email, cidade, estado, area_total_hectares)
    if result and isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"success": True, "message": "Cliente atualizado com sucesso", "client_id": cliente_id}


@router.post("/{cliente_id}/excluir")
async def excluir_cliente_route(
    cliente_id: str,
    justificativa: str = Form(""),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission_web("clientes:delete"))
):
    """
    Excluir cliente - exige permissão clientes:delete
    """
    service = ClientesService(db, user)
    result = service.excluir(cliente_id, justificativa)
    return result
