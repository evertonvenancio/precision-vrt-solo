"""
Precision VRT Solo — Submódulo de Comparação Temporal

Implementa funcionalidades para comparação temporal de imagens,
detecção de mudanças e análise de evolução temporal.
"""

from .motor import AnalisadorComparacao, AgrupadorTemporal, GerenciadorAlertas

__all__ = [
    'AnalisadorComparacao',
    'AgrupadorTemporal',
    'GerenciadorAlertas'
]