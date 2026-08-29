"""
Precision VRT Solo - Serviço de Autenticação

Responsabilidade exclusiva: regras de negócio de autenticação.
Zero consulta direta ao banco. Zero endpoints web.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import os
import hashlib
import secrets
from cryptography.fernet import Fernet
import jwt
from jwt.exceptions import PyJWTError
from passlib.hash import pbkdf2_sha256

class AuthService:
    """
    Serviço de Autenticação oficial do Precision VRT Solo.
    
    Responsabilidades:
    - Validação de credenciais
    - Geração e validação de JWT
    - Gestão de sessão
    - Verificação de permissões
    """
    
    def __init__(self, secret_key: str = None):
        # Segredo para JWT - usar variável de ambiente em produção
        self.secret_key = secret_key or "precision_vrt_solo_secret_key_2024"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        
        # Criptografia para armazenamento seguro de dados sensíveis
        self.fernet_key = Fernet.generate_key()
        self.cipher = Fernet(self.fernet_key)
        
        # Banco de dados de usuário - modo demonstrativo
        # EM PRODUÇÃO: substituir por integração real com banco de dados
        self.users_db = {}
        
        # Em modo desenvolvimento, inicializar com dados de demonstração
        if os.getenv('DEMO_MODE', 'false').lower() == 'true':
            self._init_demo_users()
    
    def _init_demo_users(self):
        """Inicializar usuários de demonstração - SOMENTE EM MODO DE DESENVOLVIMENTO"""
        if not self.users_db:  # Só inicializar se vazio
            self.users_db = {
                "demo_user": {
                    "id": 1,
                    "username": "demo_user",
                    "email": "demo@precisionvrt.com.br",
                    "password_hash": self._hash_password("demo_password"),
                    "role": "demo",
                    "permissions": ["dashboard:read"],
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "is_active": True
                }
            }
    
    def _hash_password(self, password: str) -> str:
        """
        Gera hash seguro da senha usando PBKDF2.
        
        Args:
            password: Senha em texto plano
            
        Returns:
            Hash da senha
        """
        salt = secrets.token_hex(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}:{key.hex()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verifica se a senha corresponde ao hash.
        
        Args:
            password: Senha em texto plano
            password_hash: Hash armazenado
            
        Returns:
            True se senha correta, False caso contrário
        """
        try:
            salt, key_hash = password_hash.split(':')
            key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return key_hash == key.hex()
        except Exception:
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica usuário e retorna dados básicos.
        
        Args:
            username: Nome de usuário
            password: Senha
            
        Returns:
            Dados do usuário se autenticado, None caso contrário
        """
        print(f"🔍 Tentativa de autenticação para: {username}")
        
        # Verificar se usuário existe
        user_data = self.users_db.get(username.lower())
        if not user_data:
            print(f"❌ Usuário não encontrado: {username}")
            return None
        
        # Verificar se usuário está ativo
        if not user_data.get('is_active', False):
            print(f"❌ Usuário inativo: {username}")
            return None
        
        # Verificar senha
        if not self._verify_password(password, user_data['password_hash']):
            print(f"❌ Senha incorreta para: {username}")
            return None
        
        # Retornar dados básicos do usuário (sem hash de senha)
        return {
            'id': user_data['id'],
            'username': user_data['username'],
            'email': user_data.get('email'),
            'role': user_data['role'],
            'permissions': user_data.get('permissions', [])
        }
    
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
            
            # Gerar novo token de acesso
            user_data = self.users_db.get(payload['sub'])
            if user_data:
                return self.create_access_token(user_data)
            else:
                print(f"❌ Usuário não encontrado: {payload['sub']}")
                return None
                
        except PyJWTError:
            print(f"❌ Refresh token inválido")
            return None
    
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
        
        username = payload.get('sub')
        user_data = self.users_db.get(username)
        
        if not user_data:
            print(f"❌ Usuário não encontrado no banco: {username}")
            return None
        
        return {
            'id': user_data['id'],
            'username': user_data['username'],
            'email': user_data.get('email'),
            'role': user_data['role'],
            'permissions': user_data.get('permissions', [])
        }
    
    def has_permission(self, user_data: Dict[str, Any], permission: str) -> bool:
        """
        Verifica se usuário tem permissão específica.
        
        Args:
            user_data: Dados do usuário
            permission: Permissão a verificar
            
        Returns:
            True se tem permissão, False caso contrário
        """
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