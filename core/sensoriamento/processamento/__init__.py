"""
Precision VRT Solo — Módulo de Processamento de Imagens

Processa imagens de satélites e drones com alinhamento, recorte, normalização,
máscara, remoção de nuvens e padronização.
"""

from .motor import MotorProcessamentoSensoriamento

__all__ = ['MotorProcessamentoSensoriamento']