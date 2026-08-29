"""
Precision VRT Solo — Routers da API

Endpoints HTTP da camada de API.
Cada rota chama exclusivamente o Service correspondente.
"""

from . import (
    prescricao_vrt,
    compactacao,
    nematoides,
    fertirrigacao,
    sensoriamento,
    monitoramento,
    exportacao,
    validacao,
    configuracoes,
    cadastros,
    financeiro,
    crm
)

__all__ = [
    'prescricao_vrt',
    'compactacao', 
    'nematoides',
    'fertirrigacao',
    'sensoriamento',
    'monitoramento',
    'exportacao',
    'validacao',
    'configuracoes',
    'cadastros',
    'financeiro',
    'crm'
]