"""
Precision VRT Solo — Fluxos de Aprovação

Implementa fluxos de aprovação para operações protegidas.
Não contém lógica de negócio.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod

class StatusFluxo(Enum):
    """Status do fluxo de aprovação."""
    PENDENTE = "pendente"
    EM_APROVACAO = "em_aprovacao"
    APROVADO = "aprovado"
    REJEITADO = "rejeitado"
    CANCELADO = "cancelado"

class NivelAprovacao(Enum):
    """Níveis de aprovação."""
    AUTOMATICA = "automatica"
    GERENTE = "gerente"
    DIRETOR = "diretor"
    ADMINISTRADOR = "administrador"
    MULTI_NIVEL = "multi_nivel"

class TipoOperacao(Enum):
    """Tipos de operação que requerem aprovação."""
    LIBERAR_DESCONTOS = "liberar_descontos"
    LIBERAR_VENDAS = "liberar_vendas"
    LIBERAR_CLIENTES = "liberar_clientes"
    LIBERAR_PATRIMONIO = "liberar_patrimonio"
    LIBERAR_FINANCEIRO = "liberar_financeiro"
    LIBERAR_RH = "liberar_rh"
    LIBERAR_CRM = "liberar_crm"
    LIBERAR_INTEGRACOES = "liberar_integracoes"
    LIBERAR_MODULOS = "liberar_modulos"
    ALTERAR_METODOLOGIA = "alterar_metodologia"
    ALTERAR_CONFIGURACOES = "alterar_configuracoes"
    ALTERAR_PRECOS = "alterar_precos"
    ALTERAR_PRODUTOS = "alterar_produtos"
    ALTERAR_PARAMETROS = "alterar_parametros"
    CADASTRAR_USUARIOS = "cadastrar_usuarios"

class Aprovacao:
    """
    Representa uma aprovação individual no fluxo.
    """
    
    def __init__(self, 
                 aprovador_id: str, 
                 data_aprovacao: datetime,
                 justificativa: str,
                 aprovado: bool):
        self.aprovador_id = aprovador_id
        self.data_aprovacao = data_aprovacao
        self.justificativa = justificativa
        self.aprovado = aprovado
        
    def __str__(self):
        status = "Aprovado" if self.aprovado else "Rejeitado"
        return f"Aprovacao({self.aprovador_id}, {self.data_aprovacao}, {status})"

class FluxoAprovacao:
    """
    Fluxo de aprovação para operações protegidas.
    """
    
    def __init__(self,
                 id_fluxo: str,
                 tipo_operacao: TipoOperacao,
                 solicitante_id: str,
                 operacao_descricao: str,
                 nivel_aprovacao: NivelAprovacao = NivelAprovacao.GERENTE,
                 clientes_envolvidos: Optional[List[str]] = None,
                 modulo: Optional[str] = None,
                 aprovadores_necessarios: int = 1,
                 observacoes: Optional[str] = None):
        self.id_fluxo = id_fluxo
        self.tipo_operacao = tipo_operacao
        self.solicitante_id = solicitante_id
        self.operacao_descricao = operacao_descricao
        self.nivel_aprovacao = nivel_aprovacao
        self.clientes_envolvidos = clientes_envolvidos or []
        self.modulo = modulo
        self.aprovadores_necessarios = aprovadores_necessarios
        self.observacoes = observacoes
        self.status = StatusFluxo.PENDENTE
        self.data_solicitacao = datetime.now()
        self.aprovacoes: List[Aprovacao] = []
        self.justificativa_obrigatoria = True
        self.ip_solicitante = None
        self.localizacao_solicitante = None
        
    def adicionar_aprovacao(self, 
                           aprovador_id: str, 
                           aprovado: bool, 
                           justificativa: str = "") -> bool:
        """
        Adiciona aprovação ao fluxo.
        """
        if self.status not in [StatusFluxo.PENDENTE, StatusFluxo.EM_APROVACAO]:
            return False
            
        if aprovado:
            self.aprovacoes.append(Aprovacao(aprovador_id, datetime.now(), justificativa, True))
            
            # Verificar se todos os aprovadores necessários foram obtidos
            if len([a for a in self.aprovacoes if a.aprovado]) >= self.aprovadores_necessarios:
                self.status = StatusFluxo.APROVADO
            else:
                self.status = StatusFluxo.EM_APROVACAO
        else:
            self.aprovacoes.append(Aprovacao(aprovador_id, datetime.now(), justificativa, False))
            self.status = StatusFluxo.REJEITADO
            
        return True
        
    def pode_aprovar(self, usuario_id: str) -> bool:
        """
        Verifica se usuário pode aprovar este fluxo.
        """
        # Verificar se fluxo está em aprovação
        if self.status != StatusFluxo.EM_APROVACAO:
            return False
            
        # Verificar se usuário já aprovou
        for aprovacao in self.aprovacoes:
            if aprovacao.aprovador_id == usuario_id:
                return False
                
        # Verificar se o usuário tem permissão para aprovar no nível necessário
        return True  # Detalhes de permissão são verificados em outro módulo
        
    def pode_solicitar_autenticacao(self, usuario_id: str) -> bool:
        """
        Verifica se usuário pode solicitar autenticação superior.
        """
        # Apenas o solicitante pode solicitar autenticação superior
        return usuario_id == self.solicitante_id and self.status == StatusFluxo.PENDENTE
        
    def obter_status_completo(self) -> Dict[str, Any]:
        """
        Obtém status completo do fluxo.
        """
        aprovacoes_aprovadas = [a for a in self.aprovacoes if a.aprovado]
        aprovacoes_rejeitadas = [a for a in self.aprovacoes if not a.aprovado]
        
        return {
            'id_fluxo': self.id_fluxo,
            'tipo_operacao': self.tipo_operacao.value,
            'status': self.status.value,
            'solicitante': self.solicitante_id,
            'descricao_operacao': self.operacao_descricao,
            'data_solicitacao': self.data_solicitacao,
            'nivel_aprovacao': self.nivel_aprovacao.value,
            'aprovadores_necessarios': self.aprovadores_necessarios,
            'aprovacoes_recebidas': len(aprovacoes_aprovadas),
            'aprovacoes_rejeitadas': len(aprovacoes_rejeitadas),
            'aprovacoes': [str(aprovacao) for aprovacao in self.aprovacoes],
            'observacoes': self.observacoes,
            'justificativa_obrigatoria': self.justificativa_obrigatoria,
            'clientes_envolvidos': self.clientes_envolvidos,
            'modulo': self.modulo,
            'concluido': self.status in [StatusFluxo.APROVADO, StatusFluxo.REJEITADO, StatusFluxo.CANCELADO]
        }
        
    def cancelar(self, usuario_id: str, justificativa: str) -> bool:
        """
        Cancela o fluxo de aprovação.
        """
        if self.status in [StatusFluxo.APROVADO, StatusFluxo.REJEITADO, StatusFluxo.CANCELADO]:
            return False
            
        self.status = StatusFluxo.CANCELADO
        self.aprovacoes.append(Aprovacao(usuario_id, datetime.now(), justificativa, False))
        return True

class ProcessoAprovacao:
    """
    Gerencia processo de aprovação com múltiplos fluxos.
    """
    
    def __init__(self):
        self.fluxos: Dict[str, FluxoAprovacao] = {}
        self.usuarios_envolvidos: Dict[str, List[str]] = {}  # usuario_id -> [fluxos_ids]
        
    def criar_fluxo(self, fluxo: FluxoAprovacao) -> str:
        """
        Cria novo fluxo de aprovação.
        """
        fluxo.id_fluxo = f"fluxo_{int(datetime.now().timestamp())}_{len(self.fluxos)}"
        self.fluxos[fluxo.id_fluxo] = fluxo
        
        # Indexar usuário
        if fluxo.solicitante_id not in self.usuarios_envolvidos:
            self.usuarios_envolvidos[fluxo.solicitante_id] = []
        self.usuarios_envolvidos[fluxo.solicitante_id].append(fluxo.id_fluxo)
        
        return fluxo.id_fluxo
        
    def obter_fluxo(self, fluxo_id: str) -> Optional[FluxoAprovacao]:
        """
        Obtém fluxo pelo ID.
        """
        return self.fluxos.get(fluxo_id)
        
    def obter_fluxos_usuario(self, usuario_id: str) -> List[FluxoAprovacao]:
        """
        Obtém todos os fluxos envolvendo um usuário.
        """
        fluxos_ids = self.usuarios_envolvidos.get(usuario_id, [])
        return [self.fluxos[fluxo_id] for fluxo_id in fluxos_ids if fluxo_id in self.fluxos]
        
    def obter_fluxos_pendentes_aprovacao(self, usuario_id: str) -> List[FluxoAprovacao]:
        """
        Obtém fluxos pendentes que usuário pode aprovar.
        """
        fluxos_pendentes = []
        for fluxo in self.obter_fluxos_usuario(usuario_id):
            if fluxo.status == StatusFluxo.EM_APROVACAO and fluxo.pode_aprovar(usuario_id):
                fluxos_pendentes.append(fluxo)
        return fluxos_pendentes
        
    def remover_fluxo_concluido(self, fluxo_id: str):
        """
        Remove fluxo concluído da lista ativa.
        """
        if fluxo_id in self.fluxos:
            fluxo = self.fluxos[fluxo_id]
            
            # Remover do índice de usuários
            if fluxo.solicitante_id in self.usuarios_envolvidos:
                if fluxo_id in self.usuarios_envolvidos[fluxo.solicitante_id]:
                    self.usuarios_envolvidos[fluxo.solicitante_id].remove(fluxo_id)
                    
            # Remover da lista principal
            del self.fluxos[fluxo_id]

# Instância global do processo de aprovação
processo_aprovacao = ProcessoAprovacao()

def criar_fluxo_aprovacao(tipo_operacao: TipoOperacao,
                         solicitante_id: str,
                         operacao_descricao: str,
                         nivel_aprovacao: NivelAprovacao = NivelAprovacao.GERENTE,
                         clientes_envolvidos: Optional[List[str]] = None,
                         modulo: Optional[str] = None,
                         aprovadores_necessarios: int = 1,
                         observacoes: Optional[str] = None) -> str:
    """
    Cria novo fluxo de aprovação.
    """
    fluxo = FluxoAprovacao(
        id_fluxo="",
        tipo_operacao=tipo_operacao,
        solicitante_id=solicitante_id,
        operacao_descricao=operacao_descricao,
        nivel_aprovacao=nivel_aprovacao,
        clientes_envolvidos=clientes_envolvidos,
        modulo=modulo,
        aprovadores_necessarios=aprovadores_necessarios,
        observacoes=observacoes
    )
    
    return processo_aprovacao.criar_fluxo(fluxo)

def obter_fluxo(fluxo_id: str) -> Optional[FluxoAprovacao]:
    """
    Obtém fluxo pelo ID.
    """
    return processo_aprovacao.obter_fluxo(fluxo_id)

def aprovar_fluxo(fluxo_id: str, aprovador_id: str, justificativa: str = "") -> bool:
    """
    Aprova fluxo de aprovação.
    """
    fluxo = processo_aprovacao.obter_fluxo(fluxo_id)
    if not fluxo:
        return False
        
    return fluxo.adicionar_aprovacao(aprovador_id, True, justificativa)

def rejeitar_fluxo(fluxo_id: str, aprovador_id: str, justificativa: str) -> bool:
    """
    Rejeita fluxo de aprovação.
    """
    fluxo = processo_aprovacao.obter_fluxo(fluxo_id)
    if not fluxo:
        return False
        
    return fluxo.adicionar_aprovacao(aprovador_id, False, justificativa)

def cancelar_fluxo(fluxo_id: str, usuario_id: str, justificativa: str) -> bool:
    """
    Cancela fluxo de aprovação.
    """
    fluxo = processo_aprovacao.obter_fluxo(fluxo_id)
    if not fluxo:
        return False
        
    return fluxo.cancelar(usuario_id, justificativa)