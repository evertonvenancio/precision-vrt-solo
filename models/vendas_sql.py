"""
Precision VRT Solo - Modelos SQLAlchemy para Vendas e Títulos Financeiros
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class Venda(Base):
    """Modelo ORM SQLAlchemy para a tabela 'vendas'."""
    __tablename__ = "vendas"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), index=True, default='default')
    orcamento_id = Column(String(36), ForeignKey("orcamentos.id"), index=True, nullable=False)
    cliente_id = Column(String(36), ForeignKey("clientes.id"), index=True, nullable=False)
    valor_total = Column(Numeric(14, 2), nullable=False)
    tipo_venda = Column(String(20), nullable=False, default='AVISTA')  # AVISTA ou APRAZO
    status = Column(String(30), nullable=False, default='aberta', index=True) # aberta, concluida, cancelada
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relacionamentos
    titulos = relationship("TituloFinanceiro", back_populates="venda", cascade="all, delete-orphan")

    @property
    def total_liquidado(self) -> Decimal:
        """Soma dos valores já pagos de todos os títulos."""
        return sum((t.valor_liquidado for t in self.titulos if t.status == 'pago' and t.valor_liquidado), Decimal('0.00'))

    @property
    def esta_quitada(self) -> bool:
        """Verifica se todos os títulos da venda estão pagos."""
        if not self.titulos:
            return False
        return all(t.status == 'pago' for t in self.titulos)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "orcamento_id": self.orcamento_id,
            "cliente_id": self.cliente_id,
            "valor_total": float(self.valor_total),
            "tipo_venda": self.tipo_venda,
            "status": self.status,
            "total_liquidado": float(self.total_liquidado),
            "esta_quitada": self.esta_quitada,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None,
            "titulos": [t.to_dict() for t in self.titulos]
        }


class TituloFinanceiro(Base):
    """Modelo ORM SQLAlchemy para a tabela 'titulos_financeiros'."""
    __tablename__ = "titulos_financeiros"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), index=True, default='default')
    cliente_id = Column(String(36), ForeignKey("clientes.id"), index=True, nullable=False)
    orcamento_id = Column(String(36), ForeignKey("orcamentos.id"), index=True, nullable=True)
    venda_id = Column(String(36), ForeignKey("vendas.id"), index=True, nullable=True)
    tipo = Column(String(20), nullable=False, default='RECEBER') # RECEBER ou PAGAR
    valor_original = Column(Numeric(14, 2), nullable=False)
    valor_liquidado = Column(Numeric(14, 2), nullable=True)
    data_emissao = Column(Date, nullable=False, default=date.today)
    data_vencimento = Column(Date, nullable=False)
    data_pagamento = Column(Date, nullable=True)
    status = Column(String(30), nullable=False, default='pendente', index=True) # pendente, pago, atrasado, cancelado
    metodo_pagamento = Column(String(30), nullable=True) # pix, boleto, cartao, dinheiro
    parcela_numero = Column(Integer, nullable=True)
    parcela_total = Column(Integer, nullable=True)
    titulo_original_id = Column(String(36), nullable=True) # Para títulos residuais
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relacionamentos
    venda = relationship("Venda", back_populates="titulos")

    @property
    def saldo_residual(self) -> Optional[Decimal]:
        if self.valor_liquidado and self.valor_liquidado < self.valor_original:
            return self.valor_original - self.valor_liquidado
        return None

    @property
    def esta_vencido(self) -> bool:
        return self.status == 'pendente' and self.data_vencimento < date.today()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "cliente_id": self.cliente_id,
            "orcamento_id": self.orcamento_id,
            "venda_id": self.venda_id,
            "tipo": self.tipo,
            "valor_original": float(self.valor_original),
            "valor_liquidado": float(self.valor_liquidado) if self.valor_liquidado else None,
            "data_emissao": self.data_emissao.isoformat() if self.data_emissao else None,
            "data_vencimento": self.data_vencimento.isoformat() if self.data_vencimento else None,
            "data_pagamento": self.data_pagamento.isoformat() if self.data_pagamento else None,
            "status": self.status,
            "metodo_pagamento": self.metodo_pagamento,
            "parcela_numero": self.parcela_numero,
            "parcela_total": self.parcela_total,
            "saldo_residual": float(self.saldo_residual) if self.saldo_residual else None,
            "esta_vencido": self.esta_vencido,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None,
        }
