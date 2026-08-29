"""
Precision VRT Solo — Limitadores e Guardrails Ambientais

Implementa limitadores ambientais e restrições de aplicação.
"""
from typing import Dict, Any

def calcular_guardrail_fosforo(
    p_mg: float,
    guardrail_p_max: float,
    config: Dict[str, Any]
) -> Dict[str, bool]:
    """
    Calcula guardrail de P conforme CONAMA 357/2005.
    
    Args:
        p_mg: Teor de P no solo (mg/dm3).
        guardrail_p_max: Limite máximo para aplicação.
        config: Configuração do motor.
    
    Returns:
        Dict com 'bloqueado' e 'alerta' se aplicável.
    """
    p_bloqueado = False
    p_alerta = None
    
    # GUARDRAIL: P > 40 mg/dm3 bloqueia aplicacao de P2O5
    if p_mg > guardrail_p_max:
        p_bloqueado = True
        p_alerta = (
            "ALERTA AMBIENTAL: Teor de P muito alto (%.1f mg/dm3). "
            "Aplicacao de P2O5 bloqueada por risco de eutrofizacao (CONAMA 357/2005)."
        ) % p_mg
    
    return {
        "bloqueado": p_bloqueado,
        "alerta": p_alerta
    }