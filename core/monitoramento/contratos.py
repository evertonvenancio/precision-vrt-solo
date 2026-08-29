"""
Precision VRT Solo — Contratos do Módulo de Monitoramento

Define modelos de dados para o sistema de monitoramento temporal.
Extraído e adaptado de core_agronomia_monitoramento_legado.py.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TipoSensor(Enum):
    """Tipos de sensores suportados."""
    SENTINEL = "sentinel"
    LANDSAT = "landsat"
    DRONE_RGB = "drone_rgb"
    DRONE_MULTIESPECTRAL = "drone_multispectral"
    DRONE_THERMAL = "drone_thermal"
    DRONE_HYPERSPECTRAL = "drone_hyperspectral"
    RGB = "rgb"
    MULTIESPECTRAL = "multispectral"
    THERMAL = "thermal"
    HYPERSPECTRAL = "hyperspectral"


class TipoIndice(Enum):
    """Índices espectrais suportados."""
    NDVI = "NDVI"
    EVI = "EVI"
    SAVI = "SAVI"
    NDWI = "NDWI"
    GNDVI = "GNDVI"
    MSAVI = "MSAVI"
    NDRE = "NDRE"
    GCI = "GCI"
    RECI = "RECI"
    MTCI = "MTCI"
    OSAVI = "OSAVI"
    TVI = "TVI"
    CVI = "CVI"
    DVI = "DVI"
    RVI = "RVI"
    IPVI = "IPVI"
    NBR = "NBR"
    NBR2 = "NBR2"
    NDSI = "NDSI"
    BAI = "BAI"


class TipoIntervalo(Enum):
    """Tipos de intervalos temporais."""
    DIA = "dia"
    SEMANA = "semana"
    MES = "mes"
    SAFRA = "safra"
    ANO = "ano"
    PERSONALIZADO = "personalizado"


class TipoComparacao(Enum):
    """Tipos de comparação temporal."""
    SUBTRACAO = "subtracao"
    RAZAO = "razao"
    COVARIANCIA = "covariancia"
    CORRELACAO = "correlacao"
    ANOMALIA = "anomalia"


@dataclass
class ImagemMonitoramento:
    """Representação de uma imagem para monitoramento."""
    
    imagem_id: str
    sensor: TipoSensor
    tipo_imagem: TipoIndice
    data_captura: str
    caminho_arquivo: str
    resolucao_m: float = 10.0
    cloud_cover_pct: float = 0.0
    formatos_disponiveis: List[str] = field(default_factory=list)
    metadados: Dict[str, Any] = field(default_factory=dict)
    status_processamento: str = "pendente"
    areas_pertencentes: List[str] = field(default_factory=list)


@dataclass
class SerieTemporalVigor:
    """Série temporal de vigor para uma zona de manejo."""
    zona_id: int
    datas: List[str] = field(default_factory=list)
    valores_medios: Dict[str, List[float]] = field(default_factory=dict)
    desvios: Dict[str, List[float]] = field(default_factory=dict)
    anomalias: List[Dict] = field(default_factory=list)


@dataclass
class AnomaliaMonitoramento:
    """Representa uma anomalia detectada no monitoramento."""
    zona_id: int
    data: str
    indice: str
    valor_observado: float
    valor_esperado: float
    desvio_percentual: float
    tipo: str  # 'positiva' ou 'negativa'
    severidade: str  # 'leve', 'moderada', 'grave'
    possiveis_causas: List[str] = field(default_factory=list)
    contexto: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigComparacaoTemporal:
    """Configuração para comparação temporal."""
    intervalo: TipoIntervalo = TipoIntervalo.MES
    tipo_comparacao: TipoComparacao = TipoComparacao.SUBTRACAO
    indice_padrao: TipoIndice = TipoIndice.NDVI
    limite_tolerancia_desvio: float = 2.0
    detectar_anomalias: bool = True
    salvar_intermediarios: bool = True
    formatos_saida: List[str] = field(default_factory=list)


@dataclass
class ConfigAlerta:
    """Configuração de alertas para monitoramento."""
    tipo_alerta: str
    condicao: str
    limite_superior: Optional[float] = None
    limite_inferior: Optional[float] = None
    severidade: str = "moderada"
    ativo: bool = True
    canais_notificacao: List[str] = field(default_factory=list)
    historico: List[Dict] = field(default_factory=list)


@dataclass
class ResultadoComparacao:
    """Resultado da comparação temporal entre imagens."""
    imagem_base_id: str
    imagem_comparada_id: str
    intervalo_dias: int
    indice_analisado: str
    diferenca_media: float
    diferenca_maxima: float
    diferenca_minima: float
    areas_mudancas: Dict[str, Any]
    estatisticas: Dict[str, float]
    anomalias_detectadas: List[AnomaliaMonitoramento]
    data_comparacao: str
    matriz_diferenca: Optional[np.ndarray] = None
    mapa_mudancas: Optional[Dict[str, Any]] = None


@dataclass
class HistoricoMonitoramento:
    """Histórico completo do monitoramento de uma área."""
    area_id: str
    safra: str
    inicio_monitoramento: str
    fim_monitoramento: Optional[str] = None
    imagens_processadas: List[ImagemMonitoramento] = field(default_factory=list)
    series_temporais: Dict[int, SerieTemporalVigor] = field(default_factory=dict)
    comparacoes_realizadas: List[ResultadoComparacao] = field(default_factory=list)
    anomalias_registradas: List[AnomaliaMonitoramento] = field(default_factory=list)
    alertas_disparados: List[Dict] = field(default_factory=list)
    resumo_final: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigExportacao:
    """Configuração para exportação de dados de monitoramento."""
    formatos: List[str] = field(default_factory=lambda: ["PDF", "CSV", "Excel", "GeoJSON", "Shapefile", "GeoTIFF"])
    incluir_series_temporais: bool = True
    incluir_comparacoes: bool = True
    incluir_anomalias: bool = True
    incluir_historico_completo: bool = True
    parametrizacao_personalizada: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AreaMonitoramento:
    """Área de monitoramento definida pelo usuário."""
    area_id: str
    nome: str
    geometria: Dict[str, Any]
    data_inicio: str
    data_fim: Optional[str] = None
    sensores_suportados: List[TipoSensor] = field(default_factory=list)
    indices_prioritarios: List[TipoIndice] = field(default_factory=list)
    frequencia_desejada: TipoIntervalo = TipoIntervalo.SEMANA
    zonas_monitoramento: List[int] = field(default_factory=list)
    configuracoes: Dict[str, Any] = field(default_factory=dict)