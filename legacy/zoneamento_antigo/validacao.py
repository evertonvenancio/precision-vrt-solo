"""
Precision VRT Solo — Validação do Módulo de Zoneamento

Funções puras de validação de dados e configurações.
"""

import logging
from typing import List

import geopandas as gpd
import numpy as np

from .configuracao import MAX_ZONAS, MIN_ZONAS
from .contratos import ConfigZoneamento
from .exceptions import DadosInsuficientesError, ValidacaoError


def validar_geodataframe(gdf: gpd.GeoDataFrame) -> None:
    """
    Valida um GeoDataFrame para uso no zoneamento.
    
    Args:
        gdf: GeoDataFrame a ser validado
        
    Raises:
        ValidacaoError: Se o GeoDataFrame não for válido
    """
    if not isinstance(gdf, gpd.GeoDataFrame):
        raise ValidacaoError("O dado de entrada deve ser um GeoDataFrame")
    
    if gdf.empty:
        raise ValidacaoError("O GeoDataFrame não pode estar vazio")
    
    if gdf.geometry.isnull().any():
        raise ValidacaoError("O GeoDataFrame não pode geometrias nulas")
    
    if gdf.geometry.empty:
        raise ValidacaoError("O GeoDataFrame não pode geometrias vazias")
    
    if gdf.crs is None:
        raise ValidacaoError("O GeoDataFrame deve ter um CRS definido")


def validar_configuracao(config: ConfigZoneamento, gdf: gpd.GeoDataFrame) -> None:
    """
    Valida uma configuração de zoneamento em relação aos dados.
    
    Args:
        config: Configuração a ser validada
        gdf: GeoDataFrame para validação
        
    Raises:
        ValidacaoError: Se a configuração for inválida
        DadosInsuficientesError: Se houver insuficiência de dados
    """
    # Validar número de zonas
    if not MIN_ZONAS <= config.n_zonas <= MAX_ZONAS:
        raise ValidacaoError(f"n_zonas deve estar entre {MIN_ZONAS} e {MAX_ZONAS}")
    
    # Validar suficiência de dados
    if config.n_zonas >= len(gdf):
        raise DadosInsuficientesError(
            f"Não há dados suficientes para {config.n_zonas} zonas "
            f"(apenas {len(gdf)} amostras disponíveis)"
        )
    
    # Validar colunas features
    if config.colunas_features is not None:
        colunas_numericas = gdf.select_dtypes(include=[np.number]).columns.tolist()
        colunas_numericas = [col for col in colunas_numericas if col != 'geometry']
        
        for coluna in config.colunas_features:
            if coluna not in gdf.columns:
                raise ValidacaoError(f"Coluna '{coluna}' não existe no GeoDataFrame")
            
            if coluna not in colunas_numericas and coluna != 'geometry':
                raise ValidacaoError(f"Coluna '{coluna}' não é numérica")


def extrair_features(gdf: gpd.GeoDataFrame, config: ConfigZoneamento) -> np.ndarray:
    """
    Extrai features do GeoDataFrame para uso em algoritmos de clustering.
    
    Args:
        gdf: GeoDataFrame de entrada
        config: Configuração de zoneamento
        
    Returns:
        Matriz numpy 2D com as features selecionadas
        
    Raises:
        ValidacaoError: Se não houver features suficientes
    """
    # Selecionar colunas numéricas
    colunas_numericas = gdf.select_dtypes(include=[np.number]).columns.tolist()
    colunas_numericas = [col for col in colunas_numericas if col != 'geometry']
    
    if config.colunas_features is not None:
        features_selecionadas = config.colunas_features
    else:
        features_selecionadas = colunas_numericas
    
    # Verificar se há features suficientes
    if len(features_selecionadas) == 0:
        raise ValidacaoError("Não há colunas numéricas suficientes para extrair features")
    
    # Extrair matriz de features
    X = gdf[features_selecionadas].values
    
    # Verificar se há valores válidos
    if np.isnan(X).all():
        raise ValidacaoError("Todas as features são NaN")
    
    return X


def verificar_nan_inf(X: np.ndarray) -> None:
    """
    Verifica presença de NaN ou Infinitos na matriz de features.
    
    Args:
        X: Matriz numpy de features
        
    Raises:
        ValidacaoError: Se houver NaN ou Infinitos
    """
    if config.remover_outliers:
        logging.info("Flag remover_outliers=True, mas tratamento real virá na Z2")
        return
    
    if np.isnan(X).any():
        raise ValidacaoError("Matriz de features contém valores NaN")
    
    if np.isinf(X).any():
        raise ValidacaoError("Matriz de features contém valores infinitos")