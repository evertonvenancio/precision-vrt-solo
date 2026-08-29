"""
Precision VRT Solo — Exportação de Dados em Shapefile

Funções para exportação de dados em formato Shapefile.
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import geopandas as gpd

from ..configuracao import FormatoExportacao

logger = logging.getLogger(__name__)


def exportar_shapefile(gdf: gpd.GeoDataFrame, nome_arquivo: str, subpasta: Optional[str] = None, 
                      output_dir: str = "data/output", **kwargs: Any) -> str:
    """Exporta GeoDataFrame para Shapefile."""
    pasta = Path(output_dir)
    if subpasta:
        pasta = pasta / subpasta
        pasta.mkdir(parents=True, exist_ok=True)
    
    caminho = pasta / f"{nome_arquivo}.shp"
    
    try:
        gdf.to_file(caminho, driver="ESRI Shapefile")
        logger.info("Shapefile exportado: %s", caminho)
        return str(caminho)
    except Exception as e:
        logger.error("Erro ao exportar Shapefile: %s", e)
        raise