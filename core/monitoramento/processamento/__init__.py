"""
Precision VRT Solo — Submódulo de Processamento

Implementa o pipeline completo de processamento de imagens:
normalização, alinhamento, recorte e padronização.
Nunca altera a imagem original.
"""

from .motor import (
    ConfigProcessamento,
    ResultadoProcessamento,
    NormalizadorImagens,
    AlinhadorImagens,
    RecortadorImagens,
    PadronizadorImagens,
    MotorProcessamento
)

__all__ = [
    'ConfigProcessamento',
    'ResultadoProcessamento',
    'NormalizadorImagens',
    'AlinhadorImagens',
    'RecortadorImagens',
    'PadronizadorImagens',
    'MotorProcessamento'
]