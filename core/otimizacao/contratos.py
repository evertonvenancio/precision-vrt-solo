"""
Precision VRT Solo — Contratos do Módulo de Otimização

Definições de tipos, enums e protocols que formam o contrato público do módulo.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Importar as classes base do core.tipos
from core.tipos import ConfigBase, ResultadoBase

__all__ = [
    "ProblemaOtimizacao",
]


@dataclass
class ProblemaOtimizacao(ConfigBase):
    """Problema de otimização para blendagem de fertilizantes."""
    objetivo: str = ""
    restricoes: Dict[str, Any] = field(default_factory=dict)
    variaveis: List[Any] = field(default_factory=list)
    funcao_objetivo: str = ""


@dataclass
class ResultadoOtimizacao(ResultadoBase):
    """Resultado da otimização."""
    blend: Optional[Dict[str, Any]] = None
    custo_total: float = 0.0
    restricoes_violadas: List[str] = field(default_factory=list)
    status: str = "sucesso"
    mensagens: List[str] = field(default_factory=list)
    config: Optional[ProblemaOtimizacao] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "blend": self.blend,
            "custo_total": self.custo_total,
            "restricoes_violadas": self.restricoes_violadas,
            "status": self.status,
            "mensagens": self.mensagens,
            "config": self.config,
            **super().to_dict(),
        }