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
from .formatos import (
    exportar_csv, exportar_csv_prescricao, exportar_geojson, 
    exportar_shapefile, exportar_png, exportar_txt, exportar_kml, 
    exportar_geopackage, raster_para_zonas_poligonos, gerar_imagem_mapa
)
from .relatorios import gerar_relatorio_texto, gerar_cartao_cabine

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
            return exportar_geojson(gdf, nome_arquivo, subpasta, self.config.output_dir, **kwargs)
        elif formato == FormatoExportacao.SHAPEFILE:
            return exportar_shapefile(gdf, nome_arquivo, subpasta, self.config.output_dir, **kwargs)
        elif formato == FormatoExportacao.CSV:
            return exportar_csv(gdf, nome_arquivo, subpasta, self.config.output_dir, **kwargs)
        elif formato == FormatoExportacao.PNG:
            gdf_poligono = kwargs.pop('gdf_poligono', None)
            return exportar_png(gdf, nome_arquivo, subpasta, output_dir=self.config.output_dir, gdf_poligono=gdf_poligono, **kwargs)
        elif formato == FormatoExportacao.TXT:
            nome_talhao = kwargs.pop('nome_talhao', 'Talhao')
            return exportar_txt(gdf, prescricoes, perfis_zonas, nome_arquivo, subpasta, nome_talhao=nome_talhao, output_dir=self.config.output_dir, **kwargs)
        elif formato == FormatoExportacao.KML:
            layer_name = kwargs.pop('layer_name', 'zonas')
            return exportar_kml(gdf, nome_arquivo, subpasta, output_dir=self.config.output_dir, layer_name=layer_name, **kwargs)
        elif formato == FormatoExportacao.GEOPACKAGE:
            layer_name = kwargs.pop('layer_name', 'zonas')
            return exportar_geopackage(gdf, nome_arquivo, subpasta, output_dir=self.config.output_dir, layer_name=layer_name, **kwargs)
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

    def exportar_kml(
        self,
        gdf: gpd.GeoDataFrame,
        nome_arquivo: str,
        subpasta: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Exporta GeoDataFrame para KML."""
        # KML requer CRS EPSG:4326
        gdf_kml = gdf.copy()
        if gdf_kml.crs is not None and gdf_kml.crs.to_epsg() != 4326:
            gdf_kml = gdf_kml.to_crs("EPSG:4326")

        pasta = self._obter_pasta(subpasta)
        caminho = pasta / f"{nome_arquivo}.kml"

        try:
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

    def raster_para_zonas_poligonos(
        self,
        raster_zonas: np.ndarray,
        grid_x: np.ndarray,
        grid_y: np.ndarray,
        atributos_zonas: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> gpd.GeoDataFrame:
        """Converte raster de zonas em poligonos vetoriais (GeoDataFrame)."""
        return raster_para_zonas_poligonos(raster_zonas, grid_x, grid_y, atributos_zonas)

    def gerar_imagem_mapa(
        self,
        gdf_zonas: gpd.GeoDataFrame,
        gdf_poligono: Optional[gpd.GeoDataFrame],
        caminho_saida: str,
    ) -> str:
        """Gera imagem estatica (PNG) do mapa de zonas de manejo."""
        return gerar_imagem_mapa(gdf_zonas, gdf_poligono, caminho_saida)

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
        from .configuracao import FormatoExportacao
        
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
                caminho_csv = exportar_csv_prescricao(
                    prescricoes,
                    nome_arquivo,
                    subpasta,
                    self.config.output_dir,
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