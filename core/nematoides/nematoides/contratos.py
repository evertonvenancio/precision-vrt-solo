"""
Precision VRT Solo — Contratos do Módulo de Nematoides

Dataclasses, enums e modelos de dados para análise de nematoides.
Estruturas puras de dados — sem lógica de negócio.

Extraído de legacy/core_agronomia_nematoides_legado.py
"""

import numpy as np
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

from ...tipos.base import ConfigBase, ResultadoBase, IdentificavelMixin, TimestampMixin
from ...tipos.geoespacial import Coordenada, Bounds


class NivelRiscoNematoides(str, Enum):
    """Classificação de risco de nematoides por zona."""
    BAIXO = "baixo"
    MODERADO = "moderado"
    ALTO = "alto"
    CRITICO = "critico"


class EspecieNematoides(str, Enum):
    """Espécies de nematoides comuns na agricultura."""
    MELOIDOGYNE = "meloidogyne"
    PRATYLENCHUS = "pratylenchus"
    HETERODERA = "heterodera"
    GALLUS = "gallus"
    OUTROS = "outros"


@dataclass
class PontoAmostraNematoides:
    """Representa um ponto de amostra para nematoides."""
    ponto_id: str
    coordenada: Coordenada
    profundidade_cm: int
    populacao_nematoides_100g_solo: float
    especie_predominante: EspecieNematoides
    observacoes: str = ""
    
    # Índices específicos por espécie
    indice_gall: Optional[float] = None
    indice_meloidogyne: Optional[float] = None
    indice_pratylenchus: Optional[float] = None
    indice_heterodera: Optional[float] = None


@dataclass
class ConfigInterpolacaoNematoides(ConfigBase):
    """Configuração para interpolação de dados de nematoides."""
    resolucao_grade: float = 10.0  # metros
    metodo: str = "kriging"  # kriging, idw, natural_neighbor
    variograma_modelo: str = "spherical"
    max_distancia_interpolacao: float = 100.0  # metros


@dataclass
class ConfigZoneamentoNematoides(ConfigBase):
    """Configuração para zoneamento de risco de nematoides."""
    algoritmo: str = "kmeans"  # kmeans, dbscan, aglomerativo
    n_zonas: int = 5
    limite_similaridade: float = 0.8
    metodo_agrupamento: str = "ward"


@dataclass
class ConfigExportacaoNematoides(ConfigBase):
    """Configuração para exportação de resultados de nematoides."""
    formatos: List[str] = field(default_factory=list)
    incluir_amostras_individuais: bool = True
    incluir_estatisticas: bool = True
    incluir_recomendacoes: bool = True


@dataclass
class ConfigAgronomiaNematoides(ConfigBase):
    """Configuração para recomendações agronômicas de nematoides."""
    cultura: str = "milho"
    tipo_solo: str = "misto"
    historia_nematoides: List[str] = field(default_factory=list)
    tolerancia_adesao: float = 0.8
    custo_maximo_hectare: float = 500.0
    preferencia_metodo_controle: str = "integrado"


@dataclass
class ZonaRiscoNematoides:
    """Zona de manejo classificada por risco de nematoides."""
    
    # Campos sem valores padrão (obrigatórios)
    zona_id: int
    risco_classificacao: NivelRiscoNematoides
    populacao_media: float
    populacao_maxima: float
    
    # Campos com valores padrão (opcionais)
    timestamp: datetime = field(default_factory=datetime.now)
    tempo_execucao_ms: float = 0.0
    config: Optional[ConfigBase] = None
    generos_detectados: List[EspecieNematoides] = field(default_factory=list)
    recomendacao_manejo: str = ""
    necessita_tratamento: bool = False
    area_hectares: float = 0.0
    correlacao_produtividade_risco: float = 0.0
    prioridade_acao: str = ""


@dataclass
class ResultadoInterpolacaoNematoides:
    """Resultado da interpolação de nematoides."""
    
    # Campos sem valores padrão (obrigatórios)
    valores_interpolados: np.ndarray
    coordenadas_grade: List[Tuple[float, float]]
    pontos_originais: List[PontoAmostraNematoides]
    configuracao_usada: ConfigInterpolacaoNematoides
    
    # Campos com valores padrão (opcionais)
    timestamp: datetime = field(default_factory=datetime.now)
    tempo_execucao_ms: float = 0.0
    config: Optional[ConfigBase] = None
    mapa_risco: np.ndarray = field(default_factory=lambda: None)


@dataclass
class ResultadoZoneamentoNematoides:
    """Resultado do zoneamento de risco de nematoides."""
    
    # Campos sem valores padrão (obrigatórios)
    zonas_risco: List[ZonaRiscoNematoides]
    mapa_zonas: np.ndarray
    configuracao_usada: ConfigZoneamentoNematoides
    
    # Campos com valores padrão (opcionais)
    timestamp: datetime = field(default_factory=datetime.now)
    tempo_execucao_ms: float = 0.0
    config: Optional[ConfigBase] = None
    estatisticas_gerais: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResultadoNematoides:
    """Resultado completo da análise de nematoides."""
    
    # Campos sem valores padrão (obrigatórios)
    resultado_interpolacao: ResultadoInterpolacaoNematoides
    resultado_zoneamento: ResultadoZoneamentoNematoides
    
    # Campos com valores padrão (opcionais)
    timestamp: datetime = field(default_factory=datetime.now)
    tempo_execucao_ms: float = 0.0
    config: Optional[ConfigBase] = None
    recomendacoes_gerais: List[str] = field(default_factory=list)
    risco_global: NivelRiscoNematoides = NivelRiscoNematoides.MODERADO
    area_total_analisada: float = 0.0
    custo_estimado_tratamento: float = 0.0