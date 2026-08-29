"""
Precision VRT Solo — Operações Críticas e Segurança Operacional

Implementa controle de operações críticas com fluxos de aprovação.
Não contém lógica de negócio.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from .hierarquia import Cargo, PerfilGovernanca
from .permissoes_granulares import RecursoSistema, OperacaoSistema, MatrizPermissoes

class CategoriaOperacao(Enum):
    """Categorias de operações críticas."""
    FINANCEIRO = "financeiro"
    CRM = "crm"
    PATRIMONIO = "patrimonio"
    CONFIGURACAO = "configuracao"
    METODOLOGIA = "metodologia"
    USUARIO = "usuario"
    DADO = "dado"
    SEGURANCA = "seguranca"

class OperacaoCritica:
    """
    Representa uma operação crítica do sistema.
    """
    
    def __init__(self,
                 id_operacao: str,
                 categoria: CategoriaOperacao,
                 recurso: RecursoSistema,
                 operacao: OperacaoSistema,
                 descricao: str,
                 nivel_risco: str = "alto",
                 aprovadores_necessarios: int = 1,
                 cliente_id: Optional[str] = None,
                 modulo: Optional[str] = None,
                 restricoes: Optional[Dict[str, Any]] = None):
        self.id_operacao = id_operacao
        self.categoria = categoria
        self.recurso = recurso
        self.operacao = operacao
        self.descricao = descricao
        self.nivel_risco = nivel_risco
        self.aprovadores_necessarios = aprovadores_necessarios
        self.cliente_id = cliente_id
        self.modulo = modulo
        self.restricoes = restricoes or {}
        self.criado_em = datetime.now()
        self.ativa = True
        
    def __str__(self):
        return f"OperacaoCritica({self.id_operacao}, {self.categoria.value}, {self.operacao.value})"

class ExecutorOperacao:
    """
    Executor de operações críticas.
    """
    
    def __init__(self, usuario_id: str, matriz_permissoes: MatrizPermissoes):
        self.usuario_id = usuario_id
        self.matriz_permissoes = matriz_permissoes
        self.operacoes_realizadas: List[Dict[str, Any]] = []
        self.operacoes_pendentes: List[str] = []
        
    def pode_iniciar_operacao(self, operacao: OperacaoCritica) -> bool:
        """
        Verifica se usuário pode iniciar operação crítica.
        """
        return self.matriz_permissoes.pode_executar(
            self.usuario_id,
            operacao.recurso,
            operacao.operacao,
            operacao.cliente_id,
            operacao.modulo,
            operacao.restricoes
        )
        
    def iniciar_operacao(self, operacao: OperacaoCritica) -> Dict[str, Any]:
        """
        Inicia operação crítica.
        """
        if not self.pode_iniciar_operacao(operacao):
            return {
                'sucesso': False,
                'motivo': 'Usuário não tem permissão para iniciar esta operação',
                'operacao': str(operacao)
            }
            
        # Registrar início da operação
        registro_operacao = {
            'id_operacao': operacao.id_operacao,
            'inicio_em': datetime.now(),
            'executor': self.usuario_id,
            'status': 'pendente',
            'aprovacoes_recebidas': 0,
            'aprovacoes_necessarias': operacao.aprovadores_necessarios,
            'categoria': operacao.categoria.value,
            'recurso': operacao.recurso.value,
            'operacao': operacao.operacao.value,
            'cliente_id': operacao.cliente_id,
            'modulo': operacao.modulo
        }
        
        self.operacoes_pendentes.append(operacao.id_operacao)
        self.operacoes_realizadas.append(registro_operacao)
        
        return {
            'sucesso': True,
            'id_operacao': operacao.id_operacao,
            'mensagem': 'Operação iniciada com sucesso',
            'registro': registro_operacao
        }
        
    def adicionar_aprovacao(self, id_operacao: str, aprovador_id: str, justificativa: str = "") -> Dict[str, Any]:
        """
        Adiciona aprovação a operação pendente.
        """
        if id_operacao not in self.operacoes_pendentes:
            return {
                'sucesso': False,
                'motivo': 'Operação não encontrada ou já concluída'
            }
            
        # Encontrar registro da operação
        registro = None
        for op_reg in self.operacoes_realizadas:
            if op_reg['id_operacao'] == id_operacao:
                registro = op_reg
                break
                
        if not registro:
            return {
                'sucesso': False,
                'motivo': 'Registro da operação não encontrado'
            }
            
        # Adicionar aprovação
        registro['aprovacoes_recebidas'] += 1
        registro['aprovacoes'].append({
            'aprovador': aprovador_id,
            'data_aprovacao': datetime.now(),
            'justificativa': justificativa
        })
        
        # Verificar se operação foi totalmente aprovada
        if registro['aprovacoes_recebidas'] >= registro['aprovacoes_necessarias']:
            registro['status'] = 'aprovada'
            registro['conclusao_em'] = datetime.now()
            self.operacoes_pendentes.remove(id_operacao)
        else:
            registro['status'] = 'aguardando_aprovacao'
            
        return {
            'sucesso': True,
            'id_operacao': id_operacao,
            'aprovacoes_recebidas': registro['aprovacoes_recebidas'],
            'aprovacoes_necessarias': registro['aprovacoes_necessarias'],
            'status': registro['status']
        }

class ValidadorOperacao:
    """
    Validador de operações críticas.
    """
    
    def __init__(self, operacoes_criticas: List[OperacaoCritica]):
        self.operacoes_criticas = {op.id_operacao: op for op in operacoes_criticas}
        
    def validar_operacao(self, operacao_id: str, contexto: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Valida se operação pode ser executada.
        """
        if operacao_id not in self.operacoes_criticas:
            return {
                'valida': False,
                'motivo': 'Operação crítica não encontrada',
                'operacao_id': operacao_id
            }
            
        operacao = self.operacoes_criticas[operacao_id]
        
        # Validar contexto se fornecido
        if contexto and operacao.restricoes:
            for chave, valor_restricao in operacao.restricoes.items():
                if chave in contexto:
                    if isinstance(valor_restricao, dict):
                        if 'max' in valor_restricao and contexto[chave] > valor_restricao['max']:
                            return {
                                'valida': False,
                                'motivo': f'Valor excede máximo permitido para {chave}: {contexto[chave]} > {valor_restricao["max"]}',
                                'operacao_id': operacao_id,
                                'campo': chave,
                                'valor': contexto[chave],
                                'maximo': valor_restricao['max']
                            }
                    elif contexto[chave] != valor_restricao:
                        return {
                            'valida': False,
                            'motivo': f'Valor não corresponde ao esperado para {chave}: esperado {valor_restricao}, encontrado {contexto[chave]}',
                            'operacao_id': operacao_id,
                            'campo': chave,
                            'esperado': valor_restricao,
                            'encontrado': contexto[chave]
                        }
                        
        return {
            'valida': True,
            'operacao_id': operacao_id,
            'operacao': str(operacao),
            'contexto_valido': True
        }

# Instâncias globais
operacoes_criticas: List[OperacaoCritica] = []
validador_operacao = ValidadorOperacao(operacoes_criticas)

def adicionar_operacao_critica(operacao: OperacaoCritica):
    """
    Adiciona operação crítica ao sistema.
    """
    operacoes_criticas.append(operacao)
    validador_operacao.operacoes_criticas[operacao.id_operacao] = operacao

def configurar_operacoes_criticas_padrao():
    """
    Configura operações críticas padrão do sistema.
    """
    # Operações Financeiras
    operacoes_financeiras = [
        OperacaoCritica(
            "financeiro_desconto",
            CategoriaOperacao.FINANCEIRO,
            RecursoSistema.FINANCEIRO,
            OperacaoSistema.LIBERAR_DESCONTOS,
            "Liberação de descontos",
            nivel_risco="alto",
            aprovadores_necessarios=2,
            restricoes={"valor_maximo": 1000}
        ),
        OperacaoCritica(
            "financeiro_venda",
            CategoriaOperacao.FINANCEIRO,
            RecursoSistema.FINANCEIRO,
            OperacaoSistema.LIBERAR_VENDAS,
            "Liberação de vendas",
            nivel_risco="alto",
            aprovadores_necessarios=1
        ),
        OperacaoCritica(
            "financeiro_cancelamento",
            CategoriaOperacao.FINANCEIRO,
            RecursoSistema.FINANCEIRO,
            OperacaoSistema.APROVAR,
            "Cancelamento financeiro",
            nivel_risco="alto",
            aprovadores_necessarios=2
        ),
        OperacaoCritica(
            "financeiro_recebimento",
            CategoriaOperacao.FINANCEIRO,
            RecursoSistema.FINANCEIRO,
            OperacaoSistema.APROVAR,
            "Recebimento financeiro",
            nivel_risco="medio",
            aprovadores_necessarios=1
        ),
        OperacaoCritica(
            "financeiro_pagamento",
            CategoriaOperacao.FINANCEIRO,
            RecursoSistema.FINANCEIRO,
            OperacaoSistema.APROVAR,
            "Pagamento financeiro",
            nivel_risco="alto",
            aprovadores_necessarios=2
        )
    ]
    
    # Operações CRM
    operacoes_crm = [
        OperacaoCritica(
            "crm_cliente",
            CategoriaOperacao.CRM,
            RecursoSistema.CRM,
            OperacaoSistema.LIBERAR_CLIENTES,
            "Liberação de clientes",
            nivel_risco="medio",
            aprovadores_necessarios=1
        ),
        OperacaoCritica(
            "crm_venda",
            CategoriaOperacao.CRM,
            RecursoSistema.CRM,
            OperacaoSistema.LIBERAR_VENDAS,
            "Liberação de vendas",
            nivel_risco="alto",
            aprovadores_necessarios=2
        ),
        OperacaoCritica(
            "crm_orcamento",
            CategoriaOperacao.CRM,
            RecursoSistema.CRM,
            OperacaoSistema.APROVAR,
            "Aprovação de orçamento",
            nivel_risco="medio",
            aprovadores_necessarios=1
        ),
        OperacaoCritica(
            "crm_contrato",
            CategoriaOperacao.CRM,
            RecursoSistema.CRM,
            OperacaoSistema.APROVAR,
            "Aprovação de contrato",
            nivel_risco="alto",
            aprovadores_necessarios=2
        )
    ]
    
    # Operações de Patrimônio
    operacoes_patrimonio = [
        OperacaoCritica(
            "patrimonio_aquisicao",
            CategoriaOperacao.PATRIMONIO,
            RecursoSistema.PATRIMONIO,
            OperacaoSistema.APROVAR,
            "Aquisição patrimonial",
            nivel_risco="alto",
            aprovadores_necessarios=2
        ),
        OperacaoCritica(
            "patrimonio_baixa",
            CategoriaOperacao.PATRIMONIO,
            RecursoSistema.PATRIMONIO,
            OperacaoSistema.EXCLUIR,
            "Baixa patrimonial",
            nivel_risco="alto",
            aprovadores_necessarios=2
        ),
        OperacaoCritica(
            "patrimonio_manutencao",
            CategoriaOperacao.PATRIMONIO,
            RecursoSistema.PATRIMONIO,
            OperacaoSistema.EDITAR,
            "Manutenção patrimonial",
            nivel_risco="medio",
            aprovadores_necessarios=1
        )
    ]
    
    # Adicionar todas as operações
    for operacao in operacoes_financeiras + operacoes_crm + operacoes_patrimonio:
        adicionar_operacao_critica(operacao)

# Configurar operações críticas padrão
configurar_operacoes_criticas_padrao()