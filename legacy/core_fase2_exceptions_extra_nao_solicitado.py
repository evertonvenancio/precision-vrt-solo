"""
Precision VRT Solo — Exceções do CORE

Exceções personalizadas para erros específicos do módulo.
"""

class CoreError(Exception):
    """Base de todas as exceções do CORE."""
    pass


class ZoneamentoError(CoreError):
    """Erros específicos do módulo de zoneamento."""
    pass


class ValidacaoError(CoreError):
    """Erros de validação de dados."""
    pass


class AlgoritmoError(CoreError):
    """Erros em algoritmos de processamento."""
    pass


class ConfiguracaoError(CoreError):
    """Erros de configuração."""
    pass


class DadosInsuficientesError(CoreError):
    """Dados insuficientes para processamento."""
    pass


class InterpolacaoError(CoreError):
    """Erros de interpolação."""
    pass


class ExportacaoError(CoreError):
    """Erros de exportação."""
    pass


class PrescricaoError(CoreError):
    """Erros de prescrição."""
    pass


class OtimizacaoError(CoreError):
    """Erros de otimização."""
    pass


class BlendagemError(OtimizacaoError):
    """Erros específicos de blendagem."""
    pass


class RestricaoError(OtimizacaoError):
    """Erros de restrições."""
    pass


class SegurancaError(CoreError):
    """Erros de segurança."""
    pass


class PermissaoError(SegurancaError):
    """Erros de permissão."""
    pass


class AuditoriaError(SegurancaError):
    """Erros de auditoria."""
    pass