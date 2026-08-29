"""
Precision VRT Solo — Enums e Tipos de Execução do CORE

Enums e tipos relacionados à execução de processos no CORE.
"""

from enum import Enum, auto


class StatusExecucaoEnum(Enum):
    """
    Enum global de status de execução de qualquer processo no core.
    Substitui/centraliza enums locais como StatusDoseEnum, StatusSolucaoEnum, etc.
    """
    SUCESSO = "sucesso"
    PARCIAL = "parcial"
    FALHA = "falha"
    CANCELADO = "cancelado"
    TIMEOUT = "timeout"
    NAO_INICIADO = "nao_iniciado"


class ModoExecucaoEnum(Enum):
    """Modo de execução de processos."""
    AUTOMATICO = "automatico"
    MANUAL = "manual"
    BATCH = "batch"
    INTERATIVO = "interativo"


class NivelLogEnum(Enum):
    """Nível de log padronizado."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"