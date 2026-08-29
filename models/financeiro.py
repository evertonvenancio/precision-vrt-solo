
"""
Precision VRT Solo — Modelo Financeiro

Implementa modelos de dados para gestão financeira, orçamentos e contas a receber.
"""

from typing import Optional, List
from datetime import date
from decimal import Decimal
from enum import Enum

class TipoOrcamento(Enum):
    """Tipos de orçamentos."""
    PROJETO = "projeto"
    SERVICO = "servico"
    PRODUTO = "produto"
    COMBUSTIVEL = "combustivel"
    MANUTENCAO = "manutencao"
    OUTROS = "outros"

class StatusOrcamento(Enum):
    """Status dos orçamentos."""
    rascunho = "rascunho"
    enviado = "enviado"
    aprovado = "aprovado"
    recusado = "recusado"
    cancelado = "cancelado"
    executado = "executado"

class Orcamento:
    """
    Representa um orçamento.
    """
    
    def __init__(self,
                 id: str,
                 tenant_id: str,
                 cliente_id: str,
                 tipo: TipoOrcamento,
                 status: StatusOrcamento,
                 descricao: str,
                 valor_total: Decimal,
                 data_emissao: date,
                 data_validade: date,
                 itens: List[dict] = None,
                 observacoes: Optional[str] = None,
                 dados_adicionais: Optional[dict] = None):
        self.id = id
        self.tenant_id = tenant_id
        self.cliente_id = cliente_id
        self.tipo = tipo
        self.status = status
        self.descricao = descricao
        self.valor_total = valor_total
        self.data_emissao = data_emissao
        self.data_validade = data_validade
        self.itens = itens or []
        self.observacoes = observacoes
        self.dados_adicionais = dados_adicionais or {}
        self.criado_em = date.today()
        self.atualizado_em = date.today()
        
    def to_dict(self) -> dict:
        """
        Converte para dicionário.
        """
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'cliente_id': self.cliente_id,
            'tipo': self.tipo.value,
            'status': self.status.value,
            'descricao': self.descricao,
            'valor_total': str(self.valor_total),
            'data_emissao': self.data_emissao.isoformat(),
            'data_validade': self.data_validade.isoformat(),
            'itens': self.itens,
            'observacoes': self.observacoes,
            'dados_adicionais': self.dados_adicionais,
            'criado_em': self.criado_em.isoformat(),
            'atualizado_em': self.atualizado_em.isoformat()
        }

# Removido TituloFinanceiro e Venda pois já existem em models/vendas
