"""
Precision VRT Solo - Modelo Cliente SQLAlchemy (compatível com tabela existente)
"""

from sqlalchemy import Column, String, Text, Float, Boolean, DateTime
from sqlalchemy.sql import func
from db.database import Base
import uuid


class Cliente(Base):
    """
    Modelo de dados do cliente usando SQLAlchemy.
    Mapeia a tabela 'clientes' existente do banco de dados.
    """
    
    __tablename__ = "clientes"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), index=True, default='default')
    nome = Column(String(255), nullable=False, index=True)
    cpf_cnpj = Column(String(20), index=True)
    telefone = Column(String(30))
    email = Column(String(255), nullable=False, unique=True, index=True)
    endereco = Column(String(500))
    cidade = Column(String(100))
    estado = Column(String(2))
    cep = Column(String(10))
    area_total_hectares = Column(Float)
    data_nascimento = Column(String(10))
    ativo = Column(Boolean, default=True, index=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self) -> dict:
        """Converte para dicionário compatível com frontend."""
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "telefone": self.telefone,
            "cpf_cnpj": self.cpf_cnpj,
            "endereco": self.endereco,
            "cidade": self.cidade,
            "estado": self.estado,
            "cep": self.cep,
            "area_total_hectares": self.area_total_hectares,
            "ativo": self.ativo,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }