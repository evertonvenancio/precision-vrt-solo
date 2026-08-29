"""
Precision VRT Solo — Contratos de Dados de Sensoriamento Remoto

Define estruturas de dados, enums e modelos para módulo de sensoriamento.
"""

import enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime

from core.tipos.base import ConfigBase


# ========================================
# ENUMS E TIPOS BASICOS
# ========================================

class TipoSatelite(str, enum.Enum):
    """Tipos de satélites suportados."""
    SENTINEL = "sentinel"
    LANDSAT = "landsat"
    PLANET = "planet"
    CBERS = "cbers"
    SENTINEL_2 = "sentinel_2"
    SENTINEL_1 = "sentinel_1"
    MODIS = "modis"


class TipoSensor(str, enum.Enum):
    """Tipos de sensores suportados."""
    RGB = "rgb"
    MULTIESPECTRAL = "multiespectral"
    HIPERSPECTRAL = "hiperspectral"
    TERMAL = "termal"
    RADAR = "radar"


class TipoImagem(str, enum.Enum):
    """Tipos de imagens suportadas."""
    SATELITE = "satelite"
    DRONE = "drone"
    COMBINADA = "combinada"


class StatusProcessamento(str, enum.Enum):
    """Status de processamento de imagens."""
    PENDENTE = "pendente"
    RECEBIDA = "recebida"
    PROCESSANDO = "processando"
    FINALIZADA = "finalizada"
    FALHA = "falha"
    CANCELADA = "cancelada"


class TipoIndice(str, enum.Enum):
    """Tipos de índices espectrais suportados."""
    NDVI = "ndvi"
    NDRE = "ndre"
    GNDVI = "gndvi"
    SAVI = "savi"
    MSAVI = "msavi"
    EVI = "evi"
    PRI = "pri"
    NDWI = "ndwi"
    NDBI = "ndbi"
    NBR = "nbr"
    PSRI = "psri"
    SIPI = "sipi"
    # Outros índices podem ser adicionados
    ARBITRARIO = "arbitrario"


# ========================================
# CONFIGURAÇÕES
# ========================================

@dataclass
class ConfigAreaSensoriamento(ConfigBase):
    """Configuração para área de sensoriamento."""
    
    area_id: str = ""
    poligono: Dict[str, Any] = field(default_factory=dict)
    crs: str = "EPSG:4326"
    resolucao_min_m: float = 10.0
    resolucao_max_m: float = 30.0
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    max_safras: int = 10


@dataclass
class ConfigSatelite(ConfigBase):
    """Configuração para satélite."""
    
    satelite: TipoSatelite = TipoSatelite.SENTINEL
    sensor: TipoSensor = TipoSensor.MULTIESPECTRAL
    resolucao_m: float = 10.0
    cobertura_max_graus: float = 180.0
    frequencia_dias: int = 5
    disponivel: bool = True


@dataclass
class ConfigProcessamentoImagem(ConfigBase):
    """Configuração para processamento de imagens."""
    
    # Parâmetros de processamento
    alinhar_imagens: bool = True
    rec_area_interesse: bool = True
    normalizar: bool = True
    remover_nuvens: bool = True
    aplicar_mascara: bool = True
    padronizar_formato: bool = True
    
    # Parâmetros específicos
    threshold_nuvens: float = 0.1
    metodo_normalizacao: str = "min_max"
    formato_saida: str = "geotiff"


@dataclass
class ConfigIndicesEspectrais(ConfigBase):
    """Configuração para cálculo de índices espectrais."""
    
    indices_calcular: List[TipoIndice] = field(default_factory=list)
    incluir_indices_arbitrarios: bool = True
    aplicar_correcoes_atmosfericas: bool = True


@dataclass
class ConfigMesclagem(ConfigBase):
    """Configuração para mesclagem de imagens."""
    
    # Estratégia de mesclagem
    estrategia: str = "complementar"
    prioridade_fonte: str = "resolucao"
    aplicar_ponderacao: bool = True
    
    # Parâmetros de mesclagem
    tolerancia_espacial: float = 5.0
    criterio_qualidade: str = "snr"


@dataclass
class ConfigTemas(ConfigBase):
    """Configuração para geração de mapas temáticos."""
    
    tema_principal: str = "vegetacao"
    temas_secundarios: List[str] = field(default_factory=list)
    resolucao_saida: float = 10.0
    paleta_cores: str = "viridis"


@dataclass
class ConfigExportacaoSensoriamento(ConfigBase):
    """Configuração para exportação de resultados."""
    
    formatos_suportados: List[str] = field(default_factory=list)
    
    # Parâmetros específicos
    incluir_moldura: bool = True
    incluir_legenda: bool = True
    incluir_escalas: bool = True
    resolucao_dpi: int = 300
    qualidade_imagem: int = 95


# ========================================
# MODELOS DE DADOS
# ========================================

@dataclass
class ImagemSatelite:
    """Representação de uma imagem de satélite."""
    
    # Dados obrigatórios
    imagem_id: str
    satelite: TipoSatelite
    sensor: TipoSensor
    tipo_imagem: TipoImagem
    caminho_arquivo: str
    
    # Metadados
    data_captura: str
    hora_captura: str
    
    # Metadados opcionais
    cloud_cover_pct: float = 0.0
    resolucao_m: float = 10.0
    formatos_disponiveis: List[str] = field(default_factory=list)
    
    # Status
    status_processamento: StatusProcessamento = StatusProcessamento.PENDENTE
    safra_id: str = ""
    areas_pertencentes: List[str] = field(default_factory=list)


@dataclass
class CamadaIndice:
    """Resultado do cálculo de um índice espectral."""
    
    nome_indice: TipoIndice
    imagem_origem: str
    caminho_saida: str
    valores: Dict[str, Any] = field(default_factory=dict)
    estatisticas: Dict[str, float] = field(default_factory=dict)
    data_calculo: str = ""


@dataclass
class ImagemProcessada:
    """Imagem após processamento."""
    
    imagem_id: str
    imagem_origem: ImagemSatelite
    status_processamento: StatusProcessamento
    processos_aplicados: List[str] = field(default_factory=list)
    caminho_saida: str = ""
    formatos: List[str] = field(default_factory=list)
    metadados: Dict[str, Any] = field(default_factory=dict)
    data_processamento: str = ""


@dataclass
class CamadaMesclada:
    """Resultado da mesclagem de múltiplas imagens."""
    
    mesclagem_id: str
    imagens_origem: List[ImagemSatelite]
    estrategia: str = "combinacao_linear"
    caminho_saida: str = ""
    resolucao_final_m: float = 10.0
    data_mesclagem: str = ""
    metadados: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MapaTematico:
    """Mapa temático gerado a partir de dados processados."""
    
    mapa_id: str
    tema: str
    caminho_arquivo: str = ""
    formato: str = "geotiff"
    resolucao_m: float = 10.0
    data_geracao: str = ""
    legenda: str = ""
    metadados: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResultadoProcessamento:
    """Resultado completo do processamento de sensoriamento."""
    
    area_id: str
    imagens_originais: List[ImagemSatelite]
    imagens_processadas: List[ImagemProcessada]
    camadas_indices: List[CamadaIndice]
    camadas_mescladas: List[CamadaMesclada]
    mapas_tematicos: List[MapaTematico]
    processamento_ok: bool = True
    mensagem_erro: str = ""
    data_inicio: str = ""
    data_fim: str = ""