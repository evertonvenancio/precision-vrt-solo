"""
Precision VRT Solo — Configuração de Otimização

Classes de configuração para algoritmos de otimização.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

from ..exceptions import OtimizacaoError
from .contratos import ProblemaOtimizacao


@dataclass
class ProblemaOtimizacao:
    """Configuração de um problema de otimização."""
    pass


DEFAULT_CONFIG = {
    'max_iteracoes': 1000,
    'tolerancia': 1e-6,
    'otimizador': 'scipy'
}