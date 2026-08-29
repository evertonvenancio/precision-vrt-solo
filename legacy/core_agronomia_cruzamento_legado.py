"""
Motor de cruzamento espacial Solo x Planta.

Recebe camadas GeoJSON de zonas de solo e zonas de planta (NDVI ou produtividade),
realiza intersecção espacial via GeoPandas e classifica a fertilidade e desempenho
da planta para alimentar o motor de diagnóstico.

Dependências: geopandas, shapely
"""

import logging
from typing import Optional

import geopandas as gpd
import pandas as pd

logger = logging.getLogger(__name__)


# ===================== CLASSIFICAÇÃO DE FERTILIDADE =====================

class ClassificadorFertilidade:
    """Classifica zonas de solo em níveis de fertilidade."""

    # Limites baseados em EMBRAPA/IAC para solos tropicais
    LIMITES = {
        "ph": {
            "baixo": (0.0, 5.0),
            "medio": (5.0, 5.5),
            "alto": (5.5, 7.0),
        },
        "p_mg_dm3": {
            "baixo": (0.0, 10.0),
            "medio": (10.0, 20.0),
            "alto": (20.0, float("inf")),
        },
        "k_mg_dm3": {
            "baixo": (0.0, 60.0),
            "medio": (60.0, 120.0),
            "alto": (120.0, float("inf")),
        },
        "v_percent": {
            "baixo": (0.0, 40.0),
            "medio": (40.0, 60.0),
            "alto": (60.0, 100.0),
        },
        "mo_percent": {
            "baixo": (0.0, 1.5),
            "medio": (1.5, 3.0),
            "alto": (3.0, float("inf")),
        },
    }

    @classmethod
    def classificar_atributo(cls, atributo: str, valor: float) -> str:
        """
        Classifica um atributo de solo em 'baixo', 'medio' ou 'alto'.

        Args:
            atributo: Nome do atributo (ph, p_mg_dm3, k_mg_dm3, v_percent, mo_percent).
            valor: Valor medido.

        Returns:
            Classe de fertilidade: 'baixo', 'medio' ou 'alto'.
        """
        limites = cls.LIMITES.get(atributo)
        if limites is None:
            logger.warning(f"Atributo desconhecido para classificação: {atributo}")
            return "desconhecido"

        for classe, (minimo, maximo) in limites.items():
            if minimo <= valor < maximo:
                return classe

        return "alto"

    @classmethod
    def classificar_fertilidade_zona(cls, atributos: dict) -> str:
        """
        Classifica fertilidade geral de uma zona de solo.

        A fertilidade é ALTA se: P > 20, pH entre 5.5-6.5 E V% > 60
        A fertilidade é BAIXA se: P < 10 OU pH < 5.0 OU V% < 40
        Caso contrário: MEDIA

        Args:
            atributos: Dict com ph, p_mg_dm3, k_mg_dm3, v_percent, mo_percent.

        Returns:
            'alta', 'media' ou 'baixa'.
        """
        ph = atributos.get("ph")
        p = atributos.get("p_mg_dm3")
        v = atributos.get("v_percent")

        # Fertilidade ALTA: todos os indicadores principais adequados
        alta = (
            p is not None and p > 20.0
            and ph is not None and 5.5 <= ph <= 6.5
            and (v is None or v > 60.0)
        )
        if alta:
            return "alta"

        # Fertilidade BAIXA: qualquer indicador crítico fora
        baixa_flags = [
            (p is not None and p < 10.0),
            (ph is not None and ph < 5.0),
            (v is not None and v < 40.0),
        ]
        if any(baixa_flags):
            return "baixa"

        return "media"


# ===================== CLASSIFICAÇÃO DE PLANTA =====================

class ClassificadorPlanta:
    """Classifica zonas de planta em desempenho alto, médio ou baixo."""

    NDVI_LIMITES = {
        "baixo": (0.0, 0.4),
        "medio": (0.4, 0.65),
        "alto": (0.65, 1.0),
    }

    PRODUTIVIDADE_PERCENTIS = {
        "baixo": 33.0,
        "alto": 66.0,
    }

    @classmethod
    def classificar_ndvi(cls, ndvi: float) -> str:
        """
        Classifica valor de NDVI em 'baixo', 'medio' ou 'alto'.

        Args:
            ndvi: Valor de NDVI (0.0 a 1.0).

        Returns:
            Classe de desempenho.
        """
        for classe, (minimo, maximo) in cls.NDVI_LIMITES.items():
            if minimo <= ndvi < maximo:
                return classe
        return "alto"

    @classmethod
    def normalizar_classe_planta(cls, classe_str: Optional[str]) -> Optional[str]:
        """
        Normaliza string de classe de planta para lowercase padronizado.

        Aceita variações: 'Alto', 'ALTO', 'high', 'H', etc.

        Args:
            classe_str: String com a classe.

        Returns:
            'baixo', 'medio' ou 'alto', ou None se inválido.
        """
        if classe_str is None:
            return None

        mapa = {
            "alto": "alto",
            "alta": "alto",
            "high": "alto",
            "h": "alto",
            "a": "alto",
            "medio": "medio",
            "média": "medio",
            "media": "medio",
            "medium": "medio",
            "med": "medio",
            "m": "medio",
            "baixo": "baixo",
            "baixa": "baixo",
            "low": "baixo",
            "l": "baixo",
            "b": "baixo",
        }

        return mapa.get(classe_str.lower().strip())


# ===================== MOTOR ESPACIAL =====================

class CruzamentoEspacial:
    """Realiza processamento espacial de cruzamento Solo x Planta."""

    def __init__(
        self,
        crs_saida: str = "EPSG:4326",
    ) -> None:
        """
        Inicializa o motor de cruzamento.

        Args:
            crs_saida: Sistema de referência de coordenadas para saída.
        """
        self.crs_saida = crs_saida
        self._classificador_solo = ClassificadorFertilidade()
        self._classificador_planta = ClassificadorPlanta()

    def carregar_geojson(self, geojson: dict) -> gpd.GeoDataFrame:
        """
        Carrega e valida um GeoJSON retornando GeoDataFrame.

        Args:
            geojson: Dict com estrutura GeoJSON FeatureCollection.

        Returns:
            GeoDataFrame com geometrias e atributos.

        Raises:
            ValueError: Se GeoJSON inválido.
        """
        if geojson.get("type") != "FeatureCollection":
            raise ValueError("GeoJSON deve ser do tipo FeatureCollection.")

        features = geojson.get("features", [])
        if not features:
            raise ValueError("GeoJSON não contém features.")

        gdf = gpd.GeoDataFrame.from_features(features, crs="EPSG:4326")

        if self.crs_saida != "EPSG:4326":
            gdf = gdf.to_crs(self.crs_saida)

        # Garantir CRS projetado para cálculo de área
        if gdf.crs and gdf.crs.is_geographic:
            gdf = gdf.to_crs("EPSG:3857")

        logger.info(f"GeoJSON carregado: {len(gdf)} features, CRS: {gdf.crs}")
        return gdf

    def preparar_camada_solo(
        self,
        gdf_solo: gpd.GeoDataFrame,
        id_campo: str = "zona_id",
    ) -> gpd.GeoDataFrame:
        """
        Prepara camada de solo: adiciona campo de fertilidade classificada.

        Args:
            gdf_solo: GeoDataFrame com zonas de solo.
            id_campo: Nome do campo de ID de zona.

        Returns:
            GeoDataFrame enriquecido com 'fertilidade_classe'.
        """
        gdf = gdf_solo.copy()

        # Garantir ID único
        if id_campo not in gdf.columns:
            gdf[id_campo] = range(1, len(gdf) + 1)

        # Classificar fertilidade por zona
        fertilidades = []
        for _, row in gdf.iterrows():
            atributos = {
                "ph": row.get("ph"),
                "p_mg_dm3": row.get("p_mg_dm3"),
                "k_mg_dm3": row.get("k_mg_dm3"),
                "v_percent": row.get("v_percent"),
                "mo_percent": row.get("mo_percent"),
            }
            fertilidades.append(
                ClassificadorFertilidade.classificar_fertilidade_zona(atributos)
            )

        gdf["fertilidade_classe"] = fertilidades
        logger.info(
            f"Solo preparado: {gdf['fertilidade_classe'].value_counts().to_dict()}"
        )
        return gdf

    def preparar_camada_planta(
        self,
        gdf_planta: gpd.GeoDataFrame,
        tipo: str = "ndvi",
        campo_valor: Optional[str] = None,
    ) -> gpd.GeoDataFrame:
        """
        Prepara camada de planta: normaliza classes de NDVI ou produtividade.

        Args:
            gdf_planta: GeoDataFrame com zonas de planta.
            tipo: 'ndvi' (com classes textuais ou valores 0-1) ou 'produtividade'.
            campo_valor: Nome do campo de valor (se None, detecta automaticamente).

        Returns:
            GeoDataFrame com 'planta_classe' padronizada.
        """
        gdf = gdf_planta.copy()

        if tipo == "ndvi":
            # Tentar detectar campo NDVI
            candidatos_ndvi = [
                col for col in gdf.columns
                if "ndvi" in col.lower() or "classe" in col.lower()
            ]
            campo = campo_valor or (candidatos_ndvi[0] if candidatos_ndvi else None)

            if campo and campo in gdf.columns:
                classes = []
                for val in gdf[campo]:
                    if isinstance(val, (int, float)):
                        classes.append(ClassificadorPlanta.classificar_ndvi(float(val)))
                    else:
                        normalizado = ClassificadorPlanta.normalizar_classe_planta(str(val))
                        classes.append(normalizado or "medio")
                gdf["planta_classe"] = classes
            else:
                logger.warning("Campo NDVI não encontrado. Usando 'medio' como padrão.")
                gdf["planta_classe"] = "medio"

        elif tipo == "produtividade":
            campo = campo_valor or next(
                (c for c in gdf.columns if "produt" in c.lower() or "yield" in c.lower()),
                None,
            )
            if campo and campo in gdf.columns:
                valores = gdf[campo].dropna()
                p33 = valores.quantile(0.33)
                p66 = valores.quantile(0.66)

                def classif_prod(v):
                    if pd.isna(v):
                        return "medio"
                    if v < p33:
                        return "baixo"
                    if v > p66:
                        return "alto"
                    return "medio"

                gdf["planta_classe"] = gdf[campo].apply(classif_prod)
            else:
                logger.warning("Campo produtividade não encontrado.")
                gdf["planta_classe"] = "medio"
        else:
            raise ValueError(f"Tipo de camada de planta inválido: '{tipo}'")

        logger.info(
            f"Planta preparada ({tipo}): {gdf['planta_classe'].value_counts().to_dict()}"
        )
        return gdf

    def executar_overlay(
        self,
        gdf_solo: gpd.GeoDataFrame,
        gdf_planta: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        """
        Executa intersecção espacial entre solo e planta.

        Args:
            gdf_solo: GeoDataFrame de solo preparado.
            gdf_planta: GeoDataFrame de planta preparado.

        Returns:
            GeoDataFrame com intersecções e áreas calculadas.
        """
        # Garantir mesmo CRS
        if gdf_planta.crs != gdf_solo.crs:
            gdf_planta = gdf_planta.to_crs(gdf_solo.crs)

        logger.info("Executando overlay spatial (intersecção)...")

        try:
            gdf_intersect = gpd.overlay(
                gdf_solo,
                gdf_planta,
                how="intersection",
                keep_geom_type=True,
            )
        except Exception as e:
            logger.error(f"Erro no overlay: {e}")
            raise

        # Calcular área de cada intersecção
        gdf_intersect["area_intersect_m2"] = gdf_intersect.geometry.area

        # Remover polígonos vazios ou muito pequenos (< 100 m²)
        gdf_intersect = gdf_intersect[
            gdf_intersect["area_intersect_m2"] > 100
        ].copy()

        logger.info(f"Overlay concluído: {len(gdf_intersect)} polígonos resultantes")
        return gdf_intersect

    def calcular_classe_predominante(
        self,
        gdf_intersect: gpd.GeoDataFrame,
        campo_zona_solo: str = "zona_id",
    ) -> pd.DataFrame:
        """
        Determina a classe de planta predominante em cada zona de solo.

        A classe predominante é aquela com maior área na intersecção.

        Args:
            gdf_intersect: GeoDataFrame resultado do overlay.
            campo_zona_solo: Campo de ID da zona de solo.

        Returns:
            DataFrame com zona_id, fertilidade_classe, planta_classe_predominante, area_ha.
        """
        if campo_zona_solo not in gdf_intersect.columns:
            # Tentar variante com sufixo _1 (gerado pelo overlay)
            campo_zona_solo = campo_zona_solo + "_1"

        resultado_rows = []

        for zona_id, grupo in gdf_intersect.groupby(campo_zona_solo):
            # Área por classe de planta
            area_por_classe = (
                grupo.groupby("planta_classe")["area_intersect_m2"].sum()
            )

            if area_por_classe.empty:
                continue

            classe_predominante = area_por_classe.idxmax()
            area_total_m2 = grupo["area_intersect_m2"].sum()

            fertilidade = grupo["fertilidade_classe"].iloc[0]

            resultado_rows.append({
                "zona_id": zona_id,
                "fertilidade_classe": fertilidade,
                "planta_classe_predominante": classe_predominante,
                "area_total_ha": round(area_total_m2 / 10_000, 4),
                "distribuicao_planta": area_por_classe.to_dict(),
            })

        df_resultado = pd.DataFrame(resultado_rows)
        logger.info(
            f"Classes predominantes calculadas: {len(df_resultado)} zonas"
        )
        return df_resultado

    def processar(
        self,
        geojson_solo: dict,
        geojson_planta: dict,
        tipo_planta: str = "ndvi",
        campo_valor_planta: Optional[str] = None,
        campo_zona_id: str = "zona_id",
    ) -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
        """
        Pipeline completo de cruzamento Solo x Planta.

        Args:
            geojson_solo: GeoJSON de zonas de solo com atributos químicos.
            geojson_planta: GeoJSON de zonas de planta (NDVI ou produtividade).
            tipo_planta: 'ndvi' ou 'produtividade'.
            campo_valor_planta: Nome do campo de valor na camada de planta.
            campo_zona_id: Nome do campo de ID das zonas de solo.

        Returns:
            Tupla (gdf_overlay, df_predominancias):
            - gdf_overlay: GeoDataFrame com todas as intersecções.
            - df_predominancias: DataFrame com classe predominante por zona.
        """
        logger.info("Iniciando pipeline de cruzamento Solo x Planta...")

        gdf_solo_raw = self.carregar_geojson(geojson_solo)
        gdf_planta_raw = self.carregar_geojson(geojson_planta)

        gdf_solo = self.preparar_camada_solo(gdf_solo_raw, campo_zona_id)
        gdf_planta = self.preparar_camada_planta(gdf_planta_raw, tipo_planta, campo_valor_planta)

        gdf_overlay = self.executar_overlay(gdf_solo, gdf_planta)
        df_predominancias = self.calcular_classe_predominante(gdf_overlay, campo_zona_id)

        logger.info("Pipeline concluído com sucesso.")
        return gdf_overlay, df_predominancias


def geojson_para_gdf(geojson: dict) -> gpd.GeoDataFrame:
    """
    Converte dict GeoJSON para GeoDataFrame.

    Args:
        geojson: Dict no formato GeoJSON FeatureCollection.

    Returns:
        GeoDataFrame com CRS EPSG:4326.
    """
    return gpd.GeoDataFrame.from_features(
        geojson.get("features", []),
        crs="EPSG:4326",
    )


def gdf_para_geojson(gdf: gpd.GeoDataFrame) -> dict:
    """
    Converte GeoDataFrame para dict GeoJSON.

    Args:
        gdf: GeoDataFrame a converter.

    Returns:
        Dict no formato GeoJSON FeatureCollection.
    """
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs("EPSG:4326")

    import json
    return json.loads(gdf.to_json())
