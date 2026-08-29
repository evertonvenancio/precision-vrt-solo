"""
Precision VRT Solo — Validação do Módulo de Interpolação

Funções de validação e utilitários para interpolação espacial.
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd
import geopandas as gpd
import logging

__all__ = [
    "validar_dados_entrada",
    "detectar_coluna_coordenada",
    "selecionar_atributos_numericos",
]

logger = logging.getLogger(__name__)


def validar_dados_entrada(gdf: Union[pd.DataFrame, gpd.GeoDataFrame]) -> None:
    """
    Valida os dados de entrada para interpolação.
    
    Args:
        gdf: DataFrame ou GeoDataFrame com dados de solo
        
    Raises:
        ValueError: Se os dados não forem válidos
    """
    if gdf is None:
        raise ValueError("gdf nao pode ser None")

    if isinstance(gdf, gpd.GeoDataFrame):
        if gdf.empty:
            raise ValueError("GeoDataFrame esta vazio")
        if gdf.geometry.is_empty.all():
            raise ValueError("Todas as geometrias estao vazias")
    elif isinstance(gdf, pd.DataFrame):
        if gdf.empty:
            raise ValueError("DataFrame esta vazio")
    else:
        raise TypeError("gdf deve ser GeoDataFrame ou DataFrame")

    logger.info("Entrada validada: %d registros.", len(gdf))


def detectar_coluna_coordenada(
    df: pd.DataFrame,
    eixo: str,
    colunas_possiveis: set = None,
) -> Optional[str]:
    """
    Detecta automaticamente a coluna de coordenada no DataFrame.
    
    Args:
        df: DataFrame com os dados
        eixo: "x" ou "y" para qual coluna detectar
        colunas_possiveis: Conjunto de nomes possíveis para a coluna
        
    Returns:
        Nome da coluna detectada ou None
    """
    if colunas_possiveis is None:
        colunas_possiveis = {
            "longitude", "lon", "x", "coord_x", "lon_x", "longitud", "longit",
            "latitude", "lat", "y", "coord_y", "lat_y", "latitud", "latit",
            "altitude", "alt", "elev", "elevation", "z", "cota", "cotam",
        }
    
    colunas_lower = {c.lower(): c for c in df.columns}

    if eixo == "x":
        candidatos = ["longitude", "lon", "x", "coord_x", "lon_x"]
    else:
        candidatos = ["latitude", "lat", "y", "coord_y", "lat_y"]

    for cand in candidatos:
        if cand in colunas_lower:
            return colunas_lower[cand]

    # Busca parcial
    for cand in candidatos:
        for lower, original in colunas_lower.items():
            if cand in lower:
                return original

    raise ValueError(f"Nao foi possivel detectar coluna de coordenada {eixo}")


def selecionar_atributos_numericos(
    df: pd.DataFrame,
    colunas_excluir: set = None,
) -> List[str]:
    """
    Seleciona automaticamente os atributos numéricos para interpolação.
    
    Args:
        df: DataFrame com os dados
        colunas_excluir: Conjunto de colunas a excluir
        
    Returns:
        Lista de nomes de colunas numéricas selecionadas
    """
    if colunas_excluir is None:
        colunas_excluir = {
            "ponto_id", "id", "point_id", "sample_id", "amostra_id", "codigo", "code",
            "fid", "objectid", "gid", "seq", "numero", "num", "talhao_id", "talhao",
            "talhao", "field_id", "field", "plot_id", "plot", "parcela_id", "parcela",
            "bloco", "bloco_id", "fazenda_id", "fazenda", "safra", "crop_year", "year",
            "ano", "temporada", "season", "ciclo", "harvest", "camada", "layer", "depth",
            "profundidade", "horizonte", "stratum", "camada_solo", "data_coleta", "data",
            "date", "data_amostragem", "sampling_date", "collection_date", "dt_coleta",
            "dt_amostra", "data_aplicacao", "data_aplicacao", "application_date",
            "dt_aplicacao", "dt_aplicacao", "data_plantio", "planting_date", "sowing_date",
            "dt_plantio", "dt_semeadura", "data_colheita", "harvest_date", "dt_colheita",
            "cultura", "culture", "crop", "cultivo", "cultivar", "variedade", "variety",
            "especie", "especie", "observacao", "obs", "observacao", "observation",
            "note", "nota", "comentario", "comentario", "descricao", "descricao",
            "textura", "texture", "classe_textural", "textural_class", "textural",
            "geometry", "index",
        }

    # Detectar automaticamente: colunas numericas que nao sao coordenadas
    atributos_detectados = []
    for col in df.columns:
        col_lower = str(col).lower().strip()

        if col_lower in colunas_excluir or col_lower in {
            "longitude", "lon", "x", "coord_x", "lon_x", "longitud", "longit",
            "latitude", "lat", "y", "coord_y", "lat_y", "latitud", "latit",
            "altitude", "alt", "elev", "elevation", "z", "cota", "cotam",
        }:
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            # Verificar se tem pelo menos 4 valores nao-nulos
            n_validos = df[col].notna().sum()
            if n_validos >= 4:
                atributos_detectados.append(col)

    logger.info("Atributos detectados para interpolacao: %d", len(atributos_detectados))

    return atributos_detectados