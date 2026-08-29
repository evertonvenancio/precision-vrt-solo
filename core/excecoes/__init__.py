"""
Precision VRT Solo — Módulo de Exceções Globais

Exceções específicas para validação, metodologia e autorização.
Não contém lógica de negócio.
"""

# Importar todas as exceções para facilitar o uso
from .erros_validacao import *
from .erros_metodologia import *
from .erros_autorizacao import *

__all__ = [
    # Erros de Validação
    'ErroValidacao',
    'ErroArquivoVazio',
    'ErroArquivoCorrompido', 
    'ErroCampoObrigatorioAusente',
    'ErroColunaObrigatoriaAusente',
    'ErroDuplicidadeCampos',
    'ErroTiposIncompativeis',
    'ErroCoordenadasInvalidas',
    'ErroUnidadeInvalida',
    'ErroUnidadeNaoSuportada',
    'ErroSemUnidadeExplicita',
    
    # Erros de Metodologia
    'ErroMetodologia',
    'ErroMetodologiaNaoEncontrada',
    'ErroMetodologiaInvalida',
    'ErroMetodologiaPadrao',
    'ErroMetodologiaExcepcional',
    'ErroStatusMetodologiaInvalido',
    
    # Erros de Autorização
    'ErroAutorizacao',
    'ErroRequisicaoAutorizacaoInvalida',
    'ErroAutorizacaoInsuficiente',
    'ErroOperacaoNaoAutorizada',
    'ErroAlteracaoPadraoSemAutorizacao'
]