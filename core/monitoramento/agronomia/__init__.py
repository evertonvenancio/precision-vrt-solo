"""
Precision VRT Solo — Submódulo de Agronomia

Implementa funcionalidades de agronomia específicas para monitoramento.
Baseado em código extraído de core_agronomia_monitoramento_legado.py.

Este módulo NÃO realiza recomendações, apenas estrutura para futuras
implementações de diagnóstico agronômico.
"""

from .motor import (
    TipoSolo,
    Cultura,
    FaseFenologica,
    ConfigAgronomia,
    IndicadorAgronomico,
    AnaliseAgronomica,
    AnalisadorAgronomico,
    HistoricoAgronomico,
    MonitoramentoAgronomico
)

__all__ = [
    'TipoSolo',
    'Cultura',
    'FaseFenologica',
    'ConfigAgronomia',
    'IndicadorAgronomico',
    'AnaliseAgronomica',
    'AnalisadorAgronomico',
    'HistoricoAgronomico',
    'MonitoramentoAgronomico'
]