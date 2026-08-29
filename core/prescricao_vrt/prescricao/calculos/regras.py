"""
Precision VRT Solo — Regras de Classificação e Validação

Implementa regras para classificação de status de nutrientes e micronutrientes.
"""

from ..configuracao import LIMITES_MICRO
from ..contratos import StatusNutriente


def _classificar_status_micronutriente(
    valor_mg: float, 
    nutriente: str
) -> str:
    """
    Classifica o status de um micronutriente com base no teor no solo.
    
    Args:
        valor_mg: Teor do micronutriente (mg/dm3).
        nutriente: Codigo do nutriente.
    
    Returns:
        Status descritivo.
    """
    limites = LIMITES_MICRO.get(nutriente, LIMITES_MICRO["B"])
    
    if valor_mg < limites["baixo"]:
        return StatusNutriente.MUITO_BAIXO.value
    elif valor_mg < limites["adequado"]:
        return StatusNutriente.BAIXO.value
    elif valor_mg < limites["alto"]:
        return StatusNutriente.ADEQUADO.value
    else:
        return StatusNutriente.ALTO.value


def classificar_status_nutriente(
    dose: float,
    nutriente: str
) -> str:
    """
    Classifica o status de um nutriente baseado na dose calculada.
    
    Args:
        dose: Dose calculada (kg/ha).
        nutriente: Codigo do nutriente.
    
    Returns:
        Status descritivo.
    """
    # Esta função é chamada do módulo validacao.py, não do motor original
    # Deixando aqui como stub caso exista no futuro
    return "ADEQUADO"