"""
Precision VRT Solo — Métrica Calinski-Harabasz

Cálculo do Calinski-Harabasz index (Variance Ratio Criterion) para avaliação de qualidade de agrupamento.
Quanto maior, melhor (variância entre clusters é alta vs variância dentro de clusters é baixa).
"""

import numpy as np
from sklearn.metrics import calinski_harabasz_score


def calcular(X: np.ndarray, labels: np.ndarray) -> float:
    """
    Calcula Calinski-Harabasz index.
    Usa sklearn.metrics.calinski_harabasz_score.
    
    Args:
        X: Array numpy 2D com dados normalizados
        labels: Array numpy com rótulos de zona (começando em 0)
        
    Returns:
        Calinski-Harabasz index (quanto maior, melhor)
        
    Raises:
        ValueError: Se X não for 2D ou labels não corresponderem
    """
    if X.ndim != 2:
        raise ValueError("X deve ser array 2D para calcular Calinski-Harabasz index")
    
    if len(labels) != X.shape[0]:
        raise ValueError("Número de labels deve corresponder ao número de linhas de X")
    
    # Verificar se há pelo menos 2 clusters
    n_clusters = len(np.unique(labels))
    if n_clusters < 2:
        return 0.0  # Calinski-Harabasz não é definido para 1 cluster
    
    # Calcular Calinski-Harabasz index
    try:
        score = calinski_harabasz_score(X, labels)
        return float(score)
    except Exception as e:
        # Em caso de erro, retornar 0 (indicando qualidade ruim)
        return 0.0