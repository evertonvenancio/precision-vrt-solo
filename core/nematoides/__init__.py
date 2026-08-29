"""
Precision VRT Solo — Módulo de Nematoides do Core

Módulo independente para análise de nematoides do solo.
Implementa pipeline completo de amostragem dirigida e zoneamento de risco.

O módulo é totalmente independente e não depende de:
- prescricao_vrt
- compactacao
- fertirrigacao
- sensoriamento
- monitoramento

Dependências permitidas:
- core/tipos (tipos base do core)
- core/utilitarios (funções utilitárias)
"""

from .nematoides.motor import MotorNematoides
from .nematoides.contratos import (
    NivelRiscoNematoides,
    EspecieNematoides,
    PontoAmostraNematoides,
    ZonaRiscoNematoides,
    ResultadoNematoides,
    ConfigInterpolacaoNematoides,
    ConfigZoneamentoNematoides,
    ConfigExportacaoNematoides,
    ConfigAgronomiaNematoides
)
from .interpolacao.motor import MotorInterpolacaoNematoides
from .zoneamento.motor import MotorZoneamentoNematoides
from .exportacao.motor import MotorExportacaoNematoides
from .agronomia.motor import MotorAgronomiaNematoides, Cultura, TipoSolo, MetodoControle

__all__ = [
    # Motor principal de nematoides
    "MotorNematoides",
    
    # Contratos de dados
    "NivelRiscoNematoides",
    "EspecieNematoides", 
    "PontoAmostraNematoides",
    "ZonaRiscoNematoides",
    "ResultadoNematoides",
    "ConfigInterpolacaoNematoides",
    "ConfigZoneamentoNematoides",
    "ConfigExportacaoNematoides",
    "ConfigAgronomiaNematoides",
    
    # Módulos específicos
    "MotorInterpolacaoNematoides",
    "MotorZoneamentoNematoides",
    "MotorExportacaoNematoides",
    "MotorAgronomiaNematoides",
    
    # Enums agronômicos
    "Cultura",
    "TipoSolo", 
    "MetodoControle"
]