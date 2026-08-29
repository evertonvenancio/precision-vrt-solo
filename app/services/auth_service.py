"""
Precision VRT Solo - Serviço de Autenticação
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import hashlib
import secrets
import os
import binascii
import jwt
from jwt.exceptions import PyJWTError
from sqlalchemy.orm import Session
from sqlalchemy import text

from models.usuario import Usuario


def hash_senha(senha: str) -> str:
    """Gera hash PBKDF2 da senha. Formato: salt_hex:hash_hex"""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        100000
    )
    return f"{binascii.hexlify(salt).decode()}:{binascii.hexlify(key).decode()}"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Verifica senha contra hash PBKDF2 ou SHA-256 legado."""
    try:
        if ":" in senha_hash:
            salt_hex, key_hash = senha_hash.split(":")
            # CORREÇÃO: decodificar salt de hex para bytes
            salt_bytes = binascii.unhexlify(salt_hex)
            computed_key = hashlib.pbkdf2_hmac(
                "sha256",
                senha.encode("utf-8"),
                salt_bytes,
                100000
            )
            return key_hash == computed_key.hex()
        else:
            # Fallback SHA-256 legado (remover após reset de senhas)
            return hashlib.sha256(senha.encode("utf-8")).hexdigest() == senha_hash
    except Exception:
        return False


class AuthService:
    """
    Serviço central de autenticação.
    """

    def __init__(self, db_session: Session = None, secret_key: str = None):
        self.secret_key = secret_key or "precision_vrt_solo_secret_key_2024"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        self.db_session = db_session
        self.token_blacklist = set()
        print("[OK] AuthService inicializado com banco oficial")

    def _get_db_session(self):
        """
        Cria uma nova sessão de banco por chamada.
        Isso evita a reutilização de sessões SQLite entre requests,
        que causavam 'SQLite objects created in a thread can only be used
        in that same thread' e sessões obsoletas no nível módulo.
        """
        from db.database import SessionLocal
        return SessionLocal()

    def autenticar(self, usuario: str, senha: str) -> Optional[Usuario]:
        """Autentica um usuário pelo login e senha. Retorna o modelo ORM ou None."""
        db = self._get_db_session()
        try:
            user = db.query(Usuario).filter(Usuario.login == usuario).first()
            if not user or not verificar_senha(senha, user.senha_hash or ""):
                return None
            return user
        finally:
            if db != self.db_session:
                db.close()

    def buscar_usuario(self, usuario: str) -> Optional[Usuario]:
        """Busca um usuário pelo login."""
        db = self._get_db_session()
        try:
            return db.query(Usuario).filter(Usuario.login == usuario).first()
        finally:
            if db != self.db_session:
                db.close()

    def authenticate_user(
        self, username: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """Autentica usuário e retorna dados dict."""
        print(f"[DEBUG] Tentativa de autenticação para: {username}")

        db = self._get_db_session()
        try:
            result = db.execute(
                text(
                    "SELECT id, login, senha_hash, ativo, criado_em "
                    "FROM usuarios WHERE login = :username"
                ),
                {"username": username},
            )
            usuario_data = result.fetchone()

            if not usuario_data:
                print(f"[ERROR] Usuário não encontrado: {username}")
                return None

            if not usuario_data[3]:
                print(f"[ERROR] Usuário inativo: {username}")
                return None

            if not verificar_senha(password, usuario_data[2] or ""):
                print(f"[ERROR] Senha incorreta para: {username}")
                return None

            user_data = {
                "id": usuario_data[0],
                "username": usuario_data[1],
                "email": None,
                "role": "admin",
                "permissions": [
                    "dashboard:read",
                    "dashboard:write",
                    "usuarios:read",
                    "usuarios:write",
                ],
                "nome": username,
            }

            print(f"[OK] Usuário autenticado: {username} (perfil: {user_data['role']})")
            return user_data

        except Exception as e:
            print(f"[ERROR] Erro na autenticação: {str(e)}")
            return None
        finally:
            if db != self.db_session:
                db.close()

    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        expire = datetime.utcnow() + timedelta(
            minutes=self.access_token_expire_minutes
        )
        payload = {
            "sub": user_data["username"],
            "user_id": user_data["id"],
            "role": user_data["role"],
            "permissions": user_data.get("permissions", []),
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        print(f"[OK] Token de acesso gerado para: {user_data['username']}")
        return token

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            if token in self.token_blacklist:
                return None
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return payload
        except PyJWTError:
            return None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Busca usuário pelo login SEM verificar senha (para uso pós-auth)."""
        db = self._get_db_session()
        try:
            result = db.execute(
                text(
                    "SELECT id, login, senha_hash, ativo, criado_em "
                    "FROM usuarios WHERE login = :username"
                ),
                {"username": username},
            )
            row = result.fetchone()
            if not row or not row[3]:
                return None
            return {
                "id": row[0],
                "username": row[1],
                "email": None,
                "role": "admin",
                "permissions": [
                    "dashboard:read",
                    "dashboard:write",
                    "usuarios:read",
                    "usuarios:write",
                ],
                "nome": row[1],
            }
        finally:
            if db != self.db_session:
                db.close()

    def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        payload = self.verify_token(token)
        if not payload:
            return None
        return self.get_user_by_username(payload["sub"])

    def logout_user(self, access_token: str, refresh_token: str = None):
        self.token_blacklist.add(access_token)
        if refresh_token:
            self.token_blacklist.add(refresh_token)

    def is_token_blacklisted(self, token: str) -> bool:
        return token in self.token_blacklist

    def create_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """Gera um refresh token com expiração estendida (7 dias)."""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        payload = {
            "sub": user_data["username"],
            "user_id": user_data["id"],
            "role": user_data["role"],
            "permissions": user_data.get("permissions", []),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Renova um access token usando um refresh token válido."""
        try:
            if refresh_token in self.token_blacklist:
                return None
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "refresh":
                return None
            # Buscar dados atualizados do usuário
            user_data = self.get_user_by_username(payload["sub"])
            if not user_data:
                return None
            return self.create_access_token(user_data)
        except PyJWTError:
            return None

    def get_user_count(self) -> int:
        """Retorna a contagem total de usuários ativos no sistema."""
        db = self._get_db_session()
        try:
            result = db.execute(text("SELECT COUNT(*) FROM usuarios WHERE ativo = 1"))
            return result.scalar() or 0
        except Exception:
            return 0
        finally:
            if db != self.db_session:
                db.close()
