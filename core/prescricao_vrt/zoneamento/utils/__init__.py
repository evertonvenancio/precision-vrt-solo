"""
Precision VRT Solo — Módulo de Utilidades

Funções utilitárias genéricas para o módulo zoneamento.
"""

from .estatistica import media, desvio_padrao, variancia
from .matriz import remover_nan_por_linha, detectar_outliers_iqr, escalonar_min_max, padronizar_zscore, aplicar_pesos_features
from .normalizacao import Normalizador, CalculadorMetricas

__all__ = [
    'media',
    'desvio_padrao', 
    'variancia',
    'remover_nan_por_linha',
    'detectar_outliers_iqr',
    'escalonar_min_max',
    'padronizar_zscore',
    'aplicar_pesos_features',
    'Normalizador',
    'CalculadorMetricas',
]