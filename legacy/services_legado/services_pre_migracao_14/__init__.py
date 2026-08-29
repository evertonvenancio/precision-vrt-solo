"""
Precision VRT Solo — Camada de Services

Camada de serviços responsável apenas por orquestrar os módulos do Core.
Nenhuma lógica de negócio permanece aqui - tudo é delegado ao Core.
"""

# Serviços principais
from .prescricao_vrt_service import PrescricaoVrtService
from .compactacao_service import CompactacaoService
from .nematoides_service import NematoidesService
from .fertirrigacao_service import FertirrigacaoService
from .sensoriamento_service import SensoriamentoService
from .monitoramento_service import MonitoramentoService
from .exportacao_service import ExportacaoService
from .validacao_service import ValidacaoService

__all__ = [
    # Serviços principais
    'PrescricaoVrtService',
    'CompactacaoService',
    'NematoidesService',
    'FertirrigacaoService',
    'SensoriamentoService',
    'MonitoramentoService',
    'ExportacaoService',
    'ValidacaoService'
]