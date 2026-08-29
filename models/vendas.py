
"""
Precision VRT Solo — Modelo Vendas

Representa dados de vendas e títulos financeiros.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

class TipoVenda(Enum):
    """Tipos de vendas."""
    A_VISTA = "a_vista"
    A_PRAZO = "a_prazo"
    PARCIAL = "parcial"
    BOLETO = "boleto"
    CARTAO = "cartao"
    TRANSFERENCIA = "transferencia"
    DINHEIRO = "dinheiro"

class StatusVenda(Enum):
    """Status das vendas."""
    rascunho = "rascunho"
    aguardando_pagamento = "aguardando_pagamento"
    pagamento_parcial = "pagamento_parcial"
    pago = "pago"
    cancelado = "cancelado"
    reembolsado = "reembolsado"

class TituloFinanceiro:
    """
    Representa um título financeiro (contas a receber/pagar).
    """
    
    def __init__(self,
                 id: str,
                 venda_id: str,
                 tipo: str,
                 valor: Decimal,
                 data_vencimento: date,
                 data_emissao: date,
                 status: str = "pendente",
                 observacoes: Optional[str] = None,
                 dados_adicionais: Optional[Dict[str, Any]] = None):
        self.id = id
        self.venda_id = venda_id
        self.tipo = tipo
        self.valor = valor
        self.data_vencimento = data_vencimento
        self.data_emissao = data_emissao
        self.status = status
        self.observacoes = observacoes
        self.dados_adicionais = dados_adicionais or {}
        self.criado_em = datetime.now()
        self.atualizado_em = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte para dicionário.
        """
        return {
            'id': self.id,
            'venda_id': self.venda_id,
            'tipo': self.tipo,
            'valor': str(self.valor),
            'data_vencimento': self.data_vencimento.isoformat(),
            'data_emissao': self.data_emissao.isoformat(),
            'status': self.status,
            'observacoes': self.observacoes,
            'dados_adicionais': self.dados_adicionais,
            'criado_em': self.criado_em.isoformat(),
            'updated_at': self.atualizado_em.isoformat()
        }

class Venda:
    """
    Representa uma venda.
    """
    
    def __init__(self,
                 id: str,
                 tenant_id: str,
                 cliente_id: str,
                 orcamento_id: Optional[str] = None,
                 tipo: TipoVenda = TipoVenda.A_VISTA,
                 status: StatusVenda = StatusVenda.rascunho,
                 valor_total: Decimal = Decimal('0'),
                 valor_pago: Decimal = Decimal('0'),
                 data_venda: Optional[date] = None,
                 data_vencimento: Optional[date] = None,
                 observacoes: Optional[str] = None,
                 dados_adicionais: Optional[Dict[str, Any]] = None):
        self.id = id
        self.tenant_id = tenant_id
        self.cliente_id = cliente_id
        self.orcamento_id = orcamento_id
        self.tipo = tipo
        self.status = status
        self.valor_total = valor_total
        self.valor_pago = valor_pago
        self.data_venda = data_venda or date.today()
        self.data_vencimento = data_vencimento
        self.observacoes = observacoes
        self.dados_adicionais = dados_adicionais or {}
        self.criado_em = datetime.now()
        self.atualizado_em = datetime.now()
        self.titulos: List[TituloFinanceiro] = []
        
    def adicionar_titulo(self, titulo: TituloFinanceiro):
        """Adicionar título à venda."""
        self.titulos.append(titulo)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte para dicionário.
        """
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'cliente_id': self.cliente_id,
            'orcamento_id': self.orcamento_id,
            'tipo': self.tipo.value,
            'status': self.status.value,
            'valor_total': str(self.valor_total),
            'valor_pago': str(self.valor_pago),
            'data_venda': self.data_venda.isoformat(),
            'data_vencimento': self.data_vencimento.isoformat() if self.data_vencimento else None,
            'observacoes': self.observacoes,
            'dados_adicionais': self.dados_adicionais,
            'criado_em': self.criado_em.isoformat(),
            'atualizado_em': self.atualizado_em.isoformat(),
            'titulos': [titulo.to_dict() for titulo in self.titulos]
        }
