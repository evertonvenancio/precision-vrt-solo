"""
Precision VRT Solo — Métrica Homogeneidade

Cálculo de homogeneidade intra-zona: para cada zona, retorna o CV médio
entre todas as features (quanto menor, mais homogênea).
"""

import numpy as np
from typing import Dict


def calcular(gdf: np.ndarray, colunas_features: list[str]) -> dict[int, float]:
    """
    Calcula homogeneidade intra-zona: para cada zona, retorna o CV médio 
    entre todas as features (quanto menor, mais homogênea).
    
    Args:
        gdf: GeoDataFrame numpy com dados e coluna 'zona'
        colunas_features: Lista de colunas de features analisadas
        
    Returns:
        Dicionário com chave = zona_id, valor = CV médio (em %)
        
    Raises:
        ValueError: Se gdf não tiver coluna 'zona' ou colunas_features inválidas
    """
    if 'zona' not in gdf.dtype.names:
        raise ValueError("GeoDataFrame deve conter coluna 'zona'")
    
    # Verificar colunas de features
    for coluna in colunas_features:
        if coluna not in gdf.dtype.names:
            raise ValueError(f"Coluna '{coluna}' não encontrada no GeoDataFrame")
    
    # Obter IDs únicos de zonas
    zonas_unicas = np.unique(gdf['zona'])
    
    homogeneidades = {}
    
    for zona_id in zonas_unicas:
        # Filtrar dados da zona
        dados_zona = gdf[gdf['zona'] == zona_id]
        
        # Calcular CV para cada feature
        cvs_features = []
        
        for feature in colunas_features:
            valores = dados_zona[feature]
            
            if len(valores) > 1:
                # Calcular coeficiente de variação
                media_val = np.mean(valores)
                desvio_val = np.std(valores)
                
                # Evitar divisão por zero
                cv = (desvio_val / abs(media_val)) * 100 if abs(media_val) > 1e-10 else 0.0
                cvs_features.append(cv)
            else:
                # Se apenas 1 ponto, CV = 0
                cvs_features.append(0.0)
        
        # Calcular CV médio da zona
        cv_medio = np.mean(cvs_features) if cvs_features else 0.0
        homogeneidades[int(zona_id)] = float(cv_medio)
    
    return homogeneidades


def calcular_homogeneidade_media(gdf: np.ndarray, colunas_features: list[str]) -> float:
    """
    Calcula homogeneidade média de todas as zonas.
    Valor médio dos CVs médios de cada zona.
    
    Args:
        gdf: GeoDataFrame numpy com dados e coluna 'zona'
        colunas_features: Lista de colunas de features analisadas
        
    Returns:
        Homogeneidade média (CV médio em %)
    """
    homogeneidades_por_zona = calcular(gdf, colunas_features)
    return float(np.mean(list(homogeneidades_por_zona.values()))) if homogeneidades_por_zona else 0.0