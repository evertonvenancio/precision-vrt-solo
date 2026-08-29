"""
ConfiguraÃ§Ã£o central de banco de dados para o projeto Precision VRT Solo.

Fornece:
- Engine SQLAlchemy 2.0 (SQLite)
- SessionLocal para criaÃ§Ã£o de sessÃµes
- Base declarativa para modelos ORM
- get_db() como dependÃªncia de injeÃ§Ã£o para FastAPI
"""

import logging
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURAÃ‡ÃƒO DA ENGINE
# =============================================================================

SQLALCHEMY_DATABASE_URL: str = "sqlite:///./precision_vrt.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,  # True para debug de queries SQL
)

# =============================================================================
# SESSION LOCAL
# =============================================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# =============================================================================
# BASE DECLARATIVA
# =============================================================================

class Base(DeclarativeBase):
    """Base declarativa para todos os modelos SQLAlchemy 2.0."""
    pass


# =============================================================================
# DEPENDÃŠNCIA FASTAPI
# =============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    DependÃªncia de injeÃ§Ã£o para obter sessÃ£o do banco no FastAPI.

    Yields:
        Session: SessÃ£o SQLAlchemy ativa.

    Garante fechamento da sessÃ£o ao final da requisiÃ§Ã£o,
    mesmo em caso de exceÃ§Ã£o.
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
