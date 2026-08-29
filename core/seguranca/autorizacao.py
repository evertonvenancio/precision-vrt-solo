"""
Precision VRT Solo — Autorização Global

Responsável pelo fluxo de autorização de operações críticas.
Não contém lógica de negócio.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from abc import ABC, abstractmethod

class RequisicaoAutorizacao:
    """
    Representa uma requisição de autorização.
    Apenas dados, não lógica.
    """
    
    def __init__(self,
                 acao: str,
                 modulo: str,
                 usuario: str,
                 recursos: Optional[List[str]] = None,
                 justificativa: Optional[str] = None,
                 dados: Optional[Dict[str, Any]] = None):
        self.acao = acao
        self.modulo = modulo
        self.usuario = usuario
        self.recursos = recursos or []
        self.justificativa = justificativa
        self.dados = dados or {}
        self.data_solicitacao = datetime.now()
        self.status = 'pendente'
        self.autorizador = None
        self.data_autorizacao = None
        justificativa_autorizacao = None
        
    def __str__(self):
        return f"RequisicaoAutorizacao({self.acao}, {self.modulo}, {self.usuario}, {self.status})"

class FluxoAutorizacao:
    """
    Gerencia fluxo de autorização.
    Não contém lógica de negócio.
    """
    
    def __init__(self):
        self.requisicoes: Dict[str, RequisicaoAutorizacao] = {}
        self.historico: List[Dict[str, Any]] = []
        
    def criar_requisicao(self, requisicao: RequisicaoAutorizacao) -> str:
        """
        Cria requisição de autorização.
        Não valida, apenas cria.
        """
        id_requisicao = f"auth_{int(datetime.now().timestamp())}"
        requisicao.id = id_requisicao
        self.requisicoes[id_requisicao] = requisicao
        return id_requisicao
        
    def obter_requisicao(self, id_requisicao: str) -> Optional[RequisicaoAutorizacao]:
        """
        Obtém requisição pelo ID.
        """
        return self.requisicoes.get(id_requisicao)
        
    def listar_requisicoes(self, status: Optional[str] = None) -> List[RequisicaoAutorizacao]:
        """
        Lista requisições por status.
        """
        requisicoes = list(self.requisicoes.values())
        
        if status:
            requisicoes = [r for r in requisicoes if r.status == status]
            
        return requisicoes
        
    def atualizar_status(self, id_requisicao: str, status: str, autorizador: Optional[str] = None) -> bool:
        """
        Atualiza status da requisição.
        """
        requisicao = self.requisicoes.get(id_requisicao)
        if not requisicao:
            return False
            
        requisicao.status = status
        requisicao.data_autorizacao = datetime.now()
        requisicao.autorizador = autorizador
        
        # Registrar no histórico
        self.historico.append({
            'id_requisicao': id_requisicao,
            'status_anterior': getattr(requisicao, 'status_anterior', 'pendente'),
            'novo_status': status,
            'data': datetime.now(),
            'autorizador': autorizador
        })
        
        requisicao.status_anterior = status
        return True

class RequisicaoAlteracaoPadrao(RequisicaoAutorizacao):
    """
    Requisição específica para alteração de padrões.
    Apenas dados, não lógica.
    """
    
    def __init__(self,
                 modulo: str,
                 usuario: str,
                 padrao_anterior: Dict[str, Any],
                 padrao_novo: Dict[str, Any],
                 justificativa: Optional[str] = None):
        super().__init__(
            acao='alterar_padrao',
            modulo=modulo,
            usuario=usuario,
            justificativa=justificativa,
            dados={
                'padrao_anterior': padrao_anterior,
                'padrao_novo': padrao_novo
            }
        )
        self.padrao_anterior = padrao_anterior
        self.padrao_novo = padrao_novo

class Autorizador(ABC):
    """
    Classe abstrata para autorizadores.
    """
    
    @abstractmethod
    def pode_autorizar(self, requisicao: RequisicaoAutorizacao) -> bool:
        """
        Verifica se pode autorizar.
        """
        pass
        
    @abstractmethod
    def autorizar(self, requisicao: RequisicaoAutorizacao, justificativa: str) -> bool:
        """
        Autoriza requisição.
        """
        pass

class GerenciadorAutorizacao:
    """
    Gerencia o fluxo de autorização.
    Não contém lógica de negócio.
    """
    
    def __init__(self):
        self.fluxo = FluxoAutorizacao()
        self.autorizadores: List[Autorizador] = []
        
    def adicionar_autorizador(self, autorizador: Autorizador):
        """
        Adiciona autorizador.
        """
        self.autorizadores.append(autorizador)
        
    def solicitar_autorizacao(self, requisicao: RequisicaoAutorizacao) -> str:
        """
        Solicita autorização.
        Não valida, apenas solicita.
        """
        return self.fluxo.criar_requisicao(requisicao)
        
    def processar_autorizacao(self, id_requisicao: str, resposta: str, justificativa: str, autorizador: str) -> bool:
        """
        Processa resposta de autorização.
        Apenas infraestrutura.
        """
        # Obter requisição
        requisicao = self.fluxo.obter_requisicao(id_requisicao)
        if not requisicao:
            return False
            
        # Prepara estrutura para processamento
        estrutura_processamento = {
            'id_requisicao': id_requisicao,
            'requisicao': requisicao,
            'resposta': resposta,
            'justificativa': justificativa,
            'autorizador': autorizador,
            'status': 'pendente'
        }
        
        # Atualiza status da requisição
        status_final = 'aprovado' if resposta.lower() == 'aprovar' else 'rejeitado'
        return self.fluxo.atualizar_status(id_requisicao, status_final, autorizador)

# Instância global
gerenciador_autorizacao = GerenciadorAutorizacao()

# Funções utilitárias
def solicitar_autorizacao_padrao(modulo: str,
                                 usuario: str,
                                 padrao_anterior: Dict[str, Any],
                                 padrao_novo: Dict[str, Any],
                                 justificativa: Optional[str] = None) -> str:
    """
    Solicita autorização para alteração de padrão.
    """
    requisicao = RequisicaoAlteracaoPadrao(
        modulo=modulo,
        usuario=usuario,
        padrao_anterior=padrao_anterior,
        padrao_novo=padrao_novo,
        justificativa=justificativa
    )
    
    return gerenciador_autorizacao.solicitar_autorizacao(requisicao)

def obter_requisicao_autorizacao(id_requisicao: str) -> Optional[RequisicaoAutorizacao]:
    """
    Obtém requisição de autorização.
    """
    return gerenciador_autorizacao.fluxo.obter_requisicao(id_requisicao)