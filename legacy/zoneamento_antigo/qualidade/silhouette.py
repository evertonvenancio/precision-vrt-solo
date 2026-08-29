"""
Precision VRT Solo — Métrica Silhouette

Cálculo do silhouette score para avaliação de qualidade de agrupamento.
"""

import numpy as np
from sklearn.metrics import silhouette_score


def calcular(X: np.ndarray, labels: np.ndarray) -> float:
    """
    Calcula silhouette score médio.
    Usa sklearn.metrics.silhouette_score.
    
    Args:
        X: Array numpy 2D com dados normalizados
        labels: Array numpy com rótulos de zona (começando em 0)
        
    Returns:
        Silhouette score médio (entre -1 e 1)
        
    Raises:
        ValueError: Se X não for 2D ou labels não corresponderem
    """
    if X.ndim != 2:
        raise ValueError("X deve ser array 2D para calcular silhouette score")
    
    if len(labels) != X.shape[0]:
        raise ValueError("Número de labels deve corresponder ao número de linhas de X")
    
    # Verificar se há pelo menos 2 clusters
    n_clusters = len(np.unique(labels))
    if n_clusters < 2:
        return 0.0  # Silhouette não é definido para 1 cluster
    
    # Calcular silhouette score
    try:
        score = silhouette_score(X, labels)
        return float(score)
    except Exception as e:
        # Em caso de erro (ex: apenas 1 amostra por cluster), retornar 0
        return 0.0