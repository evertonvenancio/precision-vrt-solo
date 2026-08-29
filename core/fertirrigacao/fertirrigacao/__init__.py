"""
Precision VRT Solo — Módulo de Fertirrigação do Core

Módulo principal com lógica de negócio para fertirrigação.
Implementa pipeline completo de amostragem dirigida e recomendação nutricional.
"""

from .motor import MotorFertirrigacao
from .contratos import (
    Cultura, SistemaIrrigacao, MetodoAnalise, TipoFertilizante, ModoRecomendacao,
    ConfigAreaFertirrigacao, ConfigAnaliseSolucao, ConfigNutricao, ConfigRecomendacao,
    ConfigExportacaoFertirrigacao, ConfigAgronomiaFertirrigacao,
    LeituraSolucao, AreaFertirrigacao, PrescricaoNutricional,
    ResultadoAnaliseSolucao, ResultadoNutricao, ResultadoRecomendacao, ResultadoFertirrigacao
)

__all__ = [
    # Classes principais
    'MotorFertirrigacao',
    
    # Enums
    'Cultura', 'SistemaIrrigacao', 'MetodoAnalise', 'TipoFertilizante', 'ModoRecomendacao',
    
    # Configurações
    'ConfigAreaFertirrigacao', 'ConfigAnaliseSolucao', 'ConfigNutricao', 'ConfigRecomendacao',
    'ConfigExportacaoFertirrigacao', 'ConfigAgronomiaFertirrigacao',
    
    # Modelos de dados
    'LeituraSolucao', 'AreaFertirrigacao', 'PrescricaoNutricional',
    'ResultadoAnaliseSolucao', 'ResultadoNutricao', 'ResultadoRecomendacao', 'ResultadoFertirrigacao'
]