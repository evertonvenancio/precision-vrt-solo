"""
Precision VRT Solo — Contratos de Dados de Fertirrigação

Define estruturas de dados, enums e modelos para módulo de fertirrigação.
"""

import numpy as np
import enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field

from core.tipos.base import ConfigBase, ResultadoBase


# --------------------------------------------------
# ENUMS
# --------------------------------------------------

class Cultura(str, enum.Enum):
    """Culturas suportadas no sistema."""
    TOMATE = "tomate"
    PIMENTAO = "pimentao"
    ALFACE = "alface"
    MORANGO = "morango"
    CAFE = "cafe"
    MILHO = "milho"
    SOJA = "soja"
    TRIGO = "trigo"
    CANA = "cana"
    CITROS = "citros"
    UVA = "uva"


class SistemaIrrigacao(str, enum.Enum):
    """Sistemas de irrigação suportados."""
    GOTEJO = "gotejo"
    ASPERSAO = "aspersao"
    PIVOR = "pivor"
    HIDROPONIA = "hidroponia"
    SUBIRRIGACAO = "subirrigacao"


class MetodoAnalise(str, enum.Enum):
    """Métodos de análise de solução."""
    LABORATORIO = "laboratorio"
    ION_METRO = "ion_metro"
    COLORIMETRO = "colorimetro"
    SENSOR = "sensor"


class TipoFertilizante(str, enum.Enum):
    """Tipos de fertilizantes para recomendação."""
    COMERCIAL = "comercial"
    MAP = "map"
    DAP = "dap"
    KCL = "kcl"
    UREIA = "ureia"
    NITRATO_CALCIO = "nitrato_calcio"
    SULFATO_AMONIO = "sulfato_amonio"
    ACIDO_FOSFORICO = "acido_fosforico"
    FERTILIZANTE_INDIVIDUAL = "fertilizante_individual"


class ModoRecomendacao(str, enum.Enum):
    """Modos de recomendação de fertilizantes."""
    PRODUTO_COMERCIAL = "produto_comercial"
    FONTES_INDIVIDUAIS = "fontes_individuais"


class NivelRiscoNutricao(str, enum.Enum):
    """Níveis de risco nutricional."""
    BAIXO = "baixo"
    MEDIO = "medio"
    ALTO = "alto"


# --------------------------------------------------
# DATACLASSES DE CONFIGURAÇÃO
# --------------------------------------------------

@dataclass
class ConfigAreaFertirrigacao(ConfigBase):
    """Configuração para cadastro de área de fertirrigação."""
    
    area_id: str = ""
    poligono: Dict[str, Any] = field(default_factory=dict)
    talhao: str = ""
    cultura: Cultura = Cultura.TOMATE
    sistema_irrigacao: SistemaIrrigacao = SistemaIrrigacao.GOTEJO
    area_ha: float = 0.0
    propriedade_id: str = ""


@dataclass
class ConfigAnaliseSolucao(ConfigBase):
    """Configuração para análise de soluções."""
    
    # Fontes de entrada
    usar_extrator_solucao: bool = True
    usar_laboratorio: bool = False
    usar_entrada_manual: bool = False
    usar_arquivos_csv: bool = False
    usar_arquivos_xlsx: bool = False
    
    # Parâmetros de processamento
    metodologia_analise: MetodoAnalise = MetodoAnalise.LABORATORIO
    tolerancia_ce_pct: float = 5.0
    limiar_ce_min_ds_m: float = 0.5
    limiar_ce_max_ds_m: float = 3.5


@dataclass
class ConfigNutricao(ConfigBase):
    """Configuração para processamento nutricional."""
    
    # Macronutrientes
    objetivo_n_kg_ha: float = 0.0
    objetivo_p2o5_kg_ha: float = 0.0
    objetivo_k2o_kg_ha: float = 0.0
    
    # Micronutrientes
    objetivo_ca_mg_L: float = 0.0
    objetivo_mg_mg_L: float = 0.0
    objetivo_s_mg_L: float = 0.0
    objetivo_fe_mg_L: float = 0.0
    objetivo_mn_mg_L: float = 0.0
    objetivo_zn_mg_L: float = 0.0
    objetivo_cu_mg_L: float = 0.0
    objetivo_b_mg_L: float = 0.0
    objetivo_mo_mg_L: float = 0.0
    
    # Balanço
    tolerancia_nutricional_pct: float = 5.0
    calcular_pH: bool = True
    objetivo_pH_min: float = 6.0
    objetivo_pH_max: float = 6.5


@dataclass
class ConfigRecomendacao(ConfigBase):
    """Configuração para recomendação de fertilizantes."""
    
    # Modo de operação
    modo: ModoRecomendacao = ModoRecomendacao.PRODUTO_COMERCIAL
    
    # Produtos comerciais (quando modo = PRODUTO_COMERCIAL)
    produtos_comerciais: List[str] = field(default_factory=list)
    
    # Fontes individuais (quando modo = FONTES_INDIVIDUAIS)
    fontes_preferenciais: List[str] = field(default_factory=list)
    
    # Parâmetros de otimização
    capacidade_misturador_kg: float = 3000.0
    custo_mao_obra_hora: float = 25.0
    custo_energia_kwh: float = 0.80


@dataclass
class ConfigExportacaoFertirrigacao(ConfigBase):
    """Configuração para exportação de resultados."""
    
    formatos: List[str] = field(default_factory=list)
    
    # Parâmetros específicos
    incluir_moldura: bool = True
    incluir_legenda: bool = True
    incluir_escalas: bool = True
    resolucao_dpi: int = 300


@dataclass
class ConfigAgronomiaFertirrigacao(ConfigBase):
    """Configuração para processamento agronômico."""
    
    # Cultura e sistema
    cultura: Cultura = Cultura.TOMATE
    sistema_irrigacao: SistemaIrrigacao = SistemaIrrigacao.GOTEJO
    
    # Fases fenológicas
    fase_atual: str = "vegetativo"
    data_plantio: Optional[str] = None
    
    # Parâmetros de calibração
    eficiencia_aplicacao_pct: float = 85.0
    perdas_transporte_pct: float = 5.0


# --------------------------------------------------
# DATACLASSES DE MODELOS DE DADOS
# --------------------------------------------------

@dataclass
class LeituraSolucao:
    """Leitura de solução coletada em ponto de monitoramento."""
    
    ponto_id: str
    data_leitura: str
    hora_leitura: str = ""
    
    # Parâmetros principais
    ph: Optional[float] = None
    ce_ds_m: float = 0.0
    no3_mg_L: Optional[float] = None
    k_mg_L: Optional[float] = None
    ca_mg_L: Optional[float] = None
    mg_mg_L: Optional[float] = None
    po4_mg_L: Optional[float] = None
    so4_mg_L: Optional[float] = None
    
    # Micronutrientes
    b_mg_L: Optional[float] = None
    fe_mg_L: Optional[float] = None
    mn_mg_L: Optional[float] = None
    zn_mg_L: Optional[float] = None
    cu_mg_L: Optional[float] = None
    
    # Metadados
    metodo_analise: MetodoAnalise = MetodoAnalise.LABORATORIO
    laboratorio: Optional[str] = None
    volume_coletado_ml: Optional[float] = None
    observacoes: Optional[str] = None


@dataclass
class AreaFertirrigacao:
    """Área de fertirrigação com seus atributos."""
    
    area_id: str
    poligono: Dict[str, Any]
    talhao: str
    cultura: Cultura
    sistema_irrigacao: SistemaIrrigacao
    area_ha: float
    propriedade_id: str = "PROP001"
    pontos_monitoramento: List[str] = field(default_factory=list)


@dataclass
class PrescricaoNutricional:
    """Prescrição nutricional convertida para demanda."""
    
    prescricao_id: int
    zona_id: str
    area_ha: float
    dose_kg_ha: float
    nutrientes_kg_ha: Dict[str, float]
    cultura: str = ""
    metodologia: str = ""
    fontes_preferenciais: List[str] = field(default_factory=list)

    @property
    def peso_total_kg(self) -> float:
        """Peso total necessário em kg."""
        return self.area_ha * self.dose_kg_ha

    @property
    def demanda_por_tonelada(self) -> Dict[str, float]:
        """Converte demanda kg/ha para kg por tonelada de blend."""
        if self.dose_kg_ha <= 0:
            return {}
        return {
            nut: (quantidade / self.dose_kg_ha) * 1000.0
            for nut, quantidade in self.nutrientes_kg_ha.items()
            if quantidade > 0
        }


# --------------------------------------------------
# DATACLASSES DE RESULTADOS
# --------------------------------------------------

@dataclass
class ResultadoAnaliseSolucao:
    """Resultado da análise de soluções."""
    
    leituras_originais: List[LeituraSolucao]
    leituras_validadas: List[LeituraSolucao]
    estatisticas: Dict[str, Any]
    curva_nutritiva: Dict[str, Any]
    anomalias: List[str]
    recomendacoes_imediatas: List[str]
    config: Any = None
    timestamp: float = 0
    tempo_execucao_ms: int = 0


@dataclass
class ResultadoNutricao:
    """Resultado do processamento nutricional."""
    
    macronutrientes_analisados: Dict[str, float]
    micronutrientes_analisados: Dict[str, float]
    balanco_nutricional: Dict[str, Any]
    interpretacao: str
    recomendacao_pH: Optional[str] = None
    pontos_criticos: List[str] = field(default_factory=list)
    config: Any = None
    timestamp: float = 0
    tempo_execucao_ms: int = 0


@dataclass
class ResultadoRecomendacao:
    """Resultado da recomendação de fertilizantes."""
    
    modo_utilizado: ModoRecomendacao
    recomendacoes: List[Dict[str, Any]]
    composicao_mistura: Dict[str, float]
    custo_estimado: float
    lotes_aplicacao: List[Dict[str, Any]]
    observacoes_tecnicas: List[str]
    config: Any = None
    timestamp: float = 0
    tempo_execucao_ms: int = 0


@dataclass
class ResultadoFertirrigacao:
    """Resultado completo da análise de fertirrigação."""
    
    area_analisada: AreaFertirrigacao
    resultado_analise_solucao: ResultadoAnaliseSolucao
    resultado_nutricao: ResultadoNutricao
    resultado_recomendacao: ResultadoRecomendacao
    mapa_interpolado: Optional[Dict[str, Any]] = None
    zonas_de_recomendacao: Optional[List[Dict[str, Any]]] = None
    config: Any = None
    timestamp: float = 0
    tempo_execucao_ms: int = 0