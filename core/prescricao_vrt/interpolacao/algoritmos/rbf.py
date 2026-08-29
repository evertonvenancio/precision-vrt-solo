"""
Precision VRT Solo — Algoritmo RBF (Radial Basis Function)

Implementa interpolação usando funções de base radial.
"""

import warnings
import numpy as np
from scipy.interpolate import RBFInterpolator


def interpolar_rbf(
    xy: np.ndarray,
    z: np.ndarray,
    grid: np.ndarray,
    shape: tuple,
    kernel: str = "multiquadric",
    smoothing: float = 0.1,
) -> np.ndarray:
    """
    Interpolação usando RBF (Radial Basis Function).
    
    Args:
        xy: Array de coordenadas normalizadas (n_pontos, 2)
        z: Array de valores observados (n_pontos,)
        grid: Array de coordenadas da grade para interpolação (n_pixels, 2)
        shape: Shape da grade original (nx, ny)
        kernel: Função RBF a ser utilizada
        smoothing: Parâmetro de suavização
        
    Returns:
        Array interpolado重塑 para shape original
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        interpolador = RBFInterpolator(
            xy,
            z,
            kernel=kernel,
            smoothing=smoothing,
        )
        pred = interpolador(grid).reshape(shape)
    
    return pred