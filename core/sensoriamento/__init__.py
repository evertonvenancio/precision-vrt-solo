"""
Precision VRT Solo — Módulo de Sensoriamento Remoto do Core

Módulo independente para processamento de imagens de satélites e drones.
Implementa pipeline completo de recebimento, processamento e análise de imagens.
"""

from .processamento.motor import MotorProcessamentoSensoriamento
from .imagens.motor import MotorGerenciamentoImagens
from .satelites.motor import MotorSelecaoSatelites
from .indices.motor import MotorCalculoIndices
from .exportacao.motor import MotorExportacaoSensoriamento
from .agronomia.motor import MotorAgronomiaSensoriamento

__all__ = [
    'MotorProcessamentoSensoriamento',
    'MotorGerenciamentoImagens', 
    'MotorSelecaoSatelites',
    'MotorCalculoIndices',
    'MotorExportacaoSensoriamento',
    'MotorAgronomiaSensoriamento'
]