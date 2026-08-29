"""
Precision VRT Solo — Erros de Autorização

Exceções específicas para falhas na autorização de operações.
Não contém lógica de negócio.
"""

from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod

class ErroAutorizacao(Exception, ABC):
    """
    Classe base para erros de autorização.
    """
    
    def __init__(self, mensagem: str, detalhes: Optional[Dict[str, Any]] = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.detalhes = detalhes or {}
        
    def __str__(self):
        return f"ErroAutorizacao: {self.mensagem}"
        
    def obter_detalhes(self) -> Dict[str, Any]:
        """
        Retorna detalhes do erro.
        """
        return self.detalhes.copy()

class ErroRequisicaoAutorizacaoInvalida(ErroAutorizacao):
    """
    Erro quando requisição de autorização é inválida.
    """
    
    def __init__(self, motivo: str, requisicao_detalhes: Optional[Dict[str, Any]] = None):
        mensagem = f"Requisição de autorização inválida: {motivo}"
        
        detalhes = {
            'motivo': motivo,
            'tipo': 'requisicao_autorizacao_invalida'
        }
        if requisicao_detalhes:
            detalhes['requisicao'] = requisicao_detalhes
            
        super().__init__(mensagem, detalhes)

class ErroAutorizacaoInsuficiente(ErroAutorizacao):
    """
    Erro quando autorização é insuficiente para a operação.
    """
    
    def __init__(self, usuario: str, acao: str, recursos: List[str]):
        mensagem = f"Autorização insuficiente: usuário '{usuario}' não pode realizar ação '{acao}' nos recursos {recursos}"
        
        detalhes = {
            'usuario': usuario,
            'acao': acao,
            'recursos': recursos,
            'tipo': 'autorizacao_insuficiente'
        }
        
        super().__init__(mensagem, detalhes)

class ErroOperacaoNaoAutorizada(ErroAutorizacao):
    """
    Erro quando operação não é autorizada.
    """
    
    def __init__(self, operacao: str, modulo: str, usuario: str, motivo: Optional[str] = None):
        mensagem = f"Operação não autorizada: '{operacao}' no módulo '{modulo}' pelo usuário '{usuario}'"
        if motivo:
            mensagem += f" - {motivo}"
            
        detalhes = {
            'operacao': operacao,
            'modulo': modulo,
            'usuario': usuario,
            'tipo': 'operacao_nao_autorizada'
        }
        if motivo:
            detalhes['motivo'] = motivo
            
        super().__init__(mensagem, detalhes)

class ErroAlteracaoPadraoSemAutorizacao(ErroAutorizacao):
    """
    Erro quando alteração de padrão é tentada sem autorização.
    """
    
    def __init__(self, padrao: str, usuario: str):
        mensagem = f"Alteração de padrão não autorizada: '{padrao}' pelo usuário '{usuario}'. Fluxo de autorização obrigatório."
        
        detalhes = {
            'padrao': padrao,
            'usuario': usuario,
            'tipo': 'alteracao_padrao_sem_autorizacao'
        }
        
        super().__init__(mensagem, detalhes)

class ErroAutorizadorInexistente(ErroAutorizacao):
    """
    Erro quando autorizador não existe.
    """
    
    def __init__(self, identificador: str):
        mensagem = f"Autorizador não encontrado: {identificador}"
        
        detalhes = {
            'identificador': identificador,
            'tipo': 'autorizador_inexistente'
        }
        
        super().__init__(mensagem, detalhes)

class ErroAutorizadorSemAutoridade(ErroAutorizacao):
    """
    Erro quando autorizador não tem autoridade para a operação.
    """
    
    def __init__(self, identificador: str, operacao: str, modulo: str):
        mensagem = f"Autorizador '{identificador}' não tem autoridade para '{operacao}' no módulo '{modulo}'"
        
        detalhes = {
            'identificador': identificador,
            'operacao': operacao,
            'modulo': modulo,
            'tipo': 'autorizador_sem_autoridade'
        }
        
        super().__init__(mensagem, detalhes)

class ErroRequisicaoAutorizacaoExpirada(ErroAutorizacao):
    """
    Erro quando requisição de autorização expirou.
    """
    
    def __init__(self, id_requisicao: str, tempo_limite: int):
        mensagem = f"Requisição de autorização expirada: {id_requisicao} (limite de {tempo_limite} segundos)"
        
        detalhes = {
            'id_requisicao': id_requisicao,
            'tempo_limite': tempo_limite,
            'tipo': 'requisicao_autorizacao_expirada'
        }
        
        super().__init__(mensagem, detalhes)

class ErroRequisicaoAutorizacaoJaProcessada(ErroAutorizacao):
    """
    Erro quando requisição de autorização já foi processada.
    """
    
    def __init__(self, id_requisicao: str, status_atual: str):
        mensagem = f"Requisição de autorização já processada: {id_requisicao} (status: {status_atual})"
        
        detalhes = {
            'id_requisicao': id_requisicao,
            'status_atual': status_atual,
            'tipo': 'requisicao_autorizacao_ja_processada'
        }
        
        super().__init__(mensagem, detalhes)

class ErroPermissaoInexistente(ErroAutorizacao):
    """
    Erro quando permissão não existe no perfil do usuário.
    """
    
    def __init__(self, perfil: str, recurso: str, acao: str, modulo: Optional[str] = None):
        modulo_str = f" no módulo '{modulo}'" if modulo else ""
        mensagem = f"Permissão inexistente no perfil '{perfil}': recurso '{recurso}', ação '{acao}'{modulo_str}"
        
        detalhes = {
            'perfil': perfil,
            'recurso': recurso,
            'acao': acao,
            'modulo': modulo,
            'tipo': 'permissao_inexistente'
        }
        
        super().__init__(mensagem, detalhes)

class ErroFluxoAutorizacaoInterrompido(ErroAutorizacao):
    """
    Erro quando fluxo de autorização é interrompido por falhas.
    """
    
    def __init__(self, motivo: str, etapa: Optional[str] = None):
        mensagem = f"Fluxo de autorização interrompido: {motivo}"
        if etapa:
            mensagem += f" (etapa: {etapa})"
            
        detalhes = {
            'motivo': motivo,
            'etapa': etapa,
            'tipo': 'fluxo_autorizacao_interrompido'
        }
        
        super().__init__(mensagem, detalhes)

# Validador global para lançamento de erros de autorização
class LancadorErrosAutorizacao:
    """
    Utilitário para lançar erros de autorização consistentes.
    """
    
    @staticmethod
    def requisicao_autorizacao_invalida(motivo: str, requisicao_detalhes: Optional[Dict[str, Any]] = None):
        """Lança erro de requisição de autorização inválida."""
        raise ErroRequisicaoAutorizacaoInvalida(motivo, requisicao_detalhes)
        
    @staticmethod
    def autorizacao_insuficiente(usuario: str, acao: str, recursos: List[str]):
        """Lança erro de autorização insuficiente."""
        raise ErroAutorizacaoInsuficiente(usuario, acao, recursos)
        
    @staticmethod
    def operacao_nao_autorizada(operacao: str, modulo: str, usuario: str, motivo: Optional[str] = None):
        """Lança erro de operação não autorizada."""
        raise ErroOperacaoNaoAutorizada(operacao, modulo, usuario, motivo)
        
    @staticmethod
    def alteracao_padrao_sem_autorizacao(padrao: str, usuario: str):
        """Lança erro de alteração de padrão sem autorização."""
        raise ErroAlteracaoPadraoSemAutorizacao(padrao, usuario)
        
    @staticmethod
    def autorizador_inexistente(identificador: str):
        """Lança erro de autorizador inexistente."""
        raise ErroAutorizadorInexistente(identificador)
        
    @staticmethod
    def autorizador_sem_autoridade(identificador: str, operacao: str, modulo: str):
        """Lança erro de autorizador sem autoridade."""
        raise ErroAutorizadorSemAutoridade(identificador, operacao, modulo)
        
    @staticmethod
    def requisicao_autorizacao_expirada(id_requisicao: str, tempo_limite: int):
        """Lança erro de requisição de autorização expirada."""
        raise ErroRequisicaoAutorizacaoExpirada(id_requisicao, tempo_limite)
        
    @staticmethod
    def requisicao_autorizacao_ja_processada(id_requisicao: str, status_atual: str):
        """Lança erro de requisição de autorização já processada."""
        raise ErroRequisicaoAutorizacaoJaProcessada(id_requisicao, status_atual)
        
    @staticmethod
    def permissao_inexistente(perfil: str, recurso: str, acao: str, modulo: Optional[str] = None):
        """Lança erro de permissão inexistente."""
        raise ErroPermissaoInexistente(perfil, recurso, acao, modulo)
        
    @staticmethod
    def fluxo_autorizacao_interrompido(motivo: str, etapa: Optional[str] = None):
        """Lança erro de fluxo de autorização interrompido."""
        raise ErroFluxoAutorizacaoInterrompido(motivo, etapa)

# Instância global
lancador_erros_autorizacao = LancadorErrosAutorizacao()

# Funções utilitárias
def validar_autorizacao_e_lancar_erro(valido: bool, erro_class, *args, **kwargs):
    """
    Valida condição de autorização e lança erro se falhar.
    """
    if not valido:
        raise erro_class(*args, **kwargs)

def formatar_mensagem_autorizacao(acao: str, modulo: str, usuario: str, detalhes: Optional[str] = None) -> str:
    """
    Formata mensagem de erro de autorização.
    """
    mensagem = f"Falha na autorização para ação '{acao}' no módulo '{modulo}' pelo usuário '{usuario}'"
    if detalhes:
        mensagem += f": {detalhes}"
    return mensagem