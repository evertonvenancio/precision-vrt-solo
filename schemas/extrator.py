"""Schemas Pydantic v2 para validação de dados do Módulo Extrator.

Define schemas para:
- Criação/atualização de pontos de monitoramento
- Upload e validação de leituras
- Respostas de diagnóstico e recomendação
- Histórico temporal
- Curvas nutritivas de referência
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# =========================================================================
# Enums
# =========================================================================

class TipoExtrator(str, Enum):
    """Tipos de extratores suportados."""
    CAPSULA_SUCCAO = "capsula_sucção"
    LISIMETRO = "lisimetro"
    EXTRATOR_VACUO = "extrator_vacuo"
    HIDROPONIA = "hidroponia"


class FaseFenologica(str, Enum):
    """Fases fenológicas de culturas HF."""
    VEGETATIVO = "vegetativo"
    FLORESCIMENTO = "florescimento"
    FRUTIFICACAO = "frutificacao"
    MATURACAO = "maturacao"
    COLHEITA = "colheita"


class SistemaIrrigacao(str, Enum):
    """Sistemas de irrigação suportados."""
    GOTEJO = "gotejo"
    ASPERSAO = "aspersao"
    PIVOR = "pivor"
    HIDROPONIA = "hidroponia"
    SUBIRRIGACAO = "subirrigacao"


class MetodoAnalise(str, Enum):
    """Métodos de análise de solução."""
    LABORATORIO = "laboratorio"
    ION_METRO = "ion_metro"
    COLORIMETRO = "colorimetro"
    SENSOR = "sensor"


class StatusNutriente(str, Enum):
    """Status de nutriente relativo à curva ideal."""
    DEFICIENTE = "deficiente"
    ADEQUADO = "adequado"
    EXCESSO = "excesso"
    SEM_DADOS = "sem_dados"


class TendenciaNutriente(str, Enum):
    """Tendência do nutriente nas últimas leituras."""
    AUMENTANDO = "aumentando"
    ESTAVEL = "estavel"
    DIMINUINDO = "diminuindo"
    SEM_HISTORICO = "sem_historico"


# =========================================================================
# Pontos de Monitoramento
# =========================================================================

class PontoExtratorCreate(BaseModel):
    """Schema para criação de ponto de monitoramento."""

    codigo: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Código único do ponto",
        examples=["EXT-001", "HID-A1"],
    )
    nome: Optional[str] = Field(
        None,
        max_length=100,
        description="Nome descritivo do ponto",
    )
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Latitude em graus decimais",
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitude em graus decimais",
    )
    profundidade_cm: int = Field(
        ...,
        gt=0,
        le=300,
        description="Profundidade de instalação em cm",
    )
    capsula_id: Optional[str] = Field(
        None,
        max_length=50,
        description="ID da cápsula de sucção",
    )
    tipo_extrator: TipoExtrator = Field(
        default=TipoExtrator.CAPSULA_SUCCAO,
        description="Tipo de extrator instalado",
    )
    propriedade_id: Optional[str] = Field(None, description="ID da propriedade (UUID)")
    talhao_id: Optional[str] = Field(None, description="ID do talhão (UUID)")
    cultura: Optional[str] = Field(
        None,
        max_length=50,
        description="Cultura atual no ponto",
    )
    variedade: Optional[str] = Field(None, max_length=50)
    fase_fenologica: Optional[FaseFenologica] = None
    data_plantio: Optional[date] = None
    sistema_irrigacao: Optional[SistemaIrrigacao] = None
    eh_hidroponia: bool = Field(
        default=False,
        description="Indica se é ponto hidropônico",
    )
    observacoes: Optional[str] = None

    @field_validator("codigo")
    @classmethod
    def validar_codigo(cls, v: str) -> str:
        """Valida formato do código."""
        return v.strip().upper()


class PontoExtratorUpdate(BaseModel):
    """Schema para atualização parcial de ponto."""

    nome: Optional[str] = Field(None, max_length=100)
    cultura: Optional[str] = Field(None, max_length=50)
    variedade: Optional[str] = Field(None, max_length=50)
    fase_fenologica: Optional[FaseFenologica] = None
    ativo: Optional[bool] = None
    observacoes: Optional[str] = None


class PontoExtratorResponse(BaseModel):
    """Schema de resposta para ponto de monitoramento."""

    id: str
    codigo: str
    nome: Optional[str]
    latitude: float
    longitude: float
    profundidade_cm: int
    capsula_id: Optional[str]
    tipo_extrator: str
    propriedade_id: Optional[str]
    talhao_id: Optional[str]
    cultura: Optional[str]
    variedade: Optional[str]
    fase_fenologica: Optional[str]
    data_plantio: Optional[date]
    sistema_irrigacao: Optional[str]
    eh_hidroponia: bool
    ativo: bool
    observacoes: Optional[str]
    criado_em: datetime
    atualizado_em: datetime
    total_leituras: int = 0

    model_config = ConfigDict(from_attributes=True)


# =========================================================================
# Leituras
# =========================================================================

class LeituraExtratorCreate(BaseModel):
    """Schema para criação de leitura individual."""

    ponto_id: str = Field(..., min_length=1)
    data_leitura: date
    hora_leitura: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}:\d{2}$")

    ph: Optional[float] = Field(
        None,
        ge=0.0,
        le=14.0,
        description="pH da solução",
    )
    ce_ds_m: float = Field(
        ...,
        ge=0.0,
        le=15.0,
        description="Condutividade elétrica em dS/m",
    )

    # Macronutrientes
    no3_mg_L: Optional[float] = Field(None, ge=0, le=1000, description="Nitrato")
    k_mg_L: Optional[float] = Field(None, ge=0, le=1000, description="Potássio")
    ca_mg_L: Optional[float] = Field(None, ge=0, le=1000, description="Cálcio")
    mg_mg_L: Optional[float] = Field(None, ge=0, le=500, description="Magnésio")
    po4_mg_L: Optional[float] = Field(None, ge=0, le=500, description="Fosfato")
    so4_mg_L: Optional[float] = Field(None, ge=0, le=1000, description="Sulfato")

    # Micronutrientes
    b_mg_L: Optional[float] = Field(None, ge=0, le=10, description="Boro")
    fe_mg_L: Optional[float] = Field(None, ge=0, le=50, description="Ferro")
    mn_mg_L: Optional[float] = Field(None, ge=0, le=20, description="Manganês")
    zn_mg_L: Optional[float] = Field(None, ge=0, le=20, description="Zinco")
    cu_mg_L: Optional[float] = Field(None, ge=0, le=10, description="Cobre")

    metodo_analise: Optional[MetodoAnalise] = None
    laboratorio: Optional[str] = Field(None, max_length=100)
    volume_coletado_ml: Optional[float] = Field(None, ge=0, le=500)
    observacoes: Optional[str] = None

    @field_validator("data_leitura")
    @classmethod
    def validar_data(cls, v: date) -> date:
        """Valida se data não é futura."""
        if v > date.today():
            raise ValueError("Data de leitura não pode ser futura")
        return v


class LeituraExtratorResponse(BaseModel):
    """Schema de resposta para leitura."""

    id: str
    ponto_id: str
    data_leitura: date
    hora_leitura: Optional[str]
    ph: Optional[float]
    ce_ds_m: float
    no3_mg_L: Optional[float]
    k_mg_L: Optional[float]
    ca_mg_L: Optional[float]
    mg_mg_L: Optional[float]
    po4_mg_L: Optional[float]
    so4_mg_L: Optional[float]
    b_mg_L: Optional[float]
    fe_mg_L: Optional[float]
    mn_mg_L: Optional[float]
    zn_mg_L: Optional[float]
    cu_mg_L: Optional[float]
    metodo_analise: Optional[str]
    laboratorio: Optional[str]
    volume_coletado_ml: Optional[float]
    validada: bool
    outlier: bool
    observacoes: Optional[str]
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class UploadCSVResponse(BaseModel):
    """Resposta para upload de CSV com mapeamento de colunas."""

    sucesso: bool
    total_registros: int
    registros_importados: int
    registros_ignorados: int
    colunas_mapeadas: dict[str, str]
    erros: list[str]
    mensagem: str


# =========================================================================
# Diagnóstico
# =========================================================================

class DiagnosticoNutriente(BaseModel):
    """Diagnóstico individual de um nutriente."""

    nutriente: str
    valor_atual: Optional[float]
    unidade: str = "mg/L"
    faixa_ideal: tuple[float, float]
    status: StatusNutriente
    percentual_ideal: Optional[float] = Field(
        None,
        description="Percentual relativo à faixa ideal (0-100%)",
    )
    diferenca_mg_L: Optional[float] = Field(
        None,
        description="Diferença em relação ao mínimo ideal",
    )


class AnaliseTendencia(BaseModel):
    """Análise de tendência de um nutriente."""

    nutriente: str
    tendencia: TendenciaNutriente
    variacao_percentual: Optional[float]
    leituras_analisadas: int
    alerta: bool = Field(
        default=False,
        description="Tendência preocupante",
    )
    mensagem: Optional[str] = None


class RecomendacaoSais(BaseModel):
    """Recomendação de sais para ajuste da fertirrigação."""

    sal_chave: str
    nome_comercial: str
    quantidade_g: float = Field(description="Quantidade em gramas")
    nutrientes_fornecidos: dict[str, float] = Field(
        description="Nutrientes fornecidos em g"
    )
    ce_esperada_dS_m: float = Field(description="Incremento de CE esperado")
    ordem_aplicacao: int = Field(description="Ordem de aplicação no tanque")
    observacoes: Optional[str] = None

    @model_validator(mode="after")
    def checar_incompatibilidades(self) -> "RecomendacaoSais":
        """Verifica incompatibilidades — seria validado no service."""
        return self


class DiagnosticoCompleto(BaseModel):
    """Diagnóstico completo com recomendações."""

    ponto_id: int
    ponto_codigo: str
    data_leitura: date
    cultura: Optional[str]
    fase_fenologica: Optional[str]

    # Alertas gerais
    alerta_ce: bool = Field(
        default=False,
        description="CE acima do limite tolerado",
    )
    alerta_ph: bool = Field(
        default=False,
        description="pH fora da faixa ideal",
    )
    nivel_risco: str = Field(
        default="baixo",
        description="baixo, medio, alto, critico",
    )

    # Diagnósticos por nutriente
    diagnosticos_macronutrientes: list[DiagnosticoNutriente]
    diagnosticos_micronutrientes: list[DiagnosticoNutriente]

    # Análise de tendências
    tendencias: list[AnaliseTendencia]

    # Recomendações
    sais_recomendados: list[RecomendacaoSais]
    compatibilidade_sais: dict[str, list[str] | bool]
    observacoes_gerais: str
    proxima_leitura_dias: int = Field(
        default=7,
        description="Dias sugeridos para próxima coleta",
    )

    model_config = ConfigDict(from_attributes=False)


# =========================================================================
# Histórico
# =========================================================================

class LeituraHistorico(BaseModel):
    """Leitura simplificada para histórico."""

    data: date
    ce_ds_m: float
    ph: Optional[float]
    no3_mg_L: Optional[float]
    k_mg_L: Optional[float]
    ca_mg_L: Optional[float]
    mg_mg_L: Optional[float]


class HistoricoResponse(BaseModel):
    """Resposta com série histórica de leituras."""

    ponto_id: int
    ponto_codigo: str
    cultura: Optional[str]
    fase_fenologica: Optional[str]
    total_leituras: int
    data_inicio: date
    data_fim: date
    leituras: list[LeituraHistorico]

    # Resumo estatístico
    ce_media: float
    ce_min: float
    ce_max: float
    ph_media: Optional[float]

    model_config = ConfigDict(from_attributes=False)


# =========================================================================
# Curvas Nutritivas
# =========================================================================

class CurvaNutritivaCreate(BaseModel):
    """Schema para criação de curva nutritiva."""

    cultura: str = Field(..., min_length=1, max_length=50)
    fase_fenologica: FaseFenologica

    ph_min: float = Field(default=6.0, ge=0, le=14)
    ph_max: float = Field(default=6.5, ge=0, le=14)
    ce_min_ds_m: float = Field(..., ge=0)
    ce_max_ds_m: float = Field(..., ge=0)

    # Macronutrientes
    no3_min_mg_L: float = Field(..., ge=0)
    no3_max_mg_L: float = Field(..., ge=0)
    k_min_mg_L: float = Field(..., ge=0)
    k_max_mg_L: float = Field(..., ge=0)
    ca_min_mg_L: float = Field(..., ge=0)
    ca_max_mg_L: float = Field(..., ge=0)
    mg_min_mg_L: float = Field(..., ge=0)
    mg_max_mg_L: float = Field(..., ge=0)
    po4_min_mg_L: float = Field(..., ge=0)
    po4_max_mg_L: float = Field(..., ge=0)
    so4_min_mg_L: float = Field(..., ge=0)
    so4_max_mg_L: float = Field(..., ge=0)

    # Micronutrientes
    b_min_mg_L: float = Field(default=0.1, ge=0)
    b_max_mg_L: float = Field(default=0.5, ge=0)
    fe_min_mg_L: float = Field(default=0.5, ge=0)
    fe_max_mg_L: float = Field(default=2.0, ge=0)
    mn_min_mg_L: float = Field(default=0.3, ge=0)
    mn_max_mg_L: float = Field(default=1.0, ge=0)
    zn_min_mg_L: float = Field(default=0.3, ge=0)
    zn_max_mg_L: float = Field(default=1.0, ge=0)
    cu_min_mg_L: float = Field(default=0.01, ge=0)
    cu_max_mg_L: float = Field(default=0.1, ge=0)

    # Razões iônicas
    ratio_n_k: Optional[float] = Field(None, ge=0)
    ratio_k_ca: Optional[float] = Field(None, ge=0)
    ratio_ca_mg: Optional[float] = Field(None, ge=0)

    fonte: Optional[str] = Field(None, max_length=100)
    observacoes: Optional[str] = None

    @model_validator(mode="after")
    def validar_faixas(self) -> "CurvaNutritivaCreate":
        """Valida se mínimos são menores que máximos."""
        if self.ph_min > self.ph_max:
            raise ValueError("ph_min deve ser menor que ph_max")
        if self.ce_min_ds_m > self.ce_max_ds_m:
            raise ValueError("ce_min_ds_m deve ser menor que ce_max_ds_m")
        return self


class CurvaNutritivaResponse(BaseModel):
    """Schema de resposta para curva nutritiva."""

    id: str
    cultura: str
    fase_fenologica: str
    ph_min: float
    ph_max: float
    ce_min_ds_m: float
    ce_max_ds_m: float
    no3_min_mg_L: float
    no3_max_mg_L: float
    k_min_mg_L: float
    k_max_mg_L: float
    ca_min_mg_L: float
    ca_max_mg_L: float
    mg_min_mg_L: float
    mg_max_mg_L: float
    po4_min_mg_L: float
    po4_max_mg_L: float
    so4_min_mg_L: float
    so4_max_mg_L: float
    b_min_mg_L: float
    b_max_mg_L: float
    fe_min_mg_L: float
    fe_max_mg_L: float
    mn_min_mg_L: float
    mn_max_mg_L: float
    zn_min_mg_L: float
    zn_max_mg_L: float
    cu_min_mg_L: float
    cu_max_mg_L: float
    ratio_n_k: Optional[float]
    ratio_k_ca: Optional[float]
    ratio_ca_mg: Optional[float]
    fonte: Optional[str]
    observacoes: Optional[str]
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)