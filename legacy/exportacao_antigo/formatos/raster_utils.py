"""
Precision VRT Solo — Ferramentas para Exportação de Raster

Funções para conversão de raster para poligonos.
"""
import logging
import numpy as np
from pathlib import Path
from typing import Any, Dict, List, Optional

import geopandas as gpd
from rasterio.features import shapes
from rasterio.transform import from_bounds
from shapely.geometry import shape

logger = logging.getLogger(__name__)


def raster_para_zonas_poligonos(raster_zonas: np.ndarray, grid_x: np.ndarray, 
                                grid_y: np.ndarray, 
                                atributos_zonas: Optional[Dict[str, Dict[str, Any]]] = None) -> gpd.GeoDataFrame:
    """Converte raster de zonas em poligonos vetoriais (GeoDataFrame)."""
    grid_x = np.asarray(grid_x).flatten()
    grid_y = np.asarray(grid_y).flatten()

    ny, nx = raster_zonas.shape

    x_min = float(grid_x.min())
    x_max = float(grid_x.max())
    y_min = float(grid_y.min())
    y_max = float(grid_y.max())

    dx = (x_max - x_min) / (nx - 1) if nx > 1 else 1.0
    dy = (y_max - y_min) / (ny - 1) if ny > 1 else 1.0

    x_min_corner = x_min - dx / 2.0
    x_max_corner = x_max + dx / 2.0
    y_min_corner = y_min - dy / 2.0
    y_max_corner = y_max + dy / 2.0

    transform = from_bounds(
        x_min_corner, y_min_corner,
        x_max_corner, y_max_corner,
        nx, ny,
    )

    mask = raster_zonas >= 0

    results = (
        {"properties": {"zona": int(v)}, "geometry": s}
        for i, (s, v) in enumerate(
            shapes(
                raster_zonas.astype(np.int32),
                mask=mask,
                transform=transform,
            )
        )
    )

    geometrias: List[Any] = []
    zonas: List[int] = []

    for r in results:
        geom = shape(r["geometry"])
        geometrias.append(geom)
        zonas.append(r["properties"]["zona"])

    gdf = gpd.GeoDataFrame({
        "zona": zonas,
        "geometry": geometrias,
    })

    gdf.set_crs(epsg=4326, inplace=True)
    gdf = gdf.dissolve(by="zona").reset_index()
    gdf["geometry"] = gdf["geometry"].buffer(0)
    gdf["geometry"] = gdf["geometry"].simplify(
        tolerance=0.00001,
        preserve_topology=True,
    )

    if atributos_zonas:
        for zona_id in gdf["zona"]:
            if zona_id in atributos_zonas:
                for attr, valor in atributos_zonas[zona_id].items():
                    gdf.loc[gdf["zona"] == zona_id, attr] = valor

    return gdf