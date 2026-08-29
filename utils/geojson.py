"""
Utilitarios para serializacao segura de GeoDataFrames para GeoJSON.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path

import numpy as np
import geopandas as gpd
from shapely.geometry import (
    shape, mapping, Point, MultiPoint, Polygon, MultiPolygon,
    LineString, MultiLineString, GeometryCollection
)
from shapely.ops import unary_union
from shapely import wkt

logger = logging.getLogger(__name__)


# =============================================================================
# SERIALIZACAO SEGURA DE VALORES
# =============================================================================

def limpar_valor(valor: Any) -> Any:
    """Converte valores numpy/NaN para tipos Python nativos serializaveis."""
    if valor is None or (isinstance(valor, float) and np.isnan(valor)):
        return None
    if isinstance(valor, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(valor)
    if isinstance(valor, (np.floating, np.float64, np.float32, np.float16)):
        return float(valor)
    if isinstance(valor, np.ndarray):
        return valor.tolist()
    if isinstance(valor, (np.bool_)):
        return bool(valor)
    if isinstance(valor, (list, tuple)):
        return [limpar_valor(v) for v in valor]
    if isinstance(valor, dict):
        return {k: limpar_valor(v) for k, v in valor.items()}
    return valor


def limpar_propriedades(props: Dict[str, Any]) -> Dict[str, Any]:
    """Limpa todas as propriedades de um dicionario para serializacao JSON."""
    if not isinstance(props, dict):
        return {}
    return {str(k): limpar_valor(v) for k, v in props.items()}


# =============================================================================
# CONVERSAO GDF -> GEOJSON
# =============================================================================

def gdf_para_geojson_dict(gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
    """Converte GeoDataFrame para dict GeoJSON FeatureCollection limpo."""
    if gdf is None or gdf.empty:
        return {"type": "FeatureCollection", "features": []}

    gdf = gdf.copy()

    if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs("EPSG:4326")
    elif gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326", allow_override=True)

    invalidas = ~gdf.geometry.is_valid
    if invalidas.any():
        logger.warning("%d geometrias invalidas encontradas. Corrigindo com buffer(0).", invalidas.sum())
        gdf.loc[invalidas, "geometry"] = gdf.loc[invalidas, "geometry"].buffer(0)

    gdf = gdf[~gdf.geometry.is_empty].copy()

    if gdf.empty:
        return {"type": "FeatureCollection", "features": []}

    geojson = gdf.__geo_interface__

    for feature in geojson.get("features", []):
        props = feature.get("properties", {})
        feature["properties"] = limpar_propriedades(props)

        geom = feature.get("geometry")
        if geom and "coordinates" in geom:
            geom["coordinates"] = limpar_valor(geom["coordinates"])

    return geojson


def gdf_para_geojson_str(gdf: gpd.GeoDataFrame, indent: Optional[int] = None) -> str:
    """Converte GeoDataFrame para string GeoJSON."""
    geojson_dict = gdf_para_geojson_dict(gdf)
    return json.dumps(geojson_dict, ensure_ascii=False, indent=indent)


def gdf_para_geojson_arquivo(gdf: gpd.GeoDataFrame, caminho: Union[str, Path], indent: Optional[int] = 2) -> str:
    """Converte GeoDataFrame para arquivo GeoJSON."""
    caminho = Path(caminho)
    geojson_dict = gdf_para_geojson_dict(gdf)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(geojson_dict, f, ensure_ascii=False, indent=indent)
    return str(caminho)


# =============================================================================
# CONVERSAO GEOJSON -> GDF
# =============================================================================

def geojson_dict_para_gdf(geojson: Dict[str, Any], crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
    """Converte dict GeoJSON para GeoDataFrame."""
    if not validar_geojson(geojson):
        raise ValueError("GeoJSON invalido ou malformado")

    features = geojson.get("features", [])
    if not features:
        return gpd.GeoDataFrame(geometry=[], crs=crs)

    gdf = gpd.GeoDataFrame.from_features(features, crs=crs)

    if gdf.crs is None:
        gdf = gdf.set_crs(crs, allow_override=True)
    elif gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs("EPSG:4326")

    return gdf


def geojson_str_para_gdf(geojson_str: str, crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
    """Converte string GeoJSON para GeoDataFrame."""
    try:
        geojson = json.loads(geojson_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"String GeoJSON invalida: {e}")
    return geojson_dict_para_gdf(geojson, crs=crs)


def geojson_arquivo_para_gdf(caminho: Union[str, Path], crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
    """Converte arquivo GeoJSON para GeoDataFrame."""
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {caminho}")

    with open(caminho, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    return geojson_dict_para_gdf(geojson, crs=crs)


# =============================================================================
# VALIDACAO DE GEOJSON
# =============================================================================

def validar_geojson(geojson: Any) -> bool:
    """Valida estrutura basica de um GeoJSON FeatureCollection."""
    if not isinstance(geojson, dict):
        return False
    if geojson.get("type") != "FeatureCollection":
        return False
    if "features" not in geojson:
        return False
    if not isinstance(geojson["features"], list):
        return False
    return True


def validar_feature(feature: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Valida uma Feature individual do GeoJSON."""
    if not isinstance(feature, dict):
        return False, "Feature deve ser um dict"

    if feature.get("type") != "Feature":
        return False, "Tipo deve ser 'Feature'"

    if "geometry" not in feature:
        return False, "Feature deve conter 'geometry'"

    geom = feature.get("geometry")
    if geom is not None and not isinstance(geom, dict):
        return False, "Geometry deve ser um dict ou null"

    if geom is not None and "type" not in geom:
        return False, "Geometry deve conter 'type'"

    if geom is not None and "coordinates" not in geom:
        return False, "Geometry deve conter 'coordinates'"

    return True, None


def validar_geometria(geom: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Valida uma geometria GeoJSON individual."""
    if not isinstance(geom, dict):
        return False, "Geometria deve ser um dict"

    tipo = geom.get("type")
    if tipo is None:
        return False, "Geometria deve ter 'type'"

    coords = geom.get("coordinates")
    if coords is None and tipo != "GeometryCollection":
        return False, "Geometria deve ter 'coordinates'"

    tipos_validos = {
        "Point", "MultiPoint", "LineString", "MultiLineString",
        "Polygon", "MultiPolygon", "GeometryCollection"
    }

    if tipo not in tipos_validos:
        return False, f"Tipo de geometria invalido: {tipo}"

    return True, None


def validar_geojson_completo(geojson: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validacao completa de um GeoJSON FeatureCollection com detalhes."""
    erros: List[str] = []

    if not isinstance(geojson, dict):
        erros.append("GeoJSON deve ser um dict")
        return False, erros

    if geojson.get("type") != "FeatureCollection":
        erros.append("Tipo deve ser 'FeatureCollection'")

    if "features" not in geojson:
        erros.append("Deve conter 'features'")
        return False, erros

    features = geojson["features"]
    if not isinstance(features, list):
        erros.append("'features' deve ser uma lista")
        return False, erros

    for i, feature in enumerate(features):
        valido, msg = validar_feature(feature)
        if not valido:
            erros.append(f"Feature[{i}]: {msg}")
            continue

        geom = feature.get("geometry")
        if geom is not None:
            valido_geom, msg_geom = validar_geometria(geom)
            if not valido_geom:
                erros.append(f"Feature[{i}] geometry: {msg_geom}")

    return len(erros) == 0, erros


# =============================================================================
# CORRECAO DE GEOMETRIAS
# =============================================================================

def corrigir_geometria(geom_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Tenta corrigir uma geometria GeoJSON invalida."""
    try:
        geom = shape(geom_dict)
        if geom.is_valid:
            return geom_dict

        corrigida = geom.buffer(0)
        if corrigida.is_valid and not corrigida.is_empty:
            return mapping(corrigida)

        return None
    except Exception as e:
        logger.warning("Nao foi possivel corrigir geometria: %s", e)
        return None


def corrigir_geometrias_gdf(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Corrige todas as geometrias invalidas de um GeoDataFrame."""
    if gdf is None or gdf.empty:
        return gdf

    gdf = gdf.copy()
    invalidas = ~gdf.geometry.is_valid

    if invalidas.any():
        logger.info("Corrigindo %d geometrias invalidas.", invalidas.sum())
        gdf.loc[invalidas, "geometry"] = gdf.loc[invalidas, "geometry"].buffer(0)

    gdf = gdf[~gdf.geometry.is_empty].copy()
    return gdf


def simplificar_geometria(geom_dict: Dict[str, Any], tolerancia: float = 0.0001) -> Dict[str, Any]:
    """Simplifica uma geometria GeoJSON preservando a topologia."""
    try:
        geom = shape(geom_dict)
        simplificada = geom.simplify(tolerancia, preserve_topology=True)
        if simplificada.is_valid and not simplificada.is_empty:
            return mapping(simplificada)
        return geom_dict
    except Exception as e:
        logger.warning("Erro ao simplificar geometria: %s", e)
        return geom_dict


def simplificar_gdf(gdf: gpd.GeoDataFrame, tolerancia: float = 0.0001) -> gpd.GeoDataFrame:
    """Simplifica todas as geometrias de um GeoDataFrame."""
    if gdf is None or gdf.empty:
        return gdf

    gdf = gdf.copy()
    gdf["geometry"] = gdf.geometry.simplify(tolerancia, preserve_topology=True)
    gdf = gdf[~gdf.geometry.is_empty].copy()
    return gdf


# =============================================================================
# PADRONIZACAO DE CRS
# =============================================================================

def padronizar_crs(gdf: gpd.GeoDataFrame, crs_destino: str = "EPSG:4326") -> gpd.GeoDataFrame:
    """Padroniza o CRS de um GeoDataFrame para o destino especificado."""
    if gdf is None or gdf.empty:
        return gdf

    gdf = gdf.copy()

    if gdf.crs is None:
        gdf = gdf.set_crs(crs_destino, allow_override=True)
    elif gdf.crs.to_string() != crs_destino:
        gdf = gdf.to_crs(crs_destino)

    return gdf


def garantir_crs_4326(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Garante que o GeoDataFrame esteja em EPSG:4326."""
    return padronizar_crs(gdf, crs_destino="EPSG:4326")


# =============================================================================
# MANIPULACAO DE FEATURES
# =============================================================================

def criar_feature(geometry: Any, properties: Optional[Dict[str, Any]] = None, id: Optional[str] = None) -> Dict[str, Any]:
    """Cria uma Feature GeoJSON padronizada."""
    feature: Dict[str, Any] = {
        "type": "Feature",
        "geometry": None,
        "properties": limpar_propriedades(properties or {}),
    }

    if id is not None:
        feature["id"] = str(id)

    if geometry is not None:
        if isinstance(geometry, dict):
            feature["geometry"] = geometry
        else:
            try:
                feature["geometry"] = mapping(geometry)
            except Exception as e:
                logger.error("Erro ao converter geometria: %s", e)
                feature["geometry"] = None

    return feature


def criar_feature_collection(features: List[Dict[str, Any]], crs: Optional[str] = None) -> Dict[str, Any]:
    """Cria um FeatureCollection GeoJSON padronizado."""
    fc: Dict[str, Any] = {
        "type": "FeatureCollection",
        "features": features,
    }

    if crs:
        fc["crs"] = {
            "type": "name",
            "properties": {"name": crs},
        }

    return fc


def extrair_propriedades(feature: Dict[str, Any]) -> Dict[str, Any]:
    """Extrai e limpa as propriedades de uma Feature."""
    if not isinstance(feature, dict):
        return {}
    props = feature.get("properties", {})
    return limpar_propriedades(props)


def extrair_geometria(feature: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extrai a geometria de uma Feature."""
    if not isinstance(feature, dict):
        return None
    return feature.get("geometry")


def extrair_tipo_geometria(feature: Dict[str, Any]) -> Optional[str]:
    """Extrai o tipo de geometria de uma Feature."""
    geom = extrair_geometria(feature)
    if geom is None:
        return None
    return geom.get("type")


# =============================================================================
# MANIPULACAO DE GEOMETRIAS ESPECIFICAS
# =============================================================================

def criar_point(coordinates: List[float], properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Cria uma Feature do tipo Point."""
    return criar_feature(
        {"type": "Point", "coordinates": coordinates},
        properties,
    )


def criar_multi_point(coordinates: List[List[float]], properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Cria uma Feature do tipo MultiPoint."""
    return criar_feature(
        {"type": "MultiPoint", "coordinates": coordinates},
        properties,
    )


def criar_polygon(coordinates: List[List[List[float]]], properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Cria uma Feature do tipo Polygon."""
    return criar_feature(
        {"type": "Polygon", "coordinates": coordinates},
        properties,
    )


def criar_multi_polygon(coordinates: List[List[List[List[float]]]], properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Cria uma Feature do tipo MultiPolygon."""
    return criar_feature(
        {"type": "MultiPolygon", "coordinates": coordinates},
        properties,
    )


def criar_line_string(coordinates: List[List[float]], properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Cria uma Feature do tipo LineString."""
    return criar_feature(
        {"type": "LineString", "coordinates": coordinates},
        properties,
    )


def criar_multi_line_string(coordinates: List[List[List[float]]], properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Cria uma Feature do tipo MultiLineString."""
    return criar_feature(
        {"type": "MultiLineString", "coordinates": coordinates},
        properties,
    )


# =============================================================================
# PRESERVACAO DE METADADOS E ATRIBUTOS
# =============================================================================

def preservar_metadados(gdf: gpd.GeoDataFrame, metadados: Dict[str, Any]) -> gpd.GeoDataFrame:
    """Preserva metadados no GeoDataFrame como atributos."""
    if gdf is None or gdf.empty:
        return gdf

    gdf = gdf.copy()
    for key, value in metadados.items():
        gdf.attrs[key] = value

    return gdf


def extrair_metadados(gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
    """Extrai metadados preservados no GeoDataFrame."""
    if gdf is None:
        return {}
    return dict(gdf.attrs)


def adicionar_propriedades_feature(feature: Dict[str, Any], propriedades: Dict[str, Any]) -> Dict[str, Any]:
    """Adiciona propriedades a uma Feature existente."""
    if not isinstance(feature, dict):
        return feature

    feature = feature.copy()
    if "properties" not in feature:
        feature["properties"] = {}

    feature["properties"].update(limpar_propriedades(propriedades))
    return feature


def remover_propriedades_feature(feature: Dict[str, Any], chaves: List[str]) -> Dict[str, Any]:
    """Remove propriedades especificas de uma Feature."""
    if not isinstance(feature, dict):
        return feature

    feature = feature.copy()
    if "properties" in feature:
        for chave in chaves:
            feature["properties"].pop(chave, None)

    return feature


# =============================================================================
# UTILITARIOS DE ZONAS E PRESCRICOES
# =============================================================================

def gdf_zonas_para_geojson(gdf_zonas: gpd.GeoDataFrame) -> Dict[str, Any]:
    """Converte GeoDataFrame de zonas para GeoJSON preservando atributos tecnicos."""
    if gdf_zonas is None or gdf_zonas.empty:
        return {"type": "FeatureCollection", "features": []}

    gdf = gdf_zonas.copy()

    # Garantir que colunas tecnicas estejam presentes
    colunas_tecnicas = ["zona_id", "zona_uuid", "n_pixels", "percentual_area", "homogeneidade"]
    for col in colunas_tecnicas:
        if col not in gdf.columns:
            gdf[col] = None

    return gdf_para_geojson_dict(gdf)


def geojson_para_gdf_zonas(geojson: Dict[str, Any]) -> gpd.GeoDataFrame:
    """Converte GeoJSON de zonas para GeoDataFrame."""
    gdf = geojson_dict_para_gdf(geojson)

    # Garantir colunas tecnicas
    colunas_tecnicas = ["zona_id", "zona_uuid", "n_pixels", "percentual_area", "homogeneidade"]
    for col in colunas_tecnicas:
        if col not in gdf.columns:
            gdf[col] = None

    return gdf


def gdf_prescricoes_para_geojson(gdf_prescricoes: gpd.GeoDataFrame) -> Dict[str, Any]:
    """Converte GeoDataFrame de prescricoes para GeoJSON."""
    if gdf_prescricoes is None or gdf_prescricoes.empty:
        return {"type": "FeatureCollection", "features": []}

    gdf = gdf_prescricoes.copy()

    colunas_tecnicas = ["zona_id", "zona_uuid", "dose_kg_ha", "produto", "forma"]
    for col in colunas_tecnicas:
        if col not in gdf.columns:
            gdf[col] = None

    return gdf_para_geojson_dict(gdf)


def geojson_para_gdf_prescricoes(geojson: Dict[str, Any]) -> gpd.GeoDataFrame:
    """Converte GeoJSON de prescricoes para GeoDataFrame."""
    gdf = geojson_dict_para_gdf(geojson)

    colunas_tecnicas = ["zona_id", "zona_uuid", "dose_kg_ha", "produto", "forma"]
    for col in colunas_tecnicas:
        if col not in gdf.columns:
            gdf[col] = None

    return gdf


# =============================================================================
# UTILITARIOS GERAIS
# =============================================================================

def contar_features(geojson: Dict[str, Any]) -> int:
    """Conta o numero de features em um GeoJSON."""
    if not validar_geojson(geojson):
        return 0
    return len(geojson.get("features", []))


def contar_por_tipo_geometria(geojson: Dict[str, Any]) -> Dict[str, int]:
    """Conta features por tipo de geometria."""
    if not validar_geojson(geojson):
        return {}

    contagem: Dict[str, int] = {}
    for feature in geojson.get("features", []):
        tipo = extrair_tipo_geometria(feature)
        if tipo:
            contagem[tipo] = contagem.get(tipo, 0) + 1

    return contagem


def filtrar_por_tipo_geometria(geojson: Dict[str, Any], tipo: str) -> Dict[str, Any]:
    """Filtra features por tipo de geometria."""
    if not validar_geojson(geojson):
        return {"type": "FeatureCollection", "features": []}

    features = [
        f for f in geojson.get("features", [])
        if extrair_tipo_geometria(f) == tipo
    ]

    return criar_feature_collection(features)


def mesclar_geojsons(geojsons: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Mescla multiplos GeoJSONs em um unico FeatureCollection."""
    features: List[Dict[str, Any]] = []

    for geojson in geojsons:
        if validar_geojson(geojson):
            features.extend(geojson.get("features", []))

    return criar_feature_collection(features)


def bounding_box(geojson: Dict[str, Any]) -> Optional[Tuple[float, float, float, float]]:
    """Calcula a bounding box de um GeoJSON."""
    if not validar_geojson(geojson):
        return None

    try:
        gdf = geojson_dict_para_gdf(geojson)
        if gdf.empty:
            return None
        bounds = gdf.total_bounds
        return (float(bounds[0]), float(bounds[1]), float(bounds[2]), float(bounds[3]))
    except Exception as e:
        logger.error("Erro ao calcular bounding box: %s", e)
        return None


def area_total(geojson: Dict[str, Any]) -> float:
    """Calcula a area total em graus quadrados de um GeoJSON."""
    if not validar_geojson(geojson):
        return 0.0

    try:
        gdf = geojson_dict_para_gdf(geojson)
        if gdf.empty:
            return 0.0
        return float(gdf.geometry.area.sum())
    except Exception as e:
        logger.error("Erro ao calcular area total: %s", e)
        return 0.0
