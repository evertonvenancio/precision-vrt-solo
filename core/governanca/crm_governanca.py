"""
Precision VRT Solo — Governança CRM

Implementa controle de operações CRM.
Não contém lógica de negócio.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from .fluxos_aprovacao import FluxoAprovacao, processo_aprovacao, TipoOperacao, NivelAprovacao

class TipoOperacaoCRM(Enum):
    """Tipos de operações CRM específicas."""
    CLIENTE = "cliente"
    CONTRATO = "contrato"
    VENDA = "venda"
    ORCAMENTO = "orcamento"
    TRANSFERENCIA_CLIENTE = "transferencia_cliente"
    ATENDIMENTO = "atendimento"
    PROSPECTO = "prospecto"
    COTACAO = "cotacao"
    PROPOSTA = "proposta"
    NEGOCIACAO = "negociacao"
    FECHAMENTO = "fechamento"
    RETENCAO = "retencao"
    RECLAMACAO = "reclamacao"
    SATISFACAO = "satisfacao"

class CategoriaCRM(Enum):
    """Categorias de operações CRM."""
    GESTAO_CLIENTE = "gestao_cliente"
    VENDAS = "vendas"
    ATENDIMENTO = "atendimento"
    RELACIONAMENTO = "relacionamento"
    MARKETING = "marketing"

class OperacaoCRM:
    """
    Representa uma operação CRM controlada.
    """
    
    def __init__(self,
                 id_operacao: str,
                 tipo: TipoOperacaoCRM,
                 categoria: CategoriaCRM,
                 descricao: str,
                 solicitante_id: str,
                 cliente_id: Optional[str] = None,
                contrato_id: Optional[str] = None,
                venda_id: Optional[str] = None,
                orcamento_id: Optional[str] = None,
                dados_adicionais: Optional[Dict[str, Any]] = None,
                aprovadores_necessarios: int = 1,
                restricoes: Optional[Dict[str, Any]] = None):
        self.id_operacao = id_operacao
        self.tipo = tipo
        self.categoria = categoria
        self.descricao = descricao
        self.solicitante_id = solicitante_id
        self.cliente_id = cliente_id
        self.contrato_id = contrato_id
        self.venda_id = venda_id
        self.orcamento_id = orcamento_id
        self.dados_adicionais = dados_adicionais or {}
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
                        if 'permitido' in valor_restricao and contexto[chave] not in valor_restricao['permitido']:
                            return False
                    else:
                        if contexto[chave] != valor_restricao:
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
            'descricao': self.descricao,
            'solicitante_id': self.solicitante_id,
            'cliente_id': self.cliente_id,
            'contrato_id': self.contrato_id,
            'venda_id': self.venda_id,
            'orcamento_id': self.orcamento_id,
            'dados_adicionais': self.dados_adicionais,
            'aprovadores_necessarios': self.aprovadores_necessarios,
            'aprovacoes_recebidas': len(self.aprovacoes),
            'aprovacoes_positivas': sum(1 for a in self.aprovacoes if a['aprovado']),
            'status': self.status,
            'restricoes': self.restricoes,
            'criado_em': self.criado_em,
            'historico': self.historico
        }

class AprovadorCRM:
    """
    Aprovador para operações CRM.
    """
    
    def __init__(self, usuario_id: str, nivel: str, areas_crm: List[str] = None):
        self.usuario_id = usuario_id
        self.nivel = nivel  # gerente, diretor, administrador, consultor, comercial
        self.areas_crm = areas_crm or ["vendas", "atendimento", "gestao_cliente"]
        self.operacoes_aprovadas: List[OperacaoCRM] = []
        self.operacoes_rejeitadas: List[OperacaoCRM] = []
        self.operacoes_pendentes: List[str] = []
        
    def pode_aprovar(self, operacao: OperacaoCRM) -> bool:
        """
        Verifica se aprovador pode aprovar operação.
        """
        # Verificar se área do CRM está nas áreas do aprovador
        if operacao.categoria.value not in self.areas_crm:
            return False
            
        # Verificar nível
        if self.nivel == "consultor" and operacao.tipo.value in ["contrato", "transferencia_cliente"]:
            return False
        if self.nivel == "comercial" and operacao.tipo.value == "transferencia_cliente":
            return False
        if self.nivel == "gerente" and operacao.categoria.value == "relacionamento":
            return False
        if self.nivel == "diretor" and operacao.categoria.value == "gestao_cliente":
            return False
            
        return True
        
    def aprovar_operacao(self, 
                        operacao: OperacaoCRM, 
                        justificativa: str = "",
                        dados_complementares: Optional[Dict[str, Any]] = None) -> bool:
        """
        Aprova operação CRM.
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
                         operacao: OperacaoCRM, 
                         justificativa: str = "",
                         dados_complementares: Optional[Dict[str, Any]] = None) -> bool:
        """
        Rejeita operação CRM.
        """
        sucesso = operacao.adicionar_aprovacao(
            self.usuario_id, False, justificativa, dados_complementares
        )
        
        if sucesso:
            self.operacoes_rejeitadas.append(operacao)
            if operacao.id_operacao in self.operacoes_pendentes:
                self.operacoes_pendentes.remove(operacao.id_operacao)
                
        return sucesso

class FluxoCRM:
    """
    Gerencia fluxo de aprovação para operações CRM.
    """
    
    def __init__(self):
        self.operacoes: Dict[str, OperacaoCRM] = {}
        self.aprovadores: Dict[str, AprovadorCRM] = {}
        self.mapeamento_tipo_operacao = {
            TipoOperacaoCRM.CLIENTE: TipoOperacao.LIBERAR_CLIENTES,
            TipoOperacaoCRM.CONTRATO: TipoOperacao.LIBERAR_CRM,
            TipoOperacaoCRM.VENDA: TipoOperacao.LIBERAR_VENDAS,
            TipoOperacaoCRM.ORCAMENTO: TipoOperacao.LIBERAR_CRM,
            TipoOperacaoCRM.TRANSFERENCIA_CLIENTE: TipoOperacao.LIBERAR_CLIENTES,
            TipoOperacaoCRM.ATENDIMENTO: TipoOperacao.LIBERAR_CRM,
            TipoOperacaoCRM.PROSPECTO: TipoOperacao.LIBERAR_CLIENTES,
            TipoOperacaoCRM.COTACAO: TipoOperacao.LIBERAR_CRM,
            TipoOperacaoCRM.PROPOSTA: TipoOperacao.LIBERAR_CRM,
            TipoOperacaoCRM.NEGOCIACAO: TipoOperacao.LIBERAR_CRM,
            TipoOperacaoCRM.FECHAMENTO: TipoOperacao.LIBERAR_CRM,
            TipoOperacaoCRM.RETENCAO: TipoOperacao.LIBERAR_CRM,
            TipoOperacaoCRM.RECLAMACAO: TipoOperacao.LIBERAR_CRM,
            TipoOperacaoCRM.SATISFACAO: TipoOperacao.LIBERAR_CRM
        }
        
    def criar_operacao(self, operacao: OperacaoCRM) -> str:
        """
        Cria nova operação CRM.
        """
        operacao.id_operacao = f"crm_{int(datetime.now().timestamp())}_{len(self.operacoes)}"
        self.operacoes[operacao.id_operacao] = operacao
        
        # Adicionar aos aprovadores pendentes
        for aprovador in self.aprovadores.values():
            if aprovador.pode_aprovar(operacao):
                aprovador.operacoes_pendentes.append(operacao.id_operacao)
                
        return operacao.id_operacao
        
    def obter_operacao(self, id_operacao: str) -> Optional[OperacaoCRM]:
        """
        Obtém operação pelo ID.
        """
        return self.operacoes.get(id_operacao)
        
    def adicionar_aprovador(self, aprovador: AprovadorCRM):
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
            modulo="crm",
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
fluxo_crm = FluxoCRM()

def criar_operacao_crm(tipo: TipoOperacaoCRM,
                      descricao: str,
                      solicitante_id: str,
                      cliente_id: Optional[str] = None,
                      contrato_id: Optional[str] = None,
                      venda_id: Optional[str] = None,
                      orcamento_id: Optional[str] = None,
                      dados_adicionais: Optional[Dict[str, Any]] = None,
                      aprovadores_necessarios: int = 1,
                      restricoes: Optional[Dict[str, Any]] = None) -> str:
    """
    Função utilitária para criar operação CRM.
    """
    categoria = TipoOperacaoCRM(tipo.value).categoria
    operacao = OperacaoCRM(
        id_operacao="",
        tipo=tipo,
        categoria=categoria,
        descricao=descricao,
        solicitante_id=solicitante_id,
        cliente_id=cliente_id,
        contrato_id=contrato_id,
        venda_id=venda_id,
        orcamento_id=orcamento_id,
        dados_adicionais=dados_adicionais,
        aprovadores_necessarios=aprovadores_necessarios,
        restricoes=restricoes or {}
    )
    
    return fluxo_crm.criar_operacao(operacao)