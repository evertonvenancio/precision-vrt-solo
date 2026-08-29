"""
Schemas Pydantic para validação e serialização de dados climáticos.
"""

from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class PrevisaoDiariaSchema(BaseModel):
    """Previsão climática para um único dia."""

    data: date = Field(..., description="Data da previsão")
    temp_min: float = Field(..., description="Temperatura mínima prevista (°C)")
    temp_max: float = Field(..., description="Temperatura máxima prevista (°C)")
    precipitacao_mm: float = Field(
        ..., ge=0, description="Precipitação prevista acumulada (mm)"
    )
    umidade_relativa_pct: float = Field(
        ..., ge=0, le=100, description="Umidade relativa média prevista (%)"
    )
    velocidade_vento_kmh: float = Field(
        ..., ge=0, description="Velocidade média do vento prevista (km/h)"
    )
    descricao: str = Field(..., description="Descrição textual do clima (ex: 'chuva leve')")
    icone: Optional[str] = Field(None, description="Código do ícone da condição climática")

    class Config:
        from_attributes = True


class PrevisaoResponseSchema(BaseModel):
    """Resposta completa da previsão de múltiplos dias."""

    lat: float = Field(..., description="Latitude consultada")
    lon: float = Field(..., description="Longitude consultada")
    cidade: Optional[str] = Field(None, description="Nome da cidade mais próxima")
    dias: List[PrevisaoDiariaSchema] = Field(..., description="Lista de previsões diárias")
    consultado_em: datetime = Field(..., description="Timestamp da consulta")
    fonte: str = Field(default="OpenWeatherMap", description="Fonte dos dados")


class AlertaAplicacaoSchema(BaseModel):
    """Alerta individual para uma condição específica."""

    tipo: Literal["perigo", "atencao", "ok"] = Field(
        ..., description="Nível do alerta: 'perigo', 'atencao' ou 'ok'"
    )
    parametro: str = Field(
        ..., description="Parâmetro climático analisado (ex: 'precipitacao', 'vento')"
    )
    mensagem: str = Field(..., description="Descrição legível do alerta")
    valor_atual: Optional[float] = Field(
        None, description="Valor atual do parâmetro"
    )
    limite_agronomico: Optional[float] = Field(
        None, description="Limite agronômico configurado"
    )


class JanelaAplicacaoResponseSchema(BaseModel):
    """Resposta completa da análise de janela de aplicação."""

    lat: float
    lon: float
    tipo_aplicacao: str = Field(..., description="Tipo de insumo analisado (ex: 'ureia')")
    pode_aplicar: bool = Field(
        ...,
        description="True se as condições estão favoráveis para aplicação hoje",
    )
    resumo: str = Field(
        ..., description="Texto resumido da recomendação (ex: 'Pode aplicar' / 'Evitar aplicação hoje')"
    )
    alertas: List[AlertaAplicacaoSchema] = Field(
        default_factory=list, description="Lista de alertas detalhados"
    )
    previsao_proximas_24h: Optional[PrevisaoDiariaSchema] = Field(
        None, description="Previsão resumida das próximas 24 horas"
    )
    consultado_em: datetime


class ClimaHistoricoLaudoCreateSchema(BaseModel):
    """Schema para criação de registro de clima vinculado a laudo."""

    prescricao_id: int
    data_referencia: date
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    temp_media: Optional[float] = None
    precipitacao_mm: Optional[float] = None
    umidade_relativa_pct: Optional[float] = None
    velocidade_vento_kmh: Optional[float] = None
    descricao_clima: Optional[str] = None
    fonte_dados: str = "OpenWeatherMap"

    @field_validator("precipitacao_mm")
    @classmethod
    def precipitacao_nao_negativa(cls, v: Optional[float]) -> Optional[float]:
        """Valida que precipitação não seja negativa."""
        if v is not None and v < 0:
            raise ValueError("precipitacao_mm não pode ser negativa")
        return v


class ClimaHistoricoLaudoResponseSchema(ClimaHistoricoLaudoCreateSchema):
    """Schema de resposta com campos gerados pelo banco."""

    id: int
    criado_em: datetime

    class Config:
        from_attributes = True
