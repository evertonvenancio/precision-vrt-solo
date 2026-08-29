"""
Schemas Pydantic v2 para Gestão de Ativos Patrimoniais.
"""

import logging
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)

CategoriaAtivo = Literal["veiculo", "equipamento", "imovel", "ferramenta"]


# ---------------------------------------------------------------------------
# Ativo Patrimonial
# ---------------------------------------------------------------------------


class AtivoCreate(BaseModel):
    """Payload para cadastro de um novo ativo patrimonial.

    Attributes:
        tenant_id: UUID do tenant.
        nome_bem: Nome descritivo do bem.
        categoria: Categoria do ativo.
        valor_aquisicao: Valor de compra (> 0).
        data_aquisicao: Data de aquisição.
        vida_util_anos: Vida útil em anos (> 0).
        valor_residual: Valor residual ao final da vida útil (padrão: 0).
        numero_serie: Número de série ou patrimônio (opcional).
        observacoes: Notas livres (opcional).
    """

    tenant_id: uuid.UUID = Field(..., description="UUID do tenant")
    nome_bem: str = Field(
        ..., min_length=2, max_length=255, description="Nome descritivo do bem"
    )
    categoria: CategoriaAtivo = Field(
        ..., description="Categoria: veiculo | equipamento | imovel | ferramenta"
    )
    valor_aquisicao: Decimal = Field(
        ..., gt=Decimal("0"), description="Valor de aquisição em R$ (deve ser > 0)"
    )
    data_aquisicao: date = Field(..., description="Data de aquisição do bem")
    vida_util_anos: int = Field(
        ..., gt=0, le=100, description="Vida útil estimada em anos (1 a 100)"
    )
    valor_residual: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0"),
        description="Valor residual ao final da vida útil (padrão: R$ 0,00)",
    )
    numero_serie: Optional[str] = Field(
        None, max_length=100, description="Número de série ou código de patrimônio"
    )
    observacoes: Optional[str] = Field(
        None, max_length=1000, description="Notas livres sobre o bem"
    )

    @field_validator("valor_aquisicao", "valor_residual")
    @classmethod
    def arredondar_valores(cls, v: Decimal) -> Decimal:
        return v.quantize(Decimal("0.01"))

    @model_validator(mode="after")
    def residual_menor_que_aquisicao(self) -> "AtivoCreate":
        """Garante que valor_residual < valor_aquisicao."""
        if self.valor_residual >= self.valor_aquisicao:
            raise ValueError(
                "valor_residual deve ser menor que valor_aquisicao. "
                f"Recebido: residual={self.valor_residual}, aquisicao={self.valor_aquisicao}."
            )
        return self

    model_config = {"from_attributes": True}


class AtivoResponse(AtivoCreate):
    """Resposta completa de um ativo com campos calculados pelo sistema.

    Attributes:
        id: UUID do ativo.
        depreciacao_mensal_calculada: Depreciação mensal calculada (R$).
        depreciacao_acumulada: Depreciação acumulada até hoje (R$).
        valor_contabil_atual: Valor contábil atual (R$).
        meses_vida_util: Total de meses de vida útil.
        ativo: True se o bem está em uso.
        criado_em: Timestamp de criação.
        atualizado_em: Timestamp de atualização.
    """

    id: uuid.UUID
    depreciacao_mensal_calculada: Optional[Decimal] = Field(
        None, description="Depreciação mensal calculada pelo sistema (R$)"
    )
    depreciacao_acumulada: Optional[Decimal] = Field(
        None, description="Depreciação acumulada desde aquisição até hoje (R$)"
    )
    valor_contabil_atual: Optional[Decimal] = Field(
        None, description="Valor contábil atual do bem (R$)"
    )
    meses_vida_util: int = Field(..., description="Total de meses de vida útil")
    ativo: bool = True
    criado_em: datetime
    atualizado_em: datetime


# ---------------------------------------------------------------------------
# ROI
# ---------------------------------------------------------------------------


class RoiAtivoRequest(BaseModel):
    """Payload para cálculo de ROI de um ativo.

    Attributes:
        ativo_id: UUID do ativo a analisar.
        faturamento_gerado: Faturamento total gerado pelo uso do ativo (R$).
            Ex: área atendida pelo quadriciclo × preço do serviço.
        periodo_meses: Período de apuração em meses (padrão: 12).
    """

    ativo_id: uuid.UUID = Field(..., description="UUID do ativo")
    faturamento_gerado: Decimal = Field(
        ..., gt=Decimal("0"), description="Faturamento gerado pelo ativo no período (R$)"
    )
    periodo_meses: int = Field(
        default=12, gt=0, le=120, description="Período de apuração em meses (padrão: 12)"
    )

    @field_validator("faturamento_gerado")
    @classmethod
    def arredondar(cls, v: Decimal) -> Decimal:
        return v.quantize(Decimal("0.01"))

    model_config = {"from_attributes": True}


class RoiAtivoResponse(BaseModel):
    """Resultado do cálculo de ROI de um ativo.

    Attributes:
        ativo_id: UUID do ativo analisado.
        nome_bem: Nome do ativo.
        valor_aquisicao: Valor de aquisição do bem.
        faturamento_gerado: Faturamento informado no período.
        custo_depreciacao_periodo: Custo de depreciação no período analisado.
        lucro_bruto_estimado: Faturamento menos custo de depreciação no período.
        roi_percentual: ROI = (lucro_bruto / valor_aquisicao) × 100 (%).
        payback_meses: Meses estimados para recuperar o investimento.
        periodo_meses: Período de apuração informado.
    """

    ativo_id: uuid.UUID
    nome_bem: str
    valor_aquisicao: Decimal
    faturamento_gerado: Decimal
    custo_depreciacao_periodo: Decimal
    lucro_bruto_estimado: Decimal
    roi_percentual: Decimal = Field(..., description="ROI em % sobre o valor de aquisição")
    payback_meses: Optional[Decimal] = Field(
        None, description="Meses estimados para recuperar o investimento (None se prejuízo)"
    )
    periodo_meses: int

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Ponto de Equilíbrio
# ---------------------------------------------------------------------------


class PontoEquilibrioRequest(BaseModel):
    """Payload para cálculo do ponto de equilíbrio operacional.

    Attributes:
        custo_fixo_mensal: Total de custos fixos mensais da operação (R$).
            Inclui depreciação, salários, aluguel, seguros, etc.
        ticket_medio: Receita média por serviço/atendimento realizado (R$).
        margem_variavel_pct: Percentual da receita que sobra após custos
            variáveis (ex: combustível, insumos). Padrão: 100% (sem custo
            variável por serviço).
    """

    custo_fixo_mensal: Decimal = Field(
        ..., gt=Decimal("0"), description="Total de custos fixos mensais (R$)"
    )
    ticket_medio: Decimal = Field(
        ..., gt=Decimal("0"), description="Receita média por serviço/atendimento (R$)"
    )
    margem_variavel_pct: Decimal = Field(
        default=Decimal("100.00"),
        gt=Decimal("0"),
        le=Decimal("100"),
        description=(
            "% da receita que sobra após custos variáveis por serviço "
            "(padrão: 100 = sem custo variável)"
        ),
    )

    @field_validator("custo_fixo_mensal", "ticket_medio")
    @classmethod
    def arredondar(cls, v: Decimal) -> Decimal:
        return v.quantize(Decimal("0.01"))

    model_config = {"from_attributes": True}


class PontoEquilibrioResponse(BaseModel):
    """Resultado do cálculo de ponto de equilíbrio.

    Attributes:
        custo_fixo_mensal: Custo fixo mensal informado.
        ticket_medio: Ticket médio informado.
        margem_variavel_pct: Margem variável percentual.
        margem_contribuicao: Valor que cada serviço contribui para cobrir fixos.
        servicos_ponto_equilibrio: Número mínimo de serviços/mês para cobrir fixos.
        faturamento_ponto_equilibrio: Faturamento mínimo mensal para cobrir fixos.
        servicos_para_lucro: Quantidade a partir da qual começa a gerar lucro
            (mesmo que ponto de equilíbrio, destacado para clareza).
    """

    custo_fixo_mensal: Decimal
    ticket_medio: Decimal
    margem_variavel_pct: Decimal
    margem_contribuicao: Decimal = Field(
        ..., description="Contribuição por serviço para cobrir custos fixos (R$)"
    )
    servicos_ponto_equilibrio: Decimal = Field(
        ..., description="Número mínimo de serviços/mês (pode ser fracionado)"
    )
    faturamento_ponto_equilibrio: Decimal = Field(
        ..., description="Faturamento mínimo mensal para cobrir todos os custos fixos"
    )
    servicos_para_lucro: int = Field(
        ..., description="Número inteiro de serviços a partir do qual há lucro"
    )

    model_config = {"from_attributes": True}
