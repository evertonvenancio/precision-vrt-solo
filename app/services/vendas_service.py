"""
Service layer para Vendas e Títulos Financeiros.
Regra central: toda venda gera um ou mais títulos RECEBER.
"""

import logging
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any

from sqlalchemy import select, and_
from sqlalchemy.orm import Session, selectinload

from models.orcamento_sql import Orcamento
from models.vendas_sql import TituloFinanceiro, Venda
from models.cliente_sql import Cliente
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

    def __init__(self, db: Session, tenant_id: str = None) -> None:
        self._db = db
        self.tenant_id = tenant_id

    def listar_vendas(self) -> List[Dict[str, Any]]:
        """Lista todas as vendas do tenant, enriquecendo com o nome do cliente."""
        query = self._db.query(Venda).filter(Venda.tenant_id == self.tenant_id)
        vendas = query.order_by(Venda.criado_em.desc()).all()

        retorno = []
        for v in vendas:
            d = v.to_dict()
            # Enriquecer com nome do cliente
            cliente = self._db.query(Cliente).filter(
                and_(Cliente.id == v.cliente_id, Cliente.tenant_id == self.tenant_id)
            ).first()
            d['cliente_nome'] = cliente.nome if cliente else 'N/A'
            retorno.append(d)
        return retorno

    def listar_orcamentos_aprovados(self) -> List[Dict[str, Any]]:
        """Lista orçamentos aprovados para selecionar em vendas."""
        orcamentos = self._db.query(Orcamento).filter(
            and_(
                Orcamento.tenant_id == self.tenant_id,
                Orcamento.status == 'aprovado'
            )
        ).all()
        return [o.to_dict() for o in orcamentos]

    def listar_clientes_ativos(self) -> List[Dict[str, Any]]:
        """Lista clientes ativos do tenant."""
        clientes = self._db.query(Cliente).filter(
            and_(Cliente.tenant_id == self.tenant_id, Cliente.ativo == True)
        ).order_by(Cliente.nome).all()
        return [c.to_dict() for c in clientes]

    def buscar_por_id(self, venda_id: str) -> Optional[Dict[str, Any]]:
        """Busca venda por ID garantindo isolamento por tenant."""
        venda = self._db.query(Venda).filter(
            and_(Venda.id == venda_id, Venda.tenant_id == self.tenant_id)
        ).options(selectinload(Venda.titulos)).first()

        if not venda:
            return None

        d = venda.to_dict()
        # Enriquecer com nome do cliente
        cliente = self._db.query(Cliente).filter(
            and_(Cliente.id == venda.cliente_id, Cliente.tenant_id == self.tenant_id)
        ).first()
        d['cliente_nome'] = cliente.nome if cliente else 'N/A'

        return d

    def registrar_venda_avista(self, dados: dict, usuario_id: str = None) -> Venda:
        """Registra venda à vista e gera título financeiro correspondente."""
        orcamento_id = dados.get('orcamento_id')
        cliente_id = dados.get('cliente_id')
        metodo_pagamento = dados.get('metodo_pagamento', 'dinheiro')
        valor_total = self._parse_decimal(dados.get('valor_total'))

        if not cliente_id:
            raise ValueError("cliente_id é obrigatório.")

        # Se houver orçamento, validar e usar o valor dele
        if orcamento_id:
            orcamento = self._buscar_orcamento_elegivel(orcamento_id)
            valor_final = Decimal(str(orcamento.valor_total_liquido))
        else:
            if valor_total <= 0:
                raise ValueError("valor_total deve ser informado para venda direta.")
            valor_final = valor_total

        venda = Venda(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            orcamento_id=orcamento_id,
            cliente_id=cliente_id,
            valor_total=valor_final,
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
            valor_original=valor_final,
            data_emissao=date.today(),
            data_vencimento=date.today(),
            status="pendente",
            metodo_pagamento=metodo_pagamento,
            parcela_numero=1,
            parcela_total=1
        )
        self._db.add(titulo)
        self._db.flush()

        self._registrar_auditoria(
            "criar", "vendas", usuario_id,
            f"Venda AVISTA {venda.id} registrada. Valor: R$ {valor_final:.2f}"
        )

        return venda

    def registrar_venda_prazo(self, dados: dict, usuario_id: str = None) -> Venda:
        """Registra venda a prazo com múltiplas parcelas."""
        orcamento_id = dados.get('orcamento_id')
        cliente_id = dados.get('cliente_id')
        valor_total_form = self._parse_decimal(dados.get('valor_total'))

        if not cliente_id:
            raise ValueError("cliente_id é obrigatório.")

        # Se houver orçamento, validar
        if orcamento_id:
            orcamento = self._buscar_orcamento_elegivel(orcamento_id)
            valor_referencia = Decimal(str(orcamento.valor_total_liquido))
        else:
            if valor_total_form <= 0:
                raise ValueError("valor_total deve ser informado para venda direta.")
            valor_referencia = valor_total_form

        # Processar parcelas do form (lista de dicts: valor, data_vencimento)
        parcelas_data = dados.get('parcelas', [])
        if not parcelas_data or len(parcelas_data) < 2:
            raise ValueError("Venda a prazo requer no mínimo 2 parcelas.")

        # Validar soma das parcelas
        total_parcelas = sum(self._parse_decimal(p.get('valor', 0)) for p in parcelas_data)
        if abs(total_parcelas - valor_referencia) > _TOLERANCIA:
            raise ValueError(f"Soma das parcelas (R$ {total_parcelas:.2f}) difere do valor total (R$ {valor_referencia:.2f})")

        venda = Venda(
            id=str(uuid.uuid4()),
            tenant_id=self.tenant_id,
            orcamento_id=orcamento_id,
            cliente_id=cliente_id,
            valor_total=valor_referencia,
            tipo_venda="APRAZO",
            status="aberta"
        )
        self._db.add(venda)

        for i, p in enumerate(parcelas_data, 1):
            data_venc = p.get('data_vencimento')
            if isinstance(data_venc, str):
                data_venc = date.fromisoformat(data_venc)

            titulo = TituloFinanceiro(
                id=str(uuid.uuid4()),
                tenant_id=self.tenant_id,
                cliente_id=cliente_id,
                orcamento_id=orcamento_id,
                venda_id=venda.id,
                tipo="RECEBER",
                valor_original=self._parse_decimal(p.get('valor')),
                data_emissao=date.today(),
                data_vencimento=data_venc,
                status="pendente",
                parcela_numero=i,
                parcela_total=len(parcelas_data)
            )
            self._db.add(titulo)

        self._db.flush()

        self._registrar_auditoria(
            "criar", "vendas", usuario_id,
            f"Venda APRAZO {venda.id} registrada ({len(parcelas_data)} parcelas). Valor: R$ {valor_referencia:.2f}"
        )

        return venda

    def baixar_titulo(self, titulo_id: str, dados: dict, usuario_id: str = None):
        """Realiza a baixa (pagamento) de um título financeiro."""
        titulo = self._db.query(TituloFinanceiro).filter(
            and_(
                TituloFinanceiro.id == titulo_id,
                TituloFinanceiro.tenant_id == self.tenant_id
            )
        ).first()

        if not titulo:
            raise ValueError("Título não encontrado para este tenant.")

        if titulo.status == 'pago':
            raise ValueError("Este título já foi baixado.")

        valor_pago = self._parse_decimal(dados.get('valor_pago', titulo.valor_original))
        data_pagamento = dados.get('data_pagamento', date.today())
        if isinstance(data_pagamento, str):
            data_pagamento = date.fromisoformat(data_pagamento)

        # Atualizar título
        titulo.status = "pago"
        titulo.valor_liquidado = valor_pago
        titulo.data_pagamento = data_pagamento
        titulo.metodo_pagamento = dados.get('metodo_pagamento', titulo.metodo_pagamento)

        self._db.flush()

        # Verificar se a venda foi totalmente quitada
        if titulo.venda_id:
            self._atualizar_status_venda(titulo.venda_id)

        self._registrar_auditoria(
            "alterar", "financeiro", usuario_id,
            f"Título {titulo_id} baixado. Valor: R$ {valor_pago:.2f}"
        )

    def gerar_nota_fiscal(self, venda_id: str) -> bytes:
        """Gera nota fiscal (Simulado) a partir dos dados reais da venda."""
        venda_info = self.buscar_por_id(venda_id)
        if not venda_info:
            raise ValueError("Venda não encontrada.")

        # Geração real simplificada usando FPDF se disponível
        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'PRECISION VRT SOLO - NOTA FISCAL', ln=True, align='C')
            pdf.ln(10)

            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f'Venda ID: {venda_info["id"]}', ln=True)
            pdf.cell(0, 10, f'Cliente: {venda_info.get("cliente_nome", "N/A")}', ln=True)
            pdf.cell(0, 10, f'Data: {venda_info["criado_em"]}', ln=True)
            pdf.cell(0, 10, f'Tipo: {venda_info["tipo_venda"]}', ln=True)
            pdf.ln(5)

            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f'Valor Total: R$ {venda_info["valor_total"]:,.2f}', ln=True)
            pdf.ln(10)

            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 10, 'Documento gerado eletronicamente pelo sistema Precision VRT Solo.', align='C')

            return pdf.output(dest='S').encode('latin-1')
        except ImportError:
            # Fallback para texto simples se FPDF não estiver disponível
            content = f"NOTA FISCAL - VENDA {venda_id}\nCliente: {venda_info.get('cliente_nome')}\nValor: R$ {venda_info['valor_total']:.2f}"
            return content.encode('utf-8')

    def _buscar_orcamento_elegivel(self, orcamento_id: str) -> Orcamento:
        """Busca e valida se o orçamento pode ser convertido em venda."""
        orcamento = self._db.query(Orcamento).filter(
            and_(
                Orcamento.id == orcamento_id,
                Orcamento.tenant_id == self.tenant_id
            )
        ).first()

        if not orcamento:
            raise ValueError("Orçamento não encontrado ou não pertence a este tenant.")

        if orcamento.status != 'aprovado':
            raise ValueError(f"Orçamento {orcamento_id} não está aprovado (status: {orcamento.status}).")

        # Verificar se já existe venda para este orçamento
        venda_existente = self._db.query(Venda).filter(Venda.orcamento_id == orcamento_id).first()
        if venda_existente:
            raise ValueError(f"Já existe uma venda registrada para o orçamento {orcamento_id}.")

        return orcamento

    def _atualizar_status_venda(self, venda_id: str):
        """Verifica se todos os títulos da venda estão pagos e atualiza status da venda."""
        venda = self._db.query(Venda).filter(Venda.id == venda_id).first()
        if venda and venda.esta_quitada:
            venda.status = "concluida"
            self._db.flush()

    def _parse_decimal(self, valor: Any) -> Decimal:
        """Converte valor para Decimal de forma segura."""
        if valor is None:
            return Decimal("0.00")
        if isinstance(valor, Decimal):
            return valor
        try:
            # Remove formatação de moeda se houver
            val_str = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
            return Decimal(val_str).quantize(Decimal("0.01"))
        except:
            return Decimal("0.00")

    def _registrar_auditoria(self, tipo_acao: str, modulo: str, usuario_id: str, acao: str, sucesso: bool = True, mensagem: str = None):
        """Registra evento de auditoria se o modelo estiver disponível."""
        try:
            from models.auditoria import AuditoriaEvento
            evento = AuditoriaEvento(
                tipo_acao=tipo_acao,
                modulo=modulo,
                usuario_id=usuario_id or "0",
                usuario_nome="executor",
                acao=acao,
                sucesso=sucesso,
                mensagem=mensagem,
                timestamp=datetime.utcnow(),
                tenant_id=self.tenant_id
            )
            self._db.add(evento)
            self._db.flush()
        except Exception as e:
            logger.warning(f"Falha ao registrar auditoria: {e}")
            pass
