"""
Precision VRT Solo — Módulo de Fertirrigação do Core

Módulo independente para gestão de fertirrigação e nutrição de culturas.
Implementa pipeline completo de análise de soluções e recomendação de fertilizantes.

O módulo é totalmente independente e não depende de:
- prescricao_vrt
- compactacao
- nematoides
- sensoriamento
- monitoramento

Dependências permitidas:
- core/tipos (tipos base do core)
- core/utilitarios (funções utilitárias)
- core/otimizacao (motor de otimização de misturas)
"""

from .fertirrigacao.motor import MotorFertirrigacao
from .fertirrigacao.contratos import (
    ConfigAreaFertirrigacao,
    ConfigAnaliseSolucao,
    ConfigNutricao,
    ConfigRecomendacao,
    ConfigExportacaoFertirrigacao,
    ConfigAgronomiaFertirrigacao,
    Cultura,
    SistemaIrrigacao,
    MetodoAnalise,
    TipoFertilizante,
    ModoRecomendacao,
    LeituraSolucao,
    AreaFertirrigacao,
    PrescricaoNutricional,
    ResultadoAnaliseSolucao,
    ResultadoNutricao,
    ResultadoRecomendacao,
    ResultadoFertirrigacao
)
from .interpolacao.motor import MotorInterpolacaoFertirrigacao
from .zoneamento.motor import MotorZoneamentoFertirrigacao
from .exportacao.motor import MotorExportacaoFertirrigacao
from .agronomia.motor import MotorAgronomiaFertirrigacao

__all__ = [
    # Motor principal de fertirrigação
    "MotorFertirrigacao",
    
    # Contratos de dados
    "ConfigAreaFertirrigacao",
    "ConfigAnaliseSolucao",
    "ConfigNutricao",
    "ConfigRecomendacao",
    "ConfigExportacaoFertirrigacao",
    "ConfigAgronomiaFertirrigacao",
    "Cultura",
    "SistemaIrrigacao",
    "MetodoAnalise",
    "TipoFertilizante",
    "ModoRecomendacao",
    "LeituraSolucao",
    "AreaFertirrigacao",
    "PrescricaoNutricional",
    "ResultadoAnaliseSolucao",
    "ResultadoNutricao",
    "ResultadoRecomendacao",
    "ResultadoFertirrigacao",
    
    # Módulos específicos
    "MotorInterpolacaoFertirrigacao",
    "MotorZoneamentoFertirrigacao",
    "MotorExportacaoFertirrigacao",
    "MotorAgronomiaFertirrigacao"
]