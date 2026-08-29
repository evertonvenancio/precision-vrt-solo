"""
Precision VRT Solo — Módulo de Governança Corporativa

Governança, permissões granulares, autorizações, aprovações e segurança operacional.
Infraestrutura reutilizável por todo o sistema.
"""

from .hierarquia import *
from .permissoes_granulares import *
from .operacoes_criticas import *
from .fluxos_aprovacao import *
from .clientes_responsabilidade import *
from .financeiro_governanca import *
from .crm_governanca import *
from .patrimonio_governanca import *
from .reutilizacao import *

__all__ = [
    # Hierarquia
    'Cargo', 'Hierarquia', 'PerfilGovernanca', 'CargoSistema',
    
    # Permissões Granulares
    'PermissaoGranular', 'MatrizPermissoes', 'RecursoSistema', 'OperacaoSistema',
    
    # Operações Críticas
    'OperacaoCritica', 'ExecutorOperacao', 'ValidadorOperacao',
    
    # Fluxos de Aprovação
    'FluxoAprovacao', 'NivelAprovacao', 'ProcessoAprovacao',
    
    # Clientes e Responsabilidade
    'Cliente', 'ResponsavelCliente', 'ClienteGovernanca',
    
    # Financeiro
    'OperacaoFinanceira', 'AprovadorFinanceiro', 'FluxoFinanceiro',
    
    # CRM
    'OperacaoCRM', 'AprovadorCRM', 'FluxoCRM',
    
    # Patrimônio
    'OperacaoPatrimonio', 'AprovadorPatrimonio', 'FluxoPatrimonio',
    
    # Reutilização
    'IntegradorGovernanca', 'integrador_governanca'
]