"""
Funções geoespaciais utilitárias do core.
"""
import json
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Union

import numpy as np
import pandas as pd
import geopandas as gpd

# Diretórios de dados (importados de main.py via injeção ou definidos aqui)
# Nota: UPLOAD_DIR é injetado em _salvar_upload para evitar dependência circular


def _parse_upload(caminho: Union[str, Path]) -> Dict[str, Any]:
    """Parser genérico de arquivos geoespaciais (GeoJSON, SHP, CSV, XLSX)."""
    import app.services.geo_parser_service as geo_parser_service
    return geo_parser_service.parse_upload(str(caminho))


def _gdf_para_dataframe(gdf: Optional[gpd.GeoDataFrame]) -> pd.DataFrame:
    """Converte GeoDataFrame para DataFrame plano, extraindo coords."""
    if gdf is None or gdf.empty:
        return pd.DataFrame()
    df = pd.DataFrame(gdf.drop(columns='geometry', errors='ignore'))
    try:
        df['longitude'] = gdf.geometry.x.values
        df['latitude'] = gdf.geometry.y.values
    except Exception:
        try:
            centroids = gdf.geometry.centroid
            df['longitude'] = centroids.x.values
            df['latitude'] = centroids.y.values
        except Exception:
            pass
    return df


def _calcular_area_ha(gdf_poligono: Optional[gpd.GeoDataFrame]) -> float:
    """Calcula área em hectares a partir de um GeoDataFrame poligonal."""
    if gdf_poligono is None or gdf_poligono.empty:
        return 0.0
    try:
        # Tentar usar UTM apropriada (Sul do Brasil ~ UTM 23S)
        gdf_utm = gdf_poligono.to_crs(epsg=32723)
        area_m2 = gdf_utm.geometry.area.sum()
        return round(area_m2 / 10000.0, 2)
    except Exception:
        # Fallback: calculo aproximado em graus
        try:
            area_graus = gdf_poligono.geometry.area.sum()
            # 1 grau ~ 111km, 1 grau2 ~ 12321 km2 ~ 1.2321e9 m2
            area_m2 = area_graus * 1.2321e9
            return round(area_m2 / 10000.0, 2)
        except Exception:
            return 0.0


def _raster_para_geojson(raster_zonas, grid_x, grid_y, gdf_poligono=None):
    """Converte raster de zonas em GeoJSON de poligonos vetorizados."""
    try:
        from rasterio import features
        from shapely.geometry import shape, mapping

        # Criar transform afim
        xmin, xmax = grid_x.min(), grid_x.max()
        ymin, ymax = grid_y.min(), grid_y.max()
        ny, nx = raster_zonas.shape
        dx = (xmax - xmin) / (nx - 1) if nx > 1 else 1
        dy = (ymax - ymin) / (ny - 1) if ny > 1 else 1
        transform = [dx, 0, xmin, 0, -dy, ymax]

        features_list = []
        for geom, val in features.shapes(raster_zonas.astype(np.int32), mask=raster_zonas >= 0, transform=transform):
            features_list.append({
                "type": "Feature",
                "geometry": mapping(shape(geom)),
                "properties": {"zona_id": int(val)}
            })

        geojson_zonas = {
            "type": "FeatureCollection",
            "features": features_list
        }
        return geojson_zonas
    except Exception as e:
        logging.warning(f"Nao foi possivel vetorizar raster: {e}")
        return {"type": "FeatureCollection", "features": []}


def _gdf_para_geojson(gdf: Optional[gpd.GeoDataFrame]) -> Dict[str, Any]:
    """Converte GeoDataFrame para GeoJSON dict. Retorna FeatureCollection vazia se None."""
    if gdf is None or gdf.empty:
        return {"type": "FeatureCollection", "features": []}
    try:
        return json.loads(gdf.to_json())
    except Exception:
        return {"type": "FeatureCollection", "features": []}