"""
Precision VRT Solo — Exportacao de Resultados do Pipeline VRT

Exporta resultados do pipeline para multiplos formatos:
  • GeoJSON / Shapefile (vetorial)
  • CSV (tabela de prescricao)
  • PNG (imagem estatica do mapa)
  • TXT (relatorio textual)
"""

import logging
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

import geopandas as gpd
import numpy as np
import pandas as pd
from rasterio.features import shapes
from rasterio.transform import from_bounds
from shapely.geometry import shape

from .configuracao import FormatoExportacao
from .contratos import MetadadosExportacao, ConfigExportacao
from .validacao import validar_dados_exportacao

logger = logging.getLogger(__name__)


class Exportador:
    """Exporta resultados do pipeline para multiplos formatos."""

    def __init__(
        self,
        output_dir: str = "data/output",
        config: Optional[ConfigExportacao] = None,
    ):
        """Inicializa o Exportador.

        Args:
            output_dir: Diretorio de saida para os arquivos exportados.
            config: Configuracao avancada opcional.
        """
        self.config = config or ConfigExportacao(output_dir=output_dir)
        self.output_dir = Path(self.config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.metadados: Optional[MetadadosExportacao] = None
        self.ultimo_caminho: Optional[str] = None

    def exportar(
        self,
        gdf_zonas: gpd.GeoDataFrame,
        prescricoes: Optional[Dict[str, Any]] = None,
        perfis_zonas: Optional[Dict[str, Dict[str, Any]]] = None,
        formato: Optional[FormatoExportacao] = None,
        nome_arquivo: str = "resultado",
        subpasta: Optional[str] = None,
        metadados: Optional[MetadadosExportacao] = None,
        **kwargs: Any,
    ) -> str:
        """Exporta resultados no formato especificado.

        Args:
            gdf_zonas: GeoDataFrame com as zonas de manejo.
            prescricoes: Dict com prescricoes por zona.
            perfis_zonas: Dict com perfis das zonas.
            formato: Formato de exportacao. Se None, usa o configurado.
            nome_arquivo: Nome base do arquivo de saida.
            subpasta: Subpasta dentro do diretorio de saida.
            metadados: Metadados do processamento.
            **kwargs: Parametros adicionais.

        Returns:
            Caminho do arquivo exportado.
        """
        formato = formato or self.config.formato_padrao
        self.metadados = metadados

        # Preparar dados
        gdf = self._preparar_dados(gdf_zonas, prescricoes, perfis_zonas)

        # Validar
        validar_dados_exportacao(gdf)

        # Exportar conforme formato
        if formato == FormatoExportacao.GEOJSON:
            return self.exportar_geojson(gdf, nome_arquivo, subpasta, **kwargs)
        elif formato == FormatoExportacao.SHAPEFILE:
            return self.exportar_shapefile(gdf, nome_arquivo, subpasta, **kwargs)
        elif formato == FormatoExportacao.CSV:
            return self.exportar_csv(gdf, nome_arquivo, subpasta, **kwargs)
        elif formato == FormatoExportacao.PNG:
            return self.exportar_png(gdf, nome_arquivo, subpasta, **kwargs)
        elif formato == FormatoExportacao.TXT:
            return self.exportar_txt(gdf, prescricoes, perfis_zonas, nome_arquivo, subpasta, **kwargs)
        elif formato == FormatoExportacao.KML:
            return self.exportar_kml(gdf, nome_arquivo, subpasta, **kwargs)
        elif formato == FormatoExportacao.GEOPACKAGE:
            return self.exportar_geopackage(gdf, nome_arquivo, subpasta, **kwargs)
        else:
            raise ValueError(f"Formato de exportacao nao suportado: {formato}")

    def _preparar_dados(
        self,
        gdf_zonas: gpd.GeoDataFrame,
        prescricoes: Optional[Dict[str, Any]] = None,
        perfis_zonas: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> gpd.GeoDataFrame:
        """Prepara os dados para exportacao."""
        gdf = gdf_zonas.copy()

        # Garantir CRS
        if gdf.crs is None:
            gdf = gdf.set_crs(self.config.crs_saida, allow_override=True)
        elif gdf.crs.to_string() != self.config.crs_saida:
            gdf = gdf.to_crs(self.config.crs_saida)

        # Corrigir geometrias invalidas
        invalidas = ~gdf.geometry.is_valid
        if invalidas.any():
            logger.warning("%d geometrias invalidas corrigidas.", invalidas.sum())
            gdf.loc[invalidas, "geometry"] = gdf.loc[invalidas, "geometry"].buffer(0)

        # Remover geometrias vazias
        gdf = gdf[~gdf.geometry.is_empty].copy()

        # Simplificar geometrias se configurado
        if self.config.simplificar_geometria:
            gdf["geometry"] = gdf.geometry.simplify(
                self.config.tolerancia_simplificacao,
                preserve_topology=True,
            )
            gdf = gdf[~gdf.geometry.is_empty].copy()

        # Adicionar prescricoes
        if prescricoes and self.config.incluir_prescricoes:
            gdf = self._adicionar_prescricoes(gdf, prescricoes)

        # Adicionar perfis
        if perfis_zonas and self.config.incluir_estatisticas:
            gdf = self._adicionar_perfis(gdf, perfis_zonas)

        # Adicionar metadados
        if self.metadados and self.config.incluir_metadados:
            gdf = self._adicionar_metadados(gdf, self.metadados)

        return gdf

    def adicionar_prescricao(
        self,
        gdf_zonas: gpd.GeoDataFrame,
        prescricoes: Dict[str, Any],
    ) -> gpd.GeoDataFrame:
        """Adiciona dados de prescricao ao GeoDataFrame de zonas (metodo publico).

        Alias para compatibilidade com chamadas existentes.
        """
        return self._adicionar_prescricoes(gdf_zonas, prescricoes)

    def _adicionar_prescricoes(
        self,
        gdf: gpd.GeoDataFrame,
        prescricoes: Dict[str, Any],
    ) -> gpd.GeoDataFrame:
        """Adiciona dados de prescricao ao GeoDataFrame."""
        gdf = gdf.copy()

        prescricoes_por_zona = prescricoes.get("prescricoes", {})

        for zona_id, pres in prescricoes_por_zona.items():
            mask = gdf["zona"] == zona_id
            if mask.sum() == 0:
                continue

            # Corretivos
            cal = pres.get("calagem", {})
            gdf.loc[mask, "calagem_t_ha"] = float(cal.get("dose_t_ha", 0.0))
            gdf.loc[mask, "calagem_status"] = cal.get("status", "")

            ges = pres.get("gessagem", {})
            gdf.loc[mask, "gessagem_t_ha"] = float(ges.get("dose_t_ha", 0.0))
            gdf.loc[mask, "gessagem_status"] = ges.get("status", "")

            # Macronutrientes
            n = pres.get("nitrogenio", {})
            gdf.loc[mask, "n_dose_kg_ha"] = float(n.get("dose_kg_ha", 0.0))
            gdf.loc[mask, "n_status"] = n.get("status", "")

            p = pres.get("fosforo", {})
            gdf.loc[mask, "p_dose_p2o5_kg_ha"] = float(p.get("dose_kg_ha", 0.0))
            gdf.loc[mask, "p_status"] = p.get("status", "")
            gdf.loc[mask, "p_bloqueado"] = bool(p.get("bloqueado", False))

            k = pres.get("potassio", {})
            gdf.loc[mask, "k_dose_k2o_kg_ha"] = float(k.get("dose_kg_ha", 0.0))
            gdf.loc[mask, "k_status"] = k.get("status", "")

            ca = pres.get("calcio", {})
            gdf.loc[mask, "ca_dose_kg_ha"] = float(ca.get("dose_kg_ha", 0.0))
            gdf.loc[mask, "ca_status"] = ca.get("status", "")

            mg = pres.get("magnesio", {})
            gdf.loc[mask, "mg_dose_kg_ha"] = float(mg.get("dose_kg_ha", 0.0))
            gdf.loc[mask, "mg_status"] = mg.get("status", "")

            s = pres.get("enxofre", {})
            gdf.loc[mask, "s_dose_kg_ha"] = float(s.get("dose_kg_ha", 0.0))
            gdf.loc[mask, "s_status"] = s.get("status", "")

            # Micronutrientes
            b = pres.get("boro", {})
            gdf.loc[mask, "b_dose_kg_ha"] = float(b.get("dose_kg_ha", 0.0))
            gdf.loc[mask, "b_status"] = b.get("status", "")

            cu = pres.get("cobre", {})
            gdf.loc[mask, "cu_dose_kg_ha"] = float(cu.get("dose_kg_ha", 0.0))
            gdf.loc[mask, "cu_status"] = cu.get("status", "")

            fe = pres.get("ferro", {})
            gdf.loc[mask, "fe_dose_kg_ha"] = float(fe.get("dose_kg_ha", 0.0))
            gdf.loc[mask, "fe_status"] = fe.get("status", "")

            mn = pres.get("manganes", {})
            gdf.loc[mask, "mn_dose_kg_ha"] = float(mn.get("dose_kg_ha", 0.0))
            gdf.loc[mask, "mn_status"] = mn.get("status", "")

            zn = pres.get("zinco", {})
            gdf.loc[mask, "zn_dose_kg_ha"] = float(zn.get("dose_kg_ha", 0.0))
            gdf.loc[mask, "zn_status"] = zn.get("status", "")

            # Custo
            gdf.loc[mask, "custo_ha"] = float(pres.get("custo_estimado_ha", 0.0))

        return gdf

    def _adicionar_perfis(
        self,
        gdf: gpd.GeoDataFrame,
        perfis_zonas: Dict[str, Dict[str, Any]],
    ) -> gpd.GeoDataFrame:
        """Adiciona perfis das zonas ao GeoDataFrame."""
        gdf = gdf.copy()

        for zona_id, perfil in perfis_zonas.items():
            mask = gdf["zona"] == zona_id
            if mask.sum() == 0:
                continue

            for attr, stats in perfil.get("atributos", {}).items():
                if isinstance(stats, dict):
                    for stat_key, stat_val in stats.items():
                        col_name = f"{attr}_{stat_key}"
                        try:
                            gdf.loc[mask, col_name] = float(stat_val)
                        except (TypeError, ValueError):
                            gdf.loc[mask, col_name] = stat_val

            # Adicionar metricas gerais da zona
            if "homogeneidade" in perfil:
                gdf.loc[mask, "homogeneidade"] = float(perfil["homogeneidade"])
            if "n_pixels" in perfil:
                gdf.loc[mask, "n_pixels"] = int(perfil["n_pixels"])
            if "percentual_area" in perfil:
                gdf.loc[mask, "percentual_area"] = float(perfil["percentual_area"])

        return gdf

    def _adicionar_metadados(
        self,
        gdf: gpd.GeoDataFrame,
        metadados: MetadadosExportacao,
    ) -> gpd.GeoDataFrame:
        """Adiciona metadados ao GeoDataFrame."""
        gdf = gdf.copy()

        gdf["meta_cultura"] = metadados.cultura
        gdf["meta_metodologia"] = metadados.metodologia
        gdf["meta_safra"] = metadados.safra or ""
        gdf["meta_versao"] = metadados.versao_sistema

        if metadados.camadas_utilizadas:
            gdf["meta_camadas"] = ", ".join(metadados.camadas_utilizadas)
        if metadados.indices_espectrais:
            gdf["meta_indices"] = ", ".join(metadados.indices_espectrais)

        return gdf

    def _obter_pasta(self, subpasta: Optional[str] = None) -> Path:
        """Obtem o caminho da pasta de saida."""
        pasta = self.output_dir
        if subpasta:
            pasta = pasta / subpasta
            pasta.mkdir(parents=True, exist_ok=True)
        return pasta

    def exportar_geojson(
        self,
        gdf: gpd.GeoDataFrame,
        nome_arquivo: str,
        subpasta: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Exporta GeoDataFrame para GeoJSON."""
        pasta = self._obter_pasta(subpasta)
        caminho = pasta / f"{nome_arquivo}.geojson"

        try:
            gdf.to_file(caminho, driver="GeoJSON")
            self.ultimo_caminho = str(caminho)
            logger.info("GeoJSON exportado: %s", caminho)
            return str(caminho)
        except Exception as e:
            logger.error("Erro ao exportar GeoJSON: %s", e)
            raise

    def exportar_shapefile(
        self,
        gdf: gpd.GeoDataFrame,
        nome_arquivo: str,
        subpasta: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Exporta GeoDataFrame para Shapefile."""
        pasta = self._obter_pasta(subpasta)
        caminho = pasta / f"{nome_arquivo}.shp"

        try:
            gdf.to_file(caminho, driver="ESRI Shapefile")
            self.ultimo_caminho = str(caminho)
            logger.info("Shapefile exportado: %s", caminho)
            return str(caminho)
        except Exception as e:
            logger.error("Erro ao exportar Shapefile: %s", e)
            raise

    def exportar_csv(
        self,
        gdf: gpd.GeoDataFrame,
        nome_arquivo: str,
        subpasta: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Exporta GeoDataFrame para CSV."""
        pasta = self._obter_pasta(subpasta)
        caminho = pasta / f"{nome_arquivo}.csv"

        try:
            df = pd.DataFrame(gdf.drop(columns="geometry"))
            df.to_csv(caminho, index=False, sep=";")
            self.ultimo_caminho = str(caminho)
            logger.info("CSV exportado: %s", caminho)
            return str(caminho)
        except Exception as e:
            logger.error("Erro ao exportar CSV: %s", e)
            raise

    def exportar_png(
        self,
        gdf: gpd.GeoDataFrame,
        nome_arquivo: str,
        subpasta: Optional[str] = None,
        gdf_poligono: Optional[gpd.GeoDataFrame] = None,
        **kwargs: Any,
    ) -> str:
        """Gera imagem estatica (PNG) do mapa de zonas."""
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        pasta = self._obter_pasta(subpasta)
        caminho = pasta / f"{nome_arquivo}.png"

        try:
            fig, ax = plt.subplots(figsize=(12, 12))

            gdf.plot(
                ax=ax,
                column="zona",
                categorical=True,
                cmap="RdYlGn",
                edgecolor="none",
                alpha=0.8,
                legend=True,
                legend_kwds={"title": "Zonas", "loc": "upper right"},
            )

            if gdf_poligono is not None and not gdf_poligono.empty:
                gdf_poligono.boundary.plot(ax=ax, color="black", linewidth=2)

            ax.set_title("Mapa de Zonas de Manejo", fontsize=14, fontweight="bold")
            ax.axis("off")

            plt.tight_layout()
            plt.savefig(caminho, bbox_inches="tight", dpi=150, pad_inches=0.1)
            plt.close(fig)

            self.ultimo_caminho = str(caminho)
            logger.info("PNG exportado: %s", caminho)
            return str(caminho)
        except Exception as e:
            logger.error("Erro ao exportar PNG: %s", e)
            raise

    def exportar_txt(
        self,
        gdf: gpd.GeoDataFrame,
        prescricoes: Optional[Dict[str, Any]],
        perfis_zonas: Optional[Dict[str, Dict[str, Any]]],
        nome_arquivo: str,
        subpasta: Optional[str] = None,
        nome_talhao: str = "Talhao",
        **kwargs: Any,
    ) -> str:
        """Gera relatorio em texto simples."""
        pasta = self._obter_pasta(subpasta)
        caminho = pasta / f"{nome_arquivo}_relatorio.txt"

        texto = self._gerar_relatorio_texto(prescricoes, perfis_zonas, nome_talhao)

        try:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(texto)
            self.ultimo_caminho = str(caminho)
            logger.info("Relatorio TXT exportado: %s", caminho)
            return str(caminho)
        except Exception as e:
            logger.error("Erro ao exportar TXT: %s", e)
            raise

    def exportar_kml(
        self,
        gdf: gpd.GeoDataFrame,
        nome_arquivo: str,
        subpasta: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Exporta GeoDataFrame para KML."""
        pasta = self._obter_pasta(subpasta)
        caminho = pasta / f"{nome_arquivo}.kml"

        try:
            # KML requer CRS EPSG:4326
            gdf_kml = gdf.copy()
            if gdf_kml.crs is not None and gdf_kml.crs.to_epsg() != 4326:
                gdf_kml = gdf_kml.to_crs("EPSG:4326")

            gdf_kml.to_file(caminho, driver="KML")
            self.ultimo_caminho = str(caminho)
            logger.info("KML exportado: %s", caminho)
            return str(caminho)
        except Exception as e:
            logger.error("Erro ao exportar KML: %s", e)
            raise

    def exportar_geopackage(
        self,
        gdf: gpd.GeoDataFrame,
        nome_arquivo: str,
        subpasta: Optional[str] = None,
        layer_name: str = "zonas",
        **kwargs: Any,
    ) -> str:
        """Exporta GeoDataFrame para GeoPackage."""
        pasta = self._obter_pasta(subpasta)
        caminho = pasta / f"{nome_arquivo}.gpkg"

        try:
            gdf.to_file(caminho, driver="GPKG", layer=layer_name)
            self.ultimo_caminho = str(caminho)
            logger.info("GeoPackage exportado: %s", caminho)
            return str(caminho)
        except Exception as e:
            logger.error("Erro ao exportar GeoPackage: %s", e)
            raise

    def exportar_csv_prescricao(
        self,
        prescricoes: Dict[str, Any],
        nome_arquivo: str,
        subpasta: Optional[str] = None,
        area_ha_por_zona: Optional[Dict[str, float]] = None,
    ) -> str:
        """Exporta tabela de prescricao em CSV."""
        pasta = self._obter_pasta(subpasta)
        caminho = pasta / f"{nome_arquivo}_prescricao.csv"

        rows: List[Dict[str, Any]] = []
        prescricoes_por_zona = prescricoes.get("prescricoes", {})

        for zona_id, pres in prescricoes_por_zona.items():
            row = {
                "zona": zona_id,
                "cultura": pres.get("cultura", ""),
                "produtividade_alvo_sc_ha": pres.get("produtividade_alvo", 0.0),
                "calagem_t_ha": pres.get("calagem", {}).get("dose_t_ha", 0.0),
                "calagem_status": pres.get("calagem", {}).get("status", ""),
                "gessagem_t_ha": pres.get("gessagem", {}).get("dose_t_ha", 0.0),
                "gessagem_status": pres.get("gessagem", {}).get("status", ""),
                "n_dose_kg_ha": pres.get("nitrogenio", {}).get("dose_kg_ha", 0.0),
                "n_status": pres.get("nitrogenio", {}).get("status", ""),
                "p_dose_p2o5_kg_ha": pres.get("fosforo", {}).get("dose_kg_ha", 0.0),
                "p_status": pres.get("fosforo", {}).get("status", ""),
                "p_bloqueado": pres.get("fosforo", {}).get("bloqueado", False),
                "k_dose_k2o_kg_ha": pres.get("potassio", {}).get("dose_kg_ha", 0.0),
                "k_status": pres.get("potassio", {}).get("status", ""),
                "ca_dose_kg_ha": pres.get("calcio", {}).get("dose_kg_ha", 0.0),
                "ca_status": pres.get("calcio", {}).get("status", ""),
                "mg_dose_kg_ha": pres.get("magnesio", {}).get("dose_kg_ha", 0.0),
                "mg_status": pres.get("magnesio", {}).get("status", ""),
                "s_dose_kg_ha": pres.get("enxofre", {}).get("dose_kg_ha", 0.0),
                "s_status": pres.get("enxofre", {}).get("status", ""),
                "b_dose_kg_ha": pres.get("boro", {}).get("dose_kg_ha", 0.0),
                "b_status": pres.get("boro", {}).get("status", ""),
                "cu_dose_kg_ha": pres.get("cobre", {}).get("dose_kg_ha", 0.0),
                "cu_status": pres.get("cobre", {}).get("status", ""),
                "fe_dose_kg_ha": pres.get("ferro", {}).get("dose_kg_ha", 0.0),
                "fe_status": pres.get("ferro", {}).get("status", ""),
                "mn_dose_kg_ha": pres.get("manganes", {}).get("dose_kg_ha", 0.0),
                "mn_status": pres.get("manganes", {}).get("status", ""),
                "zn_dose_kg_ha": pres.get("zinco", {}).get("dose_kg_ha", 0.0),
                "zn_status": pres.get("zinco", {}).get("status", ""),
                "custo_ha": pres.get("custo_estimado_ha", 0.0),
            }

            if area_ha_por_zona and zona_id in area_ha_por_zona:
                row["area_ha"] = area_ha_por_zona[zona_id]
                row["custo_total_zona"] = round(
                    pres.get("custo_estimado_ha", 0.0) * area_ha_por_zona[zona_id], 2
                )

            rows.append(row)

        df = pd.DataFrame(rows)

        try:
            df.to_csv(caminho, index=False, sep=";")
            logger.info("CSV prescricao exportado: %s", caminho)
            return str(caminho)
        except Exception as e:
            logger.error("Erro ao exportar CSV prescricao: %s", e)
            raise

    def raster_para_zonas_poligonos(
        self,
        raster_zonas: np.ndarray,
        grid_x: np.ndarray,
        grid_y: np.ndarray,
        atributos_zonas: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> gpd.GeoDataFrame:
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

    def gerar_imagem_mapa(
        self,
        gdf_zonas: gpd.GeoDataFrame,
        gdf_poligono: Optional[gpd.GeoDataFrame],
        caminho_saida: str,
    ) -> str:
        """Gera imagem estatica (PNG) do mapa de zonas de manejo."""
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import os

        os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)

        fig, ax = plt.subplots(figsize=(10, 10))

        gdf_zonas.plot(
            ax=ax,
            column="zona",
            categorical=True,
            cmap="RdYlGn",
            edgecolor="none",
            alpha=0.8,
        )

        if gdf_poligono is not None and not gdf_poligono.empty:
            gdf_poligono.boundary.plot(ax=ax, color="black", linewidth=2)

        ax.axis("off")

        plt.savefig(caminho_saida, bbox_inches="tight", dpi=150, pad_inches=0.1)
        plt.close(fig)

        return caminho_saida

    def _gerar_relatorio_texto(
        self,
        prescricoes: Optional[Dict[str, Any]],
        perfis_zonas: Optional[Dict[str, Dict[str, Any]]],
        nome_talhao: str = "Talhao",
    ) -> str:
        """Gera relatorio em texto simples."""
        if not prescricoes:
            return f"Relatorio de Prescricao - {nome_talhao}\nNenhuma prescricao disponivel."

        resumo = prescricoes.get("resumo", {})
        notas = prescricoes.get("notas_tecnicas", {})

        primeira_pres = list(
            prescricoes.get("prescricoes", {}).values()
        )[0] if prescricoes.get("prescricoes") else {}

        linhas = [
            "=" * 60,
            "RELATORIO DE PRESCRICAO DE TAXA VARIAVEL",
            "=" * 60,
            "",
            f"Talhao: {nome_talhao}",
            f"Cultura: {primeira_pres.get('cultura', 'N/A')}",
            f"Produtividade Alvo: {primeira_pres.get('produtividade_alvo', 0)} sc/ha",
            "",
            "-" * 60,
            "RESUMO EXECUTIVO",
            "-" * 60,
            f"Numero de zonas de manejo: {resumo.get('n_zonas', 0)}",
            f"Custo medio de fertilizacao: R$ {round(resumo.get('custo_medio_ha', 0), 2)}/ha",
            f"Custo minimo (zona mais barata): R$ {round(resumo.get('custo_min_ha', 0), 2)}/ha",
            f"Custo maximo (zona mais cara): R$ {round(resumo.get('custo_max_ha', 0), 2)}/ha",
            f"Economia potencial com VRT: R$ {round(resumo.get('economia_vrt', 0), 2)}/ha",
            "",
            "-" * 60,
            "PRESCRICAO POR ZONA",
            "-" * 60,
        ]

        nutrientes_labels = {
            "calagem": "Calagem",
            "gessagem": "Gessagem",
            "nitrogenio": "Nitrogenio (N)",
            "fosforo": "Fosforo (P2O5)",
            "potassio": "Potassio (K2O)",
            "calcio": "Calcio (Ca)",
            "magnesio": "Magnesio (Mg)",
            "enxofre": "Enxofre (S)",
            "boro": "Boro (B)",
            "cobre": "Cobre (Cu)",
            "ferro": "Ferro (Fe)",
            "manganes": "Manganes (Mn)",
            "zinco": "Zinco (Zn)",
        }

        prescricoes_por_zona = prescricoes.get("prescricoes", {})

        for zona_id, pres in prescricoes_por_zona.items():
            perfil = perfis_zonas.get(zona_id, {}) if perfis_zonas else {}

            linhas.extend([
                "",
                f"ZONA {zona_id}",
                "-" * 30,
                "Perfil do solo:",
                f"  pH: {round(perfil.get('ph', {}).get('media', 0), 2)}",
                f"  P: {round(perfil.get('p_mg_dm3', {}).get('media', 0), 1)} mg/dm3",
                f"  K: {round(perfil.get('k_mg_dm3', {}).get('media', 0), 1)} mg/dm3",
                f"  MO: {round(perfil.get('mo_percent', {}).get('media', 0), 2)}%",
                "",
                "Prescricao:",
            ])

            for nut_key, nut_label in nutrientes_labels.items():
                info = pres.get(nut_key, {})
                if nut_key in ("calagem", "gessagem"):
                    dose = info.get("dose_t_ha", 0.0)
                    unidade = "t/ha"
                else:
                    dose = info.get("dose_kg_ha", 0.0)
                    unidade = "kg/ha"
                status = info.get("status", "-")
                linhas.append(f"  {nut_label}: {dose} {unidade} ({status})")
                if info.get("bloqueado"):
                    linhas.append(f'    ALERTA: {info.get("alerta", "Bloqueado")}')

            linhas.append(
                f"  CUSTO TOTAL ZONA: R$ {round(pres.get('custo_estimado_ha', 0), 2)}/ha"
            )

        linhas.extend([
            "",
            "=" * 60,
            "NOTAS TECNICAS",
            "=" * 60,
        ])

        if notas.get("embasamento"):
            linhas.append(notas["embasamento"])
            linhas.append("")
        if notas.get("bibliografia"):
            linhas.append("Bibliografia:")
            linhas.append(f"  {notas['bibliografia']}")
            linhas.append("")
        if notas.get("referencia_legal"):
            linhas.append("Referencia Legal:")
            linhas.append(f"  {notas['referencia_legal']}")
            linhas.append("")

        linhas.extend([
            "Prescricao baseada em analise de solo georreferenciada",
            "  e interpolacao por krigagem ordinaria.",
            "Zonas definidas por clusterizacao multivariada (K-Means).",
            "Metas de produtividade conforme tabelas da Embrapa.",
            "Eficiencia dos fertilizantes: P2O5=20%, K2O=50%, N=60%.",
            "Recomenda-se validacao com amostragem apos 2 anos.",
            "",
            "Gerado automaticamente pelo sistema Precision VRT Solo.",
        ])

        return "\n".join(linhas)

    def salvar_relatorio(self, texto: str, nome_arquivo: str, subpasta: Optional[str] = None) -> str:
        """Salva relatorio em arquivo .txt."""
        pasta = self._obter_pasta(subpasta)
        caminho = pasta / f"{nome_arquivo}_relatorio.txt"

        try:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(texto)
            logger.info("Relatorio salvo: %s", caminho)
            return str(caminho)
        except Exception as e:
            logger.error("Erro ao salvar relatorio: %s", e)
            raise

    def exportar_json_metadados(
        self,
        metadados: MetadadosExportacao,
        nome_arquivo: str = "metadados",
        subpasta: Optional[str] = None,
    ) -> str:
        """Exporta metadados para arquivo JSON."""
        pasta = self._obter_pasta(subpasta)
        caminho = pasta / f"{nome_arquivo}_metadados.json"

        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(metadados.to_dict(), f, ensure_ascii=False, indent=2)
            logger.info("Metadados JSON exportados: %s", caminho)
            return str(caminho)
        except Exception as e:
            logger.error("Erro ao exportar metadados JSON: %s", e)
            raise

    def exportar_todos_formatos(
        self,
        gdf_zonas: gpd.GeoDataFrame,
        prescricoes: Optional[Dict[str, Any]] = None,
        perfis_zonas: Optional[Dict[str, Dict[str, Any]]] = None,
        nome_arquivo: str = "resultado",
        subpasta: Optional[str] = None,
        metadados: Optional[MetadadosExportacao] = None,
        **kwargs: Any,
    ) -> Dict[str, str]:
        """Exporta resultados em todos os formatos disponiveis.

        Args:
            gdf_zonas: GeoDataFrame com as zonas de manejo.
            prescricoes: Dict com prescricoes por zona.
            perfis_zonas: Dict com perfis das zonas.
            nome_arquivo: Nome base dos arquivos de saida.
            subpasta: Subpasta dentro do diretorio de saida.
            metadados: Metadados do processamento.
            **kwargs: Parametros adicionais.

        Returns:
            Dict com caminhos dos arquivos exportados por formato.
        """
        caminhos: Dict[str, str] = {}

        formatos = [
            FormatoExportacao.GEOJSON,
            FormatoExportacao.SHAPEFILE,
            FormatoExportacao.CSV,
            FormatoExportacao.KML,
            FormatoExportacao.GEOPACKAGE,
        ]

        for formato in formatos:
            try:
                caminho = self.exportar(
                    gdf_zonas,
                    prescricoes=prescricoes,
                    perfis_zonas=perfis_zonas,
                    formato=formato,
                    nome_arquivo=nome_arquivo,
                    subpasta=subpasta,
                    metadados=metadados,
                    **kwargs,
                )
                caminhos[formato.value] = caminho
            except Exception as e:
                logger.error("Erro ao exportar %s: %s", formato.value, e)
                caminhos[formato.value] = f"ERRO: {str(e)}"

        # Exportar CSV de prescricao separado
        if prescricoes:
            try:
                caminho_csv = self.exportar_csv_prescricao(
                    prescricoes,
                    nome_arquivo,
                    subpasta,
                )
                caminhos["csv_prescricao"] = caminho_csv
            except Exception as e:
                logger.error("Erro ao exportar CSV prescricao: %s", e)
                caminhos["csv_prescricao"] = f"ERRO: {str(e)}"

        # Exportar metadados JSON
        if metadados:
            try:
                caminho_meta = self.exportar_json_metadados(
                    metadados,
                    nome_arquivo,
                    subpasta,
                )
                caminhos["json_metadados"] = caminho_meta
            except Exception as e:
                logger.error("Erro ao exportar metadados JSON: %s", e)
                caminhos["json_metadados"] = f"ERRO: {str(e)}"

        return caminhos