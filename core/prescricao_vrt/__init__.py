"""
Precision VRT Solo — Módulo Prescrição VRT (compatibilidade)

Este módulo serve como ponte de compatibilidade com imports antigos.
"""

# Exportar classes principais
from .prescricao import MotorPrescricao
from .motor_composto import MotorPrescricaoComposto

# Para compatibilidade com imports diretos
__all__ = [
    'MotorPrescricao',
    'MotorPrescricaoComposto'
]