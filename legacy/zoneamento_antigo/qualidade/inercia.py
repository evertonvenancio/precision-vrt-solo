"""
Precision VRT Solo — Métrica Inércia

Cálculo manual da inércia (soma das distâncias quadradas aos centroides)
para avaliação de qualidade de agrupamento. Quanto menor, melhor.
"""

import numpy as np
from typing import Optional


def calcular(X: np.ndarray, labels: np.ndarray, centroides: Optional[np.ndarray] = None) -> float:
    """
    Calcula inércia manualmente (soma das distâncias quadradas aos centroides).
    Se centroides for None, calcula centroides a partir dos labels.
    
    Args:
        X: Array numpy 2D com dados normalizados
        labels: Array numpy com rótulos de zona (começando em 0)
        centroides: Array opcional com centroides pré-calculados
        
    Returns:
        Inércia total (soma das distâncias quadradas)
        
    Raises:
        ValueError: Se X não for 2D ou labels não corresponderem
    """
    if X.ndim != 2:
        raise ValueError("X deve ser array 2D para calcular inércia")
    
    if len(labels) != X.shape[0]:
        raise ValueError("Número de labels deve corresponder ao número de linhas de X")
    
    # Calcular centroides se não fornecidos
    if centroides is None:
        n_clusters = len(np.unique(labels))
        centroides = np.zeros((n_clusters, X.shape[1]))
        
        for i in range(n_clusters):
            mask = labels == i
            if np.any(mask):
                centroides[i] = np.mean(X[mask], axis=0)
            else:
                # Se um cluster estiver vazio, usar zero
                centroides[i] = np.zeros(X.shape[1])
    
    # Calcular distâncias quadradas aos centroides
    inertias = []
    
    for i, label in enumerate(labels):
        centroide = centroides[label]
        distancia_quadrada = np.sum((X[i] - centroide) ** 2)
        inertias.append(distancia_quadrada)
    
    return float(np.sum(inertias))