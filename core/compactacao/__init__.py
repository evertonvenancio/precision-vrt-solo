"""
Precision VRT Solo — Módulo de Compactação do Core

Módulo independente para análise de compactação do solo.
Implementa pipeline completo de análise de resistência à penetração.

O módulo é totalmente independente e não depende de:
- prescricao_vrt
- nematoides  
- fertirrigacao
- sensoriamento
- monitoramento

Dependências permitidas:
- core/tipos (tipos base do core)
- core/utilitarios (funções utilitárias)
"""

from .compactacao.motor import MotorCompactacao
from .compactacao.contratos import (
    ClassificacaoCompactacao,
    CamadaCompactacao,
    PerfilCompactacao,
    
    ClassificacaoSolo,
    ConfigCompactacao,
    ResultadoCompactacao
)
from .interpolacao.motor import MotorInterpolacaoCompactacao
from .zoneamento.motor import MotorZoneamentoCompactacao
from .exportacao.motor import MotorExportacaoCompactacao
from .agronomia.motor import MotorAgronomiaCompactacao

__all__ = [
    # Motor principal de compactação
    "MotorCompactacao",
    
    # Contratos de dados
    "ClassificacaoCompactacao",
    "CamadaCompactacao", 
    "PerfilCompactacao",
    
    "ClassificacaoSolo",
    "ConfigCompactacao",
    "ResultadoCompactacao",
    
    # Módulos específicos
    "MotorInterpolacaoCompactacao",
    "MotorZoneamentoCompactacao", 
    "MotorExportacaoCompactacao",
    "MotorAgronomiaCompactacao"
]