"""
Precision VRT Solo — Módulo de Segurança Global

Responsável por autorização, auditoria, rastreabilidade e permissões.
Não contém lógica de negócio.
"""

from .autorizacao import *
from .auditoria import *
from .rastreabilidade import GerenciadorRastreabilidade, HistoricoAlteracao, ItemRastreavel
from .permissoes import *

__all__ = [
    # Autorização
    'Autorizador', 'FluxoAutorizacao', 'RequisicaoAutorizacao',
    'RequisicaoAlteracaoPadrao', 'GerenciadorAutorizacao',
    
    # Auditoria
    'AuditoriaRegistro', 'AuditorSistema', 'RegistroAuditoria',
    'TipoAcao', 'ModuloSistema',
    
    # Rastreabilidade
    'GerenciadorRastreabilidade', 'HistoricoAlteracao', 'ItemRastreavel',
    
    # Permissões
    'Permissao', 'PerfilUsuario', 'RecursoSistema',
    'GerenciadorPermissoes', 'PermissoesPadrao'
]