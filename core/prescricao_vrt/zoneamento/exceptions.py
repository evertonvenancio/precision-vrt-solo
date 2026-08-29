"""
Precision VRT Solo — Exceções do Módulo de Zoneamento

Exceções customizadas hierárquicas para o sistema de zoneamento.
"""

from typing import Any


class ZoneamentoError(Exception):
    """Exceção base para todas as exceções do módulo zoneamento."""
    pass


class ValidacaoError(ZoneamentoError):
    """Exceção gerada durante validação de dados ou configurações."""
    pass


class AlgoritmoError(ZoneamentoError):
    """Exceção gerada durante execução de algoritmos de clustering."""
    pass


class ConfiguracaoError(ZoneamentoError):
    """Exceção gerada em erros de configuração do sistema."""
    pass


class DadosInsuficientesError(ValidacaoError):
    """Exceção gerada quando dados são insuficientes para a operação solicitada."""
    pass