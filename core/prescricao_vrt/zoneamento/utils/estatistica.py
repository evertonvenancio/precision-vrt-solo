"""
Precision VRT Solo — Funções Estatísticas Genéricas

Funções puras, sem side effects, reutilizáveis por TODO o core.
Implementadas com numpy puro sem dependências externas.
"""

import numpy as np
from typing import Optional

from ..exceptions import ValidacaoError


def media(X: np.ndarray, axis: int = 0) -> np.ndarray:
    """
    Calcula a média de um array numpy.
    
    Args:
        X: Array numpy de entrada
        axis: Eixo ao longo do qual calcular a média (0=colunas, 1=linhas)
        
    Returns:
        Array numpy com as médias calculadas
        
    Raises:
        ValidacaoError: Se o array estiver vazio
    """
    if X.size == 0:
        raise ValidacaoError("Array vazio: não é possível calcular média")
    
    return np.mean(X, axis=axis)


def desvio_padrao(X: np.ndarray, axis: int = 0) -> np.ndarray:
    """
    Calcula o desvio padrão de um array numpy.
    
    Args:
        X: Array numpy de entrada
        axis: Eixo ao longo do qual calcular o desvio padrão
        
    Returns:
        Array numpy com os desvios padrão calculados
        
    Raises:
        ValidacaoError: Se o array estiver vazio
    """
    if X.size == 0:
        raise ValidacaoError("Array vazio: não é possível calcular desvio padrão")
    
    return np.std(X, axis=axis)


def coeficiente_variacao(X: np.ndarray, axis: int = 0) -> np.ndarray:
    """
    Calcula o coeficiente de variação (CV) em porcentagem.
    CV = (desvio padrão / |média|) * 100
    
    Args:
        X: Array numpy de entrada
        axis: Eixo ao longo do qual calcular
        
    Returns:
        Array numpy com os coeficientes de variação
        
    Raises:
        ValidacaoError: Se o array estiver vazio
    """
    if X.size == 0:
        raise ValidacaoError("Array vazio: não é possível calcular coeficiente de variação")
    
    media_val = media(X, axis=axis)
    desvio_val = desvio_padrao(X, axis=axis)
    
    # Evitar divisão por zero
    cv = np.where(np.abs(media_val) > 1e-10, 
                  (desvio_val / np.abs(media_val)) * 100, 
                  0.0)
    
    return cv


def percentil(X: np.ndarray, q: float, axis: int = 0) -> np.ndarray:
    """
    Calcula o percentil de um array numpy.
    
    Args:
        X: Array numpy de entrada
        q: Percentil a ser calculado (0-100)
        axis: Eixo ao longo do qual calcular
        
    Returns:
        Array numpy com os percentis calculados
        
    Raises:
        ValidacaoError: Se o array estiver vazio ou q inválido
    """
    if X.size == 0:
        raise ValidacaoError("Array vazio: não é possível calcular percentil")
    
    if not 0 <= q <= 100:
        raise ValidacaoError(f"Percentil inválido: {q}. Deve estar entre 0 e 100")
    
    return np.percentile(X, q, axis=axis)


def variancia(X: np.ndarray, axis: int = 0) -> np.ndarray:
    """
    Calcula a variância de um array numpy.
    
    Args:
        X: Array numpy de entrada
        axis: Eixo ao longo do qual calcular
        
    Returns:
        Array numpy com as variâncias calculadas
        
    Raises:
        ValidacaoError: Se o array estiver vazio
    """
    if X.size == 0:
        raise ValidacaoError("Array vazio: não é possível calcular variância")
    
    return np.var(X, axis=axis)


def amplitude(X: np.ndarray, axis: int = 0) -> np.ndarray:
    """
    Calcula a amplitude (max - min) de um array numpy.
    
    Args:
        X: Array numpy de entrada
        axis: Eixo ao longo do qual calcular
        
    Returns:
        Array numpy com as amplitudes calculadas
        
    Raises:
        ValidacaoError: Se o array estiver vazio
    """
    if X.size == 0:
        raise ValidacaoError("Array vazio: não é possível calcular amplitude")
    
    return np.max(X, axis=axis) - np.min(X, axis=axis)


def mediana(X: np.ndarray, axis: int = 0) -> np.ndarray:
    """
    Calcula a mediana de um array numpy.
    
    Args:
        X: Array numpy de entrada
        axis: Eixo ao longo do qual calcular
        
    Returns:
        Array numpy com as medianas calculadas
        
    Raises:
        ValidacaoError: Se o array estiver vazio
    """
    if X.size == 0:
        raise ValidacaoError("Array vazio: não é possível calcular mediana")
    
    return np.median(X, axis=axis)


def minimo(X: np.ndarray, axis: int = 0) -> np.ndarray:
    """
    Calcula o mínimo de um array numpy.
    
    Args:
        X: Array numpy de entrada
        axis: Eixo ao longo do qual calcular
        
    Returns:
        Array numpy com os mínimos calculados
        
    Raises:
        ValidacaoError: Se o array estiver vazio
    """
    if X.size == 0:
        raise ValidacaoError("Array vazio: não é possível calcular mínimo")
    
    return np.min(X, axis=axis)


def maximo(X: np.ndarray, axis: int = 0) -> np.ndarray:
    """
    Calcula o máximo de um array numpy.
    
    Args:
        X: Array numpy de entrada
        axis: Eixo ao longo do qual calcular
        
    Returns:
        Array numpy com os máximos calculados
        
    Raises:
        ValidacaoError: Se o array estiver vazio
    """
    if X.size == 0:
        raise ValidacaoError("Array vazio: não é possível calcular máximo")
    
    return np.max(X, axis=axis)