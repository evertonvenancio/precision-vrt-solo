"""
Precision VRT Solo — Geração de Imagens para Exportação

Funções para geração de imagens estáticas (PNG).
"""
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import geopandas as gpd

logger = logging.getLogger(__name__)


def gerar_imagem_mapa(gdf_zonas: gpd.GeoDataFrame, gdf_poligono: Optional[gpd.GeoDataFrame], 
                     caminho_saida: str, **kwargs: Any) -> str:
    """Gera imagem estatica (PNG) do mapa de zonas de manejo."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

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


def exportar_png(gdf: gpd.GeoDataFrame, nome_arquivo: str, subpasta: Optional[str] = None, 
                 output_dir: str = "data/output", gdf_poligono: Optional[gpd.GeoDataFrame] = None, 
                 **kwargs: Any) -> str:
    """Gera imagem estatica (PNG) do mapa de zonas."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pasta = Path(output_dir)
    if subpasta:
        pasta = pasta / subpasta
        pasta.mkdir(parents=True, exist_ok=True)
    
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

        logger.info("PNG exportado: %s", caminho)
        return str(caminho)
    except Exception as e:
        logger.error("Erro ao exportar PNG: %s", e)
        raise