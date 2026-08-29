"""
Precision VRT Solo — Submódulo Monitoramento

Implementa o motor principal do sistema de monitoramento temporal.
Extraído e adaptado de core_agronomia_monitoramento_legado.py.
"""

from .motor import MotorMonitoramento

__all__ = [
    'MotorMonitoramento',
    'CalculadorIndices'
]