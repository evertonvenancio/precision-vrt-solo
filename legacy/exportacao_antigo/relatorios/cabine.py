"""
Precision VRT Solo — Geração de Cartão de Cabine

Funções para geração de cartões de cabine para implementação em tratores.
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def gerar_cartao_cabine(prescricoes: Dict[str, Any], nome_arquivo: str, 
                        subpasta: Optional[str] = None, output_dir: str = "data/output", 
                        **kwargs: Any) -> str:
    """Gera cartão de cabine em formato simplificado."""
    pasta = Path(output_dir)
    if subpasta:
        pasta = pasta / subpasta
        pasta.mkdir(parents=True, exist_ok=True)
    
    caminho = pasta / f"{nome_arquivo}_cartao_cabine.txt"
    
    try:
        texto = _formatar_cartao_cabine(prescricoes)
        
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(texto)
        logger.info("Cartão de cabine exportado: %s", caminho)
        return str(caminho)
    except Exception as e:
        logger.error("Erro ao exportar cartão de cabine: %s", e)
        raise


def _formatar_cartao_cabine(prescricoes: Dict[str, Any]) -> str:
    """Formata cartão de cabine em formato simplificado."""
    linhas = [
        "=" * 80,
        "CARTÃO DE CABINE - PRESCRIÇÃO DE TAXA VARIÁVEL",
        "=" * 80,
        "",
    ]
    
    prescricoes_por_zona = prescricoes.get("prescricoes", {})
    
    for zona_id, pres in prescricoes_por_zona.items():
        linhas.extend([
            f"ZONA {zona_id}",
            "-" * 30,
        ])
        
        # Nutrientes principais
        nutrimentos = [
            ("calagem", "Calagem"),
            ("gessagem", "Gessagem"), 
            ("nitrogenio", "Nitrogênio"),
            ("fosforo", "Fósforo"),
            ("potassio", "Potássio"),
        ]
        
        for chave, nome in nutrimentos:
            info = pres.get(chave, {})
            if chave in ("calagem", "gessagem"):
                dose = info.get("dose_t_ha", 0.0)
                unidade = "t/ha"
            else:
                dose = info.get("dose_kg_ha", 0.0)
                unidade = "kg/ha"
            status = info.get("status", "")
            
            if dose > 0:
                linhas.append(f"{nome}: {dose:.1f} {unidade} ({status})")
        
        custo = pres.get("custo_estimado_ha", 0)
        linhas.append(f"Custo total: R$ {custo:.2f}/ha")
        linhas.append("")
    
    linhas.append("=" * 80)
    linhas.append("Implementação: Aplicação com controle automático de taxa")
    linhas.append("=" * 80)
    
    return "\n".join(linhas)