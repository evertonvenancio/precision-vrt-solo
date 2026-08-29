"""
Precision VRT Solo — Cálculos Estatísticos

Funções para cálculo de estatísticas sobre resultados interpolados.
"""

import numpy as np


def calcular_estatisticas(
    z_valid: np.ndarray,
    pred: np.ndarray,
) -> dict:
    """
    Calcula estatísticas do atributo interpolado.
    
    Args:
        z_valid: Array de valores observados (filtrados)
        pred: Array de valores interpolados
        
    Returns:
        Dict com as estatísticas calculadas
    """
    media = float(np.mean(z_valid))
    desvio = float(np.std(z_valid))
    
    pred_flat = pred.ravel()
    pred_validos = pred_flat[~np.isnan(pred_flat)]
    
    n_total = pred_flat.size
    n_validos = len(pred_validos)
    pct_cobertura = (n_validos / n_total * 100) if n_total > 0 else 0.0
    
    return {
        "minimo": float(np.min(z_valid)),
        "maximo": float(np.max(z_valid)),
        "media": media,
        "mediana": float(np.median(z_valid)),
        "desvio": desvio,
        "variancia": float(np.var(z_valid)),
        "q1": float(np.percentile(z_valid, 25)),
        "q3": float(np.percentile(z_valid, 75)),
        "iqr": float(np.percentile(z_valid, 75) - np.percentile(z_valid, 25)),
        "coef_variacao": round((desvio / media * 100), 2) if media != 0 else 0.0,
        "n_pontos_validos": len(z_valid),
        "n_pontos_interpolados": n_validos,
        "pct_cobertura": round(pct_cobertura, 2),
    }