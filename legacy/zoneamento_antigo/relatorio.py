"""
Precision VRT Solo — Relatório do Módulo de Zoneamento

Geração de resumos e relatórios do processo de zoneamento.
"""

import logging
from typing import Any, Dict, Optional

from .contratos import ResultadoZoneamento

logger = logging.getLogger(__name__)

__all__ = [
    "gerar_resumo",
]


def gerar_resumo(resultado: ResultadoZoneamento) -> Dict[str, Any]:
    """
    Gera um resumo textual do zoneamento.
    
    Args:
        resultado: Resultado completo do zoneamento
        
    Returns:
        Dicionário com resumo estruturado
    """
    resumo = {
        "n_zonas": len(resultado.zonas),
        "metodologia": resultado.configuracao.metodologia,
        "tempo_processamento": f"{resultado.tempo_processamento:.2f}s",
        "metricas": resultado.metricas.to_dict(),
        "zonas": [p.to_dict() for p in resultado.perfis],
    }
    
    return resumo