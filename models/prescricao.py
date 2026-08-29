"""
Precision VRT Solo - Modelo Prescricao SQLAlchemy
"""

from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.sql import func
from db.database import Base
import uuid


class Prescricao(Base):
    """
    Modelo de dados da Prescricao usando SQLAlchemy.
    Mapeia a tabela 'prescricao' existente do banco de dados.
    """
    
    __tablename__ = "prescricao"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    cliente_id = Column(String(36), index=True)
    talhao_id = Column(String(36), index=True)
    cultura = Column(String(50))
    safra = Column(String(20))
    area_hectares = Column(Float)
    status = Column(String(30))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self) -> dict:
        """Converte para dicionário compatível com frontend."""
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "talhao_id": self.talhao_id,
            "cultura": self.cultura,
            "safra": self.safra,
            "area_hectares": float(self.area_hectares) if self.area_hectares else 0,
            "status": self.status,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }