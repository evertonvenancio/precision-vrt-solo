"""
Precision VRT Solo — Schemas da API

Schemas de entrada e saída da API.
Contém apenas tipos, sem regra de negócio.
"""

from . import (
    prescricao,
    compactacao,
    nematoides,
    fertirrigacao,
    sensoriamento,
    monitoramento,
    exportacao,
    comum
)

__all__ = [
    'prescricao',
    'compactacao',
    'nematoides', 
    'fertirrigacao',
    'sensoriamento',
    'monitoramento',
    'exportacao',
    'comum'
]