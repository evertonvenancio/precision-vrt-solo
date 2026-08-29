"""
Precision VRT Solo — Caracterização do Módulo de Zoneamento

Geração do perfil estatístico de cada zona.
Implementação pura com numpy e geopandas, sem dependências externas.
"""

import logging
from typing import List

import geopandas as gpd
import numpy as np

from .contratos import PerfilZona
from ..utilitarios.utils import (
    media, desvio_padrao, coeficiente_variacao, 
    percentil, minimo, maximo, mediana
)

logger = logging.getLogger(__name__)

__all__ = [
    'caracterizar_zonas',
]


def caracterizar_zonas(gdf: gpd.GeoDataFrame, colunas_features: List[str]) -> List[PerfilZona]:
    """
    Agrupa o gdf por coluna 'zona' e calcula estatísticas para cada feature.
    Retorna lista de PerfilZona ordenada por zona_id.
    
    Args:
        gdf: GeoDataFrame com coluna 'zona' e colunas de features
        colunas_features: Lista de colunas de features para análise
        
    Returns:
        Lista de PerfilZona ordenada por zona_id
        
    Raises:
        ValueError: Se gdf não tiver coluna 'zona' ou colunas inválidas
    """
    if 'zona' not in gdf.columns:
        raise ValueError("GeoDataFrame deve conter coluna 'zona'")
    
    # Verificar colunas de features
    for coluna in colunas_features:
        if coluna not in gdf.columns:
            raise ValueError(f"Coluna de feature '{coluna}' não encontrada no GeoDataFrame")
    
    # Obter IDs únicos de zonas
    zonas_unicas = sorted(gdf['zona'].unique())
    logger.info(f"Caracterizando {len(zonas_unicas)} zonas")
    
    perfis = []
    
    for zona_id in zonas_unicas:
        # Filtrar dados da zona
        dados_zona = gdf[gdf['zona'] == zona_id]
        n_pontos = len(dados_zona)
        
        # Calcular estatísticas para cada feature
        estatisticas_feature = {}
        
        for feature in colunas_features:
            valores = dados_zona[feature].values
            
            # Calcular estatísticas
            estatisticas_feature[feature] = {
                'media': float(media(valores)),
                'mediana': float(mediana(valores)),
                'desvio_padrao': float(desvio_padrao(valores)),
                'cv': float(coeficiente_variacao(valores)),  # Já em %
                'minimo': float(minimo(valores)),
                'maximo': float(maximo(valores)),
                'percentil_25': float(percentil(valores, 25)),
                'percentil_75': float(percentil(valores, 75)),
            }
        
        # Calcular área em hectares
        try:
            # Converter para CRS adequado para cálculo de área
            # Usar UTM local ou sistema de coordenadas projetado
            if gdf.crs is None:
                logger.warning("GeoDataFrame sem CRS definido. Usando aproximação.")
                # Aproximação: assumir coordenadas em metros, dividir por 10000 para hectares
                area_m2 = dados_zona.geometry.area.sum()
                area_ha = area_m2 / 10000
            else:
                # Converter para CRS projetado para cálculo preciso
                gdf_proj = dados_zona.to_crs('EPSG:32633')  # UTM Zone 33N (pode ajustar conforme localização)
                area_m2 = gdf_proj.geometry.area.sum()
                area_ha = area_m2 / 10000
        except Exception as e:
            logger.warning(f"Erro ao calcular área: {e}. Usando 0.0")
            area_ha = 0.0
        
        # Criar perfil da zona
        perfil = PerfilZona(
            zona_id=int(zona_id),
            area_ha=float(area_ha),
            n_pontos=int(n_pontos),
            media={feature: stats['media'] for feature, stats in estatisticas_feature.items()},
            mediana={feature: stats['mediana'] for feature, stats in estatisticas_feature.items()},
            desvio_padrao={feature: stats['desvio_padrao'] for feature, stats in estatisticas_feature.items()},
            cv={feature: stats['cv'] for feature, stats in estatisticas_feature.items()},
            minimo={feature: stats['minimo'] for feature, stats in estatisticas_feature.items()},
            maximo={feature: stats['maximo'] for feature, stats in estatisticas_feature.items()},
            percentil_25={feature: stats['percentil_25'] for feature, stats in estatisticas_feature.items()},
            percentil_75={feature: stats['percentil_75'] for feature, stats in estatisticas_feature.items()},
        )
        
        perfis.append(perfil)
        
        logger.debug(f"Zona {zona_id}: {n_pontos} pontos, área {area_ha:.2f} ha")
    
    logger.info(f"Caracterização concluída para {len(perfis)} zonas")
    return perfis