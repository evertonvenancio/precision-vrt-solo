"""
Precision VRT Solo — Utilitários Estatísticos

Funções estatísticas básicas para módulos do CORE.
"""
import numpy as np
from typing import Union


def media(valores: np.ndarray) -> float:
    """Calcula média de um array."""
    return float(np.mean(valores))


def desvio_padrao(valores: np.ndarray) -> float:
    """Calcula desvio padrão de um array."""
    return float(np.std(valores))


def coeficiente_variacao(valores: np.ndarray) -> float:
    """Calcula coeficiente de variação (%) de um array."""
    media_val = np.mean(valores)
    if media_val == 0:
        return 0.0
    return float((np.std(valores) / media_val) * 100)


def minimo(valores: np.ndarray) -> float:
    """Retorna valor mínimo de um array."""
    return float(np.min(valores))


def maximo(valores: np.ndarray) -> float:
    """Retorna valor máximo de um array."""
    return float(np.max(valores))


def mediana(valores: np.ndarray) -> float:
    """Retorna mediana de um array."""
    return float(np.median(valores))


def percentil(valores: np.ndarray, percentil: float) -> float:
    """Retorna percentil específico de um array."""
    return float(np.percentile(valores, percentil))