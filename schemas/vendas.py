"""
Schemas Pydantic v2 para Vendas e Títulos Financeiros.
"""

import logging
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)

TipoTitulo = Literal["RECEBER", "PAGAR"]
StatusTitulo = Literal["pendente", "pago", "atrasado", "cancelado"]
MetodoPagamento = Literal["pix", "boleto", "cartao", "dinheiro"]
TipoVenda = Literal["AVISTA", "APRAZO"]
StatusVenda = Literal["aberta", "concluida", "cancelada"]


# ---------------------------------------------------------------------------
# DTO de parcela (usado no registrar_venda_prazo)
# ---------------------------------------------------------------------------


class ParcelaDTO(BaseModel):
    """Define uma parcela individual em uma venda a prazo.

    Attributes:
        data_vencimento: Data de vencimento desta parcela.
        valor: Valor desta parcela em reais.
        descricao: Descrição opcional (ex: 'Safra 2025 — colheita').
    """

    data_vencimento: date = Field(..., description="Data de vencimento desta parcela")
    valor: Decimal = Field(..., gt=Decimal("0"), description="Valor da parcela (> 0)")
    descricao: Optional[str] = Field(
        None, max_length=255, description="Descrição opcional da parcela"
    )

    @field_validator("valor")
    @classmethod
    def valor_positivo(cls, v: Decimal) -> Decimal:
        return v.quantize(Decimal("0.01"))

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Título Financeiro
# ---------------------------------------------------------------------------


class TituloFinanceiroCreate(BaseModel):
    """Payload para criação manual de um título financeiro.

    Attributes:
        tenant_id: UUID do tenant.
        cliente_id: UUID do cliente.
        orcamento_id: UUID do orçamento de origem (opcional).
        tipo: 'RECEBER' ou 'PAGAR'.
        valor_original: Valor nominal do título.
        data_emissao: Data de emissão.
        data_vencimento: Data de vencimento.
        metodo_pagamento: Forma de pagamento prevista.
        parcela_numero: Número da parcela.
        parcela_total: Total de parcelas.
    """

    tenant_id: uuid.UUID
    cliente_id: uuid.UUID
    orcamento_id: Optional[uuid.UUID] = None
    tipo: TipoTitulo = Field(..., description="RECEBER ou PAGAR")
    valor_original: Decimal = Field(..., gt=Decimal("0"), description="Valor nominal > 0")
    data_emissao: date = Field(default_factory=date.today)
    data_vencimento: date = Field(..., description="Data de vencimento do título")
    metodo_pagamento: Optional[MetodoPagamento] = None
    parcela_numero: Optional[int] = Field(None, ge=1)
    parcela_total: Optional[int] = Field(None, ge=1)

    @field_validator("valor_original")
    @classmethod
    def arredondar_valor(cls, v: Decimal) -> Decimal:
        return v.quantize(Decimal("0.01"))

    @model_validator(mode="after")
    def vencimento_apos_emissao(self) -> "TituloFinanceiroCreate":
        if self.data_vencimento < self.data_emissao:
            raise ValueError("data_vencimento não pode ser anterior a data_emissao.")
        return self

    @model_validator(mode="after")
    def parcelas_consistentes(self) -> "TituloFinanceiroCreate":
        if (self.parcela_numero is None) != (self.parcela_total is None):
            raise ValueError(
                "parcela_numero e parcela_total devem ser informados juntos ou omitidos juntos."
            )
        if self.parcela_numero and self.parcela_total:
            if self.parcela_numero > self.parcela_total:
                raise ValueError("parcela_numero não pode ser maior que parcela_total.")
        return self

    model_config = {"from_attributes": True}


class TituloFinanceiroResponse(TituloFinanceiroCreate):
    """Resposta completa de um título com campos gerados pelo banco.

    Attributes:
        id: UUID do título.
        venda_id: UUID da venda de origem.
        status: Estado atual do título.
        valor_liquidado: Valor efetivamente pago.
        data_pagamento: Data de liquidação.
        saldo_residual: Saldo devedor após pagamento parcial (calculado).
        esta_vencido: True se vencido e não pago.
        criado_em: Timestamp de criação.
        atualizado_em: Timestamp de atualização.
    """

    id: uuid.UUID
    venda_id: Optional[uuid.UUID] = None
    status: StatusTitulo = "pendente"
    valor_liquidado: Optional[Decimal] = None
    data_pagamento: Optional[date] = None
    saldo_residual: Optional[Decimal] = None
    esta_vencido: bool = False
    criado_em: datetime
    atualizado_em: datetime


# ---------------------------------------------------------------------------
# Venda
# ---------------------------------------------------------------------------


class VendaCreate(BaseModel):
    """Payload base para criação de uma venda.

    Attributes:
        tenant_id: UUID do tenant.
        orcamento_id: UUID do orçamento aprovado.
        cliente_id: UUID do cliente.
        metodo_pagamento: Forma de pagamento (à vista).
    """

    tenant_id: uuid.UUID
    orcamento_id: uuid.UUID
    cliente_id: uuid.UUID
    metodo_pagamento: MetodoPagamento = Field(
        ..., description="Forma de pagamento para venda à vista"
    )

    model_config = {"from_attributes": True}


class VendaPrazoCreate(BaseModel):
    """Payload para criação de venda a prazo com múltiplas parcelas.

    Attributes:
        tenant_id: UUID do tenant.
        orcamento_id: UUID do orçamento aprovado.
        cliente_id: UUID do cliente.
        parcelas: Lista de parcelas com data de vencimento e valor.
            A soma dos valores deve ser igual ao valor do orçamento.
    """

    tenant_id: uuid.UUID
    orcamento_id: uuid.UUID
    cliente_id: uuid.UUID
    parcelas: List[ParcelaDTO] = Field(
        ..., min_length=2, description="Mínimo 2 parcelas para venda a prazo"
    )

    @model_validator(mode="after")
    def parcelas_ordenadas(self) -> "VendaPrazoCreate":
        """Garante que as parcelas estejam em ordem cronológica."""
        datas = [p.data_vencimento for p in self.parcelas]
        if datas != sorted(datas):
            raise ValueError(
                "As parcelas devem estar em ordem cronológica crescente de data_vencimento."
            )
        return self

    model_config = {"from_attributes": True}


class VendaResponse(BaseModel):
    """Resposta completa de uma venda com seus títulos gerados.

    Attributes:
        id: UUID da venda.
        tenant_id: UUID do tenant.
        orcamento_id: UUID do orçamento de origem.
        cliente_id: UUID do cliente.
        valor_total: Valor total da venda.
        tipo_venda: AVISTA ou APRAZO.
        status: Estado atual.
        total_liquidado: Soma dos valores já pagos (calculado).
        esta_quitada: True se todos os títulos estão pagos.
        criado_em: Timestamp de criação.
        titulos: Lista de títulos financeiros gerados.
    """

    id: uuid.UUID
    tenant_id: uuid.UUID
    orcamento_id: uuid.UUID
    cliente_id: uuid.UUID
    valor_total: Decimal
    tipo_venda: TipoVenda
    status: StatusVenda
    total_liquidado: Decimal = Decimal("0.00")
    esta_quitada: bool = False
    criado_em: datetime
    titulos: List[TituloFinanceiroResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Baixa de Pagamento
# ---------------------------------------------------------------------------


class BaixaPagamentoRequest(BaseModel):
    """Payload para registrar o pagamento (baixa) de um título.

    Attributes:
        titulo_id: UUID do título a ser baixado.
        data_pagamento: Data efetiva de recebimento/pagamento.
        valor_pago: Valor efetivamente recebido. Se menor que o valor
            original, um título residual é criado automaticamente.
        metodo_pagamento: Forma de pagamento utilizada.
        observacao: Observação livre (ex: número do comprovante Pix).
    """

    titulo_id: uuid.UUID = Field(..., description="UUID do título a baixar")
    data_pagamento: date = Field(
        default_factory=date.today,
        description="Data efetiva de recebimento/pagamento",
    )
    valor_pago: Decimal = Field(
        ..., gt=Decimal("0"), description="Valor efetivamente pago (deve ser > 0)"
    )
    metodo_pagamento: MetodoPagamento = Field(
        ..., description="Forma de pagamento utilizada"
    )
    observacao: Optional[str] = Field(
        None, max_length=500, description="Observação livre (ex: ID do Pix)"
    )

    @field_validator("valor_pago")
    @classmethod
    def arredondar_valor(cls, v: Decimal) -> Decimal:
        return v.quantize(Decimal("0.01"))

    model_config = {"from_attributes": True}


class BaixaPagamentoResponse(BaseModel):
    """Resposta após a baixa de um título.

    Attributes:
        titulo_baixado: Título atualizado após a baixa.
        titulo_residual: Título residual gerado (se pagamento parcial).
        pagamento_parcial: True se o valor pago foi menor que o original.
        saldo_quitado: Valor total quitado nesta operação.
    """

    titulo_baixado: TituloFinanceiroResponse
    titulo_residual: Optional[TituloFinanceiroResponse] = None
    pagamento_parcial: bool = False
    saldo_quitado: Decimal

    model_config = {"from_attributes": True}
