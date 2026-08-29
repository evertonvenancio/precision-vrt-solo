"""
Precision VRT Solo — Submódulo de Alertas

Implementa sistema de alertas para monitoramento.
Prepara arquitetura para futuramente identificar possíveis deficiências,
pragas, doenças, falhas e estresses.
"""

from .motor import (
    TipoAlerta,
    SeveridadeAlerta, 
    CanalNotificacao,
    AlertaConfigurado,
    AlertaDisparado,
    ConfiguradorAlertas,
    DisparadorAlertas,
    GerenciadorAlertas
)

__all__ = [
    'TipoAlerta',
    'SeveridadeAlerta',
    'CanalNotificacao', 
    'AlertaConfigurado',
    'AlertaDisparado',
    'ConfiguradorAlertas',
    'DisparadorAlertas', 
    'GerenciadorAlertas'
]