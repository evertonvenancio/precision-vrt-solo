"""
Precision VRT Solo — Geração de Laudo Técnico

Funções para geração de laudos técnicos.
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import geopandas as gpd
import pandas as pd

logger = logging.getLogger(__name__)


def gerar_relatorio_texto(prescricoes: Optional[Dict[str, Any]], 
                         perfis_zonas: Optional[Dict[str, Dict[str, Any]]], 
                         nome_talhao: str = "Talhao", **kwargs: Any) -> str:
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


def exportar_txt(gdf: gpd.GeoDataFrame, prescricoes: Optional[Dict[str, Any]], 
                 perfis_zonas: Optional[Dict[str, Dict[str, Any]]], nome_arquivo: str, 
                 subpasta: Optional[str] = None, nome_talhao: str = "Talhao", 
                 output_dir: str = "data/output", **kwargs: Any) -> str:
    """Gera relatorio em texto simples."""
    from ..configuracao import FormatoExportacao

    pasta = Path(output_dir)
    if subpasta:
        pasta = pasta / subpasta
        pasta.mkdir(parents=True, exist_ok=True)
    
    caminho = pasta / f"{nome_arquivo}_relatorio.txt"

    texto = gerar_relatorio_texto(prescricoes, perfis_zonas, nome_talhao)

    try:
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(texto)
        logger.info("Relatorio TXT exportado: %s", caminho)
        return str(caminho)
    except Exception as e:
        logger.error("Erro ao exportar TXT: %s", e)
        raise