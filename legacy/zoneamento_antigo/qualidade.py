"""
Precision VRT Solo — Métricas de Qualidade do Zoneamento

Implementação de métricas de qualidade para clustering agrícola.
"""
import numpy as np
from typing import Dict
import geopandas as gpd


def calcular_silhouette(X: np.ndarray, labels: np.ndarray) -> float:
    """Calcula coeficiente de Silhouette (requiere sklearn)."""
    try:
        from sklearn.metrics import silhouette_score
        if len(np.unique(labels)) < 2:
            return 0.0
        return float(silhouette_score(X, labels))
    except ImportError:
        return 0.0


def calcular_davies_bouldin(X: np.ndarray, labels: np.ndarray) -> float:
    """Calcula índice Davies-Bouldin (requiere sklearn)."""
    try:
        from sklearn.metrics import davies_bouldin_score
        if len(np.unique(labels)) < 2:
            return 0.0
        return float(davies_bouldin_score(X, labels))
    except ImportError:
        return 0.0


def calcular_calinski(X: np.ndarray, labels: np.ndarray) -> float:
    """Calcula índice Calinski-Harabasz (requiere sklearn)."""
    try:
        from sklearn.metrics import calinski_harabasz_score
        if len(np.unique(labels)) < 2:
            return 0.0
        return float(calinski_harabasz_score(X, labels))
    except ImportError:
        return 0.0


def calcular_inercia(X: np.ndarray, labels: np.ndarray) -> float:
    """Calcula inércia total dos clusters."""
    from sklearn.cluster import KMeans
    try:
        # Calcular centroides
        unique_labels = np.unique(labels)
        if len(unique_labels) < 2:
            return 0.0
            
        # Para cada cluster, calcular inércia
        total_inercia = 0.0
        for label in unique_labels:
            cluster_points = X[labels == label]
            if len(cluster_points) > 0:
                centroid = np.mean(cluster_points, axis=0)
                distances = np.linalg.norm(cluster_points - centroid, axis=1)
                total_inercia += np.sum(distances**2)
                
        return float(total_inercia)
    except Exception:
        return 0.0


def calcular_homogeneidade_media(gdf: gpd.GeoDataFrame, colunas: list[str]) -> float:
    """Calcula homogeneidade média intra-zona."""
    if 'zona' not in gdf.columns:
        return 0.0
        
    homogeneidades = []
    zonas_unicas = gdf['zona'].unique()
    
    for coluna in colunas:
        if coluna in gdf.columns:
            # Calcular CV (coeficiente de variação) para cada zona
            zone_cv = []
            for zona in zonas_unicas:
                dados_zona = gdf[gdf['zona'] == zona][coluna].values
                if len(dados_zona) > 1:
                    media_val = np.mean(dados_zona)
                    std_val = np.std(dados_zona)
                    if media_val > 0:
                        cv = (std_val / media_val) * 100
                        zone_cv.append(cv)
            
            if zone_cv:
                homogeneidades.append(100 - np.mean(zone_cv))  # Inverter CV para homogeneidade
    
    if homogeneidades:
        return float(np.mean(homogeneidades))
    else:
        return 0.0