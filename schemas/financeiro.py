"""
Schemas Pydantic v2 para Precificação Dinâmica e Orçamentos.
"""

import logging
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)

# Valores aceitos para status de orçamento
StatusOrcamento = Literal["rascunho", "aprovado", "faturado", "cancelado"]


# ---------------------------------------------------------------------------
# Serviço / Tabela de Preços
# ---------------------------------------------------------------------------


class ServicoPrecoCreate(BaseModel):
    """Payload para criação de um serviço no catálogo de preços.

    Attributes:
        tenant_id: UUID do tenant proprietário.
        nome_servico: Nome comercial do serviço.
        unidade: Unidade de medida para faturamento (ex: ha, dia, km).
        preco_base: Preço unitário base em reais. Deve ser maior que zero.
    """

    tenant_id: uuid.UUID = Field(..., description="UUID do tenant proprietário do serviço")
    nome_servico: str = Field(
        ..., min_length=2, max_length=255, description="Nome comercial do serviço"
    )
    unidade: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unidade de medida para faturamento (ex: ha, dia, km, amostra)",
    )
    preco_base: Decimal = Field(
        ..., gt=Decimal("0"), description="Preço unitário base em reais (deve ser > 0)"
    )

    @field_validator("preco_base")
    @classmethod
    def preco_base_positivo(cls, v: Decimal) -> Decimal:
        """Garante que o preço base seja estritamente positivo."""
        if v <= 0:
            raise ValueError("preco_base deve ser maior que zero")
        return v.quantize(Decimal("0.01"))

    @field_validator("unidade")
    @classmethod
    def unidade_sem_espacos_extras(cls, v: str) -> str:
        """Remove espaços extras da unidade."""
        return v.strip().lower()

    model_config = {"from_attributes": True}


class ServicoPrecoResponse(ServicoPrecoCreate):
    """Resposta completa de um serviço com campos gerados pelo banco.

    Attributes:
        id: UUID do serviço.
        criado_em: Timestamp de criação.
        regras_escala: Lista de regras de escala de volume vinculadas.
    """

    id: uuid.UUID
    criado_em: datetime
    regras_escala: List["RegraEscalaResponse"] = Field(
        default_factory=list,
        description="Regras de desconto por volume ordenadas por quantidade mínima",
    )


# ---------------------------------------------------------------------------
# Regras de Escala de Volume
# ---------------------------------------------------------------------------


class RegraEscalaCreate(BaseModel):
    """Payload para criação de uma regra de escala de volume.

    Attributes:
        servico_id: UUID do serviço ao qual a regra se aplica.
        quantidade_minima: Quantidade mínima (inteiro) para ativar o novo preço.
        novo_preco: Novo preço unitário quando a faixa é atingida. Deve ser > 0.
    """

    servico_id: uuid.UUID = Field(
        ..., description="UUID do serviço ao qual esta regra se aplica"
    )
    quantidade_minima: int = Field(
        ..., gt=0, description="Quantidade mínima para ativar este preço (> 0)"
    )
    novo_preco: Decimal = Field(
        ..., gt=Decimal("0"), description="Preço unitário a aplicar nesta faixa (> 0)"
    )

    @field_validator("novo_preco")
    @classmethod
    def novo_preco_positivo(cls, v: Decimal) -> Decimal:
        """Garante que o novo preço seja positivo e com 2 casas decimais."""
        if v <= 0:
            raise ValueError("novo_preco deve ser maior que zero")
        return v.quantize(Decimal("0.01"))

    model_config = {"from_attributes": True}


class RegraEscalaResponse(RegraEscalaCreate):
    """Resposta completa de uma regra de escala com id gerado pelo banco.

    Attributes:
        id: UUID da regra.
    """

    id: uuid.UUID


# ---------------------------------------------------------------------------
# Itens de Orçamento
# ---------------------------------------------------------------------------


class OrcamentoItemCreate(BaseModel):
    """Payload para um item dentro de um orçamento.

    O preco_aplicado é obrigatório e representa o preço congelado no momento
    da negociação — pode ser o preço de tabela, por escala ou negociado.

    Attributes:
        servico_id: UUID do serviço cotado.
        quantidade: Quantidade na unidade do serviço (> 0).
        preco_aplicado: Preço unitário efetivo negociado (> 0).
        justificativa_desconto: Texto explicativo quando o preço difere da
            tabela. Opcional, mas recomendado para auditoria.
    """

    servico_id: uuid.UUID = Field(..., description="UUID do serviço cotado")
    quantidade: Decimal = Field(
        ..., gt=Decimal("0"), description="Quantidade na unidade do serviço (deve ser > 0)"
    )
    preco_aplicado: Decimal = Field(
        ...,
        gt=Decimal("0"),
        description=(
            "Preço unitário efetivamente negociado. "
            "Congelado no orçamento — não sofre impacto de mudanças futuras no catálogo."
        ),
    )
    justificativa_desconto: Optional[str] = Field(
        None,
        max_length=500,
        description=(
            "Justificativa quando o preço aplicado difere do preço de tabela "
            "(para fins de auditoria comercial)"
        ),
    )

    @field_validator("quantidade")
    @classmethod
    def quantidade_positiva(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("quantidade deve ser maior que zero")
        return v

    @field_validator("preco_aplicado")
    @classmethod
    def preco_positivo(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("preco_aplicado deve ser maior que zero")
        return v.quantize(Decimal("0.01"))

    model_config = {"from_attributes": True}


class OrcamentoItemResponse(OrcamentoItemCreate):
    """Resposta de um item de orçamento com campos calculados.

    Attributes:
        id: UUID do item.
        subtotal: Valor calculado (quantidade × preco_aplicado).
    """

    id: uuid.UUID
    subtotal: Decimal = Field(
        ..., description="Subtotal do item (quantidade × preco_aplicado)"
    )


# ---------------------------------------------------------------------------
# Orçamento
# ---------------------------------------------------------------------------


class OrcamentoCreate(BaseModel):
    """Payload para criação de um orçamento com seus itens.

    Attributes:
        tenant_id: UUID do tenant emissor.
        cliente_id: UUID do cliente.
        usuario_id: UUID do vendedor/RT emissor.
        desconto_percentual: Desconto geral (0.00 a 100.00). Padrão: 0.
        itens: Lista de itens (deve ter ao menos 1 item).
    """

    tenant_id: uuid.UUID = Field(..., description="UUID do tenant emissor")
    cliente_id: uuid.UUID = Field(..., description="UUID do cliente destinatário")
    usuario_id: uuid.UUID = Field(..., description="UUID do vendedor/RT que emite o orçamento")
    desconto_percentual: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0"),
        le=Decimal("100"),
        description="Desconto percentual geral sobre o valor bruto (0.00 a 100.00)",
    )
    itens: List[OrcamentoItemCreate] = Field(
        ..., min_length=1, description="Lista de itens do orçamento (mínimo 1)"
    )

    @field_validator("desconto_percentual")
    @classmethod
    def desconto_no_intervalo(cls, v: Decimal) -> Decimal:
        """Garante que o desconto esteja entre 0 e 100."""
        if not (Decimal("0") <= v <= Decimal("100")):
            raise ValueError("desconto_percentual deve estar entre 0 e 100")
        return v.quantize(Decimal("0.01"))

    @model_validator(mode="after")
    def itens_nao_vazios(self) -> "OrcamentoCreate":
        """Valida que a lista de itens não esteja vazia."""
        if not self.itens:
            raise ValueError("O orçamento deve conter ao menos um item")
        return self

    model_config = {"from_attributes": True}


class OrcamentoResponse(BaseModel):
    """Resposta completa de um orçamento com totais calculados.

    Attributes:
        id: UUID do orçamento.
        tenant_id: UUID do tenant emissor.
        cliente_id: UUID do cliente.
        usuario_id: UUID do emissor.
        data_emissao: Data/hora de emissão.
        valor_total_bruto: Soma dos itens sem desconto geral.
        desconto_percentual: Desconto percentual geral.
        valor_total_liquido: Valor final após desconto.
        status: Estado atual (rascunho | aprovado | faturado | cancelado).
        criado_em: Timestamp de criação.
        atualizado_em: Timestamp de última atualização.
        itens: Lista de itens com subtotais.
    """

    id: uuid.UUID
    tenant_id: uuid.UUID
    cliente_id: uuid.UUID
    usuario_id: uuid.UUID
    data_emissao: datetime
    valor_total_bruto: Decimal = Field(
        ..., description="Soma dos itens antes do desconto percentual geral"
    )
    desconto_percentual: Decimal = Field(
        ..., description="Desconto percentual geral (0.00 a 100.00)"
    )
    valor_total_liquido: Decimal = Field(
        ..., description="Valor final após aplicação do desconto percentual"
    )
    status: StatusOrcamento = Field(
        ..., description="Estado do orçamento: rascunho | aprovado | faturado | cancelado"
    )
    criado_em: datetime
    atualizado_em: datetime
    itens: List[OrcamentoItemResponse] = Field(
        default_factory=list, description="Itens do orçamento com subtotais"
    )

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Schema para alteração de status
# ---------------------------------------------------------------------------


class OrcamentoStatusUpdate(BaseModel):
    """Payload para transição de status de um orçamento.

    Attributes:
        status: Novo status desejado.
        motivo: Motivo obrigatório para cancelamento.
    """

    status: StatusOrcamento = Field(..., description="Novo status do orçamento")
    motivo: Optional[str] = Field(
        None,
        max_length=500,
        description="Motivo (obrigatório quando status='cancelado')",
    )

    @model_validator(mode="after")
    def motivo_obrigatorio_no_cancelamento(self) -> "OrcamentoStatusUpdate":
        """Exige motivo quando o status for 'cancelado'."""
        if self.status == "cancelado" and not self.motivo:
            raise ValueError("motivo é obrigatório ao cancelar um orçamento")
        return self


# Resolve forward references
ServicoPrecoResponse.model_rebuild()
