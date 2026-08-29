"""
Precision VRT Solo — Contratos do Módulo de Zoneamento

Definições de tipos, enums e protocols que formam o contrato público do módulo.
"""

import dataclasses
from enum import Enum
from typing import Any, Dict, List, Protocol, Union

import geopandas as gpd
import numpy as np

# Importar as classes base do core.tipos
from core.tipos import ConfigBase, ResultadoBase


class AlgoritmoEnum(Enum):
    """Algoritmos disponíveis para zoneamento."""
    KMEANS = "KMEANS"
    FUZZY = "FUZZY"
    GAUSSIAN = "GAUSSIAN"
    DBSCAN = "DBSCAN"
    AGLOMERATIVO = "AGLOMERATIVO"
    SPECTRAL = "SPECTRAL"


class MetricaQualidadeEnum(Enum):
    """Métricas de qualidade do clustering (implementação futura Z2)."""
    SILHOUETTE = "SILHOUETTE"
    DAVIES_BOULDIN = "DAVIES_BOULDIN"
    CALINSKI = "CALINSKI"
    INERCIA = "INERCIA"


@dataclasses.dataclass
class ConfigZoneamento(ConfigBase):
    """Configuração de zoneamento."""
    n_zonas: int
    algoritmo: AlgoritmoEnum = AlgoritmoEnum.KMEANS
    random_state: Union[int, None] = 42
    colunas_features: Union[List[str], None] = None
    normalizar: bool = True
    remover_outliers: bool = False
    pesos_features: Union[Dict[str, float], None] = None
    diferenca_minima_dose: Union[float, None] = None


@dataclasses.dataclass
class ResultadoZoneamento(ResultadoBase):
    """Resultado do processo de zoneamento."""
    gdf: gpd.GeoDataFrame = None
    algoritmo: AlgoritmoEnum = None
    n_zonas_efetivas: int = 0
    config: ConfigZoneamento = None
    perfis: Union[List['PerfilZona'], None] = None
    metricas: Dict[str, float] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class PerfilZona:
    """Perfil detalhado de uma zona."""
    zona_id: int
    area_ha: float
    n_pontos: int
    media: Dict[str, float]
    mediana: Dict[str, float]
    desvio_padrao: Dict[str, float]
    cv: Dict[str, float]
    minimo: Dict[str, float]
    maximo: Dict[str, float]
    percentil_25: Dict[str, float]
    percentil_75: Dict[str, float]


class AlgoritmoClusteringProtocol(Protocol):
    """Protocolo para implementações de algoritmos de clustering."""
    
    def executar(self, gdf: gpd.GeoDataFrame, config: ConfigZoneamento) -> ResultadoZoneamento:
        """Executa o algoritmo de clustering."""
        ...
    
    def estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas do algoritmo após execução."""
        ...