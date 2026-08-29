"""
Precision VRT Solo — Módulo de Otimização

Biblioteca científica pura para otimização agrícola.

Este módulo fornece programação linear e blendagem de fertilizantes.
Não conhece zoneamento, prescrição, banco de dados, API ou interface gráfica.
"""

# Imports principais
from .contratos import ProblemaOtimizacao, ResultadoOtimizacao
from .exceptions import OtimizacaoError, BlendagemError, RestricaoError
from .configuracao import ProblemaOtimizacao, DEFAULT_CONFIG
from .motor import Otimizador
from .blendagem import Blendador
from .validacao import (
    validar_problema_otimizacao,
    validar_restricoes,
    validar_blendagem
)

# Export público
__all__ = [
    # Classes principais
    "ProblemaOtimizacao",
    "ResultadoOtimizacao",
    "Otimizador",
    "Blendador",
    
    # Exceções
    "OtimizacaoError",
    "BlendagemError",
    "RestricaoError",
    
    # Configurações
    "DEFAULT_CONFIG",
    
    # Validações
    "validar_problema_otimizacao",
    "validar_restricoes",
    "validar_blendagem"
]