"""
Precision VRT Solo — Validação do Módulo de Exportação

Funções de validação e utilitários para exportação de resultados.
"""

from typing import Any, Dict, List, Optional
import geopandas as gpd

__all__ = ["validar_dados_exportacao"]


def validar_dados_exportacao(gdf: gpd.GeoDataFrame) -> None:
    """
    Valida dados antes da exportacao.
    
    Args:
        gdf: GeoDataFrame com os dados a serem validados
        
    Raises:
        ValueError: Se os dados não forem válidos para exportação
    """
    if gdf is None or gdf.empty:
        raise ValueError("GeoDataFrame vazio ou nulo")

    if "geometry" not in gdf.columns:
        raise ValueError("GeoDataFrame deve conter coluna 'geometry'")

    if gdf.geometry.is_empty.all():
        raise ValueError("Todas as geometrias estao vazias")

    import logging
    logger = logging.getLogger(__name__)
    logger.info("Dados validados: %d registros, %d colunas.", len(gdf), len(gdf.columns))