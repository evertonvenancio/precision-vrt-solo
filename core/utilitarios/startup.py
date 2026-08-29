"""
Precision VRT Solo - Inicialização da Aplicação
Registro de eventos de startup e setup do ambiente.
"""

import logging
import uuid

from fastapi import FastAPI
from db.database import Base, engine, SessionLocal
from models.usuario import Usuario
from core.seguranca.seguranca import hash_senha


def startup_event():
    """Cria tabelas no banco de dados."""
    logging.info("Iniciando criacao de tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    logging.info("Tabelas verificadas/criadas com sucesso.")


def registrar_startup(app: FastAPI):
    """Registra o evento de startup na aplicação FastAPI."""
    @app.on_event("startup")
    def _startup():
        startup_event()