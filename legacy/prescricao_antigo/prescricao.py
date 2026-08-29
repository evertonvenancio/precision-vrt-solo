"""
Precision VRT Solo — Stub de compatibilidade para core/prescricao.py

Este arquivo redireciona todas as importacoes para o novo pacote modular
em core/prescricao/, garantindo retrocompatibilidade total.

Para migrar completamente, substitua:
    from core.prescricao import MotorPrescricao
por:
    from core.prescricao.motor import MotorPrescricao
"""

from core.prescricao.configuracao import ConfigPrescricao
from core.prescricao.motor import MotorPrescricao
from core.prescricao.contratos import (
    NotasTecnicas,
    PrescricaoZona,
    ResumoPrescricao,
    ResultadoCorretivo,
    ResultadoNutriente,
    StatusNutriente,
    TipoCorretivo,
)
from core.prescricao.validacao import (
    calcular_custo_nutriente,
    calcular_dose_corrigida,
    calcular_exportacao,
    classificar_status_nutriente,
    get_parametros_metodo,
)

__all__ = [
    "MotorPrescricao",
    "ConfigPrescricao",
    "ResultadoNutriente",
    "ResultadoCorretivo",
    "PrescricaoZona",
    "ResumoPrescricao",
    "NotasTecnicas",
    "StatusNutriente",
    "TipoCorretivo",
    "calcular_exportacao",
    "get_parametros_metodo",
    "classificar_status_nutriente",
    "calcular_dose_corrigida",
    "calcular_custo_nutriente",
]
