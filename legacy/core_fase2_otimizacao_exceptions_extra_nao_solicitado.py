"""
Precision VRT Solo — Exceções de Otimização

Exceções específicas para erros de otimização.
"""

from ..exceptions import OtimizacaoError


class BlendagemError(OtimizacaoError):
    """Erros específicos de blendagem."""
    pass


class RestricaoError(OtimizacaoError):
    """Erros de restrições."""
    pass