"""
Precision VRT Solo — Configuração do Módulo de Interpolação

Constantes, enums e parâmetros de configuração para interpolação espacial.
"""

from enum import Enum

__all__ = [
    "MetodoInterpolacao",
    "RESOLUCAO_PADRAO_M",
    "FUNCAO_RBF_PADRAO",
    "SUAVIZACAO_PADRAO",
    "RANDOM_STATE_PADRAO",
    "COLUNAS_COORDENADAS",
    "COLUNAS_EXCLUIR",
]


class MetodoInterpolacao(Enum):
    """Métodos de interpolação suportados."""
    RBF = "rbf"
    IDW = "idw"
    NEAREST = "nearest"
    LINEAR = "linear"
    CUBIC = "cubic"


RESOLUCAO_PADRAO_M = 10
FUNCAO_RBF_PADRAO = "thin_plate_spline"
SUAVIZACAO_PADRAO = 0.0
RANDOM_STATE_PADRAO = 42

COLUNAS_COORDENADAS = {
    "longitude", "lon", "x", "coord_x", "lon_x", "longitud", "longit",
    "latitude", "lat", "y", "coord_y", "lat_y", "latitud", "latit",
    "altitude", "alt", "elev", "elevation", "z", "cota", "cotam",
}

COLUNAS_EXCLUIR = {
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