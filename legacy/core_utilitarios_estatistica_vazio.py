"""
Precision VRT Solo — Estatística Utils do CORE
"""

from typing import Any, Dict, List, Optional

def media_lista(valores: List[float]) -> float:
    """Calcula média de lista."""
    return sum(valores) / len(valores) if valores else 0.0

def desvio_padrao_lista(valores: List[float]) -> float:
    """Calcula desvio padrão."""
    if not valores:
        return 0.0
    media = media_lista(valores)
    variancia = sum((x - media) ** 2 for x in valores) / len(valores)
    return variancia ** 0.5

def media(valores: List[float]) -> float:
    """Calcula média (alias para media_lista)."""
    return media_lista(valores)

def desvio_padrao(valores: List[float]) -> float:
    """Calcula desvio padrão (alias para desvio_padrao_lista)."""
    return desvio_padrao_lista(valores)

def coeficiente_variacao(valores: List[float]) -> float:
    """Calcula coeficiente de variação."""
    if not valores:
        return 0.0
    media_val = media_lista(valores)
    if media_val == 0:
        return 0.0
    return (desvio_padrao_lista(valores) / abs(media_val)) * 100

def minimo(valores: List[float]) -> float:
    """Retorna mínimo."""
    return min(valores) if valores else 0.0

def maximo(valores: List[float]) -> float:
    """Retorna máximo."""
    return max(valores) if valores else 0.0

def percentil(valores: List[float], q: float) -> float:
    """Calcula percentil."""
    if not valores:
        return 0.0
    import numpy as np
    return np.percentile(valores, q)

def mediana(valores: List[float]) -> float:
    """Calcula mediana."""
    if not valores:
        return 0.0
    sorted_vals = sorted(valores)
    n = len(sorted_vals)
    if n % 2 == 1:
        return sorted_vals[n//2]
    else:
        return (sorted_vals[n//2 - 1] + sorted_vals[n//2]) / 2
