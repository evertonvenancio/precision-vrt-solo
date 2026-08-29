"""
Service layer para Vendas e TÃ­tulos Financeiros.

Regra central: toda venda gera um ou mais tÃ­tulos RECEBER.
- Venda Ã  vista â†’ 1 tÃ­tulo com vencimento hoje.
- Venda a prazo â†’ N tÃ­tulos com datas negociadas (ex: safra/colheita).
- Pagamento parcial â†’ gera tÃ­tulo residual automaticamente.
"""

import logging
import uuid
from datetime import date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models.financeiro import Orcamento
from models.vendas import TituloFinanceiro, Venda
from schemas.vendas import (
    BaixaPagamentoRequest,
    BaixaPagamentoResponse,
    VendaCreate,
    VendaPrazoCreate,
)

logger = logging.getLogger(__name__)

# TolerÃ¢ncia para comparar valores decimais (evita falsos positivos por arredondamento)
_TOLERANCIA = Decimal("0.01")


class VendasService:
    """ServiÃ§o para registro de vendas e controle de tÃ­tulos financeiros.

    Todas as operaÃ§Ãµes recebem uma Session ativa e nÃ£o fazem commit
    internamente â€” o chamador (endpoint FastAPI) controla a transaÃ§Ã£o.

    Args:
        db: SessÃ£o ativa do SQLAlchemy 2.0.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    # -----------------------------------------------------------------------
    # Venda Ã  Vista
    # -----------------------------------------------------------------------

    def registrar_venda_avista(
        self,
        payload: VendaCreate,
    ) -> Venda:
        """Registra uma venda Ã  vista e gera 1 tÃ­tulo RECEBER com vencimento hoje.

        Fluxo:
        1. Valida que o orÃ§amento existe e estÃ¡ aprovado/faturado.
        2. Cria o registro de Venda (tipo AVISTA).
        3. Gera 1 TituloFinanceiro RECEBER com data_vencimento = hoje.

        Args:
            payload: Dados validados pelo schema VendaCreate.

        Returns:
            InstÃ¢ncia de Venda com 1 tÃ­tulo financeiro vinculado (sem commit).

        Raises:
            ValueError: Se o orÃ§amento nÃ£o existir, nÃ£o estiver em status
                elegÃ­vel, ou jÃ¡ tiver uma venda registrada.

        Example::

            venda = service.registrar_venda_avista(payload)
            db.commit()
        """
        orcamento = self._buscar_orcamento_elegivel(payload.orcamento_id)

        venda = Venda(
            tenant_id=payload.tenant_id,
            orcamento_id=payload.orcamento_id,
            cliente_id=payload.cliente_id,
            valor_total=orcamento.valor_total_liquido,
            tipo_venda="AVISTA",
            status="aberta",
        )
        self._db.add(venda)
        self._db.flush()

        titulo = TituloFinanceiro(
            tenant_id=payload.tenant_id,
            cliente_id=payload.cliente_id,
            orcamento_id=payload.orcamento_id,
            venda_id=venda.id,
            tipo="RECEBER",
            valor_original=orcamento.valor_total_liquido,
            data_emissao=date.today(),
            data_vencimento=date.today(),
            status="pendente",
            metodo_pagamento=payload.metodo_pagamento,
            parcela_numero=1,
            parcela_total=1,
        )
        self._db.add(titulo)
        venda.titulos.append(titulo)
        self._db.flush()

        logger.info(
            "Venda Ã  vista registrada: venda=%s orcamento=%s cliente=%s "
            "valor=%s titulo=%s",
            venda.id,
            payload.orcamento_id,
            payload.cliente_id,
            orcamento.valor_total_liquido,
            titulo.id,
        )
        return venda

    # -----------------------------------------------------------------------
    # Venda a Prazo
    # -----------------------------------------------------------------------

    def registrar_venda_prazo(
        self,
        payload: VendaPrazoCreate,
    ) -> Venda:
        """Registra uma venda a prazo e gera N tÃ­tulos RECEBER com datas futuras.

        Ideal para negociaÃ§Ãµes vinculadas Ã  safra/colheita: o vencimento de
        cada parcela pode ser configurado para datas de entrega da produÃ§Ã£o.

        Valida que a soma das parcelas Ã© compatÃ­vel com o valor lÃ­quido do
        orÃ§amento (tolerÃ¢ncia de R$ 0,01 para arredondamento).

        Args:
            payload: Dados validados pelo schema VendaPrazoCreate, incluindo
                a lista de ParcelaDTO com data_vencimento e valor de cada
                parcela.

        Returns:
            InstÃ¢ncia de Venda com N tÃ­tulos financeiros vinculados (sem commit).

        Raises:
            ValueError: Se o orÃ§amento nÃ£o existir, nÃ£o estiver em status
                elegÃ­vel, ou a soma das parcelas divergir do valor do orÃ§amento.

        Example::

            venda = service.registrar_venda_prazo(payload)
            db.commit()
        """
        orcamento = self._buscar_orcamento_elegivel(payload.orcamento_id)

        soma_parcelas = sum(
            (p.valor for p in payload.parcelas), Decimal("0.00")
        )
        diferenca = abs(soma_parcelas - orcamento.valor_total_liquido)
        if diferenca > _TOLERANCIA:
            raise ValueError(
                f"A soma das parcelas ({soma_parcelas}) difere do valor lÃ­quido "
                f"do orÃ§amento ({orcamento.valor_total_liquido}). "
                f"DiferenÃ§a: {diferenca}."
            )

        venda = Venda(
            tenant_id=payload.tenant_id,
            orcamento_id=payload.orcamento_id,
            cliente_id=payload.cliente_id,
            valor_total=orcamento.valor_total_liquido,
            tipo_venda="APRAZO",
            status="aberta",
        )
        self._db.add(venda)
        self._db.flush()

        total_parcelas = len(payload.parcelas)
        for numero, parcela in enumerate(payload.parcelas, start=1):
            titulo = TituloFinanceiro(
                tenant_id=payload.tenant_id,
                cliente_id=payload.cliente_id,
                orcamento_id=payload.orcamento_id,
                venda_id=venda.id,
                tipo="RECEBER",
                valor_original=parcela.valor,
                data_emissao=date.today(),
                data_vencimento=parcela.data_vencimento,
                status="pendente",
                parcela_numero=numero,
                parcela_total=total_parcelas,
            )
            self._db.add(titulo)
            venda.titulos.append(titulo)

        self._db.flush()

        logger.info(
            "Venda a prazo registrada: venda=%s orcamento=%s cliente=%s "
            "valor=%s parcelas=%d",
            venda.id,
            payload.orcamento_id,
            payload.cliente_id,
            orcamento.valor_total_liquido,
            total_parcelas,
        )
        return venda

    # -----------------------------------------------------------------------
    # Baixa de TÃ­tulo
    # -----------------------------------------------------------------------

    def baixar_titulo(
        self,
        request: BaixaPagamentoRequest,
    ) -> BaixaPagamentoResponse:
        """Registra o pagamento de um tÃ­tulo financeiro.

        Comportamento:
        - Se valor_pago >= valor_original (com tolerÃ¢ncia): marca como 'pago'.
        - Se valor_pago < valor_original: marca como 'pago' e gera um tÃ­tulo
          residual RECEBER com o saldo devedor, herdando as mesmas
          informaÃ§Ãµes de tenant/cliente/venda, sem data_vencimento definida
          (a renegociar).
        - Atualiza o status da venda para 'concluida' se todos os tÃ­tulos
          estiverem pagos.

        Args:
            request: Payload validado por BaixaPagamentoRequest com
                titulo_id, data_pagamento, valor_pago e metodo_pagamento.

        Returns:
            BaixaPagamentoResponse com o tÃ­tulo baixado e, se houver,
            o tÃ­tulo residual gerado.

        Raises:
            ValueError: Se o tÃ­tulo nÃ£o existir ou jÃ¡ estiver pago/cancelado.

        Example::

            resp = service.baixar_titulo(request)
            if resp.titulo_residual:
                logging.info(f"Saldo residual: R$ {resp.titulo_residual.valor_original}")
        """
        titulo = self._db.scalar(
            select(TituloFinanceiro)
            .options(selectinload(TituloFinanceiro.venda).selectinload(Venda.titulos))
            .where(TituloFinanceiro.id == request.titulo_id)
        )
        if titulo is None:
            raise ValueError(f"TÃ­tulo {request.titulo_id} nÃ£o encontrado.")

        if titulo.status in ("pago", "cancelado"):
            raise ValueError(
                f"TÃ­tulo {request.titulo_id} estÃ¡ com status '{titulo.status}' "
                f"e nÃ£o pode ser baixado."
            )

        valor_pago = request.valor_pago
        valor_original = titulo.valor_original
        saldo = (valor_original - valor_pago).quantize(Decimal("0.01"))
        pagamento_parcial = saldo > _TOLERANCIA
        titulo_residual: Optional[TituloFinanceiro] = None

        titulo.valor_liquidado = valor_pago
        titulo.data_pagamento = request.data_pagamento
        titulo.metodo_pagamento = request.metodo_pagamento
        titulo.status = "pago"

        logger.info(
            "TÃ­tulo baixado: id=%s valor_original=%s valor_pago=%s "
            "parcial=%s data=%s",
            titulo.id,
            valor_original,
            valor_pago,
            pagamento_parcial,
            request.data_pagamento,
        )

        if pagamento_parcial:
            titulo_residual = TituloFinanceiro(
                tenant_id=titulo.tenant_id,
                cliente_id=titulo.cliente_id,
                orcamento_id=titulo.orcamento_id,
                venda_id=titulo.venda_id,
                tipo=titulo.tipo,
                valor_original=saldo,
                data_emissao=request.data_pagamento,
                data_vencimento=request.data_pagamento,
                status="pendente",
                titulo_original_id=titulo.id,
                parcela_numero=None,
                parcela_total=None,
            )
            self._db.add(titulo_residual)
            self._db.flush()

            logger.info(
                "TÃ­tulo residual gerado: id=%s saldo=%s titulo_original=%s",
                titulo_residual.id,
                saldo,
                titulo.id,
            )

        self._db.flush()
        self._atualizar_status_venda(titulo)

        return BaixaPagamentoResponse(
            titulo_baixado=self._to_response(titulo),
            titulo_residual=self._to_response(titulo_residual) if titulo_residual else None,
            pagamento_parcial=pagamento_parcial,
            saldo_quitado=valor_pago,
        )

    # -----------------------------------------------------------------------
    # Consultas
    # -----------------------------------------------------------------------

    def buscar_venda(self, venda_id: uuid.UUID) -> Venda:
        """Busca uma venda pelo UUID com tÃ­tulos carregados via eager load.

        Args:
            venda_id: UUID da venda.

        Returns:
            InstÃ¢ncia de Venda com tÃ­tulos carregados.

        Raises:
            ValueError: Se nÃ£o encontrada.
        """
        venda = self._db.scalar(
            select(Venda)
            .options(selectinload(Venda.titulos))
            .where(Venda.id == venda_id)
        )
        if venda is None:
            raise ValueError(f"Venda {venda_id} nÃ£o encontrada.")
        return venda

    def listar_titulos_cliente(
        self,
        cliente_id: uuid.UUID,
        status: Optional[str] = None,
        tipo: Optional[str] = None,
    ) -> List[TituloFinanceiro]:
        """Lista tÃ­tulos de um cliente com filtros opcionais de status e tipo.

        Args:
            cliente_id: UUID do cliente.
            status: Filtro por status (pendente | pago | atrasado | cancelado).
            tipo: Filtro por tipo (RECEBER | PAGAR).

        Returns:
            Lista de TituloFinanceiro ordenada por data_vencimento.
        """
        query = (
            select(TituloFinanceiro)
            .where(TituloFinanceiro.cliente_id == cliente_id)
            .order_by(TituloFinanceiro.data_vencimento)
        )
        if status:
            query = query.where(TituloFinanceiro.status == status)
        if tipo:
            query = query.where(TituloFinanceiro.tipo == tipo)

        return list(self._db.scalars(query))

    def sincronizar_status_atrasados(self, tenant_id: uuid.UUID) -> int:
        """Atualiza para 'atrasado' todos os tÃ­tulos vencidos e pendentes.

        Deve ser chamado por um job agendado (ex: cron diÃ¡rio) para manter
        os status sincronizados com a data real.

        Args:
            tenant_id: UUID do tenant a sincronizar.

        Returns:
            NÃºmero de tÃ­tulos atualizados.
        """
        from sqlalchemy import and_, update

        resultado = self._db.execute(
            update(TituloFinanceiro)
            .where(
                and_(
                    TituloFinanceiro.tenant_id == tenant_id,
                    TituloFinanceiro.status == "pendente",
                    TituloFinanceiro.data_vencimento < date.today(),
                )
            )
            .values(status="atrasado")
        )
        atualizados = resultado.rowcount
        if atualizados:
            logger.info(
                "Status de %d tÃ­tulo(s) atualizado(s) para 'atrasado' â€” tenant=%s",
                atualizados,
                tenant_id,
            )
        return atualizados

    # -----------------------------------------------------------------------
    # Helpers privados
    # -----------------------------------------------------------------------

    def _buscar_orcamento_elegivel(self, orcamento_id: uuid.UUID) -> Orcamento:
        """Busca e valida que o orÃ§amento existe e estÃ¡ em status elegÃ­vel.

        Status elegÃ­veis: 'aprovado' ou 'faturado'.

        Args:
            orcamento_id: UUID do orÃ§amento.

        Returns:
            InstÃ¢ncia de Orcamento validada.

        Raises:
            ValueError: Se nÃ£o encontrado, status inelegÃ­vel ou jÃ¡ com venda.
        """
        orcamento = self._db.scalar(
            select(Orcamento).where(Orcamento.id == orcamento_id)
        )
        if orcamento is None:
            raise ValueError(f"OrÃ§amento {orcamento_id} nÃ£o encontrado.")

        if orcamento.status not in ("aprovado", "faturado"):
            raise ValueError(
                f"OrÃ§amento {orcamento_id} estÃ¡ com status '{orcamento.status}'. "
                "Apenas orÃ§amentos 'aprovado' ou 'faturado' podem gerar venda."
            )

        venda_existente = self._db.scalar(
            select(Venda).where(Venda.orcamento_id == orcamento_id)
        )
        if venda_existente:
            raise ValueError(
                f"O orÃ§amento {orcamento_id} jÃ¡ possui uma venda registrada "
                f"(venda_id={venda_existente.id})."
            )

        return orcamento

    def _atualizar_status_venda(self, titulo: TituloFinanceiro) -> None:
        """Atualiza o status da venda para 'concluida' se todos os tÃ­tulos pagos.

        Args:
            titulo: TituloFinanceiro com relacionamento 'venda' carregado.
        """
        if titulo.venda is None:
            return

        venda = titulo.venda
        if venda.esta_quitada:
            venda.status = "concluida"
            logger.info("Venda concluÃ­da (quitada): venda=%s", venda.id)

    def _to_response(self, titulo: TituloFinanceiro):
        """Converte TituloFinanceiro para schema de resposta.

        Args:
            titulo: InstÃ¢ncia do modelo.

        Returns:
            DicionÃ¡rio compatÃ­vel com TituloFinanceiroResponse.
        """
        from schemas.vendas import TituloFinanceiroResponse

        return TituloFinanceiroResponse(
            id=titulo.id,
            tenant_id=titulo.tenant_id,
            cliente_id=titulo.cliente_id,
            orcamento_id=titulo.orcamento_id,
            venda_id=titulo.venda_id,
            tipo=titulo.tipo,
            valor_original=titulo.valor_original,
            valor_liquidado=titulo.valor_liquidado,
            data_emissao=titulo.data_emissao,
            data_vencimento=titulo.data_vencimento,
            data_pagamento=titulo.data_pagamento,
            status=titulo.status,
            metodo_pagamento=titulo.metodo_pagamento,
            parcela_numero=titulo.parcela_numero,
            parcela_total=titulo.parcela_total,
            saldo_residual=titulo.saldo_residual,
            esta_vencido=titulo.esta_vencido,
            criado_em=titulo.criado_em,
            atualizado_em=titulo.atualizado_em,
        )

