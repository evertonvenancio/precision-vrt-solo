"""
Precision VRT Solo - Rotas de Autenticação

Responsabilidade exclusiva: receber requisição → chamar service → retornar response.
Zero consulta ao banco. Zero regra de negócio.
"""

from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
import os

# Importação do serviço de autenticação
from app.services.auth_service import AuthService, verificar_senha
import secrets

# Inicialização do serviço de autenticação
# ATENÇÃO: Não criamos sessão de DB no nível do módulo.
# O AuthService cria sua própria sessão por requisição (lazy) para evitar
# sessões SQLite obsoletas entre requests.
try:
    auth_service = AuthService()
    AUTH_SERVICE_AVAILABLE = True
except Exception as e:
    print(f"[ERROR] Erro ao inicializar AuthService: {e}")
    auth_service = None
    AUTH_SERVICE_AVAILABLE = False

router = APIRouter()
from app.template_config import templates  # compartilhado - globals de RBAC

# Sistema de autenticação
# Usa auto_error=False para permitir login via cookie sem header obrigatório
security = HTTPBearer(auto_error=False)


def get_token_from_cookie(request) -> str:
    """Extrai o token JWT do cookie access_token."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    return token


# Wrapper para autenticação que tenta cookie primeiro
def get_current_user_fallback(request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Tenta obter usuário primeiro do cookie, depois do header.
    """
    # Tentar cookie primeiro
    try:
        token = request.cookies.get("access_token")
        if token and auth_service:
            payload = auth_service.verify_token(token)
            if payload:
                # Buscar dados do usuário
                from db.database import SessionLocal
                db = SessionLocal()
                try:
                    from sqlalchemy import text
                    result = db.execute(text('SELECT nome, email, ativo FROM usuarios WHERE id = :user_id'), 
                                       {'user_id': payload['sub']})
                    user_info = result.fetchone()
                    if user_info:
                        return {
                            "id": payload['sub'],
                            "username": payload.get('username', payload['sub']),
                            "nome": user_info[0],
                            "email": user_info[1],
                            "role": payload.get('role', 'user'),
                            "permissions": payload.get('permissions', []),
                            "ativo": user_info[2]
                        }
                finally:
                    db.close()
    except Exception:
        pass
    
    # Se cookie falhou, usar fallback original
    return get_current_user(credentials)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Obtém usuário atual a partir do token JWT.
    Valida token, expiração, usuário ativo e retorna dados completos.
    """
    if not auth_service:
        raise HTTPException(status_code=401, detail="Sistema de autenticação não disponível")
    
    # 1. Validar token JWT
    user = auth_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
    # 2. Validar que usuário está ativo no banco
    try:
        from db.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        result = db.execute(text('SELECT ativo FROM usuarios WHERE id = :user_id LIMIT 1'), 
                           {'user_id': user['id']})
        user_status = result.fetchone()
        db.close()
        
        if not user_status or not user_status[0]:
            raise HTTPException(status_code=401, detail="Usuário desativado no sistema")
            
    except Exception as e:
        print(f"[ERROR] Erro ao verificar status do usuário: {e}")
        raise HTTPException(status_code=401, detail="Erro ao validar usuário")
    
    return user

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Página de login com formulário seguro.
    """
    return templates.TemplateResponse(request=request, name="login.html", context={
        "error": None,
        "username": ""
    })

@router.post("/login")
async def processar_login(
    request: Request,
    usuario: str = Form(...),
    senha: str = Form(...),
    remember_me: bool = Form(False)
):
    """
    Processa login com autenticação segura.
    
    Args:
        usuario: Nome de usuário
        senha: Senha do usuário
        remember_me: Manter sessão ativa
        
    Returns:
        Redirecionamento para dashboard ou erro
    """
    if not auth_service:
        raise HTTPException(status_code=503, detail="Sistema de autenticação não disponível")
    
    # Validação básica
    if not usuario or not senha:
        raise HTTPException(status_code=400, detail="Usuario e senha sao obrigatorios")
    
    # Autenticar usuário
    user_data = auth_service.authenticate_user(usuario, senha)
    
    if not user_data:
        # Login falhou - registrar tentativa
        print(f"[ERROR] Falha na autenticação para: {usuario}")
        
        # Registrar evento de falha no login
        try:
            from db.database import SessionLocal
            db = SessionLocal()
            from app.services.auditoria_service import AuditoriaPersistenteService
            
            # Obter IP da requisição
            import socket
            client_ip = request.client.host
            
            auditoria_service = AuditoriaPersistenteService(db)
            auditoria_service.registrar_login(
                usuario_id=0,  # Usuário não encontrado
                usuario_nome=usuario,
                ip_origem=client_ip,
                sucesso=False,
                mensagem="Usuário ou senha incorretos"
            )
            db.close()
        except Exception as e:
            print(f"Erro ao registrar auditoria de falha: {e}")
        
        return templates.TemplateResponse(request=request, name="login.html", context={
            "error": "Usuário ou senha incorretos",
            "username": usuario
        })
    
    # Gerar tokens
    access_token = auth_service.create_access_token(user_data)
    
    # Gerar refresh token se solicitado
    refresh_token = None
    if remember_me:
        refresh_token = auth_service.create_refresh_token(user_data)
    
    # Criar resposta
    response = RedirectResponse(url="/web/dashboard", status_code=303)
    
    # Armazenar token no cookie seguro (melhor que localStorage)
    import secrets
    session_id = secrets.token_urlsafe(32)
    
    # Configurar cookie seguro
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Permitir HTTP para desenvolvimento
        samesite="lax",
        path="/",  # Cookie válido para toda a aplicação
        max_age=108000 if remember_me else 1800  # 30 horas ou 30 minutos
    )
    
    # Armazenar refresh token se existir
    if refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # Permitir HTTP para desenvolvimento
            samesite="lax",
            max_age=604800  # 7 dias
        )

    # Armazenar session_id para controle de sessão
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,  # Permitir HTTP para desenvolvimento
        samesite="lax"
    )
    
    # Registrar evento de login bem-sucedido
    try:
        from db.database import SessionLocal
        db = SessionLocal()
        from app.services.auditoria_service import AuditoriaPersistenteService
        
        # Obter IP da requisição
        import socket
        client_ip = request.client.host
        
        auditoria_service = AuditoriaPersistenteService(db)
        auditoria_service.registrar_login(
            usuario_id=user_data['id'],
            usuario_nome=user_data['username'],
            ip_origem=client_ip,
            sucesso=True,
            mensagem="Login bem-sucedido"
        )
        db.close()
    except Exception as e:
        print(f"Erro ao registrar auditoria de sucesso: {e}")
    
    # Log de sucesso
    print(f"[OK] Login bem-sucedido para: {user_data['username']} (role: {user_data['role']})")
    
    return response

@router.post("/logout")
async def logout(request: Request):
    """
    Realiza logout seguro.
    """
    response = RedirectResponse(url="/login", status_code=303)
    
    # Obter tokens dos cookies
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    # Obter usuário atual para auditoria
    current_user = None
    if access_token and auth_service:
        try:
            user_info = auth_service.get_current_user(access_token)
            if user_info:
                current_user = user_info
        except Exception:
            pass
    
    # Revogar tokens se serviço disponível
    if auth_service and access_token:
        auth_service.logout_user(access_token, refresh_token)
    
    # Limpar cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("session_id")
    
    # Registrar evento de logout
    try:
        from db.database import SessionLocal
        db = SessionLocal()
        from app.services.auditoria_service import AuditoriaPersistenteService
        
        auditoria_service = AuditoriaPersistenteService(db)
        auditoria_service.registrar_operacao(
            tipo_acao=core.seguranca.auditoria.TipoAcao.EXCLUIR,
            modulo=core.seguranca.auditoria.ModuloSistema.USUARIOS,
            usuario_id=current_user['id'] if current_user else 0,
            usuario_nome=current_user['username'] if current_user else "desconhecido",
            acao="logout",
            sucesso=True,
            mensagem="Logout realizado"
        )
        db.close()
    except Exception as e:
        print(f"Erro ao registrar auditoria de logout: {e}")
    
    print("👋 Logout realizado")
    return response

@router.get("/current-user")
async def get_current_user_endpoint(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Obtém usuário atual via endpoint de API.
    """
    user = get_current_user(credentials)
    return {
        "success": True,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "nome": user.get("nome", user["username"]),  # Adicionar nome real
            "email": user["email"],
            "role": user["role"],
            "permissions": user["permissions"]
        }
    }

@router.get("/me")
async def get_current_user_complete(request: Request):
    """
    Endpoint de identidade completa do usuário autenticado.
    Aceita token via cookie (access_token) ou header Authorization.
    """
    # Tentar cookie primeiro
    token = request.cookies.get("access_token")
    if not token:
        # Fallback para header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token or not auth_service:
        return {"success": False, "error": "Não autenticado"}

    user = auth_service.get_current_user(token)
    if not user:
        return {"success": False, "error": "Token inválido ou expirado"}

    # Obter dados adicionais do banco
    from db.database import SessionLocal
    db = SessionLocal()

    try:
        from sqlalchemy import text
        result = db.execute(text('SELECT nome, email, ativo FROM usuarios WHERE id = :user_id'),
                           {'user_id': user['id']})
        user_info = result.fetchone()

        if user_info:
            return {
                "success": True,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "nome": user_info[0],  # Nome real do banco
                    "email": user_info[1],  # Email real do banco
                    "role": user["role"],
                    "permissions": user["permissions"],
                    "ativo": user_info[2],  # Status no banco
                    "session": {
                        "authenticated": True,
                        "expires_at": user.get("exp"),
                        "issued_at": user.get("iat")
                    }
                }
            }
        else:
            return {
                "success": False,
                "error": "Usuário não encontrado no banco"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao obter dados do usuário: {str(e)}"
        }
    finally:
        db.close()

@router.get("/user-role")
async def get_user_role(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Obtém papel do usuário atual.
    """
    user = get_current_user(credentials)
    return {
        "success": True,
        "role": user["role"]
    }

@router.get("/check-auth")
async def check_auth_status(request: Request):
    """
    Verifica status de autenticação.
    """
    try:
        # Verificar se usuário está logado via cookie
        access_token = request.cookies.get("access_token")
        if not access_token:
            return {"authenticated": False}
        
        # Verificar token se serviço disponível
        if auth_service:
            payload = auth_service.verify_token(access_token)
            if payload:
                return {
                    "authenticated": True,
                    "user": {
                        "username": payload.get("sub"),
                        "role": payload.get("role"),
                        "permissions": payload.get("permissions", [])
                    }
                }
        
        return {"authenticated": False}
        
    except Exception as e:
        print(f"[ERROR] Erro ao verificar autenticação: {str(e)}")
        return {"authenticated": False}

@router.post("/refresh-token")
async def refresh_token_endpoint(request: Request):
    """
    Renova token de acesso usando refresh token.
    """
    if not auth_service:
        raise HTTPException(status_code=503, detail="Sistema de autenticação não disponível")
    
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token não fornecido")
    
    # Gerar novo token de acesso
    new_access_token = auth_service.refresh_access_token(refresh_token)
    if not new_access_token:
        raise HTTPException(status_code=401, detail="Refresh token inválido ou expirado")
    
    # Criar resposta com novo token
    response = JSONResponse({"success": True, "message": "Token renovado"})
    
    # Atualizar cookie com novo token
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=1800  # 30 minutos
    )
    
    print("[OK] Token de acesso renovado")
    return response

@router.get("/permissions")
async def get_user_permissions(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Obtém permissões do usuário atual.
    """
    user = get_current_user(credentials)
    return {
        "success": True,
        "permissions": user["permissions"]
    }

@router.get("/api/me")
async def api_me(request: Request):
    """
    Endpoint API para obter informações do usuário autenticado via cookie.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    
    # Reutilizar a mesma lógica de decode que já existe no sistema
    if not auth_service:
        raise HTTPException(status_code=503, detail="Sistema de autenticação não disponível")
    
    try:
        # Decodificar JWT e retornar dados do usuário
        payload = auth_service.verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Token inválido ou expirado")
        
        # Buscar dados completos do usuário
        from db.database import SessionLocal
        db = SessionLocal()
        try:
            from sqlalchemy import text
            result = db.execute(text('SELECT nome, email, ativo FROM usuarios WHERE id = :user_id'), 
                               {'user_id': payload['sub']})
            user_info = result.fetchone()
            
            if user_info:
                return {
                    "nome": user_info[0],
                    "login": payload['sub'],
                    "role": payload.get('role', 'user'),
                    "email": user_info[1],
                    "ativo": user_info[2]
                }
            else:
                raise HTTPException(status_code=401, detail="Usuário não encontrado")
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Erro na autenticação: {str(e)}")

# Endpoint para informações do sistema (sem autenticação)
@router.get("/system-info")
async def system_info():
    """
    Retorna informações do sistema de autenticação.
    """
    return {
        "auth_service_available": AUTH_SERVICE_AVAILABLE,
        "users_count": auth_service.get_user_count() if auth_service else 0,
        "algorithms": ["HS256"] if auth_service else [],
        "token_expiry_minutes": auth_service.access_token_expire_minutes if auth_service else 30,
        "refresh_token_expiry_days": auth_service.refresh_token_expire_days if auth_service else 7,
        "security_mode": "production" if AUTH_SERVICE_AVAILABLE else "demo_mode"
    }


@router.post("/verify-password", response_class=JSONResponse)
async def verify_security_password(
    request: Request,
    password: str = Form(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Popup de Re-Autenticação de Segurança.
    Verifica a senha do usuário atual para autorizar operações sensíveis
    (sobrescrita de preço, exceção de desconto, alteração de metodologia, deleção).
    Retorna {success: bool, message: str} para uso em modais de segurança.
    """
    from app.services.auditoria_service import AuditoriaPersistenteService
    from core.seguranca.auditoria import TipoAcao, ModuloSistema

    user = get_current_user(credentials)

    from db.database import SessionLocal
    db = SessionLocal()
    try:
        # Buscar hash da senha do usuário
        from sqlalchemy import text
        result = db.execute(
            text("SELECT senha_hash FROM usuarios WHERE id = :user_id LIMIT 1"),
            {"user_id": user["id"]}
        )
        row = result.fetchone()
        if not row:
            return JSONResponse({"success": False, "message": "Usuário não encontrado"}, status_code=404)

        # Verificar senha via PBKDF2
        if verificar_senha(password, row[0]):
            # Log de sucesso na re-autenticação
            try:
                audit = AuditoriaPersistenteService(db)
                audit.registrar_operacao(
                    tipo_acao=TipoAcao.ALTERAR,
                    modulo=ModuloSistema.USUARIOS,
                    usuario_id=user["id"],
                    usuario_nome=user["username"],
                    acao="re_autenticacao_seguranca",
                    sucesso=True,
                    mensagem="Re-autenticação de segurança bem-sucedida"
                )
            except Exception as e:
                print(f"[WARN] Erro ao registrar auditoria de re-auth: {e}")
            return JSONResponse({"success": True, "message": "Senha confirmada"})
        else:
            # Log de falha na re-autenticação
            try:
                audit = AuditoriaPersistenteService(db)
                audit.registrar_operacao(
                    tipo_acao=TipoAcao.ALTERAR,
                    modulo=ModuloSistema.USUARIOS,
                    usuario_id=user["id"],
                    usuario_nome=user["username"],
                    acao="re_autenticacao_seguranca",
                    sucesso=False,
                    mensagem="Senha incorreta na re-autenticação de segurança"
                )
            except Exception as e:
                print(f"[WARN] Erro ao registrar auditoria de re-auth: {e}")
            return JSONResponse({"success": False, "message": "Senha incorreta"}, status_code=401)
    except Exception as e:
        return JSONResponse({"success": False, "message": f"Erro: {str(e)}"}, status_code=500)
    finally:
        db.close()
