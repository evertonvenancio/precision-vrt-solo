"""
Servico de parse de arquivos geoespaciais e tabulares para o Precision VRT Solo.

Regras de negocio:
- GeoJSON/SHP: contem poligonos (limite do talhao) e pontos (amostragem com lat/lon e id).
- CSV/XLSX: contem APENAS dados quimicos de solo e a coluna ponto_id.
- NUNCA exige lat/lon no CSV/XLSX.
- Fallback: se CSV/XLSX vier com tudo em 1 coluna, dividir por virgula.
"""

import os
import tempfile
import zipfile
import re
import json
import logging
from typing import Dict, Optional, List, Tuple, Any, Union
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from contextlib import contextmanager

import pandas as pd
import geopandas as gpd
import numpy as np

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS E CONSTANTES
# =============================================================================

class TipoArquivo(Enum):
    TABULAR = "tabular"
    PONTOS = "pontos"
    POLIGONO = "poligono"
    RASTER = "raster"
    AMBOS = "ambos"
    DESCONHECIDO = "desconhecido"


class TipoDado(Enum):
    ANALISE_LABORATORIAL = "analise_laboratorial"
    PONTOS_AMOSTRAIS = "pontos_amostrais"
    POLIGONO_TALHAO = "poligono_talhao"
    MAPA_PRODUTIVIDADE = "mapa_produtividade"
    MAPA_FERTILIDADE = "mapa_fertilidade"
    MAPA_COMPACTACAO = "mapa_compactacao"
    MAPA_UMIDADE = "mapa_umidade"
    MAPA_CONDUTIVIDADE = "mapa_condutividade"
    DEM = "dem"
    MAPA_DECLIVIDADE = "mapa_declividade"
    INDICE_ESPECTRAL = "indice_espectral"
    EXTRATOR = "extrator"
    DESCONHECIDO = "desconhecido"


CRS_PADRAO = "EPSG:4326"


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class Metadados:
    """Metadados padronizados para qualquer arquivo processado."""
    tipo_arquivo: str = ""
    tipo_dado: str = ""
    formato_origem: str = ""
    crs: str = CRS_PADRAO
    safra: Optional[str] = None
    camada: Optional[str] = None
    indice_espectral: Optional[str] = None
    total_registros: int = 0
    colunas_originais: List[str] = field(default_factory=list)
    colunas_padronizadas: List[str] = field(default_factory=list)
    bbox: Optional[Tuple[float, float, float, float]] = None
    resolucao: Optional[float] = None
    unidade: Optional[str] = None
    fonte: Optional[str] = None
    data_coleta: Optional[str] = None
    validacoes: List[str] = field(default_factory=list)
    erros: List[str] = field(default_factory=list)
    avisos: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ResultadoParse:
    """Resultado padronizado do parser."""
    tipo: str = ""
    tipo_dado: str = ""
    df: Optional[pd.DataFrame] = None
    gdf_pontos: Optional[gpd.GeoDataFrame] = None
    gdf_poligono: Optional[gpd.GeoDataFrame] = None
    raster: Optional[Any] = None
    metadados: Metadados = field(default_factory=Metadados)
    crs: str = CRS_PADRAO
    merge_info: Optional[Dict[str, Any]] = None

    def get(self, key: str, default: Any = None) -> Any:
        """Compatibilidade com acesso dict-like."""
        mapping = {
            "tipo": self.tipo,
            "tipo_dado": self.tipo_dado,
            "df": self.df,
            "gdf": self.gdf_poligono if self.gdf_poligono is not None else self.gdf_pontos,
            "gdf_pontos": self.gdf_pontos,
            "gdf_poligono": self.gdf_poligono,
            "raster": self.raster,
            "metadados": self.metadados,
            "crs": self.crs,
            "merge_info": self.merge_info,
            "registros": self.metadados.total_registros if self.metadados else 0,
            "origem": self.metadados.formato_origem if self.metadados else "desconhecido",
        }
        return mapping.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tipo": self.tipo,
            "tipo_dado": self.tipo_dado,
            "df_shape": self.df.shape if self.df is not None else None,
            "gdf_pontos_shape": self.gdf_pontos.shape if self.gdf_pontos is not None else None,
            "gdf_poligono_shape": self.gdf_poligono.shape if self.gdf_poligono is not None else None,
            "raster_presente": self.raster is not None,
            "metadados": self.metadados.to_dict(),
            "crs": self.crs,
            "merge_info": self.merge_info,
        }


# =============================================================================
# MAPEAMENTOS DE COLUNAS
# =============================================================================

MAPEAMENTO_COLUNAS = {
    # Identificadores
    "id": ["id", "ponto_id", "point_id", "sample_id", "amostra_id", "codigo", "code", "fid", "objectid", "gid", "seq", "numero", "número", "num"],
    "ponto_id": ["ponto_id", "point_id", "sample_id", "amostra_id", "id_ponto", "id_amostra", "codigo_ponto", "cod_ponto", "pt_id"],
    "talhao_id": ["talhao_id", "talhao", "talhão", "field_id", "field", "plot_id", "plot", "parcela_id", "parcela", "bloco", "bloco_id", "fazenda_id", "fazenda"],
    "safra": ["safra", "crop_year", "year", "ano", "temporada", "season", "ciclo", "harvest"],
    "camada": ["camada", "layer", "depth", "profundidade", "horizonte", "stratum", "camada_solo"],

    # Coordenadas
    "latitude": ["latitude", "lat", "y", "coord_y", "lat_y", "latitud", "latit"],
    "longitude": ["longitude", "lon", "x", "coord_x", "lon_x", "longitud", "longit"],
    "altitude": ["altitude", "alt", "elev", "elevation", "z", "cota", "cotam"],

    # Macro
    "ph": ["ph", "ph_h2o", "ph_cacl2", "ph_agua", "ph_agua_1_2_5", "ph_smp", "ph", "ph"],
    "fosforo": ["p", "fosforo", "fósforo", "phosphorus", "p_mehlich", "p_resina", "p_bray", "p_olsen", "p_disponivel", "p_assimilavel", "p_rem", "p_mg_kg", "p_mg_dm3", "p_ppm"],
    "potassio": ["k", "potassio", "potássio", "potassium", "k_mehlich", "k_disponivel", "k_trocavel", "k_mg_kg", "k_mg_dm3", "k_ppm", "k_cmolc", "k_cmolc_dm3"],
    "calcio": ["ca", "calcio", "cálcio", "calcium", "ca_trocavel", "ca_disponivel", "ca_mg_kg", "ca_mg_dm3", "ca_ppm", "ca_cmolc", "ca_cmolc_dm3"],
    "magnesio": ["mg", "magnesio", "magnésio", "magnesium", "mg_trocavel", "mg_disponivel", "mg_mg_kg", "mg_mg_dm3", "mg_ppm", "mg_cmolc", "mg_cmolc_dm3"],
    "enxofre": ["s", "enxofre", "sulfur", "sulfato", "so4", "s_disponivel", "s_mg_kg", "s_mg_dm3", "s_ppm"],
    "aluminio": ["al", "aluminio", "alumínio", "aluminum", "al_trocavel", "al_troc", "al_mg_kg", "al_mg_dm3", "al_ppm", "al_cmolc", "al_cmolc_dm3"],
    "sodio": ["na", "sodio", "sódio", "sodium", "na_trocavel", "na_mg_kg", "na_mg_dm3", "na_ppm", "na_cmolc", "na_cmolc_dm3"],
    "boro": ["b", "boro", "boron", "b_disponivel", "b_mg_kg", "b_mg_dm3", "b_ppm"],
    "cobre": ["cu", "cobre", "copper", "cu_disponivel", "cu_dta", "cu_mg_kg", "cu_mg_dm3", "cu_ppm"],
    "ferro": ["fe", "ferro", "iron", "fe_disponivel", "fe_dta", "fe_mg_kg", "fe_mg_dm3", "fe_ppm"],
    "manganes": ["mn", "manganes", "manganês", "manganese", "mn_disponivel", "mn_dta", "mn_mg_kg", "mn_mg_dm3", "mn_ppm"],
    "zinco": ["zn", "zinco", "zinc", "zn_disponivel", "zn_dta", "zn_mg_kg", "zn_mg_dm3", "zn_ppm"],
    "molibdenio": ["mo", "molibdenio", "molibdênio", "molybdenum", "mo_disponivel", "mo_mg_kg", "mo_mg_dm3", "mo_ppm"],
    "cloro": ["cl", "cloro", "chlorine", "chloride", "cl_mg_kg", "cl_mg_dm3", "cl_ppm"],
    "carbono_organico": ["c_org", "c_organico", "carbono_organico", "organic_carbon", "oc", "c_total", "c", "ct", "carbono", "carbon"],
    "materia_organica": ["mo", "materia_organica", "matéria_organica", "organic_matter", "om", "m_o", "materia_org", "mat_org"],
    "ctc": ["ctc", "ctc_efetiva", "ctc_pH7", "ctc_ph7", "capacidade_troca_cationica", "cec", "cec_ph7", "t", "t_value"],
    "ctc_efetiva": ["ctc_efetiva", "ctc_ef", "ctc_e", "t_efetiva", "cec_efetiva", "v_e"],
    "saturacao_bases": ["v", "saturacao_bases", "saturação_bases", "base_saturation", "bs", "v_percent", "v_%"],
    "saturacao_aluminio": ["m", "saturacao_al", "saturação_al", "saturacao_aluminio", "saturação_alumínio", "al_saturation", "al_sat", "m_percent", "m_%"],
    "relacao_ca_mg": ["ca_mg", "ca/mg", "ca:mg", "relacao_ca_mg", "relação_ca_mg", "ca_mg_ratio"],
    "relacao_ca_k": ["ca_k", "ca/k", "ca:k", "relacao_ca_k", "relação_ca_k", "ca_k_ratio"],
    "relacao_mg_k": ["mg_k", "mg/k", "mg:k", "relacao_mg_k", "relação_mg_k", "mg_k_ratio"],
    "soma_bases": ["sb", "soma_bases", "sum_bases", "base_sum", "soma_de_bases"],
    "indice_smp": ["smp", "indice_smp", "índice_smp", "smp_index", "smp_buffer"],
    "indice_y": ["y", "indice_y", "índice_y", "y_index", "ind_y"],
    "carbonatos": ["co3", "carbonatos", "carbonates", "caco3", "calcario", "calcário"],
    "gesso": ["gesso", "gypsum", "sulfato_calcio", "sulfato_cálcio", "caso4"],
    "silte": ["silte", "silt", "silte_%", "silte_percent", "silt_percent"],
    "areia": ["areia", "sand", "areia_%", "areia_percent", "sand_percent"],
    "argila": ["argila", "clay", "argila_%", "argila_percent", "clay_percent"],
    "textura": ["textura", "texture", "classe_textural", "textural_class", "textural"],
    "densidade": ["ds", "densidade", "density", "bulk_density", "densidade_aparente", "rho", "rho_b"],
    "porosidade": ["porosidade", "porosity", "poro", "pore"],

    # Produtividade
    "produtividade": ["produtividade", "productivity", "yield", "rendimento", "producao", "produção", "ton_ha", "ton/ha", "sc_ha", "saca_ha", "kg_ha", "bu_ac", "massa_seca", "dry_matter", "biomassa"],
    "umidade_grao": ["umidade_grao", "grain_moisture", "moisture_content", "umidade", "h2o_grao"],

    # Compactacao
    "resistencia_penetracao": ["rp", "resistencia_penetracao", "resistência_penetração", "penetration_resistance", "cone_index", "ci", "resistencia", "resistência"],
    "densidade_relativa": ["dr", "densidade_relativa", "relative_density", "compaction", "compactacao", "compactação"],
    "profundidade_compactacao": ["prof_compactacao", "profundidade_compactacao", "profundidade_compactação", "compaction_depth", "depth_compaction"],

    # Umidade
    "umidade_solo": ["umidade_solo", "soil_moisture", "water_content", "theta", "vwc", "swc", "umidade_volumetrica", "umidade_gravimetrica", "water_content_volumetric", "water_content_gravimetric"],

    # Condutividade
    "condutividade_eletrica": ["ce", "condutividade_eletrica", "condutividade_elétrica", "electrical_conductivity", "ec", "condutividade", "conductivity", "ec_aparente", "ec_a", "eca", "em38", "veris"],

    # DEM / Topografia
    "elevacao": ["elevacao", "elevação", "elevation", "dem", "altitude", "alt", "z", "cota", "cotam", "mdt", "digital_elevation_model"],
    "declividade": ["declividade", "slope", "inclinacao", "inclinação", "gradiente", "grade", "pendente", "steepness", "slope_percent", "slope_degree"],
    "aspecto": ["aspecto", "aspect", "exposicao", "exposição", "orientacao", "orientação", "face"],
    "curvatura": ["curvatura", "curvature", "curv", "profile_curvature", "plan_curvature", "tangential_curvature"],
    "indice_topografico": ["twi", "topographic_wetness_index", "indice_umidade_topografico", "índice_umidade_topográfico", "wetness_index", "spi", "stream_power_index", "ls_factor"],

    # Indices espectrais (genericos)
    "indice_espectral": ["ndvi", "ndre", "gndvi", "evi", "savi", "msavi", "osavi", "vari", "arvi", "ccci", "sipi", "mcari", "mtvi2", "ci_green", "ci_rededge", "lai", "fapar", "fractional_cover", "biomassa", "clorofila", "ndwi", "nbr", "nbr2", "gci", "reci", "sipi", "pri", "wdrvi", "gli", "ngrdi", "exg", "exr", "exb", "grvi", "rgbvi", "ikaw", "sccci", "mtci", "ci", "psri", "cri1", "cri2", "ari1", "ari2", "mari", "si", "ndmi", "msi", "swir", "nir", "red", "green", "blue", "red_edge", "rededge", "re"],

    # Extrator
    "extrator_id": ["extrator_id", "ext_id", "solucao_id", "solution_id", "receita_id", "recipe_id"],
    "dose": ["dose", "dosagem", "dosage", "rate", "taxa", "quantidade", "qtd", "amount", "volume", "massa"],
    "produto": ["produto", "product", "insumo", "input", "fertilizante", "fertilizer", "corretivo", "amendment", "adubo", "nutriente"],
    "forma_aplicacao": ["forma_aplicacao", "forma_aplicação", "application_method", "metodo", "método", "modo_aplicacao", "modo_aplicação", "aplicacao", "aplicação"],

    # Datas
    "data_coleta": ["data_coleta", "data", "date", "data_amostragem", "sampling_date", "collection_date", "dt_coleta", "dt_amostra"],
    "data_aplicacao": ["data_aplicacao", "data_aplicação", "application_date", "dt_aplicacao", "dt_aplicação"],
    "data_plantio": ["data_plantio", "planting_date", "sowing_date", "dt_plantio", "dt_semeadura"],
    "data_colheita": ["data_colheita", "harvest_date", "dt_colheita"],

    # Outros
    "area": ["area", "area_ha", "area_m2", "area_km2", "area_ac", "hectares", "hectare", "ha", "acre", "acres"],
    "cultura": ["cultura", "culture", "crop", "cultivo", "cultivar", "variedade", "variety", "especie", "espécie"],
    "observacao": ["obs", "observacao", "observação", "observation", "note", "nota", "comentario", "comentário", "descricao", "descrição"],
}


# =============================================================================
# FUNCOES UTILITARIAS
# =============================================================================

def _normalizar_nome_coluna(nome: str) -> str:
    """Normaliza um nome de coluna para o formato padrao."""
    nome = str(nome).strip().lower()
    nome = nome.replace(" ", "_")
    nome = nome.replace("-", "_")
    nome = nome.replace("/", "_")
    nome = nome.replace("\\", "_")
    nome = nome.replace("(", "")
    nome = nome.replace(")", "")
    nome = nome.replace("[", "")
    nome = nome.replace("]", "")
    nome = nome.replace("{", "")
    nome = nome.replace("}", "")
    nome = nome.replace(".", "_")
    nome = nome.replace(",", "_")
    nome = nome.replace(";", "_")
    nome = nome.replace(":", "_")
    nome = nome.replace("=", "_")
    nome = nome.replace("+", "_")
    nome = nome.replace("%", "percent")
    nome = nome.replace("&", "e")
    nome = nome.replace("*", "x")
    nome = nome.replace("@", "at")
    nome = nome.replace("#", "num")
    nome = nome.replace("$", "dolar")
    nome = nome.replace("!", "")
    nome = nome.replace("?", "")
    nome = nome.replace("'", "")
    nome = nome.replace('"', "")
    nome = nome.replace("`", "")
    nome = nome.replace("~", "")
    nome = nome.replace("^", "")
    nome = nome.replace("<", "_lt_")
    nome = nome.replace(">", "_gt_")
    nome = re.sub(r"_+", "_", nome)
    nome = nome.strip("_")
    return nome


def _mapear_colunas(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """Mapeia colunas do DataFrame para nomes padronizados."""
    colunas_originais = list(df.columns)
    mapeamento: Dict[str, str] = {}
    colunas_padronizadas: List[str] = []

    for col in colunas_originais:
        col_norm = _normalizar_nome_coluna(col)
        nome_padrao = col_norm

        for padrao, sinonimos in MAPEAMENTO_COLUNAS.items():
            if col_norm in sinonimos or any(sin in col_norm for sin in sinonimos):
                nome_padrao = padrao
                break

        mapeamento[col] = nome_padrao
        colunas_padronizadas.append(nome_padrao)

    df.columns = colunas_padronizadas
    return df, mapeamento


def _inferir_tipo_dado(df: pd.DataFrame, gdf_pontos: Optional[gpd.GeoDataFrame] = None,
                       gdf_poligono: Optional[gpd.GeoDataFrame] = None,
                       raster: Optional[Any] = None) -> str:
    """Infere o tipo de dado com base nas colunas presentes."""
    colunas = set(df.columns) if df is not None else set()

    # Analise laboratorial
    nutrientes = {"ph", "fosforo", "potassio", "calcio", "magnesio", "enxofre", "aluminio",
                  "sodio", "boro", "cobre", "ferro", "manganes", "zinco", "molibdenio", "cloro",
                  "carbono_organico", "materia_organica", "ctc", "ctc_efetiva", "saturacao_bases",
                  "saturacao_aluminio", "soma_bases", "indice_smp", "indice_y", "relacao_ca_mg",
                  "relacao_ca_k", "relacao_mg_k", "carbonatos", "gesso", "silte", "areia", "argila",
                  "textura", "densidade", "porosidade"}
    if len(colunas.intersection(nutrientes)) >= 3:
        return TipoDado.ANALISE_LABORATORIAL.value

    # Mapa de produtividade
    if "produtividade" in colunas:
        return TipoDado.MAPA_PRODUTIVIDADE.value

    # Mapa de compactacao
    if "resistencia_penetracao" in colunas or "densidade_relativa" in colunas:
        return TipoDado.MAPA_COMPACTACAO.value

    # Mapa de umidade
    if "umidade_solo" in colunas:
        return TipoDado.MAPA_UMIDADE.value

    # Mapa de condutividade
    if "condutividade_eletrica" in colunas:
        return TipoDado.MAPA_CONDUTIVIDADE.value

    # DEM
    if "elevacao" in colunas and raster is not None:
        return TipoDado.DEM.value

    # Declividade
    if "declividade" in colunas:
        return TipoDado.MAPA_DECLIVIDADE.value

    # Indice espectral
    indices_espectrais = {"ndvi", "ndre", "gndvi", "evi", "savi", "msavi", "osavi", "vari",
                          "arvi", "ccci", "sipi", "mcari", "mtvi2", "ci_green", "ci_rededge",
                          "lai", "fapar", "fractional_cover", "biomassa", "clorofila", "ndwi",
                          "nbr", "nbr2", "gci", "reci", "pri", "wdrvi", "gli", "ngrdi", "exg",
                          "exr", "exb", "grvi", "rgbvi", "ikaw", "sccci", "mtci", "ci", "psri",
                          "cri1", "cri2", "ari1", "ari2", "mari", "si", "ndmi", "msi", "swir",
                          "nir", "red", "green", "blue", "red_edge", "rededge", "re"}
    if len(colunas.intersection(indices_espectrais)) >= 1:
        return TipoDado.INDICE_ESPECTRAL.value

    # Extrator
    if "dose" in colunas and "produto" in colunas:
        return TipoDado.EXTRATOR.value

    # Pontos amostrais
    if gdf_pontos is not None:
        return TipoDado.PONTOS_AMOSTRAIS.value

    # Poligono de talhao
    if gdf_poligono is not None:
        return TipoDado.POLIGONO_TALHAO.value

    return TipoDado.DESCONHECIDO.value


def _inferir_safra(df: pd.DataFrame) -> Optional[str]:
    """Tenta inferir a safra a partir dos dados."""
    if df is None:
        return None
    if "safra" in df.columns:
        valores = df["safra"].dropna().astype(str).unique()
        if len(valores) > 0:
            return str(valores[0])
    return None


def _inferir_camada(df: pd.DataFrame) -> Optional[str]:
    """Tenta inferir a camada/profundidade a partir dos dados."""
    if df is None:
        return None
    if "camada" in df.columns:
        valores = df["camada"].dropna().astype(str).unique()
        if len(valores) > 0:
            return str(valores[0])
    return None


def _inferir_indice_espectral(df: pd.DataFrame) -> Optional[str]:
    """Tenta inferir o indice espectral a partir dos dados."""
    if df is None:
        return None
    indices = {"ndvi", "ndre", "gndvi", "evi", "savi", "msavi", "osavi", "vari", "arvi",
               "ccci", "sipi", "mcari", "mtvi2", "ci_green", "ci_rededge", "lai", "fapar",
               "fractional_cover", "biomassa", "clorofila", "ndwi", "nbr", "nbr2", "gci",
               "reci", "pri", "wdrvi", "gli", "ngrdi", "exg", "exr", "exb", "grvi", "rgbvi",
               "ikaw", "sccci", "mtci", "ci", "psri", "cri1", "cri2", "ari1", "ari2", "mari",
               "si", "ndmi", "msi", "swir", "nir", "red", "green", "blue", "red_edge",
               "rededge", "re"}
    for col in df.columns:
        if col in indices:
            return col
    return None


def _calcular_bbox(gdf: Optional[gpd.GeoDataFrame] = None,
                   raster: Optional[Any] = None) -> Optional[Tuple[float, float, float, float]]:
    """Calcula a bounding box dos dados."""
    if gdf is not None and not gdf.empty:
        bounds = gdf.total_bounds
        return (float(bounds[0]), float(bounds[1]), float(bounds[2]), float(bounds[3]))
    if raster is not None:
        try:
            bounds = raster.bounds
            return (float(bounds.left), float(bounds.bottom), float(bounds.right), float(bounds.top))
        except Exception:
            pass
    return None


def _validar_tabular(df: pd.DataFrame) -> List[str]:
    """Valida dados tabulares e retorna lista de erros."""
    erros = []
    if df is None or df.empty:
        erros.append("DataFrame vazio ou nulo.")
        return erros
    if df.shape[0] == 0:
        erros.append("Nenhum registro encontrado.")
    if df.shape[1] == 0:
        erros.append("Nenhuma coluna encontrada.")
    if df.isna().all().all():
        erros.append("Todos os valores sao nulos.")
    return erros


def _validar_geometria(gdf: Optional[gpd.GeoDataFrame]) -> List[str]:
    """Valida geometria de um GeoDataFrame."""
    erros = []
    if gdf is None:
        return erros
    if gdf.empty:
        erros.append("GeoDataFrame vazio.")
        return erros
    if gdf.crs is None:
        erros.append("CRS nao definido.")
    invalidas = gdf[~gdf.is_valid]
    if not invalidas.empty:
        erros.append(f"{len(invalidas)} geometria(s) invalida(s).")
    return erros


def _normalizar_gdf(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Normaliza nomes de colunas e forca CRS EPSG:4326."""
    gdf.columns = gdf.columns.astype(str).str.strip().str.lower().str.replace(" ", "_")
    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326)
    elif gdf.crs.to_string() != CRS_PADRAO:
        gdf = gdf.to_crs(epsg=4326)
    return gdf


def _separar_geometrias(gdf: gpd.GeoDataFrame) -> Tuple[Optional[gpd.GeoDataFrame], Optional[gpd.GeoDataFrame]]:
    """Separa um GeoDataFrame misto em pontos e poligonos."""
    gdf_pontos = None
    gdf_poligono = None

    geom_types = gdf.geometry.type.unique()

    if "Point" in geom_types or "MultiPoint" in geom_types:
        gdf_pontos = gdf[gdf.geometry.type.isin(["Point", "MultiPoint"])].copy()
        gdf_pontos["longitude"] = gdf_pontos.geometry.x
        gdf_pontos["latitude"] = gdf_pontos.geometry.y

    if "Polygon" in geom_types or "MultiPolygon" in geom_types:
        gdf_poligono = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])].copy()

    return gdf_pontos, gdf_poligono


@contextmanager
def _temp_dir_context():
    """Context manager para diretorio temporario."""
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def _extrair_zip(file_path: str) -> str:
    """Extrai ZIP e retorna o diretorio temporario."""
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)
    return temp_dir


def _listar_arquivos_geoespaciais(diretorio: str) -> List[str]:
    """Lista arquivos geoespaciais em um diretorio."""
    extensoes = {".shp", ".geojson", ".json", ".tif", ".tiff", ".geotiff", ".asc", ".img", ".dem", ".hgt", ".grd"}
    arquivos = []
    for root, _, files in os.walk(diretorio):
        for f in files:
            ext = os.path.splitext(f.lower())[1]
            if ext in extensoes:
                arquivos.append(os.path.join(root, f))
    return arquivos


def _detectar_tipo_raster(file_path: str) -> str:
    """Detecta o tipo de dado contido em um raster."""
    try:
        import rasterio
        with rasterio.open(file_path) as src:
            tags = src.tags()
            desc = tags.get("DESCRIPTION", "").lower()
            nome = os.path.basename(file_path).lower()

            # Indicadores por nome de arquivo
            if any(x in nome for x in ["ndvi", "ndre", "gndvi", "evi", "savi", "msavi", "osavi", "vari",
                                         "arvi", "ccci", "sipi", "mcari", "mtvi2", "ci_green", "ci_rededge",
                                         "lai", "fapar", "fractional_cover", "biomassa", "clorofila", "ndwi",
                                         "nbr", "nbr2", "gci", "reci", "pri", "wdrvi", "gli", "ngrdi", "exg",
                                         "exr", "exb", "grvi", "rgbvi", "ikaw", "sccci", "mtci", "ci", "psri",
                                         "cri1", "cri2", "ari1", "ari2", "mari", "si", "ndmi", "msi"]):
                return TipoDado.INDICE_ESPECTRAL.value
            if any(x in nome for x in ["dem", "elevation", "elevacao", "elevação", "mdt", "altitude", "srtm", "topo"]):
                return TipoDado.DEM.value
            if any(x in nome for x in ["slope", "declividade", "inclinacao", "inclinação", "pendente"]):
                return TipoDado.MAPA_DECLIVIDADE.value
            if any(x in nome for x in ["produtividade", "yield", "rendimento", "producao", "produção", "biomassa"]):
                return TipoDado.MAPA_PRODUTIVIDADE.value
            if any(x in nome for x in ["compactacao", "compactação", "compaction", "resistencia", "resistência", "cone_index", "ci"]):
                return TipoDado.MAPA_COMPACTACAO.value
            if any(x in nome for x in ["umidade", "moisture", "water_content", "vwc", "swc"]):
                return TipoDado.MAPA_UMIDADE.value
            if any(x in nome for x in ["condutividade", "conductivity", "ec", "em38", "veris"]):
                return TipoDado.MAPA_CONDUTIVIDADE.value
            if any(x in nome for x in ["fertilidade", "fertility", "nutriente", "nutrient"]):
                return TipoDado.MAPA_FERTILIDADE.value

            # Indicadores por descricao
            if any(x in desc for x in ["ndvi", "ndre", "evi", "savi"]):
                return TipoDado.INDICE_ESPECTRAL.value
            if "elevation" in desc or "dem" in desc:
                return TipoDado.DEM.value
            if "slope" in desc:
                return TipoDado.MAPA_DECLIVIDADE.value

            return TipoDado.DESCONHECIDO.value
    except ImportError:
        logger.warning("rasterio nao disponivel para deteccao de tipo raster.")
        return TipoDado.DESCONHECIDO.value
    except Exception as e:
        logger.error(f"Erro ao detectar tipo raster: {e}")
        return TipoDado.DESCONHECIDO.value


def _processar_raster(file_path: str) -> Tuple[Optional[Any], Metadados]:
    """Processa um arquivo raster e retorna os dados e metadados."""
    metadados = Metadados()
    metadados.formato_origem = os.path.splitext(file_path)[1].lower()

    try:
        import rasterio
        from rasterio.transform import from_bounds

        with rasterio.open(file_path) as src:
            metadados.crs = src.crs.to_string() if src.crs else CRS_PADRAO
            metadados.resolucao = float(src.res[0]) if src.res else None
            metadados.bbox = (float(src.bounds.left), float(src.bounds.bottom),
                              float(src.bounds.right), float(src.bounds.top))
            metadados.total_registros = src.width * src.height
            metadados.colunas_originais = list(src.descriptions) if src.descriptions else [f"banda_{i+1}" for i in range(src.count)]
            metadados.colunas_padronizadas = metadados.colunas_originais.copy()

            # Ler dados
            data = src.read()

            # Criar GeoDataFrame com pontos para cada pixel nao-nulo
            rows, cols = np.where(data[0] != src.nodata if src.nodata is not None else data[0] != 0)
            if len(rows) > 0:
                xs, ys = rasterio.transform.xy(src.transform, rows, cols)
                valores = data[0][rows, cols]

                gdf = gpd.GeoDataFrame(
                    {"valor": valores, "banda_1": valores},
                    geometry=gpd.points_from_xy(xs, ys),
                    crs=src.crs if src.crs else CRS_PADRAO
                )
                gdf = _normalizar_gdf(gdf)

                metadados.tipo_arquivo = TipoArquivo.RASTER.value
                metadados.tipo_dado = _detectar_tipo_raster(file_path)
                metadados.validacoes.append("Raster processado com sucesso.")

                return gdf, metadados
            else:
                metadados.avisos.append("Raster sem dados validos.")
                return None, metadados

    except ImportError:
        metadados.erros.append("Biblioteca rasterio nao disponivel.")
        return None, metadados
    except Exception as e:
        metadados.erros.append(f"Erro ao processar raster: {str(e)}")
        return None, metadados


# =============================================================================
# FUNCAO PRINCIPAL
# =============================================================================

def parse_upload(file_path: str, merge_com: Optional[ResultadoParse] = None) -> ResultadoParse:
    """
    Faz o parse de um arquivo de upload e retorna um ResultadoParse estruturado.

    Args:
        file_path: Caminho do arquivo a ser processado.
        merge_com: Opcional. Outro ResultadoParse para fazer merge (dados tabulares + pontos).

    Returns:
        ResultadoParse com todos os dados e metadados padronizados.
    """
    resultado = ResultadoParse()
    metadados = Metadados()

    if not os.path.exists(file_path):
        metadados.erros.append(f"Arquivo nao encontrado: {file_path}")
        resultado.metadados = metadados
        return resultado

    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename.lower())[1]
    metadados.formato_origem = ext

    df_tabular: Optional[pd.DataFrame] = None
    gdf_pontos: Optional[gpd.GeoDataFrame] = None
    gdf_poligono: Optional[gpd.GeoDataFrame] = None
    raster_gdf: Optional[gpd.GeoDataFrame] = None

    try:
        # --------------------------------------------------
        # CASO 1: Arquivo tabular (CSV ou XLSX)
        # --------------------------------------------------
        if ext in (".csv", ".xlsx", ".xls"):
            if ext == ".csv":
                df_tabular = pd.read_csv(
                    file_path,
                    sep=None,
                    engine="python",
                    encoding="utf-8-sig",
                    encoding_errors="ignore"
                )
            else:
                df_tabular = pd.read_excel(file_path, engine="openpyxl")

            # Fallback: se tudo veio em uma unica coluna, dividir por virgula
            if len(df_tabular.columns) == 1:
                col_name = df_tabular.columns[0]
                df_tabular = df_tabular[col_name].str.split(",", expand=True)
                if len(df_tabular) > 0:
                    df_tabular.columns = df_tabular.iloc[0]
                    df_tabular = df_tabular.iloc[1:].reset_index(drop=True)

            # Padronizar colunas
            colunas_originais = list(df_tabular.columns)
            df_tabular, mapeamento = _mapear_colunas(df_tabular)

            # Remover duplicatas
            df_tabular = df_tabular.drop_duplicates()

            # Validar
            erros_validacao = _validar_tabular(df_tabular)
            metadados.erros.extend(erros_validacao)

            metadados.tipo_arquivo = TipoArquivo.TABULAR.value
            metadados.tipo_dado = _inferir_tipo_dado(df_tabular)
            metadados.total_registros = len(df_tabular)
            metadados.colunas_originais = colunas_originais
            metadados.colunas_padronizadas = list(df_tabular.columns)
            metadados.safra = _inferir_safra(df_tabular)
            metadados.camada = _inferir_camada(df_tabular)
            metadados.indice_espectral = _inferir_indice_espectral(df_tabular)
            metadados.validacoes.append("Arquivo tabular processado com sucesso.")

            resultado.tipo = TipoArquivo.TABULAR.value
            resultado.tipo_dado = metadados.tipo_dado
            resultado.df = df_tabular
            resultado.metadados = metadados
            resultado.crs = CRS_PADRAO

        # --------------------------------------------------
        # CASO 2: GeoJSON ou JSON
        # --------------------------------------------------
        elif ext in (".geojson", ".json"):
            gdf = gpd.read_file(file_path)
            gdf = _normalizar_gdf(gdf)
            gdf_pontos, gdf_poligono = _separar_geometrias(gdf)

            erros_pontos = _validar_geometria(gdf_pontos)
            erros_poligono = _validar_geometria(gdf_poligono)
            metadados.erros.extend(erros_pontos + erros_poligono)

            tipo = TipoArquivo.AMBOS.value
            if gdf_pontos is not None and gdf_poligono is None:
                tipo = TipoArquivo.PONTOS.value
            elif gdf_pontos is None and gdf_poligono is not None:
                tipo = TipoArquivo.POLIGONO.value
            elif gdf_pontos is None and gdf_poligono is None:
                metadados.erros.append("Nenhuma geometria valida encontrada no arquivo.")

            metadados.tipo_arquivo = tipo
            metadados.tipo_dado = _inferir_tipo_dado(None, gdf_pontos, gdf_poligono)
            metadados.total_registros = len(gdf)
            metadados.colunas_originais = list(gdf.columns)
            metadados.colunas_padronizadas = list(gdf.columns)
            metadados.bbox = _calcular_bbox(gdf)
            metadados.crs = str(gdf.crs) if gdf.crs else CRS_PADRAO
            metadados.validacoes.append("GeoJSON processado com sucesso.")

            resultado.tipo = tipo
            resultado.tipo_dado = metadados.tipo_dado
            resultado.gdf_pontos = gdf_pontos
            resultado.gdf_poligono = gdf_poligono
            resultado.metadados = metadados
            resultado.crs = metadados.crs

        # --------------------------------------------------
        # CASO 3: Shapefile (.shp) ou ZIP com shapefile
        # --------------------------------------------------
        elif ext == ".shp":
            gdf = gpd.read_file(file_path)
            gdf = _normalizar_gdf(gdf)
            gdf_pontos, gdf_poligono = _separar_geometrias(gdf)

            erros_pontos = _validar_geometria(gdf_pontos)
            erros_poligono = _validar_geometria(gdf_poligono)
            metadados.erros.extend(erros_pontos + erros_poligono)

            tipo = TipoArquivo.AMBOS.value
            if gdf_pontos is not None and gdf_poligono is None:
                tipo = TipoArquivo.PONTOS.value
            elif gdf_pontos is None and gdf_poligono is not None:
                tipo = TipoArquivo.POLIGONO.value
            elif gdf_pontos is None and gdf_poligono is None:
                metadados.erros.append("Nenhuma geometria valida encontrada no arquivo.")

            metadados.tipo_arquivo = tipo
            metadados.tipo_dado = _inferir_tipo_dado(None, gdf_pontos, gdf_poligono)
            metadados.total_registros = len(gdf)
            metadados.colunas_originais = list(gdf.columns)
            metadados.colunas_padronizadas = list(gdf.columns)
            metadados.bbox = _calcular_bbox(gdf)
            metadados.crs = str(gdf.crs) if gdf.crs else CRS_PADRAO
            metadados.validacoes.append("Shapefile processado com sucesso.")

            resultado.tipo = tipo
            resultado.tipo_dado = metadados.tipo_dado
            resultado.gdf_pontos = gdf_pontos
            resultado.gdf_poligono = gdf_poligono
            resultado.metadados = metadados
            resultado.crs = metadados.crs

        # --------------------------------------------------
        # CASO 4: ZIP contendo arquivos geoespaciais
        # --------------------------------------------------
        elif ext == ".zip":
            temp_dir = _extrair_zip(file_path)
            try:
                arquivos = _listar_arquivos_geoespaciais(temp_dir)

                if not arquivos:
                    metadados.erros.append("Nenhum arquivo geoespacial encontrado dentro do ZIP.")
                    resultado.metadados = metadados
                    return resultado

                # Processar todos os arquivos encontrados
                todos_pontos = []
                todos_poligonos = []
                todos_rasters = []

                for arq in arquivos:
                    arq_ext = os.path.splitext(arq.lower())[1]
                    if arq_ext == ".shp":
                        gdf = gpd.read_file(arq)
                        gdf = _normalizar_gdf(gdf)
                        pts, pol = _separar_geometrias(gdf)
                        if pts is not None:
                            todos_pontos.append(pts)
                        if pol is not None:
                            todos_poligonos.append(pol)
                    elif arq_ext in (".geojson", ".json"):
                        gdf = gpd.read_file(arq)
                        gdf = _normalizar_gdf(gdf)
                        pts, pol = _separar_geometrias(gdf)
                        if pts is not None:
                            todos_pontos.append(pts)
                        if pol is not None:
                            todos_poligonos.append(pol)
                    elif arq_ext in (".tif", ".tiff", ".geotiff"):
                        raster_gdf_temp, raster_meta = _processar_raster(arq)
                        if raster_gdf_temp is not None:
                            todos_rasters.append(raster_gdf_temp)
                            metadados.avisos.append(f"Raster processado: {os.path.basename(arq)}")

                # Consolidar
                if todos_pontos:
                    gdf_pontos = pd.concat(todos_pontos, ignore_index=True)
                    gdf_pontos = gpd.GeoDataFrame(gdf_pontos, geometry="geometry", crs=CRS_PADRAO)
                if todos_poligonos:
                    gdf_poligono = pd.concat(todos_poligonos, ignore_index=True)
                    gdf_poligono = gpd.GeoDataFrame(gdf_poligono, geometry="geometry", crs=CRS_PADRAO)
                if todos_rasters:
                    raster_gdf = pd.concat(todos_rasters, ignore_index=True)
                    raster_gdf = gpd.GeoDataFrame(raster_gdf, geometry="geometry", crs=CRS_PADRAO)

                tipo = TipoArquivo.AMBOS.value
                if gdf_pontos is not None and gdf_poligono is None and raster_gdf is None:
                    tipo = TipoArquivo.PONTOS.value
                elif gdf_pontos is None and gdf_poligono is not None and raster_gdf is None:
                    tipo = TipoArquivo.POLIGONO.value
                elif gdf_pontos is None and gdf_poligono is None and raster_gdf is not None:
                    tipo = TipoArquivo.RASTER.value

                metadados.tipo_arquivo = tipo
                metadados.tipo_dado = _inferir_tipo_dado(None, gdf_pontos, gdf_poligono)
                metadados.total_registros = (
                    (len(gdf_pontos) if gdf_pontos is not None else 0) +
                    (len(gdf_poligono) if gdf_poligono is not None else 0) +
                    (len(raster_gdf) if raster_gdf is not None else 0)
                )
                metadados.validacoes.append(f"ZIP processado: {len(arquivos)} arquivo(s) encontrado(s).")

                resultado.tipo = tipo
                resultado.tipo_dado = metadados.tipo_dado
                resultado.gdf_pontos = gdf_pontos
                resultado.gdf_poligono = gdf_poligono
                resultado.raster = raster_gdf
                resultado.metadados = metadados
                resultado.crs = CRS_PADRAO
            finally:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)

        # --------------------------------------------------
        # CASO 5: TIFF/GeoTIFF
        # --------------------------------------------------
        elif ext in (".tif", ".tiff", ".geotiff"):
            raster_gdf, raster_meta = _processar_raster(file_path)

            metadados = raster_meta
            metadados.formato_origem = ext

            if raster_gdf is not None:
                resultado.tipo = TipoArquivo.RASTER.value
                resultado.tipo_dado = metadados.tipo_dado
                resultado.gdf_pontos = raster_gdf
                resultado.metadados = metadados
                resultado.crs = metadados.crs
            else:
                metadados.erros.append("Falha ao processar raster.")
                resultado.metadados = metadados

        # --------------------------------------------------
        # CASO 6: Formato nao suportado
        # --------------------------------------------------
        else:
            metadados.erros.append(f"Formato de arquivo nao suportado: {ext}")
            resultado.metadados = metadados
            return resultado

        # --------------------------------------------------
        # MERGE: Dados tabulares + pontos geoespaciais
        # --------------------------------------------------
        if merge_com is not None:
            merge_info = _executar_merge(resultado, merge_com)
            resultado.merge_info = merge_info
            if merge_info.get("sucesso"):
                metadados.validacoes.append("Merge entre dados tabulares e geoespaciais realizado com sucesso.")
            else:
                metadados.avisos.append(f"Merge nao realizado: {merge_info.get('motivo', 'desconhecido')}")

        return resultado

    except Exception as e:
        logger.error(f"Erro ao fazer parse do arquivo {filename}: {e}")
        metadados.erros.append(f"Erro inesperado: {str(e)}")
        resultado.metadados = metadados
        return resultado


def _executar_merge(base: ResultadoParse, merge_com: ResultadoParse) -> Dict[str, Any]:
    """
    Executa merge entre dados tabulares e dados geoespaciais.
    Une DataFrame tabular com GeoDataFrame de pontos via coluna 'ponto_id'.
    """
    merge_info = {"sucesso": False, "motivo": "", "registros_antes": 0, "registros_depois": 0}

    # Identificar qual tem df tabular e qual tem pontos
    df_tab = base.df if base.df is not None else merge_com.df
    gdf_pts = base.gdf_pontos if base.gdf_pontos is not None else merge_com.gdf_pontos

    if df_tab is None:
        merge_info["motivo"] = "Nenhum DataFrame tabular disponivel para merge."
        return merge_info
    if gdf_pts is None:
        merge_info["motivo"] = "Nenhum GeoDataFrame de pontos disponivel para merge."
        return merge_info
    if "ponto_id" not in df_tab.columns:
        merge_info["motivo"] = "Coluna 'ponto_id' nao encontrada no DataFrame tabular."
        return merge_info
    if "ponto_id" not in gdf_pts.columns:
        merge_info["motivo"] = "Coluna 'ponto_id' nao encontrada no GeoDataFrame de pontos."
        return merge_info

    try:
        merge_info["registros_antes"] = len(df_tab)

        # Converter ponto_id para string para merge seguro
        df_tab["ponto_id"] = df_tab["ponto_id"].astype(str)
        gdf_pts["ponto_id"] = gdf_pts["ponto_id"].astype(str)

        # Fazer merge
        gdf_merged = gdf_pts.merge(df_tab, on="ponto_id", how="left")

        merge_info["registros_depois"] = len(gdf_merged)
        merge_info["sucesso"] = True

        # Atualizar o resultado base
        if base.gdf_pontos is not None:
            base.gdf_pontos = gdf_merged
        else:
            base.gdf_pontos = gdf_merged
            base.df = None

        base.tipo = TipoArquivo.PONTOS.value
        base.metadados.total_registros = len(gdf_merged)
        base.metadados.validacoes.append(f"Merge: {merge_info['registros_depois']} registros unidos.")

    except Exception as e:
        merge_info["motivo"] = f"Erro durante merge: {str(e)}"

    return merge_info


# =============================================================================
# FUNCOES AUXILIARES PUBLICAS
# =============================================================================

def inferir_tipo_dado(resultado: ResultadoParse) -> str:
    """Re-inferencia o tipo de dado de um resultado ja processado."""
    return _inferir_tipo_dado(resultado.df, resultado.gdf_pontos, resultado.gdf_poligono)


def validar_resultado(resultado: ResultadoParse) -> List[str]:
    """Valida um ResultadoParse e retorna lista de problemas."""
    problemas = []
    if resultado.df is not None:
        problemas.extend(_validar_tabular(resultado.df))
    if resultado.gdf_pontos is not None:
        problemas.extend(_validar_geometria(resultado.gdf_pontos))
    if resultado.gdf_poligono is not None:
        problemas.extend(_validar_geometria(resultado.gdf_poligono))
    return problemas


def merge_dados(tabular: ResultadoParse, geoespacial: ResultadoParse) -> ResultadoParse:
    """Merge explicito entre resultado tabular e geoespacial."""
    return parse_upload("", merge_com=geoespacial) if tabular.df is None else _executar_merge(tabular, geoespacial)


def adicionar_mapeamento_coluna(padrao: str, sinonimos: List[str]) -> None:
    """Adiciona novos sinonimos ao mapeamento de colunas em tempo de execucao."""
    if padrao in MAPEAMENTO_COLUNAS:
        MAPEAMENTO_COLUNAS[padrao].extend(sinonimos)
        MAPEAMENTO_COLUNAS[padrao] = list(set(MAPEAMENTO_COLUNAS[padrao]))
    else:
        MAPEAMENTO_COLUNAS[padrao] = sinonimos


def listar_mapeamentos() -> Dict[str, List[str]]:
    """Retorna uma copia do dicionario de mapeamento de colunas."""
    return {k: v.copy() for k, v in MAPEAMENTO_COLUNAS.items()}


# =============================================================================
# FUNCOES ASYNC PARA ENDPOINTS FASTAPI
# =============================================================================

import tempfile
import shutil

async def async_parse_upload(file_obj, merge_com: Optional[ResultadoParse] = None) -> ResultadoParse:
    """Wrapper assincrono para parse_upload que aceita UploadFile do FastAPI."""
    import tempfile
    import shutil
    from pathlib import Path

    # Salvar arquivo em arquivo temporario
    suffix = Path(file_obj.filename).suffix if hasattr(file_obj, 'filename') else ''
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        if hasattr(file_obj, 'file'):
            shutil.copyfileobj(file_obj.file, tmp)
        else:
            tmp.write(file_obj.read())
        tmp_path = tmp.name

    try:
        resultado = parse_upload(tmp_path, merge_com=merge_com)
        return resultado
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def merge_dados(tabular: ResultadoParse, geoespacial: ResultadoParse) -> ResultadoParse:
    """Merge explicito entre resultado tabular e geoespacial."""
    if tabular.df is None:
        raise ValueError("Resultado tabular nao possui DataFrame")
    if geoespacial.gdf_pontos is None:
        raise ValueError("Resultado geoespacial nao possui pontos")

    df_tab = tabular.df.copy()
    gdf_pts = geoespacial.gdf_pontos.copy()

    # Padronizar ponto_id
    if "ponto_id" in df_tab.columns:
        df_tab["ponto_id"] = df_tab["ponto_id"].astype(str)
    if "ponto_id" in gdf_pts.columns:
        gdf_pts["ponto_id"] = gdf_pts["ponto_id"].astype(str)
    elif "id" in gdf_pts.columns:
        gdf_pts["ponto_id"] = gdf_pts["id"].astype(str)

    # Fazer merge
    if "ponto_id" in df_tab.columns and "ponto_id" in gdf_pts.columns:
        gdf_merged = gdf_pts.merge(df_tab, on="ponto_id", how="left")

        resultado = ResultadoParse()
        resultado.tipo = "pontos"
        resultado.tipo_dado = tabular.tipo_dado or geoespacial.tipo_dado
        resultado.gdf_pontos = gdf_merged
        resultado.df = None
        resultado.metadados = tabular.metadados
        resultado.metadados.validacoes.append(f"Merge: {len(gdf_merged)} registros unidos.")
        resultado.crs = geoespacial.crs or tabular.crs
        resultado.merge_info = {
            "sucesso": True,
            "registros_antes": len(df_tab),
            "registros_depois": len(gdf_merged),
        }
        return resultado
    else:
        raise ValueError("Coluna 'ponto_id' nao encontrada em ambos os dados para merge")
