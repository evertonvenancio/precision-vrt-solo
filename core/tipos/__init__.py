"""
Precision VRT Solo — Tipos do CORE

Centralização de contratos, protocols e tipos base do CORE.
"""

from .base import ConfigBase, ResultadoBase, IdentificavelMixin, TimestampMixin, Serializavel
from .protocols import Orquestravel, Exportavel, Cacheavel, Validavel, Metrico
from .geoespacial import Coordenada, Bounds, ResolucaoEspacial, AffineTransform
from .execucao import StatusExecucaoEnum, ModoExecucaoEnum, NivelLogEnum

__all__ = [
    # Classes Base
    "ConfigBase",
    "ResultadoBase", 
    "IdentificavelMixin",
    "TimestampMixin",
    "Serializavel",
    
    # Protocols
    "Orquestravel",
    "Exportavel", 
    "Cacheavel",
    "Validavel",
    "Metrico",
    
    # Geoespaciais
    "Coordenada",
    "Bounds",
    "ResolucaoEspacial", 
    "AffineTransform",
    
    # Execução
    "StatusExecucaoEnum",
    "ModoExecucaoEnum",
    "NivelLogEnum"
]