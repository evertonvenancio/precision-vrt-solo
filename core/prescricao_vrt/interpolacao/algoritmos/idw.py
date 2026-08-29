"""
Precision VRT Solo — Algoritmo IDW (Inverse Distance Weighting)

Implementa interpolação ponderada por distância inversa.
"""

import numpy as np
from scipy.spatial import cKDTree


def interpolar_idw(
    xy: np.ndarray,
    z: np.ndarray,
    grid: np.ndarray,
    shape: tuple,
    potencia: float = 2.0,
) -> np.ndarray:
    """
    Interpolação usando IDW (Inverse Distance Weighting).
    
    Args:
        xy: Array de coordenadas normalizadas (n_pontos, 2)
        z: Array de valores observados (n_pontos,)
        grid: Array de coordenadas da grade para interpolação (n_pixels, 2)
        shape: Shape da grade original (nx, ny)
        potencia: Potência para cálculo dos pesos
        
    Returns:
        Array interpolado重塑 para shape original
    """
    tree = cKDTree(xy)
    distancias, indices = tree.query(grid, k=min(8, len(z)))
    
    # Evitar divisão por zero
    distancias = np.where(distancias < 1e-10, 1e-10, distancias)
    pesos = 1.0 / (distancias ** potencia)
    pesos_sum = pesos.sum(axis=1)
    
    pred = np.sum(pesos * z[indices], axis=1) / pesos_sum
    return pred.reshape(shape)