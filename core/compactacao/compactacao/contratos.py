"""
Precision VRT Solo — Contratos do Módulo de Compactação

Dataclasses, enums e modelos de dados para análise de compactação.
Estruturas puras de dados — sem lógica de negócio.
"""

import numpy as np
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from ...tipos.base import ConfigBase, ResultadoBase, IdentificavelMixin, TimestampMixin
from ...tipos.geoespacial import Coordenada, Bounds


class ClassificacaoSolo(str, Enum):
    """Classificação da resistência à penetração do solo."""
    APTO = "apto"
    RESTRICAO = "restricao"
    IMPEDIMENTO_SEVERO = "impedimento_severo"


class ClassificacaoCompactacao(str, Enum):
    """Classificação da compactação do solo."""
    APTO = "Apto"
    RESTRICAO = "Restricao"
    IMPEDIMENTO_SEVERO = "Impedimento Severo"


@dataclass
class CamadaCompactacao:
    """Dados de uma camada de compactação."""
    profundidade_inicio: float  # cm
    profundidade_fim: float     # cm
    resistencia_mpa: float      # MPa
    classificacao: str
    necessita_escarificacao: bool = False
    umidade: Optional[float] = None  # %
    temperatura: Optional[float] = None  # °C


@dataclass 
class PontoAmostral(IdentificavelMixin):
    """Ponto de amostragem de compactação."""
    identificador_ponto: str
    coordenada: Coordenada
    dados_equipamento: Dict[str, Any]
    camadas: List[CamadaCompactacao] = field(default_factory=list)
    classificacao_geral: str = ""
    necessita_escarificacao: bool = False
    profundidade_maxima_restricao: Optional[float] = None


@dataclass
class PerfilCompactacao(IdentificavelMixin, TimestampMixin):
    """Perfil completo de compactação de um ponto/talhão."""
    ponto_id: str
    coordenada: Coordenada
    camadas: List[CamadaCompactacao]
    classificacao_geral: str
    necessita_escarificacao: bool
    profundidade_maxima_restricao: Optional[float]
    dados_grafico: Dict[str, Any]
    
    @classmethod
    def from_analisador(cls, ponto_amostral: PontoAmostral, analisador) -> "PerfilCompactacao":
        """Cria perfil a partir do analisador e ponto amostral."""
        # Copiar dados básicos
        perfil = cls(
            ponto_id=ponto_amostral.id,
            coordenada=ponto_amostral.coordenada,
            camadas=ponto_amostral.camadas,
            classificacao_geral=ponto_amostral.classificacao_geral,
            necessita_escarificacao=ponto_amostral.necessita_escarificacao,
            profundidade_maxima_restricao=ponto_amostral.profundidade_maxima_restricao,
            dados_grafico={}
        )
        
        # Preparar dados para gráfico usando o analisador
        perfil.dados_grafico = analisador._preparar_dados_grafico(ponto_amostral.camadas)
        
        return perfil


@dataclass
class ResultadoZoneamentoCompactacao(IdentificavelMixin, TimestampMixin):
    """Resultado do zoneamento de compactação."""
    zonas: List[Dict[str, Any]]
    classificacao_predominante: str
    percentual_impedimento: float
    percentual_restricao: float
    percentual_apto: float
    recomendacao_geral: str
    mapa_final: Optional[Dict[str, Any]] = None
    zonas_suavizadas: Optional[List[Dict[str, Any]]] = None


@dataclass
class ConfigCompactacao(ConfigBase):
    """Configuração para análise de compactação."""
    
    # Dados da área
    bounds: Bounds
    resolucao_grade: float = 50.0  # metros
    
    # Configuração de amostragem
    usar_imagens_historicas: bool = False
    lista_satelites: List[str] = field(default_factory=list)
    
    # Configuração de interpolação
    metodo_interpolacao: str = "kriging"
    variograma_modelo: str = "spherical"
    max_distancia: float = 100.0  # metros
    
    # Configuração de zoneamento
    metodo_zoneamento: str = "kmeans"
    n_zonas: int = 5
    estrategia_fusao: str = "manual"  # manual ou automatico
    
    # Configuração de exportação
    formatos_exportacao: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Valida configuração após inicialização."""
        if self.metodo_interpolacao not in ["kriging", "idw", "natural_neighbor"]:
            raise ValueError(f"Método de interpolação inválido: {self.metodo_interpolacao}")
        
        if self.metodo_zoneamento not in ["kmeans", "dbscan", "agglomerative"]:
            raise ValueError(f"Método de zoneamento inválido: {self.metodo_zoneamento}")
        
        if self.estrategia_fusao not in ["manual", "automatico"]:
            raise ValueError(f"Estratégia de fusão inválida: {self.estrategia_fusao}")


@dataclass
class ResultadoCompactacao(ResultadoBase):
    """Resultado completo da análise de compactação."""
    
    # Pipeline results
    perfil_inicial: Optional[PontoAmostral] = None
    resultado_interpolacao: Optional[Dict[str, Any]] = None
    resultado_zoneamento: Optional[ResultadoZoneamentoCompactacao] = None
    mapa_final: Optional[Dict[str, Any]] = None
    
    # Estatísticas
    pontos_analisados: int = 0
    camadas_analisadas: int = 0
    areas_impedimento: float = 0.0  # hectares
    areas_restricao: float = 0.0    # hectares
    areas_apto: float = 0.0         # hectares
    
    # Flags e recomendações
    flags_escarificacao: List[Dict[str, Any]] = field(default_factory=list)
    recomendacoes: List[str] = field(default_factory=list)
    
    # Metadados
    metadados_poco: Dict[str, Any] = field(default_factory=dict)
    metadados_interpolacao: Dict[str, Any] = field(default_factory=dict)
    metadados_zoneamento: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DadosEquipamento:
    """Dados do equipamento de medição."""
    
    # Equipamento de impacto
    tipo: str = "impacto"  # "impacto" ou "eletronico"
    gps: Optional[Coordenada] = None
    profundidade: float = 0.0  # cm
    numero_impactos: Optional[int] = None
    distancia_penetrada: Optional[float] = None  # cm
    
    # Equipamento eletrônico  
    resistencia: Optional[float] = None  # MPa
    umidade: Optional[float] = None     # %
    temperatura: Optional[float] = None  # °C
    
    def validar(self) -> List[str]:
        """Valida dados do equipamento e retorna lista de erros."""
        erros = []
        
        if self.tipo not in ["impacto", "eletronico"]:
            erros.append("Tipo de equipamento inválido. Deve ser 'impacto' ou 'eletronico'")
        
        if self.gps is None:
            erros.append("GPS é obrigatório")
        
        if self.tipo == "impacto":
            if self.numero_impactos is None and self.distancia_penetrada is None:
                erros.append("Para equipamento de impacto, informe número de impactos ou distância penetrada")
        elif self.tipo == "eletronico":
            if self.resistencia is None:
                erros.append("Para equipamento eletrônico, resistência é obrigatória")
        
        return erros


@dataclass 
class AmostraCampo:
    """Amostra de campo para análise de compactação."""
    identificador: str
    equipamento: DadosEquipamento
    timestamp: datetime
    
    def obter_resistencias(self) -> List[float]:
        """Extrai resistências da amostra."""
        if self.equipamento.tipo == "impacto":
            # Para equipamento de impacto, calcular resistência baseada em impactos
            if self.equipamento.numero_impactos:
                # Exemplo: resistência inversamente proporcional a impactos
                return [10.0 / self.equipamento.numero_impactos]
            else:
                # Para equipamento com distância, usar fórmula simples
                return [self.equipamento.distancia_penetrada / 10.0] if self.equipamento.distancia_penetrada else [0.0]
        else:
            # Equipamento eletrônico - retorna resistência direta
            return [self.equipamento.resistencia] if self.equipamento.resistencia else [0.0]