"""
Precision VRT Solo — Configuração de Execução do Módulo de Prescrição

APENAS parâmetros de runtime e constantes científicas/regulatórias universais.
Dados de domínio (culturas, metodologias, fertilizantes) foram movidos para config/.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Constantes científicas/regulatórias universais
GUARDRAIL_P_MAX_PADRAO = 40.0   # mg/dm3 — CONAMA 357/2005

# Limites críticos de micronutrientes (mg/dm3) — universal (IAC/Embrapa)
LIMITES_MICRO = {
    "B": {"baixo": 0.20, "adequado": 0.50, "alto": 1.00},
    "Cu": {"baixo": 0.30, "adequado": 0.80, "alto": 3.00},
    "Fe": {"baixo": 10.0, "adequado": 20.0, "alto": 100.0},
    "Mn": {"baixo": 2.00, "adequado": 5.00, "alto": 50.0},
    "Zn": {"baixo": 0.50, "adequado": 1.50, "alto": 5.00},
}

# =============================================================================#
# DATACLASS DE CONFIGURAÇÃO                                                   #
# =============================================================================#

@dataclass
class ConfigPrescricao:
    """Configuração de execução do motor de prescrição."""
    
    # Parâmetros de entrada (dados de domínio vindos do caller)
    cultura: str = "soja"
    produtividade: float = 3.0
    teor_argila: float = 20.0
    metodo_id: str = "IAC_Graos"
    safra: Optional[str] = None
    safras: List[str] = field(default_factory=list)
    mapas_auxiliares: Dict[str, Any] = field(default_factory=dict)
    
    # Preços (podem ser sobrescritos pelo caller, padrão universal)
    preco_cal: float = 150.0      # R$/t
    preco_gesso: float = 200.0    # R$/t
    preco_n: float = 8.0          # R$/kg N
    preco_p2o5: float = 6.0       # R$/kg P2O5
    preco_k2o: float = 5.0        # R$/kg K2O
    preco_ca: float = 3.0         # R$/kg Ca
    preco_mg: float = 4.0         # R$/kg Mg
    preco_s: float = 5.0          # R$/kg S
    preco_micro: float = 50.0     # R$/kg micronutriente
    preco_fe: float = 30.0        # R$/kg Fe
    preco_mn: float = 30.0        # R$/kg Mn
    
    # Eficiências (podem ser sobrescritas pelo caller, padrão universal)
    eficiencia_n: float = 0.6
    eficiencia_p2o5: float = 0.2
    eficiencia_k2o: float = 0.5
    eficiencia_ca: float = 0.8
    eficiencia_mg: float = 0.8
    eficiencia_s: float = 0.7
    
    # Calagem
    prnt_percent: float = 67.0
    
    # Guardrail
    guardrail_p_max: float = GUARDRAIL_P_MAX_PADRAO
    
    def to_dict(self) -> Dict[str, Any]:
        """Exporta configuração como dicionário para serialização."""
        return {
            "cultura": self.cultura,
            "produtividade": self.produtividade,
            "teor_argila": self.teor_argila,
            "metodo_id": self.metodo_id,
            "safra": self.safra,
            "safras": self.safras,
            "mapas_auxiliares": list(self.mapas_auxiliares.keys()),
            "guardrail_p_max": self.guardrail_p_max,
            "eficiencias": {
                "N": self.eficiencia_n,
                "P2O5": self.eficiencia_p2o5,
                "K2O": self.eficiencia_k2o,
                "Ca": self.eficiencia_ca,
                "Mg": self.eficiencia_mg,
                "S": self.eficiencia_s,
            },
            "prnt_percent": self.prnt_percent,
        }