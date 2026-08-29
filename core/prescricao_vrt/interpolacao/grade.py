"""
Precision VRT Solo — Geração de Grade/Meshgrid

Funções para criação de grades regulares de interpolação.
"""

import numpy as np


def gerar_malha(
    x: np.ndarray,
    y: np.ndarray,
    resolucao_m: int = 10,
) -> tuple:
    """
    Gera a malha de interpolação regular.
    
    Args:
        x: Array de coordenadas X originais
        y: Array de coordenadas Y originais
        resolucao_m: Resolução da grade em metros
        
    Returns:
        Tuple (grid_x, grid_y) com as coordenadas da grade
    """
    xmin, xmax = float(x.min()), float(x.max())
    ymin, ymax = float(y.min()), float(y.max())
    
    # Resolução aproximada em graus (~10m = 10/111320 graus)
    resolucao_graus = resolucao_m / 111320.0
    
    nx = max(int((xmax - xmin) / resolucao_graus) + 1, 20)
    ny = max(int((ymax - ymin) / resolucao_graus) + 1, 20)
    
    grid_x, grid_y = np.meshgrid(
        np.linspace(xmin, xmax, nx),
        np.linspace(ymin, ymax, ny),
    )
    
    return grid_x, grid_y


def normalizar_coordenadas(
    x_valid: np.ndarray,
    y_valid: np.ndarray,
    grid_x: np.ndarray,
    grid_y: np.ndarray,
) -> tuple:
    """
    Normaliza coordenadas para estabilidade numérica.
    
    Args:
        x_valid: Coordenadas X válidas (filtradas)
        y_valid: Coordenadas Y válidas (filtradas)
        grid_x: Coordenadas X da grade
        grid_y: Coordenadas Y da grade
        
    Returns:
        Tuple (xy_norm, grid_norm) com coordenadas normalizadas
    """
    x_mean, x_std = x_valid.mean(), x_valid.std() or 1.0
    y_mean, y_std = y_valid.mean(), y_valid.std() or 1.0
    
    xy_norm = np.column_stack([
        (x_valid - x_mean) / x_std,
        (y_valid - y_mean) / y_std,
    ])
    grid_norm = np.column_stack([
        (grid_x.ravel() - x_mean) / x_std,
        (grid_y.ravel() - y_mean) / y_std,
    ])
    
    return xy_norm, grid_norm