"""
Precision VRT Solo — Módulo de Cálculos

Cálculos de dose, limitadores e regras de prescrição.
"""

from .dose import (
    _calcular_calagem,
    _calcular_gessagem,
    _calcular_ca_necessidade,
    _calcular_mg_necessidade,
    _calcular_s_necessidade,
    _calcular_micronutrientes,
    _calcular_micronutriente_individual,
)
from .limitadores import calcular_guardrail_fosforo
from .regras import _classificar_status_micronutriente, classificar_status_nutriente

__all__ = [
    "_calcular_calagem",
    "_calcular_gessagem",
    "_calcular_ca_necessidade",
    "_calcular_mg_necessidade",
    "_calcular_s_necessidade",
    "_calcular_micronutrientes",
    "_calcular_micronutriente_individual",
    "calcular_guardrail_fosforo",
    "_classificar_status_micronutriente",
    "classificar_status_nutriente",
]