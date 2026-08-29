"""
Precision VRT Solo — Exceções de Interpolação

Exceções específicas para erros de interpolação espacial.
"""

from .exceptions import InterpolacaoError


class InterpolacaoDadosError(InterpolacaoError):
    """Erros relacionados com dados de entrada."""
    pass


class InterpolacaoConfigError(InterpolacaoError):
    """Erros de configuração da interpolação."""
    pass