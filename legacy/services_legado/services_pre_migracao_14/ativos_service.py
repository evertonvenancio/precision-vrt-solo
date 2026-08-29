"""
Service layer para GestÃ£o de Ativos Patrimoniais, ROI e Ponto de EquilÃ­brio.

MÃ©todos principais:
- cadastrar_ativo: Salva bem e calcula depreciaÃ§Ã£o mensal linear automaticamente.
- calcular_roi_ativo: ROI = (lucro_bruto / valor_aquisicao) Ã— 100.
- calcular_ponto_equilibrio: ServiÃ§os mÃ­nimos/mÃªs para cobrir custos fixos.
"""

import logging
import math
import uuid
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.seguranca.permissions import get_permissoes
from models.ativos import AtivoPatrimonial, CATEGORIAS_ATIVO
from schemas.ativos import (
    AtivoCreate,
    AtivoResponse,
    PontoEquilibrioRequest,
    PontoEquilibrioResponse,
    RoiAtivoRequest,
    RoiAtivoResponse,
)

logger = logging.getLogger(__name__)


class AtivosService:
    """ServiÃ§o para gestÃ£o de ativos patrimoniais, ROI e ponto de equilÃ­brio.

    Todas as operaÃ§Ãµes recebem uma Session ativa e nÃ£o fazem commit
    internamente â€” o chamador (endpoint FastAPI) controla a transaÃ§Ã£o.

    Args:
        db: SessÃ£o ativa do SQLAlchemy 2.0.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    # -----------------------------------------------------------------------
    # Consultas ao banco (Repository Layer interno)
    # -----------------------------------------------------------------------

    def buscar_permissoes(self) -> dict:
        """Busca as permissões do usuário no banco."""
        return get_permissoes(self._db)

    # -----------------------------------------------------------------------
    # Cadastro de Ativo
    # -----------------------------------------------------------------------

    def cadastrar_ativo(self, payload: AtivoCreate) -> AtivoPatrimonial:
        """Cadastra um bem patrimonial e calcula sua depreciaÃ§Ã£o mensal linear.

        FÃ³rmula de depreciaÃ§Ã£o (mÃ©todo linear / linha reta)::

            depreciacao_mensal = (valor_aquisicao - valor_residual)
                                 / (vida_util_anos Ã— 12)

        O campo depreciacao_mensal_calculada Ã© preenchido automaticamente
        pelo sistema â€” nunca deve ser informado pelo usuÃ¡rio.

        Args:
            payload: Dados validados pelo schema AtivoCreate.

        Returns:
            InstÃ¢ncia de AtivoPatrimonial persistida com depreciaÃ§Ã£o calculada
            (sem commit).

        Raises:
            ValueError: Se a categoria for invÃ¡lida.

        Example::

            ativo = service.cadastrar_ativo(payload)
            logging.info(f"DepreciaÃ§Ã£o mensal: R$ {ativo.depreciacao_mensal_calculada}")
        """
        if payload.categoria not in CATEGORIAS_ATIVO:
            raise ValueError(
                f"Categoria '{payload.categoria}' invÃ¡lida. "
                f"Categorias vÃ¡lidas: {CATEGORIAS_ATIVO}."
            )

        depreciacao_mensal = self._calcular_depreciacao_mensal(
            valor_aquisicao=payload.valor_aquisicao,
            valor_residual=payload.valor_residual,
            vida_util_anos=payload.vida_util_anos,
        )

        ativo = AtivoPatrimonial(
            tenant_id=payload.tenant_id,
            nome_bem=payload.nome_bem,
            categoria=payload.categoria,
            valor_aquisicao=payload.valor_aquisicao,
            data_aquisicao=payload.data_aquisicao,
            vida_util_anos=payload.vida_util_anos,
            valor_residual=payload.valor_residual,
            depreciacao_mensal_calculada=depreciacao_mensal,
            numero_serie=payload.numero_serie,
            observacoes=payload.observacoes,
            ativo=True,
        )
        self._db.add(ativo)
        self._db.flush()

        logger.info(
            "Ativo cadastrado: id=%s nome='%s' categoria=%s valor=%s "
            "depreciacao_mensal=%s",
            ativo.id,
            ativo.nome_bem,
            ativo.categoria,
            ativo.valor_aquisicao,
            depreciacao_mensal,
        )
        return ativo

    def atualizar_ativo(
        self,
        ativo_id: uuid.UUID,
        payload: AtivoCreate,
    ) -> AtivoPatrimonial:
        """Atualiza os dados de um ativo e recalcula a depreciaÃ§Ã£o mensal.

        Args:
            ativo_id: UUID do ativo a atualizar.
            payload: Novos dados do ativo.

        Returns:
            InstÃ¢ncia de AtivoPatrimonial atualizada (sem commit).

        Raises:
            ValueError: Se o ativo nÃ£o for encontrado.
        """
        ativo = self.buscar_ativo(ativo_id)

        ativo.nome_bem = payload.nome_bem
        ativo.categoria = payload.categoria
        ativo.valor_aquisicao = payload.valor_aquisicao
        ativo.data_aquisicao = payload.data_aquisicao
        ativo.vida_util_anos = payload.vida_util_anos
        ativo.valor_residual = payload.valor_residual
        ativo.numero_serie = payload.numero_serie
        ativo.observacoes = payload.observacoes
        ativo.depreciacao_mensal_calculada = self._calcular_depreciacao_mensal(
            valor_aquisicao=payload.valor_aquisicao,
            valor_residual=payload.valor_residual,
            vida_util_anos=payload.vida_util_anos,
        )

        self._db.flush()
        logger.info("Ativo atualizado: id=%s", ativo_id)
        return ativo

    def baixar_ativo(self, ativo_id: uuid.UUID) -> AtivoPatrimonial:
        """Marca um ativo como inativo (baixado/descartado).

        Args:
            ativo_id: UUID do ativo.

        Returns:
            InstÃ¢ncia atualizada (sem commit).

        Raises:
            ValueError: Se o ativo nÃ£o for encontrado ou jÃ¡ estiver baixado.
        """
        ativo = self.buscar_ativo(ativo_id)
        if not ativo.ativo:
            raise ValueError(f"Ativo {ativo_id} jÃ¡ estÃ¡ baixado.")
        ativo.ativo = False
        self._db.flush()
        logger.info("Ativo baixado: id=%s nome='%s'", ativo_id, ativo.nome_bem)
        return ativo

    def buscar_ativo(self, ativo_id: uuid.UUID) -> AtivoPatrimonial:
        """Busca um ativo pelo UUID.

        Args:
            ativo_id: UUID do ativo.

        Returns:
            InstÃ¢ncia de AtivoPatrimonial.

        Raises:
            ValueError: Se nÃ£o encontrado.
        """
        ativo = self._db.get(AtivoPatrimonial, ativo_id)
        if ativo is None:
            raise ValueError(f"Ativo {ativo_id} nÃ£o encontrado.")
        return ativo

    def listar_ativos_tenant(
        self,
        tenant_id: uuid.UUID,
        categoria: Optional[str] = None,
        apenas_ativos: bool = True,
    ) -> List[AtivoPatrimonial]:
        """Lista ativos de um tenant com filtros opcionais.

        Args:
            tenant_id: UUID do tenant.
            categoria: Filtro por categoria (veiculo | equipamento | imovel | ferramenta).
            apenas_ativos: Se True, retorna somente bens em uso (padrÃ£o: True).

        Returns:
            Lista de AtivoPatrimonial ordenada por nome.
        """
        query = (
            select(AtivoPatrimonial)
            .where(AtivoPatrimonial.tenant_id == tenant_id)
            .order_by(AtivoPatrimonial.nome_bem)
        )
        if apenas_ativos:
            query = query.where(AtivoPatrimonial.ativo.is_(True))
        if categoria:
            query = query.where(AtivoPatrimonial.categoria == categoria)

        return list(self._db.scalars(query))

    # -----------------------------------------------------------------------
    # ROI do Ativo
    # -----------------------------------------------------------------------

    def calcular_roi_ativo(self, request: RoiAtivoRequest) -> RoiAtivoResponse:
        """Calcula o ROI (Retorno sobre Investimento) de um ativo patrimonial.

        FÃ³rmulas::

            custo_depreciacao_periodo = depreciacao_mensal Ã— periodo_meses
            lucro_bruto = faturamento_gerado - custo_depreciacao_periodo
            roi_pct = (lucro_bruto / valor_aquisicao) Ã— 100
            payback_meses = valor_aquisicao / (faturamento_mensal_medio - depreciacao_mensal)

        O ROI compara o lucro bruto gerado pelo ativo no perÃ­odo com o
        capital investido na sua aquisiÃ§Ã£o. Valores negativos indicam que
        o ativo ainda nÃ£o se pagou no perÃ­odo analisado.

        Args:
            request: Dados validados pelo schema RoiAtivoRequest.

        Returns:
            RoiAtivoResponse com ROI percentual, payback e detalhamento.

        Raises:
            ValueError: Se o ativo nÃ£o existir ou a depreciaÃ§Ã£o nÃ£o tiver
                sido calculada.

        Example::

            resp = service.calcular_roi_ativo(RoiAtivoRequest(
                ativo_id=ativo_id,
                faturamento_gerado=Decimal("15000.00"),
                periodo_meses=12,
            ))
            logging.info(f"ROI: {resp.roi_percentual:.2f}%")
            logging.info(f"Payback: {resp.payback_meses} meses")
        """
        ativo = self.buscar_ativo(request.ativo_id)

        if ativo.depreciacao_mensal_calculada is None:
            raise ValueError(
                f"O ativo {request.ativo_id} nÃ£o possui depreciaÃ§Ã£o calculada. "
                "Recadastre o ativo para que o sistema calcule a depreciaÃ§Ã£o."
            )

        dep_periodo = (
            ativo.depreciacao_mensal_calculada * Decimal(request.periodo_meses)
        ).quantize(Decimal("0.01"))

        lucro_bruto = (request.faturamento_gerado - dep_periodo).quantize(
            Decimal("0.01")
        )

        roi_percentual = (
            lucro_bruto / ativo.valor_aquisicao * Decimal("100")
        ).quantize(Decimal("0.0001"))

        # Payback: meses para recuperar o investimento com a receita lÃ­quida mensal
        faturamento_mensal = (
            request.faturamento_gerado / Decimal(request.periodo_meses)
        ).quantize(Decimal("0.0001"))
        receita_liquida_mensal = faturamento_mensal - ativo.depreciacao_mensal_calculada
        payback_meses: Optional[Decimal] = None
        if receita_liquida_mensal > Decimal("0"):
            payback_meses = (
                ativo.valor_aquisicao / receita_liquida_mensal
            ).quantize(Decimal("0.01"))

        logger.info(
            "ROI calculado: ativo=%s nome='%s' periodo=%d meses faturamento=%s "
            "dep_periodo=%s lucro=%s roi=%.4f%%",
            request.ativo_id,
            ativo.nome_bem,
            request.periodo_meses,
            request.faturamento_gerado,
            dep_periodo,
            lucro_bruto,
            roi_percentual,
        )

        return RoiAtivoResponse(
            ativo_id=ativo.id,
            nome_bem=ativo.nome_bem,
            valor_aquisicao=ativo.valor_aquisicao,
            faturamento_gerado=request.faturamento_gerado,
            custo_depreciacao_periodo=dep_periodo,
            lucro_bruto_estimado=lucro_bruto,
            roi_percentual=roi_percentual,
            payback_meses=payback_meses,
            periodo_meses=request.periodo_meses,
        )

    # -----------------------------------------------------------------------
    # Ponto de EquilÃ­brio
    # -----------------------------------------------------------------------

    def calcular_ponto_equilibrio(
        self, request: PontoEquilibrioRequest
    ) -> PontoEquilibrioResponse:
        """Calcula o ponto de equilÃ­brio operacional mensal.

        Responde: "Quantos serviÃ§os/mÃªs precisamos fechar para pagar as contas?"

        FÃ³rmulas::

            margem_contribuicao = ticket_medio Ã— (margem_variavel_pct / 100)
            servicos_PE = custo_fixo_mensal / margem_contribuicao
            faturamento_PE = servicos_PE Ã— ticket_medio
            servicos_para_lucro = ceil(servicos_PE)

        A margem variÃ¡vel percentual representa quanto da receita de cada
        serviÃ§o sobra apÃ³s os custos variÃ¡veis diretos (combustÃ­vel, insumos,
        comissÃ£o). PadrÃ£o: 100% (nenhum custo variÃ¡vel por serviÃ§o).

        Args:
            request: Dados validados pelo schema PontoEquilibrioRequest.

        Returns:
            PontoEquilibrioResponse com nÃºmero de serviÃ§os e faturamento mÃ­nimo.

        Raises:
            ValueError: Se a margem de contribuiÃ§Ã£o for zero (ticket mÃ©dio ou
                margem variÃ¡vel zerados â€” impedido pela validaÃ§Ã£o do schema).

        Example::

            resp = service.calcular_ponto_equilibrio(PontoEquilibrioRequest(
                custo_fixo_mensal=Decimal("8000.00"),
                ticket_medio=Decimal("1200.00"),
                margem_variavel_pct=Decimal("70.00"),
            ))
            logging.info(f"Feche {resp.servicos_para_lucro} serviÃ§os/mÃªs para cobrir seus custos.")
        """
        margem_contribuicao = (
            request.ticket_medio * request.margem_variavel_pct / Decimal("100")
        ).quantize(Decimal("0.0001"))

        if margem_contribuicao <= Decimal("0"):
            raise ValueError(
                "A margem de contribuiÃ§Ã£o calculada Ã© zero ou negativa. "
                "Verifique ticket_medio e margem_variavel_pct."
            )

        servicos_pe = (
            request.custo_fixo_mensal / margem_contribuicao
        ).quantize(Decimal("0.0001"))

        faturamento_pe = (servicos_pe * request.ticket_medio).quantize(
            Decimal("0.01")
        )

        # Arredonda para cima: se precisa de 6,2 serviÃ§os, precisa de 7
        servicos_para_lucro = math.ceil(float(servicos_pe))

        logger.info(
            "Ponto de equilÃ­brio calculado: custo_fixo=%s ticket=%s "
            "margem_var=%.2f%% margem_contrib=%s PE=%.4f serviÃ§os faturamento_PE=%s",
            request.custo_fixo_mensal,
            request.ticket_medio,
            request.margem_variavel_pct,
            margem_contribuicao,
            servicos_pe,
            faturamento_pe,
        )

        return PontoEquilibrioResponse(
            custo_fixo_mensal=request.custo_fixo_mensal,
            ticket_medio=request.ticket_medio,
            margem_variavel_pct=request.margem_variavel_pct,
            margem_contribuicao=margem_contribuicao,
            servicos_ponto_equilibrio=servicos_pe,
            faturamento_ponto_equilibrio=faturamento_pe,
            servicos_para_lucro=servicos_para_lucro,
        )

    # -----------------------------------------------------------------------
    # Helpers privados
    # -----------------------------------------------------------------------

    @staticmethod
    def _calcular_depreciacao_mensal(
        valor_aquisicao: Decimal,
        valor_residual: Decimal,
        vida_util_anos: int,
    ) -> Decimal:
        """Calcula a depreciaÃ§Ã£o mensal pelo mÃ©todo linear (linha reta).

        FÃ³rmula::

            depreciacao_mensal = (valor_aquisicao - valor_residual)
                                 / (vida_util_anos Ã— 12)

        Args:
            valor_aquisicao: Valor de aquisiÃ§Ã£o do bem.
            valor_residual: Valor residual ao final da vida Ãºtil.
            vida_util_anos: Vida Ãºtil em anos.

        Returns:
            DepreciaÃ§Ã£o mensal em R$ com 4 casas decimais de precisÃ£o.
        """
        valor_depreciavel = valor_aquisicao - valor_residual
        meses = Decimal(vida_util_anos * 12)
        return (valor_depreciavel / meses).quantize(Decimal("0.0001"))

    def _ativo_para_response(self, ativo: AtivoPatrimonial) -> AtivoResponse:
        """Converte modelo AtivoPatrimonial para schema AtivoResponse.

        Args:
            ativo: InstÃ¢ncia do modelo.

        Returns:
            AtivoResponse com todos os campos incluindo calculados.
        """
        return AtivoResponse(
            id=ativo.id,
            tenant_id=ativo.tenant_id,
            nome_bem=ativo.nome_bem,
            categoria=ativo.categoria,
            valor_aquisicao=ativo.valor_aquisicao,
            data_aquisicao=ativo.data_aquisicao,
            vida_util_anos=ativo.vida_util_anos,
            valor_residual=ativo.valor_residual,
            depreciacao_mensal_calculada=ativo.depreciacao_mensal_calculada,
            depreciacao_acumulada=ativo.depreciacao_acumulada,
            valor_contabil_atual=ativo.valor_contabil_atual,
            meses_vida_util=ativo.meses_vida_util,
            numero_serie=ativo.numero_serie,
            observacoes=ativo.observacoes,
            ativo=ativo.ativo,
            criado_em=ativo.criado_em,
            atualizado_em=ativo.atualizado_em,
        )

