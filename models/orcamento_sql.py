"""
Precision VRT Solo - Modelo Orcamento SQLAlchemy (compatível com tabela existente)
"""

from sqlalchemy import Column, String, Numeric, DateTime
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from db.database import Base


class TipoOrcamento(PyEnum):
    """Tipos de orçamentos."""
    PROJETO = "projeto"
    SERVICO = "servico"
    PRODUTO = "produto"
    COMBUSTIVEL = "combustivel"
    MANUTENCAO = "manutencao"
    OUTROS = "outros"


class StatusOrcamento(PyEnum):
    """Status dos orçamentos."""
    RASCUNHO = "rascunho"
    ENVIADO = "enviado"
    APROVADO = "aprovado"
    RECUSADO = "recusado"
    CANCELADO = "cancelado"
    EXECUTADO = "executado"


class Orcamento(Base):
    """
    Modelo de dados do orçamento usando SQLAlchemy.
    Mapeia a tabela 'orcamentos' existente do banco de dados.
    """
    
    __tablename__ = "orcamentos"
    
    id = Column(String(36), primary_key=True, index=True)
    tenant_id = Column(String(36), index=True)
    cliente_id = Column(String(36), index=True)
    usuario_id = Column(String(36), index=True)
    data_emissao = Column(DateTime(timezone=True), server_default=func.now())
    valor_total_bruto = Column(Numeric(14, 2), nullable=False)
    desconto_percentual = Column(Numeric(5, 2), default=0)
    valor_total_liquido = Column(Numeric(14, 2), nullable=False)
    status = Column(String(30), nullable=False, index=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self) -> dict:
        """Converte para dicionário compatível com frontend."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'cliente_id': self.cliente_id,
            'usuario_id': self.usuario_id,
            'tipo': 'servico',  # Valor padrão compatível com enum
            'status': self.status,
            'descricao': f'Orçamento #{self.id[:8]}',  # Descrição padrão
            'valor_total': float(self.valor_total_liquido),
            'valor_total_bruto': float(self.valor_total_bruto),
            'desconto_percentual': float(self.desconto_percentual),
            'data_emissao': self.data_emissao.isoformat() if self.data_emissao else None,
            'data_validade': (self.data_emissao.isoformat() if self.data_emissao else None),  # Padrão igual emissão
            'itens': [],  # Não implementado ainda
            'observacoes': '',
            'dados_adicionais': {},
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }