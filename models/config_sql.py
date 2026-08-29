"""
Precision VRT Solo — SQLAlchemy ORM Models for Configurações

Maps the key-value config schema to SQLAlchemy models for real persistence.
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ConfigSistema(Base):
    """
    Tabela key-value de configurações do sistema.

    Schema esperado no SQLite:
    - id (PK, String 36)
    - chave (String, not null)
    - valor (String, nullable)
    - metodologia_padrao_id (String, nullable)
    - criado_em (DateTime, default now)
    """
    __tablename__ = "config_sistema"

    id = Column(String(36), primary_key=True)
    chave = Column(String(100), nullable=False)
    valor = Column(String(500), nullable=True)
    metodologia_padrao_id = Column(String(50), nullable=True)
    criado_em = Column(DateTime, nullable=False)