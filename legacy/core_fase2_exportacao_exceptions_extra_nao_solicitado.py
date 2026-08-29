"""
Precision VRT Solo — Exceções de Exportação

Exceções específicas para erros de exportação.
"""

from .exceptions import ExportacaoError


class ExportacaoFormatoError(ExportacaoError):
    """Erros de formato de exportação."""
    pass


class ExportacaoDadosError(ExportacaoError):
    """Erros de dados para exportação."""
    pass