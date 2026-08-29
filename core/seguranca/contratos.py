"""
Precision VRT Solo — Contratos do Módulo de Segurança

Definições de tipos, enums e protocols que formam o contrato público do módulo.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Importar as classes base do core.tipos
from core.tipos import ConfigBase, ResultadoBase

__all__ = [
    "GuardrailConfig",
]


@dataclass
class GuardrailConfig(ConfigBase):
    """Configuração de guardrails de segurança do sistema."""
    niveis_permissao: Dict[str, Any] = field(default_factory=dict)
    regras_negocio: List[Any] = field(default_factory=list)
    limites_operacionais: Dict[str, Any] = field(default_factory=dict)
    acoes_bloqueadas: List[str] = field(default_factory=list)


@dataclass
class ResultadoSeguranca(ResultadoBase):
    """Resultado da verificação de segurança."""
    status: str = "sucesso"
    violacoes: List[str] = field(default_factory=list)
    score: float = 0.0
    mensagens: List[str] = field(default_factory=list)
    config: Optional[GuardrailConfig] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "violacoes": self.violacoes,
            "score": self.score,
            "mensagens": self.mensagens,
            "config": self.config,
            **super().to_dict(),
        }