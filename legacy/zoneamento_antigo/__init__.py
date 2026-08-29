"""
Precision VRT Solo — Módulo de Zoneamento

Biblioteca científica pura para zoneamento agrícola.

Este módulo recebe camadas de dados espaciais e entrega zonas agrupadas.
Não conhece cultura, fertilizante, metodologia, banco de dados, API ou interface gráfica.
"""

# Imports principais
from .contratos import (
    AlgoritmoEnum,
    ConfigZoneamento,
    MetricaQualidadeEnum,
    PerfilZona,
    ResultadoZoneamento,
    AlgoritmoClusteringProtocol
)
from .exceptions import (
    ZoneamentoError,
    ValidacaoError,
    AlgoritmoError,
    ConfiguracaoError,
    DadosInsuficientesError
)
from .configuracao import ALGORITMO_REGISTRY, ConfigZoneamento, DEFAULT_CONFIG
from .motor import Zoneador
from .validacao import (
    validar_geodataframe,
    validar_configuracao,
    extrair_features,
    verificar_nan_inf
)

# Export público
__all__ = [
    # Classes principais
    "Zoneador",
    "ConfigZoneamento",
    "ResultadoZoneamento",
    "PerfilZona",
    
    # Enums
    "AlgoritmoEnum",
    "MetricaQualidadeEnum",
    
    # Exceções
    "ZoneamentoError",
    "ValidacaoError",
    "AlgoritmoError",
    "ConfiguracaoError",
    "DadosInsuficientesError",
    
    # Configurações
    "DEFAULT_CONFIG",
    "ALGORITMO_REGISTRY",
    
    # Validações
    "validar_geodataframe",
    "validar_configuracao",
    "extrair_features",
    "verificar_nan_inf",
]