"""
Configurações dos limites agronômicos para análise de janela de aplicação.
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class LimitesUreia:
    """Limites agronômicos para aplicação de Ureia."""
    precipitacao_max_mm: float = 20.0
    """Chuva máxima acumulada em 24h antes da aplicação (mm). Acima disso há
    risco de volatilização do nitrogênio."""
    precipitacao_prevista_max_mm: float = 15.0
    """Chuva máxima prevista nas próximas 24h após a aplicação (mm)."""
    temperatura_max_c: float = 35.0
    """Temperatura máxima tolerada durante a aplicação (°C)."""
    umidade_relativa_min_pct: float = 40.0
    """Umidade relativa mínima do ar (%). Abaixo disso aumenta volatilização."""


@dataclass
class LimitesAplicacaoFoliar:
    """Limites agronômicos para pulverização foliar."""
    velocidade_vento_max_kmh: float = 10.0
    """Velocidade máxima do vento para pulverização (km/h). Acima disso há
    deriva excessiva de calda."""
    temperatura_max_c: float = 30.0
    """Temperatura máxima para aplicação foliar (°C)."""
    temperatura_min_c: float = 10.0
    """Temperatura mínima para aplicação foliar (°C)."""
    umidade_relativa_min_pct: float = 55.0
    """Umidade relativa mínima do ar (%). Abaixo disso calda evapora antes de
    agir."""
    precipitacao_prevista_max_mm: float = 5.0
    """Chuva máxima prevista nas próximas 4h após a aplicação (mm)."""


@dataclass
class LimitesHerbicida:
    """Limites agronômicos para aplicação de herbicidas."""
    velocidade_vento_max_kmh: float = 15.0
    temperatura_max_c: float = 35.0
    temperatura_min_c: float = 5.0
    umidade_relativa_min_pct: float = 40.0
    precipitacao_prevista_max_mm: float = 10.0


@dataclass
class ConfiguracaoClima:
    """
    Configuração central de limites agronômicos para análise de janela de
    aplicação.

    Altere os valores padrão aqui ou sobrescreva por instância para ajustar
    os limiares sem modificar a lógica de negócio.
    """
    ureia: LimitesUreia = field(default_factory=LimitesUreia)
    foliar: LimitesAplicacaoFoliar = field(default_factory=LimitesAplicacaoFoliar)
    herbicida: LimitesHerbicida = field(default_factory=LimitesHerbicida)

    cache_ttl_segundos: int = 3600
    """Tempo de vida do cache de previsão em segundos (padrão: 1 hora)."""

    historico_dias: int = 7
    """Número de dias de histórico climático para auditoria."""

    previsao_dias: int = 5
    """Número de dias de previsão a buscar."""

    TIPOS_APLICACAO_VALIDOS: Dict[str, str] = field(default_factory=lambda: {
        "ureia": "Ureia (nitrogênio)",
        "foliar": "Aplicação foliar",
        "herbicida": "Herbicida",
    })


clima_config = ConfiguracaoClima()
