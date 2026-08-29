"""
Precision VRT Solo — Módulo de Seleção de Satélites

Gerencia a seleção e configuração de satélites para sensoriamento remoto.
Suporta Sentinel, Landsat, Planet, CBERS e outros satélites disponíveis.
"""

from .motor import MotorSelecaoSatelites

__all__ = ['MotorSelecaoSatelites']