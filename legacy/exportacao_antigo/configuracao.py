"""
Precision VRT Solo — Configuração do Módulo de Exportação

Constantes, enums e parâmetros de configuração para exportação de resultados.
"""

from enum import Enum

__all__ = ["FormatoExportacao"]


class FormatoExportacao(Enum):
    """Formatos de exportação suportados."""
    GEOJSON = "geojson"
    SHAPEFILE = "shapefile"
    CSV = "csv"
    PNG = "png"
    TXT = "txt"
    KML = "kml"
    GEOPACKAGE = "geopackage"