"""
Schemas Pydantic para o módulo de Compactação do Solo.

Define os modelos de dados para validação, serialização e
comunicação entre camadas da aplicação.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ClassificacaoCompactacaoSchema(str, Enum):
    """Classificação da resistência à penetração."""
    APTO = "Apto"
    RESTRICAO = "Restricao"
    IMPEDIMENTO_SEVERO = "Impedimento Severo"


class CamadaCompactacaoBase(BaseModel):
    """Schema base para camada de compactação."""
    profundidade_inicio: float = Field(..., ge=0, description="Profundidade inicial em cm")
    profundidade_fim: float = Field(..., ge=0, description="Profundidade final em cm")
    resistencia_mpa: float = Field(..., ge=0, description="Resistência à penetração em MPa")

    @field_validator("profundidade_fim")
    @classmethod
    def fim_maior_que_inicio(cls, v: float, info) -> float:
        """Valida que profundidade_fim > profundidade_inicio."""
        inicio = info.data.get("profundidade_inicio")
        if inicio is not None and v <= inicio:
            raise ValueError("profundidade_fim deve ser maior que profundidade_inicio")
        return v


class CamadaCompactacaoCreate(CamadaCompactacaoBase):
    """Schema para criação de camada (sem classificação - calculada pelo core)."""
    pass


class CamadaCompactacaoResponse(CamadaCompactacaoBase):
    """Schema de resposta para camada de compactação."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    classificacao: str = Field(..., description="Classificação da camada")
    necessita_escarificacao: bool = Field(..., description="Requer escarificação")


class PontoCompactacaoBase(BaseModel):
    """Schema base para ponto de compactação."""
    identificador_ponto: str = Field(..., min_length=1, max_length=50, description="Código do ponto")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude WGS84")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude WGS84")


class PontoCompactacaoCreate(PontoCompactacaoBase):
    """Schema para criação de ponto com camadas."""
    camadas: List[CamadaCompactacaoCreate] = Field(..., min_length=1, description="Camadas do ponto")


class PontoCompactacaoResponse(PontoCompactacaoBase):
    """Schema de resposta para ponto de compactação."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    classificacao_geral: str
    necessita_escarificacao: bool
    profundidade_maxima_restricao: Optional[float]
    camadas: List[CamadaCompactacaoResponse]


class AnaliseCompactacaoBase(BaseModel):
    """Schema base para análise de compactação."""
    talhao_id: Optional[int] = Field(None, description="ID do talhão")
    propriedade_id: Optional[int] = Field(None, description="ID da propriedade")
    data_coleta: datetime = Field(default_factory=datetime.utcnow, description="Data da coleta")
    observacoes: Optional[str] = Field(None, max_length=2000, description="Observações técnicas")


class AnaliseCompactacaoCreate(AnaliseCompactacaoBase):
    """Schema para criação de análise com pontos."""
    pontos: List[PontoCompactacaoCreate] = Field(..., min_length=1, description="Pontos amostrais")


class AnaliseCompactacaoUpdate(BaseModel):
    """Schema para atualização parcial de análise."""
    observacoes: Optional[str] = Field(None, max_length=2000)
    talhao_id: Optional[int] = None
    propriedade_id: Optional[int] = None


class AnaliseCompactacaoResponse(AnaliseCompactacaoBase):
    """Schema de resposta completo para análise de compactação."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    usuario_id: Optional[int]
    classificacao_geral: str
    necessita_escarificacao: bool
    percentual_impedimento: float
    percentual_restricao: float
    percentual_apto: float
    profundidade_maxima_restricao: Optional[float]
    arquivo_csv_origem: Optional[str]
    created_at: datetime
    updated_at: datetime
    pontos: List[PontoCompactacaoResponse]


class AnaliseCompactacaoList(BaseModel):
    """Schema resumido para listagem de análises."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    talhao_id: Optional[int]
    propriedade_id: Optional[int]
    data_coleta: datetime
    classificacao_geral: str
    necessita_escarificacao: bool
    percentual_impedimento: float
    percentual_restricao: float
    percentual_apto: float
    created_at: datetime


class ResumoEstatistico(BaseModel):
    """Resumo estatístico da análise de compactação."""
    total_pontos: int = Field(..., description="Total de pontos analisados")
    pontos_com_impedimento: int = Field(..., description="Pontos com impedimento severo")
    pontos_com_restricao: int = Field(..., description="Pontos com restrição")
    pontos_apto: int = Field(..., description="Pontos aptos")
    percentual_impedimento: float = Field(..., ge=0, le=100)
    percentual_restricao: float = Field(..., ge=0, le=100)
    percentual_apto: float = Field(..., ge=0, le=100)
    classificacao_predominante: str
    profundidade_maxima_restricao: Optional[float]
    recomendacao_geral: str
    necessita_escarificacao: bool


class FlagEscarificacao(BaseModel):
    """Flag de necessidade de escarificação."""
    ponto_id: str
    identificador_ponto: str
    tipo: str = Field(..., description="Tipo de flag")
    severidade: str = Field(..., description="Severidade do alerta")
    mensagem: str
    camadas_afetadas: List[Dict[str, Any]] = Field(default_factory=list)
    profundidade_recomendada_escarificacao: Optional[float]
    classificacao_geral: str
    dados_tecnicos: Dict[str, Any]


class GeoJSONFeature(BaseModel):
    """Feature GeoJSON para mapa de pontos."""
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: Dict[str, Any]


class GeoJSONCollection(BaseModel):
    """Coleção GeoJSON de pontos de compactação."""
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]


class CSVUploadResponse(BaseModel):
    """Resposta do upload de CSV de penetrometria."""
    analise_id: str
    resumo: ResumoEstatistico
    flags: List[FlagEscarificacao]
    mensagem: str


class CSVColumnMapping(BaseModel):
    """Mapeamento de colunas do CSV de penetrometria."""
    coluna_ponto_id: str = Field(default="ponto_id", description="Coluna do identificador do ponto")
    coluna_latitude: Optional[str] = Field(default="latitude", description="Coluna da latitude")
    coluna_longitude: Optional[str] = Field(default="longitude", description="Coluna da longitude")
    colunas_profundidade: Dict[str, str] = Field(
        default_factory=lambda: {
            "0_10": "rp_0_10",
            "10_20": "rp_10_20",
            "20_30": "rp_20_30",
            "30_40": "rp_30_40",
        },
        description="Mapeamento profundidade -> coluna CSV"
    )


class MediasPorCamada(BaseModel):
    """Médias estatísticas por camada de profundidade."""
    faixa: str = Field(..., description="Faixa de profundidade (ex: 0-10cm)")
    media: float
    minimo: float
    maximo: float
    desvio: float
