"""
Precision VRT Solo - Módulo Core

Exporta as classes principais do sistema para facilitar os imports.
"""

from .prescricao_vrt.interpolacao import InterpoladorSolo
from .prescricao_vrt.zoneamento import Zoneador  # DESCOMENTE ESTA LINHA
from .prescricao_vrt.prescricao import MotorPrescricao
from .prescricao_vrt.exportacao import Exportador

__all__ = [
    "InterpoladorSolo",
    "Zoneador",
    "MotorPrescricao",
    "Exportador"
]