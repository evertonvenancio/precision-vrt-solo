"""
Precision VRT Solo - Serviço do Módulo Autenticação
Toda consulta ao banco e regra de negócio centralizada aqui.
"""
from sqlalchemy.orm import Session

from core.seguranca.seguranca import hash_senha
from models.usuario import Usuario


class AuthService:
    """
    Serviço central do módulo Autenticação.
    Responsável por toda consulta ao banco e regra de negócio.
    """

    def __init__(self, db: Session):
        self.db = db

    def autenticar(self, usuario: str, senha: str) -> Usuario:
        """Autentica um usuário pelo login e senha."""
        user = self.db.query(models.usuario.Usuario).filter(Usuario.login == usuario).first()
        if not user or user.senha_hash != hash_senha(senha):
            return None
        return user

    def buscar_usuario(self, usuario: str) -> Usuario:
        """Busca um usuário pelo login."""
        return self.db.query(models.usuario.Usuario).filter(Usuario.login == usuario).first()
