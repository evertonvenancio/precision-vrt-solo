"""
Precision VRT Solo - Serviço Unificado do Módulo Financeiro
Integração completa com Vendas, Títulos Financeiros e Caixa.
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any

from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session

from models.vendas_sql import TituloFinanceiro, Venda
from models.cliente_sql import Cliente
from core.seguranca.permissions import get_permissoes

logger = logging.getLogger(__name__)


class FinanceiroService:
    """
    Serviço central do módulo Financeiro integrado com Vendas e Títulos.
    """

    def __init__(self, db: Session, user_data: dict = None):
        self.db = db
        self.user_data = user_data or {}
        self.tenant_id = self.user_data.get("tenant_id") or "default"

    def buscar_permissoes(self) -> dict:
        """Busca permissões do usuário."""
        return get_permissoes(self.db, self.user_data)

    def listar_contas_receber(self) -> List[Dict[str, Any]]:
        """
        Lista todos os títulos a receber do tenant, enriquecendo com dados de cliente e venda.
        """
        titulos = self.db.query(TituloFinanceiro).filter(
            and_(
                TituloFinanceiro.tenant_id == self.tenant_id,
                TituloFinanceiro.tipo == "RECEBER"
            )
        ).order_by(TituloFinanceiro.data_vencimento.asc()).all()

        retorno = []
        for t in titulos:
            d = t.to_dict()
            # Enriquecer com nome do cliente
            cliente = self.db.query(Cliente).filter(
                and_(Cliente.id == t.cliente_id, Cliente.tenant_id == self.tenant_id)
            ).first()
            d['cliente_nome'] = cliente.nome if cliente else 'N/A'
            d['cliente_cpf_cnpj'] = cliente.cpf_cnpj if cliente else ''

            # Enriquecer com dados da venda se houver
            if t.venda_id:
                venda = self.db.query(Venda).filter(
                    and_(Venda.id == t.venda_id, Venda.tenant_id == self.tenant_id)
                ).first()
                d['venda_tipo'] = venda.tipo_venda if venda else 'DIRETA'
            else:
                d['venda_tipo'] = 'DIRETA'

            retorno.append(d)
        return retorno

    def obter_resumo_caixa(self) -> Dict[str, Any]:
        """
        Calcula o resumo financeiro de caixa com base nos títulos reais do tenant.
        """
        query_base = self.db.query(TituloFinanceiro).filter(
            and_(
                TituloFinanceiro.tenant_id == self.tenant_id,
                TituloFinanceiro.tipo == "RECEBER"
            )
        )

        total_receber = query_base.with_entities(func.sum(TituloFinanceiro.valor_original)).scalar() or Decimal('0.00')
        total_recebido = self.db.query(func.sum(TituloFinanceiro.valor_liquidado)).filter(
            and_(
                TituloFinanceiro.tenant_id == self.tenant_id,
                TituloFinanceiro.tipo == "RECEBER",
                TituloFinanceiro.status == "pago"
            )
        ).scalar() or Decimal('0.00')

        pendentes = query_base.filter(TituloFinanceiro.status == "pendente").count()
        pagos = query_base.filter(TituloFinanceiro.status == "pago").count()

        return {
            "total_receber": float(total_receber),
            "total_recebido": float(total_recebido),
            "saldo_caixa": float(total_recebido),
            "titulos_pendentes": pendentes,
            "titulos_pagos": pagos
        }
