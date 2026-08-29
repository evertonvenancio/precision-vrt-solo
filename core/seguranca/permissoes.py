"""
Precision VRT Solo — Permissões Globais

Responsável pela gestão de permissões e perfis de usuário.
Não contém lógica de negócio.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

class TipoPerfil(Enum):
    """Tipos de perfis de usuário."""
    ADMINISTRADOR = "administrador"
    SUPERVISOR = "supervisor"
    CONSULTOR = "consultor"
    OPERADOR = "operador"

class RecursoSistema(Enum):
    """Recursos do sistema controlados por permissões."""
    VISUALIZAR_DADOS = "visualizar_dados"
    ALTERAR_DADOS = "alterar_dados"
    EXPORTAR_DADOS = "exportar_dados"
    CALCULAR_PRESCRICAO = "calcular_prescricao"
    GERENCIAR_USUARIOS = "gerenciar_usuarios"
    GERENCIAR_CONFIGURACOES = "gerenciar_configuracoes"
    GERENCIAR_PERMISSOES = "gerenciar_permissoes"
    APROVAR_OPERACOES = "aprovar_operacoes"
    REJEITAR_OPERACOES = "rejeitar_operacoes"

class Permissao:
    """
    Representa uma permissão de sistema.
    Apenas dados, não lógica.
    """
    
    def __init__(self,
                 recurso: RecursoSistema,
                 acao: str,
                 modulo: Optional[str] = None):
        self.recurso = recurso
        self.acao = acao
        self.modulo = modulo
        self.ativo = True
        self.data_criacao = datetime.now()
        self.criado_por = None
        
    def __str__(self):
        return f"Permissao({self.recurso.value}, {self.acao}, {self.modulo})"

class PerfilUsuario:
    """
    Representa um perfil de usuário.
    Apenas dados, não lógica.
    """
    
    def __init__(self, 
                 tipo: TipoPerfil,
                 nome: str,
                 descricao: Optional[str] = None,
                 permissoes: Optional[List[Permissao]] = None):
        self.tipo = tipo
        self.nome = nome
        self.descricao = descricao
        self.permissoes = permissoes or []
        self.criado_em = datetime.now()
        self.atualizado_em = datetime.now()
        self.criado_por = None
        self.atualizado_por = None
        self.status = 'ativo'
        
    def adicionar_permissao(self, permissao: Permissao):
        """
        Adiciona permissão ao perfil.
        Não valida, apenas adiciona.
        """
        if permissao not in self.permissoes:
            self.permissoes.append(permissao)
            self.atualizado_em = datetime.now()
            
    def remover_permissao(self, permissao: Permissao):
        """
        Remove permissão do perfil.
        """
        if permissao in self.permissoes:
            self.permissoes.remove(permissao)
            self.atualizado_em = datetime.now()
            
    def tem_permissao(self, recurso: RecursoSistema, acao: str, modulo: Optional[str] = None) -> bool:
        """
        Verifica se perfil tem permissão específica.
        """
        for permissao in self.permissoes:
            if (permissao.recurso == recurso and 
                permissao.acao == acao and
                (permissao.modulo == modulo or modulo is None or permissao.modulo is None)):
                return True
        return False

class GerenciadorPermissoes:
    """
    Gerencia permissões e perfis do sistema.
    Não contém lógica de negócio.
    """
    
    def __init__(self):
        self.perfis: Dict[str, PerfilUsuario] = {}
        self.permissoes_padrao: Dict[TipoPerfil, List[Permissao]] = {}
        self.criar_permissoes_padrao()
        
    def criar_permissoes_padrao(self):
        """
        Cria permissões padrão para cada perfil.
        """
        # Administrador: acesso total
        admin_permissoes = [
            Permissao(RecursoSistema.VISUALIZAR_DADOS, 'todos'),
            Permissao(RecursoSistema.ALTERAR_DADOS, 'todos'),
            Permissao(RecursoSistema.EXPORTAR_DADOS, 'todos'),
            Permissao(RecursoSistema.CALCULAR_PRESCRICAO, 'todos'),
            Permissao(RecursoSistema.GERENCIAR_USUARIOS, 'todos'),
            Permissao(RecursoSistema.GERENCIAR_CONFIGURACOES, 'todos'),
            Permissao(RecursoSistema.GERENCIAR_PERMISSOES, 'todos'),
            Permissao(RecursoSistema.APROVAR_OPERACOES, 'todos'),
            Permissao(RecursoSistema.REJEITAR_OPERACOES, 'todos')
        ]
        
        # Supervisor: acesso limitado
        supervisor_permissoes = [
            Permissao(RecursoSistema.VISUALIZAR_DADOS, 'todos'),
            Permissao(RecursoSistema.ALTERAR_DADOS, 'limitado'),
            Permissao(RecursoSistema.EXPORTAR_DADOS, 'todos'),
            Permissao(RecursoSistema.CALCULAR_PRESCRICAO, 'todos'),
            Permissao(RecursoSistema.APROVAR_OPERACOES, 'limitado')
        ]
        
        # Consultor: apenas visualização
        consultor_permissoes = [
            Permissao(RecursoSistema.VISUALIZAR_DADOS, 'todos'),
            Permissao(RecursoSistema.EXPORTAR_DADOS, 'proprio')
        ]
        
        # Operador: operações básicas
        operador_permissoes = [
            Permissao(RecursoSistema.VISUALIZAR_DADOS, 'proprio'),
            Permissao(RecursoSistema.ALTERAR_DADOS, 'proprio'),
            Permissao(RecursoSistema.EXPORTAR_DADOS, 'proprio')
        ]
        
        self.permissoes_padrao[TipoPerfil.ADMINISTRADOR] = admin_permissoes
        self.permissoes_padrao[TipoPerfil.SUPERVISOR] = supervisor_permissoes
        self.permissoes_padrao[TipoPerfil.CONSULTOR] = consultor_permissoes
        self.permissoes_padrao[TipoPerfil.OPERADOR] = operador_permissoes
        
    def criar_perfil(self, tipo: TipoPerfil, nome: str, descricao: Optional[str] = None, criado_por: Optional[str] = None) -> PerfilUsuario:
        """
        Cria novo perfil.
        """
        perfil = PerfilUsuario(tipo, nome, descricao, [])
        
        # Adicionar permissões padrão
        perfil.permissoes = self.permissoes_padrao[tipo].copy()
        
        # Registrar criação
        perfil.criado_por = criado_por
        perfil.criado_em = datetime.now()
        
        # Armazenar perfil
        self.perfis[nome] = perfil
        
        return perfil
        
    def obter_perfil(self, nome: str) -> Optional[PerfilUsuario]:
        """
        Obtém perfil pelo nome.
        """
        return self.perfis.get(nome)
        
    def listar_perfis(self, tipo: Optional[TipoPerfil] = None) -> List[PerfilUsuario]:
        """
        Lista perfis, filtrados por tipo se especificado.
        """
        perfis = list(self.perfis.values())
        
        if tipo:
            perfis = [p for p in perfis if p.tipo == tipo]
            
        return perfis
        
    def remover_perfil(self, nome: str) -> bool:
        """
        Remove perfil.
        """
        if nome in self.perfis:
            del self.perfis[nome]
            return True
        return False
        
    def adicionar_permissao_perfil(self, perfil_nome: str, permissao: Permissao) -> bool:
        """
        Adiciona permissão a perfil.
        """
        perfil = self.obter_perfil(perfil_nome)
        if perfil:
            perfil.adicionar_permissao(permissao)
            return True
        return False
        
    def remover_permissao_perfil(self, perfil_nome: str, permissao: Permissao) -> bool:
        """
        Remove permissão de perfil.
        """
        perfil = self.obter_perfil(perfil_nome)
        if perfil:
            perfil.remover_permissao(permissao)
            return True
        return False
        
    def verifica_permissao_usuario(self, perfil_nome: str, recurso: RecursoSistema, acao: str, modulo: Optional[str] = None) -> bool:
        """
        Verifica se perfil tem permissão específica.
        """
        perfil = self.obter_perfil(perfil_nome)
        if perfil:
            return perfil.tem_permissao(recurso, acao, modulo)
        return False

class PermissoesPadrao:
    """
    Contêiner com permissões padrão do sistema.
    Não contém lógica de negócio.
    """
    
    @staticmethod
    def get_permissoes_administrador() -> List[Permissao]:
        """Retorna permissões do administrador."""
        return [
            Permissao(RecursoSistema.VISUALIZAR_DADOS, 'todos'),
            Permissao(RecursoSistema.ALTERAR_DADOS, 'todos'),
            Permissao(RecursoSistema.EXPORTAR_DADOS, 'todos'),
            Permissao(RecursoSistema.CALCULAR_PRESCRICAO, 'todos'),
            Permissao(RecursoSistema.GERENCIAR_USUARIOS, 'todos'),
            Permissao(RecursoSistema.GERENCIAR_CONFIGURACOES, 'todos'),
            Permissao(RecursoSistema.GERENCIAR_PERMISSOES, 'todos'),
            Permissao(RecursoSistema.APROVAR_OPERACOES, 'todos'),
            Permissao(RecursoSistema.REJEITAR_OPERACOES, 'todos')
        ]
        
    @staticmethod
    def get_permissoes_supervisor() -> List[Permissao]:
        """Retorna permissões do supervisor."""
        return [
            Permissao(RecursoSistema.VISUALIZAR_DADOS, 'todos'),
            Permissao(RecursoSistema.ALTERAR_DADOS, 'limitado'),
            Permissao(RecursoSistema.EXPORTAR_DADOS, 'todos'),
            Permissao(RecursoSistema.CALCULAR_PRESCRICAO, 'todos'),
            Permissao(RecursoSistema.APROVAR_OPERACOES, 'limitado')
        ]
        
    @staticmethod
    def get_permissoes_consultor() -> List[Permissao]:
        """Retorna permissões do consultor."""
        return [
            Permissao(RecursoSistema.VISUALIZAR_DADOS, 'todos'),
            Permissao(RecursoSistema.EXPORTAR_DADOS, 'proprio')
        ]
        
    @staticmethod
    def get_permissoes_operador() -> List[Permissao]:
        """Retorna permissões do operador."""
        return [
            Permissao(RecursoSistema.VISUALIZAR_DADOS, 'proprio'),
            Permissao(RecursoSistema.ALTERAR_DADOS, 'proprio'),
            Permissao(RecursoSistema.EXPORTAR_DADOS, 'proprio')
        ]

# Instância global
gerenciador_permissoes = GerenciadorPermissoes()

# Funções utilitárias
def criar_perfil_usuario(tipo: TipoPerfil,
                         nome: str,
                         descricao: Optional[str] = None,
                         criado_por: Optional[str] = None) -> PerfilUsuario:
    """
    Cria perfil de usuário.
    """
    return gerenciador_permissoes.criar_perfil(tipo, nome, descricao, criado_por)

def verificar_permissao_usuario(perfil_nome: str,
                              recurso: RecursoSistema,
                              acao: str,
                              modulo: Optional[str] = None) -> bool:
    """
    Verifica se perfil de usuário tem permissão específica.
    """
    return gerenciador_permissoes.verifica_permissao_usuario(perfil_nome, recurso, acao, modulo)