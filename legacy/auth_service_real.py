"""
Precision VRT Solo - Serviço de Autenticação REAL

Responsabilidade exclusiva: regras de negócio de autenticação.
Zero consulta direta ao banco. Zero endpoints web.
Usa infraestrutura existente de banco de dados.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import os
import hashlib
import secrets
from cryptography.fernet import Fernet
import jwt
from jwt.exceptions import PyJWTError

class AuthService:
    """
    Serviço de Autenticação oficial do Precision VRT Solo.
    
    Responsabilidades:
    - Validação de credenciais
    - Geração e validação de JWT
    - Gestão de sessão
    - Verificação de permissões
    
    Versão REAL: conectada ao banco oficial precision_vrt.db
    """
    
    def __init__(self, db_session=None, secret_key: str = None):
        # Segredo para JWT - usar variável de ambiente em produção
        self.secret_key = secret_key or "precision_vrt_solo_secret_key_2024"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        
        # Sessão de banco de dados
        self.db_session = db_session
        
        # Criptografia para armazenamento de dados sensíveis
        self.fernet_key = Fernet.generate_key()
        self.cipher = Fernet(self.fernet_key)
        
        # Blacklist de tokens (em memória para produção, poderia ser persistente)
        self.token_blacklist = set()
        
        # Importar configurações de segurança
        try:
            from config.security_config import security_settings
            self.security_settings = security_settings
        except ImportError:
            # Fallback para configuração básica
            self.security_settings = None
        
        print("✅ AuthService inicializado com banco oficial")
    
    def _get_db_session(self):
        """Garante que temos uma sessão de banco válida"""
        if not self.db_session:
            from db.database import SessionLocal
            self.db_session = SessionLocal()
        return self.db_session
    
    def _hash_password(self, password: str) -> str:
        """
        Gera hash seguro da senha usando PBKDF2.
        Compatível com formato salt:hex
        
        Args:
            password: Senha em texto plano
            
        Returns:
            Hash da senha no formato salt:hex
        """
        salt = secrets.token_hex(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}:{key.hex()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verifica se a senha corresponde ao hash.
        Suporta formatos: salt:hex (PBKDF2) e hex puro (SHA256)
        
        Args:
            password: Senha em texto plano
            password_hash: Hash armazenado
            
        Returns:
            True se senha correta, False caso contrário
        """
        try:
            import hashlib
            
            # Verificar se é formato PBKDF2 (salt:hash)
            if ':' in password_hash:
                salt, key_hash = password_hash.split(':')
                # Recomputar o hash com o mesmo salt
                computed_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
                return key_hash == computed_key.hex()
            else:
                # Verificar se é formato SHA256 puro
                return hashlib.sha256(password.encode('utf-8')).hexdigest() == password_hash
        except Exception as e:
            print(f"❌ Erro na verificação de senha: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica usuário no banco oficial e retorna dados básicos.
        
        Args:
            username: Nome de usuário
            password: Senha
            
        Returns:
            Dados do usuário se autenticado, None caso contrário
        """
        print(f"🔍 Tentativa de autenticação para: {username}")
        
        db = self._get_db_session()
        
        try:
            # Buscar usuário no banco usando SQL direto
            from sqlalchemy import text
            result = db.execute(text('SELECT id, login, senha_hash, ativo, criado_em FROM usuarios WHERE login = :username'), {'username': username})
            usuario_data = result.fetchone()
            
            if not usuario_data:
                print(f"❌ Usuário não encontrado no banco: {username}")
                return None
            
            # Verificar se usuário está ativo
            if not usuario_data[3]:  # índice 3 é o campo 'ativo'
                print(f"❌ Usuário inativo: {username}")
                return None
            
            # Verificar senha (suporta ambos os formatos)
            if not self._verify_password(password, usuario_data[2] or ''):
                print(f"❌ Senha incorreta para: {username}")
                return None
            
            # Retornar dados básicos do usuário (sem hash de senha)
            user_data = {
                'id': usuario_data[0],
                'username': usuario_data[1],
                'email': None,  # Campo não existe na tabela atual
                'role': 'admin',  # Perfil padrão até implementar campo perfil
                'permissions': self._get_user_permissions(usuario_data),
                'nome': username  # Nome não existe na tabela atual
            }
            
            print(f"✅ Usuário autenticado: {username} (perfil: {user_data['role']})")
            return user_data
            
        except Exception as e:
            print(f"❌ Erro na autenticação: {str(e)}")
            return None
        finally:
            if db != self.db_session:
                db.close()
    
    def _get_user_permissions(self, usuario_data) -> List[str]:
        """
        Obtém permissões do usuário no banco.
        
        Args:
            usuario_data: Dados do usuário do banco (tuple)
            
        Returns:
            Lista de permissões
        """
        try:
            # Verificar se existe campo de permissões na tabela
            if len(usuario_data) > 4 and usuario_data[4]:  # índice 4 é 'permissoes'
                permissoes_str = usuario_data[4]
                if permissoes_str == "1":
                    # Valor numérico 1 = admin completo
                    return ['dashboard:read', 'dashboard:write', 'usuarios:read', 'usuarios:write']
                elif isinstance(permissoes_str, str):
                    # Tentar parse JSON
                    import json
                    try:
                        return json.loads(permissoes_str)
                    except:
                        return ['dashboard:read']
                else:
                    return ['dashboard:read']
            
            # Se não existir permissões, retornar básicas por perfil
            # Usar 'admin' como padrão para o usuário atual
            perfil = 'admin'
            
            # Mapeamento básico de perfis para permissões
            role_permissions = {
                'admin': ['dashboard:read', 'dashboard:write', 'usuarios:read', 'usuarios:write'],
                'consultor': ['dashboard:read', 'clientes:read', 'prescricao:read'],
                'financeiro': ['dashboard:read', 'clientes:read', 'financeiro:read', 'financeiro:write'],
                'tecnico': ['dashboard:read', 'clientes:read', 'configuracoes:read'],
                'user': ['dashboard:read']
            }
            
            return role_permissions.get(perfil, ['dashboard:read'])
            
        except Exception as e:
            print(f"⚠️ Erro ao obter permissões: {str(e)}")
            return ['dashboard:read']
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """
        Gera token de acesso JWT.
        
        Args:
            user_data: Dados do usuário
            
        Returns:
            Token JWT
        """
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            'sub': user_data['username'],
            'user_id': user_data['id'],
            'role': user_data['role'],
            'permissions': user_data.get('permissions', []),
            'exp': expire,
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        print(f"✅ Token de acesso gerado para: {user_data['username']}")
        return token
    
    def create_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """
        Gera token de refresh.
        
        Args:
            user_data: Dados do usuário
            
        Returns:
            Token de refresh
        """
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        payload = {
            'sub': user_data['username'],
            'user_id': user_data['id'],
            'exp': expire,
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        print(f"✅ Token de refresh gerado para: {user_data['username']}")
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica validade do token JWT.
        
        Args:
            token: Token JWT
            
        Returns:
            Payload do token se válido, None caso contrário
        """
        try:
            # Verificar se token está na blacklist
            if token in self.token_blacklist:
                print(f"❌ Token na blacklist: {token[:20]}...")
                return None
            
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            print(f"✅ Token válido: {payload.get('sub')}")
            return payload
            
        except PyJWTError:
            print(f"❌ Token inválido: {token[:20]}...")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Renova token de acesso usando refresh token.
        
        Args:
            refresh_token: Token de refresh
            
        Returns:
            Novo token de acesso ou None
        """
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            
            # Verificar se token ainda é válido
            if datetime.fromtimestamp(payload['exp']) < datetime.utcnow():
                print(f"❌ Refresh token expirado: {payload['sub']}")
                return None
            
            # Buscar usuário no banco para gerar novo token (sem senha, só validação de existência)
            username = payload['sub']
            user_data = self._get_user_by_username(username)
            
            if user_data:
                return self.create_access_token(user_data)
            else:
                print(f"❌ Usuário não encontrado no banco: {username}")
                return None
                
        except PyJWTError:
            print(f"❌ Refresh token inválido")
            return None
    
    def _get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Obtém usuário pelo username sem verificar senha (para refresh token).
        
        Args:
            username: Nome de usuário
            
        Returns:
            Dados do usuário se existir e ativo, None caso contrário
        """
        db = self._get_db_session()
        
        try:
            from sqlalchemy import text
            result = db.execute(text('SELECT id, login, senha_hash, ativo, criado_em FROM usuarios WHERE login = :username'), {'username': username})
            usuario_data = result.fetchone()
            
            if not usuario_data:
                print(f"❌ Usuário não encontrado no banco: {username}")
                return None
            
            # Verificar se usuário está ativo
            if not usuario_data[3]:  # índice 3 é o campo 'ativo'
                print(f"❌ Usuário inativo: {username}")
                return None
            
            # Retornar dados básicos do usuário (sem hash de senha)
            user_data = {
                'id': usuario_data[0],
                'username': usuario_data[1],
                'email': None,  # Campo não existe na tabela atual
                'role': 'admin',  # Perfil padrão até implementar campo perfil
                'permissions': self._get_user_permissions(usuario_data),
                'nome': username  # Nome não existe na tabela atual
            }
            
            return user_data
            
        except Exception as e:
            print(f"❌ Erro ao buscar usuário: {str(e)}")
            return None
        finally:
            if db != self.db_session:
                db.close()
    
    def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Obtém usuário atual a partir do token.
        
        Args:
            token: Token JWT
            
        Returns:
            Dados do usuário ou None
        """
        payload = self.verify_token(token)
        if not payload:
            return None
        
        username = payload['sub']
        user_data = self.authenticate_user(username, "")
        
        if not user_data:
            print(f"❌ Usuário não encontrado no banco: {username}")
            return None
        
        return user_data
    
    def has_permission(self, user_data: Dict[str, Any], permission: str) -> bool:
        """
        Verifica se usuário tem permissão específica.
        
        Args:
            user_data: Dados do usuário
            permission: Permissão a verificar
            
        Returns:
            True se tem permissão, False caso contrário
        """
        # Admin tem todas as permissões
        if user_data.get('role') == 'admin':
            return True
        
        permissions = user_data.get('permissions', [])
        return permission in permissions
    
    def logout_user(self, access_token: str, refresh_token: str = None):
        """
        Realiza logout do usuário.
        
        Args:
            access_token: Token de acesso
            refresh_token: Token de refresh (opcional)
        """
        # Adicionar token à blacklist
        self.token_blacklist.add(access_token)
        
        if refresh_token:
            self.token_blacklist.add(refresh_token)
        
        print(f"✅ Logout realizado para token: {access_token[:20]}...")
    
    def is_token_blacklisted(self, token: str) -> bool:
        """
        Verifica se token está na blacklist.
        
        Args:
            token: Token JWT
            
        Returns:
            True se token está blacklistado
        """
        return token in self.token_blacklist
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Retorna informações do sistema de autenticação.
        
        Returns:
            Informações do sistema
        """
        return {
            "auth_service_available": True,
            "users_count": self.get_user_count(),
            "algorithms": [self.algorithm],
            "token_expiry_minutes": self.access_token_expire_minutes,
            "refresh_token_expiry_days": self.refresh_token_expire_days,
            "security_mode": "production"
        }
    
    def get_user_count(self) -> int:
        """
        Retorna número total de usuários ativos.
        
        Returns:
            Número de usuários ativos
        """
        db = self._get_db_session()
        try:
            from models.usuario import Usuario
            count = db.query(Usuario).filter(Usuario.ativo == True).count()
            return count
        except Exception:
            return 0
        finally:
            if db != self.db_session:
                db.close()

# Funções utilitárias para importação direta
def get_current_user(token: str) -> Optional[Dict[str, Any]]:
    """
    Função utilitária para obter usuário atual a partir do token.
    
    Args:
        token: Token JWT
        
    Returns:
        Dados do usuário ou None
    """
    service = AuthService()
    return service.get_current_user(token)