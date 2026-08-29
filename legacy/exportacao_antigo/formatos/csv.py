"""
Precision VRT Solo — Exportação de Dados em CSV

Funções para exportação de dados em formato CSV.
"""
import logging
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional

import geopandas as gpd

from ..configuracao import FormatoExportacao

logger = logging.getLogger(__name__)


def exportar_csv(gdf: gpd.GeoDataFrame, nome_arquivo: str, subpasta: Optional[str] = None, 
                 output_dir: str = "data/output", **kwargs: Any) -> str:
    """Exporta GeoDataFrame para CSV."""
    pasta = Path(output_dir)
    if subpasta:
        pasta = pasta / subpasta
        pasta.mkdir(parents=True, exist_ok=True)
    
    caminho = pasta / f"{nome_arquivo}.csv"
    
    try:
        df = pd.DataFrame(gdf.drop(columns="geometry"))
        df.to_csv(caminho, index=False, sep=";")
        logger.info("CSV exportado: %s", caminho)
        return str(caminho)
    except Exception as e:
        logger.error("Erro ao exportar CSV: %s", e)
        raise


def exportar_csv_prescricao(prescricoes: Dict[str, Any], nome_arquivo: str, 
                          subpasta: Optional[str] = None, 
                          area_ha_por_zona: Optional[Dict[str, float]] = None,
                          output_dir: str = "data/output") -> str:
    """Exporta tabela de prescricao em CSV."""
    pasta = Path(output_dir)
    if subpasta:
        pasta = pasta / subpasta
        pasta.mkdir(parents=True, exist_ok=True)
    
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