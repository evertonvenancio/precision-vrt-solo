"""
Precision VRT Solo - Modelo Orcamento SQLAlchemy
"""

from sqlalchemy import Column, String, DateTime, Numeric
from sqlalchemy.sql import func
from db.database import Base
import uuid


class Orcamento(Base):
    """
    Modelo de dados do Orçamento usando SQLAlchemy.
    Mapeia a tabela 'orcamentos' existente do banco de dados.
    """
    
    __tablename__ = "orcamentos"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), index=True, default='default')
    cliente_id = Column(String(36), index=True)
    usuario_id = Column(String(36), index=True)
    data_emissao = Column(DateTime(timezone=True), server_default=func.now())
    valor_total_bruto = Column(Numeric(14, 2))
    desconto_percentual = Column(Numeric(5, 2))
    valor_total_liquido = Column(Numeric(14, 2))
    status = Column(String(30))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def to_dict(self) -> dict:
        """Converte para dicionário compatível com frontend."""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "cliente_id": self.cliente_id,
            "usuario_id": self.usuario_id,
            "data_emissao": self.data_emissao.isoformat() if self.data_emissao else None,
            "valor_total_bruto": float(self.valor_total_bruto) if self.valor_total_bruto else 0,
            "desconto_percentual": float(self.desconto_percentual) if self.desconto_percentual else 0,
            "valor_total_liquido": float(self.valor_total_liquido) if self.valor_total_liquido else 0,
            "status": self.status,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None,
        }