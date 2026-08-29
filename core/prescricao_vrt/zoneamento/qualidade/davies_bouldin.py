"""
Precision VRT Solo — Métrica Davies-Bouldin

Cálculo do Davies-Bouldin index para avaliação de qualidade de agrupamento.
Quanto menor, melhor (similaridade intra-clusters baixa e similaridade inter-clusters alta).
"""

import numpy as np
from sklearn.metrics import davies_bouldin_score


def calcular(X: np.ndarray, labels: np.ndarray) -> float:
    """
    Calcula Davies-Bouldin index.
    Usa sklearn.metrics.davies_bouldin_score.
    
    Args:
        X: Array numpy 2D com dados normalizados
        labels: Array numpy com rótulos de zona (começando em 0)
        
    Returns:
        Davies-Bouldin index (quanto menor, melhor)
        
    Raises:
        ValueError: Se X não for 2D ou labels não corresponderem
    """
    if X.ndim != 2:
        raise ValueError("X deve ser array 2D para calcular Davies-Bouldin index")
    
    if len(labels) != X.shape[0]:
        raise ValueError("Número de labels deve corresponder ao número de linhas de X")
    
    # Verificar se há pelo menos 2 clusters
    n_clusters = len(np.unique(labels))
    if n_clusters < 2:
        return float('inf')  # Davies-Bouldin não é definido para 1 cluster
    
    # Calcular Davies-Bouldin index
    try:
        score = davies_bouldin_score(X, labels)
        return float(score)
    except Exception as e:
        # Em caso de erro, retornar valor alto (indicando qualidade ruim)
        return float('inf')