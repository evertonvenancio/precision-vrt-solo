"""
Precision VRT Solo - Rotas do Módulo Clientes

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.clientes_service import ClientesService
from core.authorization.dependencies import require_permission

security = HTTPBearer()
router = APIRouter()
from app.template_config import templates  # compartilhado - globals de RBAC



@router.get("/")
async def clientes_page(
    request: Request, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Lista de clientes - exige permissão clientes:read
    """
    # Verificar permissão necessária
    require_permission("clientes:read")(credentials)
    
    # Obter usuário autenticado
    from app.web.auth import get_current_user
    user_data = get_current_user(credentials)
    
    service = ClientesService(db, user_data)
    permissoes = service.buscar_permissoes()
    clientes = service.listar()
    return templates.TemplateResponse(request=request, name="clientes.html", context={"clientes": clientes, "permissoes": permissoes})


@router.get("/novo")
async def novo_cliente_page(
    request: Request, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Novo cliente - exige permissão clientes:write
    """
    # Verificar permissão necessária
    require_permission("clientes:write")(credentials)
    
    from app.web.auth import get_current_user
    user_data = get_current_user(credentials)
    
    service = ClientesService(db, user_data)
    permissoes = service.buscar_permissoes()
    return templates.TemplateResponse(request=request, name="novo_cliente.html", context={"cliente": None, "permissoes": permissoes})


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
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Salvar novo cliente - exige permissão clientes:write
    """
    # Verificar permissão necessária
    require_permission("clientes:write")(credentials)
    
    from app.web.auth import get_current_user
    user_data = get_current_user(credentials)
    
    service = ClientesService(db, user_data)
    
    # Registrar auditoria da criação
    try:
        from app.services.auditoria_service import AuditoriaPersistenteService
        from core.seguranca.auditoria import TipoAcao, ModuloSistema
        
        auditoria_service = AuditoriaPersistenteService(db)
        cliente_id = service.criar(nome, cpf_cnpj, telefone, email, cidade, estado, area_total_hectares)
        
        # Se foi bem-sucedido, registrar evento
        if cliente_id and str(cliente_id) != "{'error': 'Falha ao criar cliente'}":
            auditoria_service.registrar_operacao_cliente(
                tipo_acao=TipoAcao.CRIAR,
                usuario_id=user_data['id'],
                usuario_nome=user_data['username'],
                cliente_id=str(cliente_id),
                detalhes={
                    'nome': nome,
                    'cpf_cnpj': cpf_cnpj,
                    'email': email,
                    'cidade': cidade,
                    'estado': estado,
                    'area_total_hectares': area_total_hectares
                }
            )
            
            return {
                "success": True,
                "message": "Cliente criado com sucesso",
                "client_id": cliente_id,
                "auditoria_id": f"audit_{cliente_id}"
            }
        else:
            auditoria_service.registrar_operacao(
                tipo_acao=TipoAcao.CRIAR,
                modulo=ModuloSistema.USUARIOS,
                usuario_id=user_data['id'],
                usuario_nome=user_data['username'],
                acao="criar_cliente",
                sucesso=False,
                mensagem="Falha ao criar cliente"
            )
            return service.criar(nome, cpf_cnpj, telefone, email, cidade, estado, area_total_hectares)
            
    except Exception as e:
        # Fallback para comportamento original
        return service.criar(nome, cpf_cnpj, telefone, email, cidade, estado, area_total_hectares)


@router.get("/{cliente_id}/editar")
async def editar_cliente_page(
    cliente_id: str, 
    request: Request, 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Editar cliente - exige permissão clientes:write
    """
    # Verificar permissão necessária
    require_permission("clientes:write")(credentials)
    
    from app.web.auth import get_current_user
    user_data = get_current_user(credentials)
    
    service = ClientesService(db, user_data)
    permissoes = service.buscar_permissoes()
    cliente = service.obter(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")
    return templates.TemplateResponse(request=request, name="novo_cliente.html", context={"cliente": cliente, "permissoes": permissoes})


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
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Processar edição de cliente - exige permissão clientes:write
    """
    # Verificar permissão necessária
    require_permission("clientes:write")(credentials)
    
    from app.web.auth import get_current_user
    user_data = get_current_user(credentials)
    
    service = ClientesService(db, user_data)
    
    # Registrar auditoria da edição
    try:
        from app.services.auditoria_service import AuditoriaPersistenteService
        from core.seguranca.auditoria import TipoAcao, ModuloSistema
        
        auditoria_service = AuditoriaPersistenteService(db)
        resultado = service.atualizar(cliente_id, nome, cpf_cnpj, telefone, email, cidade, estado, area_total_hectares)
        
        # Se foi bem-sucedido, registrar evento
        if resultado and str(resultado) != "{'error': 'Falha ao atualizar cliente'}":
            auditoria_service.registrar_operacao_cliente(
                tipo_acao=TipoAcao.ALTERAR,
                usuario_id=user_data['id'],
                usuario_nome=user_data['username'],
                cliente_id=cliente_id,
                detalhes={
                    'nome': nome,
                    'cpf_cnpj': cpf_cnpj,
                    'email': email,
                    'cidade': cidade,
                    'estado': estado,
                    'area_total_hectares': area_total_hectares
                }
            )
            
            return {
                "success": True,
                "message": "Cliente atualizado com sucesso",
                "client_id": cliente_id,
                "auditoria_id": f"audit_{cliente_id}"
            }
        else:
            auditoria_service.registrar_operacao(
                tipo_acao=TipoAcao.ALTERAR,
                modulo=ModuloSistema.USUARIOS,
                usuario_id=user_data['id'],
                usuario_nome=user_data['username'],
                acao="editar_cliente",
                recurso_id=cliente_id,
                sucesso=False,
                mensagem="Falha ao atualizar cliente"
            )
            return service.atualizar(cliente_id, nome, cpf_cnpj, telefone, email, cidade, estado, area_total_hectares)
            
    except Exception as e:
        # Fallback para comportamento original
        return service.atualizar(cliente_id, nome, cpf_cnpj, telefone, email, cidade, estado, area_total_hectares)


@router.post("/{cliente_id}/excluir")
async def excluir_cliente_route(
    cliente_id: str, 
    justificativa: str = Form(...), 
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Excluir cliente - exige permissão clientes:delete
    """
    # Verificar permissão necessária
    require_permission("clientes:delete")(credentials)
    
    from app.web.auth import get_current_user
    user_data = get_current_user(credentials)
    
    service = ClientesService(db, user_data)
    
    # Registrar auditoria da exclusão
    try:
        from app.services.auditoria_service import AuditoriaPersistenteService
        from core.seguranca.auditoria import TipoAcao, ModuloSistema
        
        auditoria_service = AuditoriaPersistenteService(db)
        resultado = service.excluir(cliente_id, justificativa)
        
        # Se foi bem-sucedido, registrar evento
        if resultado and resultado.get("success"):
            auditoria_service.registrar_operacao_cliente(
                tipo_acao=TipoAcao.EXCLUIR,
                usuario_id=user_data['id'],
                usuario_nome=user_data['username'],
                cliente_id=cliente_id,
                detalhes={
                    'justificativa': justificativa
                }
            )
            
            return {
                "success": True,
                "message": "Cliente excluído com sucesso",
                "client_id": cliente_id,
                "auditoria_id": f"audit_{cliente_id}"
            }
        else:
            auditoria_service.registrar_operacao(
                tipo_acao=TipoAcao.EXCLUIR,
                modulo=ModuloSistema.USUARIOS,
                usuario_id=user_data['id'],
                usuario_nome=user_data['username'],
                acao="excluir_cliente",
                recurso_id=cliente_id,
                sucesso=False,
                mensagem=resultado.get("detail", "Falha ao excluir cliente") if resultado else "Falha ao excluir cliente"
            )
            return resultado
            
    except Exception as e:
        # Fallback para comportamento original
        return service.excluir(cliente_id, justificativa)
