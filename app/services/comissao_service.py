"""
Service layer para cÃ¡lculo de comissÃµes de vendedores.

Regra do Espelho:
    Se o vendedor concedeu X% de desconto sobre o preÃ§o de tabela, a BASE
    de cÃ¡lculo da comissÃ£o dele Ã© reduzida proporcionalmente em X%.
    Isso desencoraja descontos desnecessÃ¡rios sem punir o vendedor por
    negociaÃ§Ãµes legÃ­timas com escala de volume.

FÃ³rmula::

    desconto_pct = (preco_tabela - preco_aplicado) / preco_tabela Ã— 100
    base_comissao = valor_liquido_orcamento Ã— (1 - desconto_pct / 100)
    comissao_final = base_comissao Ã— (percentual_comissao_vendedor / 100)
"""

import logging
import uuid
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models.financeiro import Orcamento, OrcamentoItem, ServicoPreco

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Resultado do cÃ¡lculo de comissÃ£o
# ---------------------------------------------------------------------------


@dataclass
class ResultadoComissao:
    """Detalhamento do cÃ¡lculo de comissÃ£o para um vendedor em um orÃ§amento.

    Attributes:
        orcamento_id: UUID do orÃ§amento analisado.
        vendedor_id: UUID do vendedor.
        valor_liquido_orcamento: Valor lÃ­quido do orÃ§amento (apÃ³s desconto geral).
        desconto_medio_pct: Percentual mÃ©dio de desconto dado pelo vendedor
            nos itens, ponderado pelo subtotal de cada item.
        base_comissao: Base de cÃ¡lculo da comissÃ£o apÃ³s aplicaÃ§Ã£o do espelho.
        percentual_comissao_vendedor: % de comissÃ£o contratual do vendedor.
        comissao_final: Valor monetÃ¡rio da comissÃ£o a pagar (R$).
        espelho_aplicado: True se algum desconto manual foi detectado e
            reduziu a base de comissÃ£o.
    """

    orcamento_id: uuid.UUID
    vendedor_id: uuid.UUID
    valor_liquido_orcamento: Decimal
    desconto_medio_pct: Decimal
    base_comissao: Decimal
    percentual_comissao_vendedor: Decimal
    comissao_final: Decimal
    espelho_aplicado: bool


# ---------------------------------------------------------------------------
# ComissaoService
# ---------------------------------------------------------------------------


class ComissaoService:
    """ServiÃ§o para cÃ¡lculo de comissÃµes com a Regra do Espelho.

    Recebe uma Session ativa e nÃ£o faz commit internamente.

    Args:
        db: SessÃ£o ativa do SQLAlchemy 2.0.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def calcular_comissao(
        self,
        orcamento_id: uuid.UUID,
        vendedor_id: uuid.UUID,
    ) -> ResultadoComissao:
        """Calcula a comissÃ£o do vendedor aplicando a Regra do Espelho.

        Passos:
        1. Busca o orÃ§amento aprovado/faturado com seus itens.
        2. Para cada item, compara o preco_aplicado com o preco_base do
           serviÃ§o (preÃ§o de tabela sem escala de volume) para detectar
           descontos manuais.
        3. Calcula o desconto mÃ©dio ponderado pelo subtotal de cada item.
        4. Reduz a base de cÃ¡lculo da comissÃ£o proporcionalmente ao desconto
           mÃ©dio (Regra do Espelho).
        5. Aplica o percentual de comissÃ£o contratual do vendedor.

        Nota: Descontos oriundos de escala de volume NÃƒO penalizam a comissÃ£o
        â€” apenas descontos manuais (preco_aplicado < preco_escala calculado).

        Args:
            orcamento_id: UUID do orÃ§amento a analisar.
            vendedor_id: UUID do vendedor (deve ser o usuario_id do orÃ§amento).

        Returns:
            ResultadoComissao com todos os valores detalhados.

        Raises:
            ValueError: Se o orÃ§amento nÃ£o existir, o vendedor nÃ£o for o
                emissor, ou o orÃ§amento estiver em status inelegÃ­vel
                (rascunho ou cancelado).

        Example::

            resultado = service.calcular_comissao(
                orcamento_id=orcamento_id,
                vendedor_id=vendedor_id,
            )
            logging.info(f"ComissÃ£o a pagar: R$ {resultado.comissao_final}")
        """
        orcamento = self._buscar_orcamento_com_itens(orcamento_id)

        if str(orcamento.usuario_id) != str(vendedor_id):
            raise ValueError(
                f"Vendedor {vendedor_id} nÃ£o Ã© o emissor do orÃ§amento {orcamento_id}. "
                f"Emissor registrado: {orcamento.usuario_id}."
            )

        if orcamento.status in ("rascunho", "cancelado"):
            raise ValueError(
                f"ComissÃ£o nÃ£o pode ser calculada para orÃ§amentos com status "
                f"'{orcamento.status}'. Aguarde aprovaÃ§Ã£o ou faturamento."
            )

        percentual_vendedor = self._buscar_percentual_comissao(vendedor_id)
        desconto_medio_pct = self._calcular_desconto_medio_ponderado(orcamento)
        espelho_aplicado = desconto_medio_pct > Decimal("0")

        valor_liquido = orcamento.valor_total_liquido
        fator_espelho = Decimal("1") - (desconto_medio_pct / Decimal("100"))
        base_comissao = (valor_liquido * fator_espelho).quantize(Decimal("0.01"))
        comissao_final = (
            base_comissao * percentual_vendedor / Decimal("100")
        ).quantize(Decimal("0.01"))

        if espelho_aplicado:
            logger.info(
                "Regra do Espelho aplicada: orcamento=%s vendedor=%s "
                "desconto_medio=%.2f%% base_original=%s base_ajustada=%s "
                "comissao=%s",
                orcamento_id,
                vendedor_id,
                desconto_medio_pct,
                valor_liquido,
                base_comissao,
                comissao_final,
            )
        else:
            logger.info(
                "ComissÃ£o calculada sem espelho: orcamento=%s vendedor=%s "
                "base=%s pct=%.2f%% comissao=%s",
                orcamento_id,
                vendedor_id,
                base_comissao,
                percentual_vendedor,
                comissao_final,
            )

        return ResultadoComissao(
            orcamento_id=orcamento_id,
            vendedor_id=vendedor_id,
            valor_liquido_orcamento=valor_liquido,
            desconto_medio_pct=desconto_medio_pct.quantize(Decimal("0.0001")),
            base_comissao=base_comissao,
            percentual_comissao_vendedor=percentual_vendedor,
            comissao_final=comissao_final,
            espelho_aplicado=espelho_aplicado,
        )

    # -----------------------------------------------------------------------
    # Helpers privados
    # -----------------------------------------------------------------------

    def _buscar_orcamento_com_itens(self, orcamento_id: uuid.UUID) -> Orcamento:
        """Carrega o orÃ§amento com itens e serviÃ§os via eager load.

        Args:
            orcamento_id: UUID do orÃ§amento.

        Returns:
            InstÃ¢ncia de Orcamento com itens â†’ servico carregados.

        Raises:
            ValueError: Se nÃ£o encontrado.
        """
        orcamento = self._db.scalar(
            select(Orcamento)
            .options(
                selectinload(Orcamento.itens).selectinload(OrcamentoItem.servico)
                .selectinload(ServicoPreco.regras_escala)
            )
            .where(Orcamento.id == orcamento_id)
        )
        if orcamento is None:
            raise ValueError(f"OrÃ§amento {orcamento_id} nÃ£o encontrado.")
        return orcamento

    def _calcular_desconto_medio_ponderado(self, orcamento: Orcamento) -> Decimal:
        """Calcula o desconto mÃ©dio ponderado pelo subtotal de cada item.

        Compara o preco_aplicado de cada item com o preco_base do serviÃ§o
        (tabela mestre). Descontos de escala de volume NÃƒO sÃ£o penalizados:
        compara com o preco_base, nÃ£o com o preco_escala calculado.

        O desconto Ã© ponderado pelo subtotal de cada item para que itens
        maiores tenham mais peso no resultado final.

        Args:
            orcamento: InstÃ¢ncia de Orcamento com itens e serviÃ§os carregados.

        Returns:
            Percentual mÃ©dio de desconto ponderado (0 a 100).
        """
        soma_ponderada = Decimal("0")
        soma_pesos = Decimal("0")

        for item in orcamento.itens:
            preco_tabela = item.servico.preco_base
            preco_aplicado = item.preco_aplicado

            if preco_tabela <= Decimal("0"):
                continue

            desconto_item = max(
                Decimal("0"),
                (preco_tabela - preco_aplicado) / preco_tabela * Decimal("100"),
            )

            peso = item.quantidade * preco_tabela
            soma_ponderada += desconto_item * peso
            soma_pesos += peso

        if soma_pesos == Decimal("0"):
            return Decimal("0")

        return (soma_ponderada / soma_pesos).quantize(Decimal("0.0001"))

    def _buscar_percentual_comissao(self, vendedor_id: uuid.UUID) -> Decimal:
        """Busca o percentual de comissÃ£o contratual do vendedor.

        Tenta importar o model de usuÃ¡rios/vendedores do projeto principal.
        Em ambiente de desenvolvimento (sem o model disponÃ­vel), retorna
        10% como valor padrÃ£o configurÃ¡vel.

        Args:
            vendedor_id: UUID do vendedor.

        Returns:
            Percentual de comissÃ£o (ex: Decimal("10.00") para 10%).

        Raises:
            ValueError: Se o vendedor nÃ£o for encontrado.
        """
        try:
            from models.usuarios import Usuario  # type: ignore[import]

            usuario = self._db.scalar(
                select(Usuario).where(Usuario.id == vendedor_id)
            )
            if usuario is None:
                raise ValueError(f"Vendedor {vendedor_id} nÃ£o encontrado.")
            if not hasattr(usuario, "percentual_comissao"):
                logger.warning(
                    "Modelo Usuario nÃ£o tem 'percentual_comissao'. "
                    "Usando padrÃ£o de 10%%."
                )
                return Decimal("10.00")
            return Decimal(str(usuario.percentual_comissao))

        except ImportError:
            logger.warning(
                "models.usuarios nÃ£o disponÃ­vel â€” usando comissÃ£o padrÃ£o de 10%% "
                "para vendedor %s (modo dev).",
                vendedor_id,
            )
            return Decimal("10.00")

