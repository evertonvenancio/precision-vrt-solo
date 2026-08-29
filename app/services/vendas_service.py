"""
Service layer para Vendas e Títulos Financeiros.

Regra central: toda venda gera um ou mais títulos RECEBER.
"""

import logging
import uuid
from datetime import date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.orm import Session, selectinload

from models.orcamento_sql import Orcamento
from models.vendas_sql import TituloFinanceiro, Venda
from schemas.vendas import (
    BaixaPagamentoRequest,
    BaixaPagamentoResponse,
    VendaCreate,
    VendaPrazoCreate,
)

logger = logging.getLogger(__name__)

# Tolerância para comparar valores decimais
_TOLERANCIA = Decimal("0.01")


class VendasService:
    """Serviço para registro de vendas e controle de títulos financeiros."""

    def __init__(self, db: Session, tenant_id: str = 'default') -> None:
        self._db = db
        self.tenant_id = tenant_id

    def listar_vendas(self):
        """Lista todas as vendas do tenant."""
        vendas = self._db.query(Venda).filter(Venda.tenant_id == self.tenant_id).all()
        return [v.to_dict() for v in vendas]

    def listar_orcamentos_aprovados(self):
        """Lista orçamentos aprovados para selecionar em vendas."""
        orcamentos = self._db.query(Orcamento).filter(
            and_(
                Orcamento.tenant_id == self.tenant_id,
                Orcamento.status == 'aprovado'
            )
        ).all()
        return [o.to_dict() for o in orcamentos]

    def listar_clientes_ativos(self):
        """Lista clientes ativos."""
        from models.cliente_sql import Cliente
        clientes = self._db.query(Cliente).filter(
            and_(Cliente.tenant_id == self.tenant_id, Cliente.ativo == True)
        ).all()
        return [c.to_dict() for c in clientes]

    def buscar_por_id(self, venda_id: str):
        """Busca venda por ID."""
        venda = self._db.query(Venda).filter(
            and_(Venda.id == venda_id, Venda.tenant_id == self.tenant_id)
        ).options(selectinload(Venda.titulos)).first()
        return venda.to_dict() if venda else None

    def registrar_venda_avista(self, dados: dict) -> Venda:
        """Registra venda à vista."""
        orcamento_id = dados.get('orcamento_id')
        cliente_id = dados.get('cliente_id')
        metodo_pagamento = dados.get('metodo_pagamento', 'dinheiro')

        orcamento = self._buscar_orcamento_elegivel(orcamento_id)

        venda = Venda(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            orcamento_id=orcamento_id,
            cliente_id=cliente_id,
            valor_total=Decimal(str(orcamento.valor_total_liquido)),
            tipo_venda="AVISTA",
            status="aberta"
        )
        self._db.add(venda)

        titulo = TituloFinanceiro(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            cliente_id=cliente_id,
            orcamento_id=orcamento_id,
            venda_id=venda.id,
            tipo="RECEBER",
            valor_original=Decimal(str(orcamento.valor_total_liquido)),
            data_vencimento=date.today(),
            status="pendente",
            metodo_pagamento=metodo_pagamento,
            parcela_numero=1,
            parcela_total=1
        )
        self._db.add(titulo)
        self._db.flush()
        return venda

    def baixar_titulo(self, titulo_id: str, dados: dict):
        """Baixa título."""
        titulo = self._db.query(TituloFinanceiro).filter(
            TituloFinanceiro.id == titulo_id
        ).first()

        if not titulo:
            raise ValueError("Título não encontrado")

        titulo.status = "pago"
        titulo.valor_liquidado = Decimal(str(dados.get('valor_pago', titulo.valor_original)))
        titulo.data_pagamento = date.today()
        self._db.flush()
        self._atualizar_status_venda(titulo)

    def _buscar_orcamento_elegivel(self, orcamento_id: str) -> Orcamento:
        """Valida orçamento."""
        orcamento = self._db.query(Orcamento).filter(Orcamento.id == orcamento_id).first()
        if not orcamento:
            raise ValueError("Orçamento não encontrado")
        return orcamento

    def _atualizar_status_venda(self, titulo: TituloFinanceiro):
        """Atualiza venda."""
        if titulo.venda and titulo.venda.esta_quitada:
            titulo.venda.status = "concluida"
            self._db.flush()

    def registrar_venda_prazo(self, dados: dict) -> Venda:
        """Registra venda a prazo com múltiplas parcelas."""
        import json
        orcamento_id = dados.get('orcamento_id')
        cliente_id = dados.get('cliente_id')
        parcelas_json = dados.get('parcelas', '[]')

        try:
            parcelas = json.loads(parcelas_json)
        except json.JSONDecodeError:
            raise ValueError("Parcelas inválidas - JSON malformado")

        if not parcelas or len(parcelas) < 2:
            raise ValueError("Venda a prazo requer mínimo 2 parcelas")

        orcamento = self._buscar_orcamento_elegivel(orcamento_id)

        # Validar soma das parcelas
        total_parcelas = sum(Decimal(str(p.get('valor', 0))) for p in parcelas)
        if abs(total_parcelas - Decimal(str(orcamento.valor_total_liquido))) > _TOLERANCIA:
            raise ValueError(f"Soma das parcelas (R$ {total_parcelas:.2f}) difere do valor do orçamento (R$ {orcamento.valor_total_liquido:.2f})")

        venda = Venda(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            orcamento_id=orcamento_id,
            cliente_id=cliente_id,
            valor_total=Decimal(str(orcamento.valor_total_liquido)),
            tipo_venda="APRAZO",
            status="aberta"
        )
        self._db.add(venda)

        for i, parcela in enumerate(sorted(parcelas, key=lambda p: p['data_vencimento']), 1):
            titulo = TituloFinanceiro(
                id=str(uuid.uuid4()),
                tenant_id=self.tenant_id,
                cliente_id=cliente_id,
                orcamento_id=orcamento_id,
                venda_id=venda.id,
                tipo="RECEBER",
                valor_original=Decimal(str(parcela['valor'])),
                data_emissao=date.today(),
                data_vencimento=parcela['data_vencimento'],
                status="pendente",
                metodo_pagamento=parcela.get('metodo_pagamento'),
                parcela_numero=i,
                parcela_total=len(parcelas)
            )
            self._db.add(titulo)

        self._db.flush()
        return venda

    def gerar_nota_fiscal(self, venda_id: str) -> bytes:
        """Gera nota fiscal PDF da venda (stub - implementar geração real)."""
        venda = self._db.query(Venda).filter(Venda.id == venda_id).first()
        if not venda:
            raise ValueError("Venda não encontrada")

        # Stub: retornar PDF mínimo
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 16)
        pdf.cell(0, 10, f'NOTA FISCAL - Venda {venda.id}', ln=True, align='C')
        pdf.ln(10)
        pdf.set_font('Helvetica', '', 12)
        pdf.cell(0, 8, f'Cliente: {venda.cliente_id}', ln=True)
        pdf.cell(0, 8, f'Orçamento: {venda.orcamento_id}', ln=True)
        pdf.cell(0, 8, f'Valor Total: R$ {venda.valor_total:.2f}', ln=True)
        pdf.cell(0, 8, f'Tipo: {venda.tipo_venda}', ln=True)
        pdf.cell(0, 8, f'Status: {venda.status}', ln=True)

        return pdf.output(dest='S').encode('latin-1')
