"""
Precision VRT Solo — Configuração do Módulo de Prescrição

Constantes agronômicas, tabelas de referência e configuração do motor.
Todas as configurações estáticas e parâmetros configuráveis centralizados aqui.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


__all__ = [
    "EFICIENCIA_FERTILIZANTES",
    "CONVERSAO_COMERCIAL",
    "PRECO_REFERENCIA",
    "LIMITES_MICRO",
    "EXPORTACAO_NUTRIENTES",
    "PARAMETROS_CALAGEM",
    "PARAMETROS_GESSAGEM",
    "PARAMETROS_MACRO",
    "TEORES_CRITICOS",
    "GUARDRAIL_P_MAX_PADRAO",
    "ConfigPrescricao",
]


# =============================================================================
# CONSTANTES E PARAMETROS AGRONOMICOS CENTRALIZADOS
# =============================================================================



# ---------------------------------------------------------------------------
# Limites criticos de micronutrientes (mg/dm3) — fonte: IAC / Embrapa
# ---------------------------------------------------------------------------
LIMITES_MICRO = {
    "B": {"baixo": 0.20, "adequado": 0.50, "alto": 1.00},
    "Cu": {"baixo": 0.30, "adequado": 0.80, "alto": 3.00},
    "Fe": {"baixo": 10.0, "adequado": 20.0, "alto": 100.0},
    "Mn": {"baixo": 2.00, "adequado": 5.00, "alto": 50.0},
    "Zn": {"baixo": 0.50, "adequado": 1.50, "alto": 5.00},
}



# ---------------------------------------------------------------------------
# Parametros de calagem por metodologia
# Fonte: IAC BT-100; CFSEMG; Embrapa
# ---------------------------------------------------------------------------
PARAMETROS_CALAGEM = {
    "IAC_Graos": {
        "meta_v_percent": 70.0,
        "fator_prnt": 0.67,
        "fator_profundidade_cm": 20.0,
        "fator_dg": 1.0,
        "formula": "SMP",
        "ph_minimo": 5.5,
        "ph_alvo": 6.0,
        "v_minimo": 50.0,
    },
    "CFSEMG": {
        "meta_v_percent": 60.0,
        "fator_prnt": 0.67,
        "fator_profundidade_cm": 20.0,
        "fator_dg": 1.0,
        "formula": "SMP",
        "ph_minimo": 5.5,
        "ph_alvo": 6.0,
        "v_minimo": 50.0,
    },
    "Embrapa_Soja": {
        "meta_v_percent": 65.0,
        "fator_prnt": 0.67,
        "fator_profundidade_cm": 20.0,
        "fator_dg": 1.0,
        "formula": "SMP",
        "ph_minimo": 5.5,
        "ph_alvo": 6.0,
        "v_minimo": 50.0,
    },
    "Embrapa_Milho": {
        "meta_v_percent": 70.0,
        "fator_prnt": 0.67,
        "fator_profundidade_cm": 20.0,
        "fator_dg": 1.0,
        "formula": "SMP",
        "ph_minimo": 5.5,
        "ph_alvo": 6.0,
        "v_minimo": 50.0,
    },
}

# ---------------------------------------------------------------------------
# Parametros de gessagem por metodologia
# Fonte: Embrapa; IAC
# ---------------------------------------------------------------------------
PARAMETROS_GESSAGEM = {
    "IAC_Graos": {
        "argila_minima_percent": 30.0,
        "fator_dose": 0.5,
        "dose_maxima_t_ha": 3.0,
        "dose_minima_t_ha": 0.5,
    },
    "CFSEMG": {
        "argila_minima_percent": 30.0,
        "fator_dose": 0.5,
        "dose_maxima_t_ha": 3.0,
        "dose_minima_t_ha": 0.5,
    },
    "Embrapa_Soja": {
        "argila_minima_percent": 30.0,
        "fator_dose": 0.5,
        "dose_maxima_t_ha": 3.0,
        "dose_minima_t_ha": 0.5,
    },
    "Embrapa_Milho": {
        "argila_minima_percent": 30.0,
        "fator_dose": 0.5,
        "dose_maxima_t_ha": 3.0,
        "dose_minima_t_ha": 0.5,
    },
}

# ---------------------------------------------------------------------------
# Parametros de macronutrientes por metodologia
# ---------------------------------------------------------------------------
PARAMETROS_MACRO = {
    "IAC_Graos": {
        "N": {"fator_classe_textural": {"arenoso": 1.2, "medio": 1.0, "argiloso": 0.9}},
        "P": {"fator_mehlich": 1.0, "fator_resina": 1.2},
        "K": {"fator_ctc": 1.0},
    },
    "CFSEMG": {
        "N": {"fator_classe_textural": {"arenoso": 1.2, "medio": 1.0, "argiloso": 0.9}},
        "P": {"fator_mehlich": 1.0, "fator_resina": 1.2},
        "K": {"fator_ctc": 1.0},
    },
    "Embrapa_Soja": {
        "N": {"fator_classe_textural": {"arenoso": 1.2, "medio": 1.0, "argiloso": 0.9}},
        "P": {"fator_mehlich": 1.0, "fator_resina": 1.2},
        "K": {"fator_ctc": 1.0},
    },
    "Embrapa_Milho": {
        "N": {"fator_classe_textural": {"arenoso": 1.2, "medio": 1.0, "argiloso": 0.9}},
        "P": {"fator_mehlich": 1.0, "fator_resina": 1.2},
        "K": {"fator_ctc": 1.0},
    },
}

# ---------------------------------------------------------------------------
# Teores criticos de macronutrientes (classificacao de status)
# Fonte: IAC BT-100; CFSEMG
# ---------------------------------------------------------------------------
TEORES_CRITICOS = {
    "N": {"muito_baixo": 0, "baixo": 30, "medio": 60, "alto": 100},
    "P": {"muito_baixo": 0, "baixo": 10, "medio": 20, "alto": 40},
    "K": {"muito_baixo": 0, "baixo": 30, "medio": 60, "alto": 100},
    "Ca": {"muito_baixo": 0, "baixo": 1.5, "medio": 3.0, "alto": 5.0},
    "Mg": {"muito_baixo": 0, "baixo": 0.5, "medio": 1.0, "alto": 2.0},
    "S": {"muito_baixo": 0, "baixo": 5, "medio": 10, "alto": 20},
}

# ---------------------------------------------------------------------------
# Guardrail ambiental
# ---------------------------------------------------------------------------
GUARDRAIL_P_MAX_PADRAO = 40.0   # mg/dm3 — CONAMA 357/2005


# =============================================================================
# DATACLASS DE CONFIGURACAO
# =============================================================================

@dataclass
class ConfigPrescricao:
    """Configuração completa do motor de prescrição."""
    cultura: str = "soja"
    produtividade: float = 3.0
    teor_argila: float = 20.0
    metodo_id: str = "IAC_Graos"
    safra: Optional[str] = None
    safras: List[str] = field(default_factory=list)
    mapas_auxiliares: Dict[str, Any] = field(default_factory=dict)
    preco_cal: float = PRECO_REFERENCIA["cal"]
    preco_gesso: float = PRECO_REFERENCIA["gesso"]
    preco_n: float = PRECO_REFERENCIA["N"]
    preco_p2o5: float = PRECO_REFERENCIA["P2O5"]
    preco_k2o: float = PRECO_REFERENCIA["K2O"]
    preco_ca: float = PRECO_REFERENCIA["Ca"]
    preco_mg: float = PRECO_REFERENCIA["Mg"]
    preco_s: float = PRECO_REFERENCIA["S"]
    preco_micro: float = PRECO_REFERENCIA["micro"]
    preco_fe: float = PRECO_REFERENCIA["Fe"]
    preco_mn: float = PRECO_REFERENCIA["Mn"]
    guardrail_p_max: float = GUARDRAIL_P_MAX_PADRAO
    eficiencia_n: float = EFICIENCIA_FERTILIZANTES["N"]["eficiencia_percent"]
    eficiencia_p2o5: float = EFICIENCIA_FERTILIZANTES["P2O5"]["eficiencia_percent"]
    eficiencia_k2o: float = EFICIENCIA_FERTILIZANTES["K2O"]["eficiencia_percent"]
    eficiencia_ca: float = EFICIENCIA_FERTILIZANTES["Ca"]["eficiencia_percent"]
    eficiencia_mg: float = EFICIENCIA_FERTILIZANTES["Mg"]["eficiencia_percent"]
    eficiencia_s: float = EFICIENCIA_FERTILIZANTES["S"]["eficiencia_percent"]
    prnt_percent: float = 67.0
    profundidade_incorporacao_cm: float = 20.0

    def to_dict(self) -> Dict[str, Any]:
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
            "profundidade_incorporacao_cm": self.profundidade_incorporacao_cm,
        }
