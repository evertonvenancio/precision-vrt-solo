"""
Precision VRT Solo — Funções Auxiliares para Matriz

Funções auxiliares para manipulação de matrizes de features.
Implementadas com numpy puro para máxima performance.
"""

import numpy as np
from typing import Dict, List


def remover_nan_por_linha(X: np.ndarray) -> np.ndarray:
    """
    Remove linhas que contenham qualquer NaN.
    Retorna cópia limpa do array.
    
    Args:
        X: Array numpy 2D de entrada
        
    Returns:
        Array numpy 2D sem linhas contendo NaN
        
    Raises:
        ValueError: Se X não for array 2D
    """
    if X.ndim != 2:
        raise ValueError("Array deve ser 2D para remover_nan_por_linha")
    
    # Criar máscara de linhas sem NaN
    mascara = ~np.any(np.isnan(X), axis=1)
    
    return X[mascara].copy()


def detectar_outliers_iqr(X: np.ndarray, fator: float = 1.5) -> np.ndarray:
    """
    Detecta outliers usando o método do Intervalo Interquartil (IQR).
    Retorna máscara booleana (True = outlier) por feature.
    
    Args:
        X: Array numpy 2D de entrada
        fator: Fator multiplicativo para o IQR (default 1.5)
        
    Returns:
        Array booleano 2D com outliers detectados
        
    Raises:
        ValueError: Se X não for array 2D ou fator <= 0
    """
    if X.ndim != 2:
        raise ValueError("Array deve ser 2D para detectar_outliers_iqr")
    
    if fator <= 0:
        raise ValueError("Fator deve ser positivo")
    
    n_linhas, n_colunas = X.shape
    outliers = np.zeros_like(X, dtype=bool)
    
    for col in range(n_colunas):
        coluna = X[:, col]
        
        # Calcular quartis
        Q1 = np.percentile(coluna, 25)
        Q3 = np.percentile(coluna, 75)
        
        # Calcular IQR
        IQR = Q3 - Q1
        
        # Calcular limites
        limite_inferior = Q1 - fator * IQR
        limite_superior = Q3 + fator * IQR
        
        # Detectar outliers
        outliers[:, col] = (coluna < limite_inferior) | (coluna > limite_superior)
    
    return outliers


def escalonar_min_max(X: np.ndarray) -> np.ndarray:
    """
    Aplica Min-Max scaling para normalizar dados para [0, 1].
    Trava divisão por zero (retém valor original se range for zero).
    
    Args:
        X: Array numpy 2D de entrada
        
    Returns:
        Array numpy 2D escalonado para [0, 1]
        
    Raises:
        ValueError: Se X não for array 2D
    """
    if X.ndim != 2:
        raise ValueError("Array deve ser 2D para escalonar_min_max")
    
    n_linhas, n_colunas = X.shape
    X_escalado = np.zeros_like(X, dtype=float)
    
    for col in range(n_colunas):
        coluna = X[:, col]
        
        min_val = np.min(coluna)
        max_val = np.max(coluna)
        
        # Evitar divisão por zero
        if max_val - min_val > 1e-10:
            X_escalado[:, col] = (coluna - min_val) / (max_val - min_val)
        else:
            # Se range for zero, manter valor original (normalizado para 0.5)
            X_escalado[:, col] = 0.5
    
    return X_escalado


def padronizar_zscore(X: np.ndarray) -> np.ndarray:
    """
    Aplica Z-score normalization (média 0, desvio 1).
    Trava divisão por zero (retém valor original se desvio for zero).
    
    Args:
        X: Array numpy 2D de entrada
        
    Returns:
        Array numpy 2D padronizado
        
    Raises:
        ValueError: Se X não for array 2D
    """
    if X.ndim != 2:
        raise ValueError("Array deve ser 2D para padronizar_zscore")
    
    n_linhas, n_colunas = X.shape
    X_padronizado = np.zeros_like(X, dtype=float)
    
    for col in range(n_colunas):
        coluna = X[:, col]
        
        media_val = np.mean(coluna)
        desvio_val = np.std(coluna)
        
        # Evitar divisão por zero
        if desvio_val > 1e-10:
            X_padronizado[:, col] = (coluna - media_val) / desvio_val
        else:
            # Se desvio for zero, manter valor original (padronizado para 0)
            X_padronizado[:, col] = 0.0
    
    return X_padronizado


def aplicar_pesos_features(X: np.ndarray, pesos: Dict[str, float], colunas: List[str]) -> np.ndarray:
    """
    Aplica pesos por feature na matriz.
    As chaves do dicionário de pesos devem corresponder às colunas.
    
    Args:
        X: Array numpy 2D de entrada
        pesos: Dicionário com pesos por feature
        colunas: Lista de nomes das colunas na ordem do array
        
    Returns:
        Array numpy 2D com pesos aplicados
        
    Raises:
        ValueError: Se pesos contiver chaves inválidas
    """
    if X.shape[1] != len(colunas):
        raise ValueError("Número de colunas não corresponde ao array")
    
    X_peso = X.copy()
    
    for i, coluna in enumerate(colunas):
        if coluna in pesos:
            peso = pesos[coluna]
            if peso < 0:
                raise ValueError(f"Peso negativo para coluna '{coluna}': {peso}")
            X_peso[:, i] *= peso
    
    return X_peso