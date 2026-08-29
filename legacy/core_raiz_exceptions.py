"""
Precision VRT Solo — Exceções do CORE

Exceções personalizadas para todo o sistema.
"""

class CoreError(Exception):
    """Exceção base do CORE."""
    pass


class CoreTypeError(CoreError):
    """Erro de tipo no CORE."""
    pass


class CoreValueError(CoreError):
    """Erro de valor no CORE."""
    pass


class CoreRuntimeError(CoreError):
    """Erro de runtime no CORE."""
    pass


class ConfiguracaoError(CoreError):
    """Erro de configuração no CORE."""
    pass