"""
Precision VRT Solo — Módulo Prescrição (compatibilidade)

Este módulo serve como ponte de compatibilidade com imports antigos.
"""

from .motor import MotorPrescricao

# Para compatibilidade com imports diretos
__all__ = ['MotorPrescricao']