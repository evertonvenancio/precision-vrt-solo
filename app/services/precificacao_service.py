"""
Service layer para cÃ¡lculo de orÃ§amentos e descontos transacionais.

Regras de ouro:
- PreÃ§o unitÃ¡rio com escala de volume â€” nunca pacotes engessados.
- Desconto do vendedor Ã© TRANSACIONAL: salvo apenas no item do orÃ§amento,
  nunca na tabela mestre 'servicos_precos'.
- Toda alteraÃ§Ã£o de preÃ§o exige senha do usuÃ¡rio e justificativa para auditoria.
"""

import hashlib
import logging
import uuid
from decimal import Decimal
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.financeiro import Orcamento, OrcamentoItem, ServicoPreco
from schemas.financeiro import OrcamentoItemCreate

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tipos auxiliares
# ---------------------------------------------------------------------------


class ItemCalculado:
    """Resultado do cÃ¡lculo de um item de orÃ§amento.

    Attributes:
        servico_id: UUID do serviÃ§o.
        nome_servico: Nome comercial do serviÃ§o.
        unidade: Unidade de medida.
        quantidade: Quantidade solicitada.
        preco_base: PreÃ§o unitÃ¡rio base do catÃ¡logo.
        preco_escala: PreÃ§o unitÃ¡rio apÃ³s aplicaÃ§Ã£o da regra de volume.
        subtotal: Valor total do item (quantidade Ã— preco_escala).
        escala_ativada: True se uma regra de volume foi aplicada.
    """

    def __init__(
        self,
        servico_id: uuid.UUID,
        nome_servico: str,
        unidade: str,
        quantidade: Decimal,
        preco_base: Decimal,
        preco_escala: Decimal,
    ) -> None:
        self.servico_id = servico_id
        self.nome_servico = nome_servico
        self.unidade = unidade
        self.quantidade = quantidade
        self.preco_base = preco_base
        self.preco_escala = preco_escala
        self.subtotal = (quantidade * preco_escala).quantize(Decimal("0.01"))
        self.escala_ativada = preco_escala != preco_base

    def __repr__(self) -> str:
        return (
            f"<ItemCalculado '{self.nome_servico}' qtd={self.quantidade} "
            f"preco={self.preco_escala} subtotal={self.subtotal}>"
        )


class ResultadoOrcamento:
    """Resultado agregado do cÃ¡lculo de um orÃ§amento.

    Attributes:
        cliente_id: UUID do cliente.
        itens: Lista de ItemCalculado.
        valor_total_bruto: Soma dos subtotais de todos os itens.
    """

    def __init__(self, cliente_id: uuid.UUID, itens: List[ItemCalculado]) -> None:
        self.cliente_id = cliente_id
        self.itens = itens
        self.valor_total_bruto = sum(
            (i.subtotal for i in itens), Decimal("0.00")
        )


# ---------------------------------------------------------------------------
# PrecificacaoService
# ---------------------------------------------------------------------------


class PrecificacaoService:
    """ServiÃ§o de cÃ¡lculo de preÃ§os e descontos transacionais.

    Todas as operaÃ§Ãµes recebem uma Session ativa e nÃ£o fazem commit
    internamente â€” o chamador (endpoint FastAPI) controla a transaÃ§Ã£o.

    Args:
        db: SessÃ£o ativa do SQLAlchemy 2.0.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    # -----------------------------------------------------------------------
    # CÃ¡lculo de OrÃ§amento
    # -----------------------------------------------------------------------

    def calcular_orcamento(
        self,
        itens: List[OrcamentoItemCreate],
        cliente_id: uuid.UUID,
    ) -> ResultadoOrcamento:
        """Calcula o valor de um orÃ§amento aplicando regras de escala de volume.

        Para cada item, busca o serviÃ§o no catÃ¡logo, percorre as regras de
        escala de volume e aplica o preÃ§o correto para a quantidade informada.
        NÃ£o persiste nada â€” apenas calcula e retorna.

        Args:
            itens: Lista de itens com servico_id, quantidade e preco_aplicado.
            cliente_id: UUID do cliente para o qual o orÃ§amento estÃ¡ sendo
                calculado (usado para registro/contexto).

        Returns:
            ResultadoOrcamento com cada item calculado e o total bruto.

        Raises:
            ValueError: Se algum serviÃ§o referenciado nÃ£o existir no catÃ¡logo.

        Example::

            resultado = service.calcular_orcamento(itens=payload.itens,
                                                   cliente_id=payload.cliente_id)
            logging.info(resultado.valor_total_bruto)
        """
        itens_calculados: List[ItemCalculado] = []

        for item in itens:
            servico = self._buscar_servico(item.servico_id)
            preco_escala = servico.preco_para_quantidade(item.quantidade)

            calculado = ItemCalculado(
                servico_id=servico.id,
                nome_servico=servico.nome_servico,
                unidade=servico.unidade,
                quantidade=item.quantidade,
                preco_base=servico.preco_base,
                preco_escala=preco_escala,
            )
            itens_calculados.append(calculado)

            if calculado.escala_ativada:
                logger.debug(
                    "Escala de volume aplicada: serviÃ§o='%s' qtd=%s "
                    "preco_base=%s â†’ preco_escala=%s",
                    servico.nome_servico,
                    item.quantidade,
                    servico.preco_base,
                    preco_escala,
                )

        resultado = ResultadoOrcamento(
            cliente_id=cliente_id, itens=itens_calculados
        )
        logger.info(
            "OrÃ§amento calculado: cliente=%s itens=%d total_bruto=%s",
            cliente_id,
            len(itens_calculados),
            resultado.valor_total_bruto,
        )
        return resultado

    # -----------------------------------------------------------------------
    # Desconto Transacional
    # -----------------------------------------------------------------------

    def aplicar_desconto_transacional(
        self,
        orcamento_id: uuid.UUID,
        servico_id: uuid.UUID,
        novo_preco: Decimal,
        senha_usuario: str,
        usuario_id: uuid.UUID,
        justificativa: str,
    ) -> OrcamentoItem:
        """Aplica desconto manual em um item de orÃ§amento de forma transacional.

        O novo preÃ§o Ã© salvo APENAS no item daquele orÃ§amento especÃ­fico â€”
        a tabela mestre 'servicos_precos' nunca Ã© alterada. Ao final do ciclo
        (fechamento do orÃ§amento), o preÃ§o transacional nÃ£o se propaga para
        novos orÃ§amentos.

        Exige autenticaÃ§Ã£o por senha para garantir que apenas usuÃ¡rios
        autorizados concedam descontos manuais.

        Args:
            orcamento_id: UUID do orÃ§amento a modificar.
            servico_id: UUID do serviÃ§o cujo preÃ§o serÃ¡ alterado.
            novo_preco: Novo preÃ§o unitÃ¡rio a aplicar (deve ser > 0).
            senha_usuario: Senha em texto claro do usuÃ¡rio solicitante.
                SerÃ¡ validada contra o hash armazenado.
            usuario_id: UUID do usuÃ¡rio que solicita o desconto.
            justificativa: Texto obrigatÃ³rio explicando o motivo do desconto
                (mÃ­nimo 10 caracteres, salvo para auditoria).

        Returns:
            InstÃ¢ncia de OrcamentoItem atualizada com o novo preco_aplicado
            e a justificativa registrada (sem commit).

        Raises:
            ValueError: Se o orÃ§amento ou item nÃ£o existir, senha invÃ¡lida,
                justificativa muito curta, preÃ§o invÃ¡lido ou orÃ§amento nÃ£o
                estiver em status 'rascunho'.
            PermissionError: Se a senha do usuÃ¡rio for invÃ¡lida.

        Example::

            item = service.aplicar_desconto_transacional(
                orcamento_id=orcamento_id,
                servico_id=servico_id,
                novo_preco=Decimal("9.50"),
                senha_usuario="senha_secreta",
                usuario_id=usuario_id,
                justificativa="Cliente fidelidade â€“ negociaÃ§Ã£o direta com gerente",
            )
        """
        if len(justificativa.strip()) < 10:
            raise ValueError(
                "Justificativa deve ter ao menos 10 caracteres para fins de auditoria."
            )

        if novo_preco <= Decimal("0"):
            raise ValueError("novo_preco deve ser maior que zero.")

        self._validar_senha_usuario(usuario_id, senha_usuario)

        orcamento = self._db.scalar(
            select(Orcamento).where(Orcamento.id == orcamento_id)
        )
        if orcamento is None:
            raise ValueError(f"OrÃ§amento {orcamento_id} nÃ£o encontrado.")

        if orcamento.status != "rascunho":
            raise ValueError(
                f"Desconto transacional sÃ³ pode ser aplicado em orÃ§amentos no "
                f"status 'rascunho'. Status atual: '{orcamento.status}'."
            )

        item = self._db.scalar(
            select(OrcamentoItem).where(
                OrcamentoItem.orcamento_id == orcamento_id,
                OrcamentoItem.servico_id == servico_id,
            )
        )
        if item is None:
            raise ValueError(
                f"Item com servico_id={servico_id} nÃ£o encontrado no "
                f"orÃ§amento {orcamento_id}."
            )

        servico = self._buscar_servico(servico_id)
        preco_anterior = item.preco_aplicado
        percentual_desconto = (
            (preco_anterior - novo_preco) / preco_anterior * 100
        ).quantize(Decimal("0.01"))

        item.preco_aplicado = novo_preco.quantize(Decimal("0.01"))
        item.justificativa_desconto = (
            f"[Desconto transacional por usuÃ¡rio {usuario_id}] {justificativa.strip()}"
        )

        orcamento.recalcular_totais()
        self._db.flush()

        logger.info(
            "Desconto transacional aplicado: orcamento=%s serviÃ§o='%s' "
            "preco_anterior=%s â†’ novo_preco=%s (%.2f%% desconto) "
            "usuario=%s justificativa='%s'",
            orcamento_id,
            servico.nome_servico,
            preco_anterior,
            novo_preco,
            percentual_desconto,
            usuario_id,
            justificativa.strip(),
        )
        return item

    # -----------------------------------------------------------------------
    # Helpers privados
    # -----------------------------------------------------------------------

    def _buscar_servico(self, servico_id: uuid.UUID) -> ServicoPreco:
        """Busca serviÃ§o pelo UUID com regras de escala carregadas.

        Args:
            servico_id: UUID do serviÃ§o.

        Returns:
            InstÃ¢ncia de ServicoPreco.

        Raises:
            ValueError: Se nÃ£o encontrado.
        """
        from sqlalchemy.orm import selectinload

        servico = self._db.scalar(
            select(ServicoPreco)
            .options(selectinload(ServicoPreco.regras_escala))
            .where(ServicoPreco.id == servico_id)
        )
        if servico is None:
            raise ValueError(f"ServiÃ§o {servico_id} nÃ£o encontrado no catÃ¡logo.")
        return servico

    def _validar_senha_usuario(
        self, usuario_id: uuid.UUID, senha_usuario: str
    ) -> None:
        """Valida a senha do usuÃ¡rio contra o hash armazenado no banco.

        Utiliza SHA-256 como mecanismo de hash. Em produÃ§Ã£o, substituir por
        bcrypt ou Argon2 via passlib.

        Args:
            usuario_id: UUID do usuÃ¡rio solicitante.
            senha_usuario: Senha em texto claro fornecida na requisiÃ§Ã£o.

        Raises:
            PermissionError: Se o usuÃ¡rio nÃ£o existir ou a senha for invÃ¡lida.
        """
        # ImportaÃ§Ã£o inline para nÃ£o criar dependÃªncia circular com o modelo
        # de usuÃ¡rios (definido em models/usuarios.py do projeto principal).
        try:
            from models.usuarios import Usuario  # type: ignore[import]
        except ImportError:
            logger.warning(
                "models.usuarios nÃ£o disponÃ­vel â€” validaÃ§Ã£o de senha pulada (modo dev)."
            )
            return

        usuario = self._db.scalar(
            select(Usuario).where(Usuario.id == usuario_id)
        )
        if usuario is None:
            raise PermissionError(f"UsuÃ¡rio {usuario_id} nÃ£o encontrado.")

        hash_fornecida = hashlib.sha256(senha_usuario.encode()).hexdigest()
        if not hasattr(usuario, "senha_hash") or usuario.senha_hash != hash_fornecida:
            logger.warning(
                "Tentativa de desconto transacional com senha invÃ¡lida: usuario=%s",
                usuario_id,
            )
            raise PermissionError("Senha invÃ¡lida. Desconto transacional negado.")


