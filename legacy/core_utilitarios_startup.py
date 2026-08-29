"""
Precision VRT Solo - Inicialização da Aplicação
Registro de eventos de startup e setup do ambiente.
"""
import logging
import uuid

from fastapi import FastAPI

from db.database import Base, engine, SessionLocal
from models.usuario import Usuario
from ..seguranca.seguranca import hash_senha


def startup_event():
    """Cria tabelas e usuário admin padrão no startup."""
    logging.info("Iniciando criacao de tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    if not db.query(Usuario).filter(Usuario.login == "admin").first():
        novo_admin = Usuario(id=str(uuid.uuid4()), login="admin", senha_hash=hash_senha("admin123"))
        db.add(novo_admin)
        db.commit()
        logging.info("Usuario admin criado.")
    db.close()
    logging.info("Tabelas verificadas/criadas com sucesso.")


def registrar_startup(app: FastAPI):
    """Registra o evento de startup na aplicação FastAPI."""
    @app.on_event("startup")
    def _startup():
        startup_event()
