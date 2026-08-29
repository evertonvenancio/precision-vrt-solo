"""
Precision VRT Solo — Normalização de Dados para Interpolação

Funções para normalização e padronização de dados de interpolação.
"""
import numpy as np
import pandas as pd
import geopandas as gpd


class NormalizadorDados:
    """Normalizador de dados para interpolação espacial."""
    
    @staticmethod
    def normalizar_coordenadas(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        """Normaliza coordenadas para [0, 1] para melhor performance numérica."""
        if df.empty:
            return np.array([]), np.array([])
        
        # Extraindo coordenadas (assume que estão na forma adequada)
        x_coords = df['longitude'].values if 'longitude' in df.columns else df['x'].values
        y_coords = df['latitude'].values if 'latitude' in df.columns else df['y'].values
        
        # Normalizar para [0, 1]
        x_min, x_max = x_coords.min(), x_coords.max()
        y_min, y_max = y_coords.min(), y_coords.max()
        
        # Evitar divisão por zero
        if x_max == x_min:
            x_coords = np.zeros_like(x_coords)
        else:
            x_coords = (x_coords - x_min) / (x_max - x_min)
            
        if y_max == y_min:
            y_coords = np.zeros_like(y_coords)
        else:
            y_coords = (y_coords - y_min) / (y_max - y_min)
            
        return x_coords, y_coords
    
    @staticmethod
    def padronizar_atributos(df: pd.DataFrame, colunas_numericas: list[str]) -> pd.DataFrame:
        """Padroniza atributos numéricos (z-score)."""
        df_normalizado = df.copy()
        
        for col in colunas_numericas:
            if col in df_normalizado.columns:
                mean = df_normalizado[col].mean()
                std = df_normalizado[col].std()
                if std > 0:
                    df_normalizado[col] = (df_normalizado[col] - mean) / std
                    
        return df_normalizado