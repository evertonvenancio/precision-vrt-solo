"""
Precision VRT Solo — Módulo de Segurança

Biblioteca científica pura para segurança do sistema.

Este módulo fornece permissões, guardrails e auditoria.
Não conhece zoneamento, prescrição, banco de dados, API ou interface gráfica.
"""

# Imports principais
from .contratos import GuardrailConfig, ResultadoSeguranca
from .exceptions import SegurancaError, PermissaoError, AuditoriaError
from .configuracao import GuardrailConfig, DEFAULT_CONFIG
from .permissions import VerificadorPermissao, Permissao
from .guardrails import Guardrails
from .auditoria import Auditoria
from .validacao import (
    validar_permissoes,
    validar_guardrails,
    validar_auditoria
)

# Export público
__all__ = [
    # Classes principais
    "GuardrailConfig",
    "ResultadoSeguranca",
    "VerificadorPermissao",
    "Permissao",
    "Guardrails",
    "Auditoria",
    
    # Exceções
    "SegurancaError",
    "PermissaoError",
    "AuditoriaError",
    
    # Configurações
    "DEFAULT_CONFIG",
    
    # Validações
    "validar_permissoes",
    "validar_guardrails",
    "validar_auditoria"
]