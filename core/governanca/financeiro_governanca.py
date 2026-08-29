"""
Precision VRT Solo — Governança Financeira

Implementa controle de aprovações para operações financeiras.
Não contém lógica de negócio.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from .fluxos_aprovacao import FluxoAprovacao, processo_aprovacao, TipoOperacao, NivelAprovacao

class CategoriaFinanceira(Enum):
    """Categorias de operações financeiras."""
    DESCONTO = "desconto"
    VENDA = "venda"
    CANCELAMENTO = "cancelamento"
    RECEBIMENTO = "recebimento"
    PAGAMENTO = "pagamento"
    COMISSAO = "comissao"
    BONIFICACAO = "bonificacao"
    SALARIO = "salario"
    PRO_LABORE = "pro_labore"
    PATRIMONIO = "patrimonio"

class TipoOperacaoFinanceira(Enum):
    """Tipos de operações financeiras específicas."""
    LIBERAR_DESCONTO = "liberar_desconto"
    LIBERAR_VENDA = "liberar_venda"
    CANCELAR_VENDA = "cancelar_venda"
    REGISTRAR_RECEBIMENTO = "registrar_recebimento"
    REGISTRAR_PAGAMENTO = "registrar_pagamento"
    LIBERAR_COMISSAO = "liberar_comissao"
    LIBERAR_BONIFICACAO = "liberar_bonificacao"
    LIBERAR_SALARIO = "liberar_salario"
    LIBERAR_PRO_LABORE = "liberar_pro_labore"
    AQUISICAO_PATRIMONIO = "aquisicao_patrimonio"
    BAIXA_PATRIMONIO = "baixa_patrimonio"
    MANUTENCAO_PATRIMONIO = "manutencao_patrimonio"

class OperacaoFinanceira:
    """
    Representa uma operação financeira controlada.
    """
    
    def __init__(self,
                 id_operacao: str,
                 tipo: TipoOperacaoFinanceira,
                 categoria: CategoriaFinanceira,
                 valor: float,
                 descricao: str,
                 solicitante_id: str,
                 cliente_id: Optional[str] = None,
                 aprovadores_necessarios: int = 1,
                 restricoes: Optional[Dict[str, Any]] = None):
        self.id_operacao = id_operacao
        self.tipo = tipo
        self.categoria = categoria
        self.valor = valor
        self.descricao = descricao
        self.solicitante_id = solicitante_id
        self.cliente_id = cliente_id
        self.aprovadores_necessarios = aprovadores_necessarios
        self.restricoes = restricoes or {}
        self.criado_em = datetime.now()
        self.status = "pendente"
        self.aprovacoes: List[Dict[str, Any]] = []
        self.historico: List[Dict[str, Any]] = []
        
    def pode_ser_aprovada(self, usuario_id: str, contexto: Optional[Dict[str, Any]] = None) -> bool:
        """
        Verifica se operação pode ser aprovada pelo usuário.
        """
        # Verificar se usuário não já aprovou
        if any(aprovacao.get('aprovador_id') == usuario_id for aprovacao in self.aprovacoes):
            return False
            
        # Verificar restrições se contexto fornecido
        if contexto:
            for chave, valor_restricao in self.restricoes.items():
                if chave in contexto:
                    if isinstance(valor_restricao, dict):
                        if 'max' in valor_restricao and contexto[chave] > valor_restricao['max']:
                            return False
                        if 'min' in valor_restricao and contexto[chave] < valor_restricao['min']:
                            return False
                            
        return True
        
    def adicionar_aprovacao(self, 
                           aprovador_id: str, 
                           aprovado: bool, 
                           justificativa: str = "",
                           dados_complementares: Optional[Dict[str, Any]] = None) -> bool:
        """
        Adiciona aprovação à operação.
        """
        aprovacao = {
            'aprovador_id': aprovador_id,
            'data_aprovacao': datetime.now(),
            'aprovado': aprovado,
            'justificativa': justificativa,
            'dados_complementares': dados_complementares or {}
        }
        
        self.aprovacoes.append(aprovacao)
        
        # Atualizar status
        aprovacoes_positivas = sum(1 for a in self.aprovacoes if a['aprovado'])
        if aprovacoes_positivas >= self.aprovadores_necessarios:
            self.status = "aprovada"
        elif any(not a['aprovado'] for a in self.aprovacoes):
            self.status = "rejeitada"
        else:
            self.status = "em_aprovacao"
            
        # Adicionar ao histórico
        self.historico.append({
            'evento': 'aprovacao' if aprovado else 'rejeicao',
            'timestamp': datetime.now(),
            'usuario': aprovador_id,
            'justificativa': justificativa,
            'dados_complementares': dados_complementares or {}
        })
        
        return True
        
    def obter_status_completo(self) -> Dict[str, Any]:
        """
        Obtém status completo da operação.
        """
        return {
            'id_operacao': self.id_operacao,
            'tipo': self.tipo.value,
            'categoria': self.categoria.value,
            'valor': self.valor,
            'descricao': self.descricao,
            'solicitante_id': self.solicitante_id,
            'cliente_id': self.cliente_id,
            'aprovadores_necessarios': self.aprovadores_necessarios,
            'aprovacoes_recebidas': len(self.aprovacoes),
            'aprovacoes_positivas': sum(1 for a in self.aprovacoes if a['aprovado']),
            'status': self.status,
            'restricoes': self.restricoes,
            'criado_em': self.criado_em,
            'historico': self.historico
        }

class AprovadorFinanceiro:
    """
    Aprovador para operações financeiras.
    """
    
    def __init__(self, usuario_id: str, nivel: str, limite_valor: float = 0.0):
        self.usuario_id = usuario_id
        self.nivel = nivel  # gerente, diretor, administrador
        self.limite_valor = limite_valor
        self.operacoes_aprovadas: List[OperacaoFinanceira] = []
        self.operacoes_rejeitadas: List[OperacaoFinanceira] = []
        self.operacoes_pendentes: List[str] = []
        
    def pode_aprovar(self, operacao: OperacaoFinanceira) -> bool:
        """
        Verifica se aprovador pode aprovar operação.
        """
        # Verificar nível
        if self.nivel == "gerente" and operacao.valor > 10000:
            return False
        if self.nivel == "diretor" and operacao.valor > 50000:
            return False
        if self.nivel == "administrador" and operacao.valor > 100000:
            return False
            
        # Verificar limite pessoal
        if self.limite_valor > 0 and operacao.valor > self.limite_valor:
            return False
            
        return True
        
    def aprovar_operacao(self, 
                        operacao: OperacaoFinanceira, 
                        justificativa: str = "",
                        dados_complementares: Optional[Dict[str, Any]] = None) -> bool:
        """
        Aprova operação financeira.
        """
        if not self.pode_aprovar(operacao):
            return False
            
        sucesso = operacao.adicionar_aprovacao(
            self.usuario_id, True, justificativa, dados_complementares
        )
        
        if sucesso:
            self.operacoes_aprovadas.append(operacao)
            if operacao.id_operacao in self.operacoes_pendentes:
                self.operacoes_pendentes.remove(operacao.id_operacao)
                
        return sucesso
        
    def rejeitar_operacao(self, 
                         operacao: OperacaoFinanceira, 
                         justificativa: str = "",
                         dados_complementares: Optional[Dict[str, Any]] = None) -> bool:
        """
        Rejeita operação financeira.
        """
        sucesso = operacao.adicionar_aprovacao(
            self.usuario_id, False, justificativa, dados_complementares
        )
        
        if sucesso:
            self.operacoes_rejeitadas.append(operacao)
            if operacao.id_operacao in self.operacoes_pendentes:
                self.operacoes_pendentes.remove(operacao.id_operacao)
                
        return sucesso

class FluxoFinanceiro:
    """
    Gerencia fluxo de aprovação para operações financeiras.
    """
    
    def __init__(self):
        self.operacoes: Dict[str, OperacaoFinanceira] = {}
        self.aprovadores: Dict[str, AprovadorFinanceiro] = {}
        fluxos_tipo_operacao = {
            TipoOperacaoFinanceira.LIBERAR_DESCONTO: TipoOperacao.LIBERAR_DESCONTOS,
            TipoOperacaoFinanceira.LIBERAR_VENDA: TipoOperacao.LIBERAR_VENDAS,
            TipoOperacaoFinanceira.CANCELAR_VENDA: TipoOperacao.LIBERAR_VENDAS,
            TipoOperacaoFinanceira.REGISTRAR_RECEBIMENTO: TipoOperacao.LIBERAR_VENDAS,
            TipoOperacaoFinanceira.REGISTRAR_PAGAMENTO: TipoOperacao.LIBERAR_VENDAS,
            TipoOperacaoFinanceira.LIBERAR_COMISSAO: TipoOperacao.LIBERAR_VENDAS,
            TipoOperacaoFinanceira.LIBERAR_BONIFICACAO: TipoOperacao.LIBERAR_VENDAS,
            TipoOperacaoFinanceira.LIBERAR_SALARIO: TipoOperacao.LIBERAR_VENDAS,
            TipoOperacaoFinanceira.LIBERAR_PRO_LABORE: TipoOperacao.LIBERAR_VENDAS,
            TipoOperacaoFinanceira.AQUISICAO_PATRIMONIO: TipoOperacao.LIBERAR_VENDAS,
            TipoOperacaoFinanceira.BAIXA_PATRIMONIO: TipoOperacao.LIBERAR_PATRIMONIO,
            TipoOperacaoFinanceira.MANUTENCAO_PATRIMONIO: TipoOperacao.LIBERAR_PATRIMONIO
        }
        
        self.mapeamento_tipo_operacao = fluxos_tipo_operacao
        
    def criar_operacao(self, operacao: OperacaoFinanceira) -> str:
        """
        Cria nova operação financeira.
        """
        operacao.id_operacao = f"financeiro_{int(datetime.now().timestamp())}_{len(self.operacoes)}"
        self.operacoes[operacao.id_operacao] = operacao
        
        # Adicionar aos aprovadores pendentes
        for aprovador in self.aprovadores.values():
            if aprovador.pode_aprovar(operacao):
                aprovador.operacoes_pendentes.append(operacao.id_operacao)
                
        return operacao.id_operacao
        
    def obter_operacao(self, id_operacao: str) -> Optional[OperacaoFinanceira]:
        """
        Obtém operação pelo ID.
        """
        return self.operacoes.get(id_operacao)
        
    def adicionar_aprovador(self, aprovador: AprovadorFinanceiro):
        """
        Adiciona aprovador ao sistema.
        """
        self.aprovadores[aprovador.usuario_id] = aprovador
        
    def obter_fluxo_aprovacao(self, id_operacao: str) -> Optional[FluxoAprovacao]:
        """
        Obtém fluxo de aprovação correspondente.
        """
        operacao = self.obter_operacao(id_operacao)
        if not operacao:
            return None
            
        # Mapear tipo de operação
        tipo_fluxo = self.mapeamento_tipo_operacao.get(operacao.tipo)
        if not tipo_fluxo:
            return None
            
        fluxo = FluxoAprovacao(
            id_fluxo=operacao.id_operacao,
            tipo_operacao=tipo_fluxo,
            solicitante_id=operacao.solicitante_id,
            operacao_descricao=operacao.descricao,
            nivel_aprovacao=NivelAprovacao.GERENTE,
            clientes_envolvidos=[operacao.cliente_id] if operacao.cliente_id else None,
            modulo="financeiro",
            aprovadores_necessarios=operacao.aprovadores_necessarios
        )
        
        # Adicionar aprovações existentes
        for aprovacao in operacao.aprovacoes:
            fluxo.adicionar_aprovacao(
                aprovacao['aprovador_id'], 
                aprovacao['aprovado'], 
                aprovacao['justificativa']
            )
            
        return fluxo
        
    def liberar_operacao(self, id_operacao: str) -> bool:
        """
        Libera operação após aprovação final.
        """
        operacao = self.obter_operacao(id_operacao)
        if not operacao or operacao.status != "aprovada":
            return False
            
        # Registrar operação como liberada
        operacao.historico.append({
            'evento': 'liberacao',
            'timestamp': datetime.now(),
            'status': 'liberada'
        })
        
        return True

# Instância global
fluxo_financeiro = FluxoFinanceiro()

def criar_operacao_financeira(tipo: TipoOperacaoFinanceira,
                              valor: float,
                              descricao: str,
                              solicitante_id: str,
                              cliente_id: Optional[str] = None,
                              aprovadores_necessarios: int = 1,
                              restricoes: Optional[Dict[str, Any]] = None) -> str:
    """
    Função utilitária para criar operação financeira.
    """
    operacao = OperacaoFinanceira(
        id_operacao="",
        tipo=tipo,
        categoria=TipoOperacaoFinanceira(tipo.value).categoria,
        valor=valor,
        descricao=descricao,
        solicitante_id=solicitante_id,
        cliente_id=cliente_id,
        aprovadores_necessarios=aprovadores_necessarios,
        restricoes=restricoes or {}
    )
    
    return fluxo_financeiro.criar_operacao(operacao)