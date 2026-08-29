"""
Precision VRT Solo — Auditoria Global

Responsável pelo registro de auditoria do sistema.
Não contém lógica de negócio.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

class TipoAcao(Enum):
    """Tipos de ações auditáveis."""
    CRIAR = "criar"
    ALTERAR = "alterar"
    EXCLUIR = "excluir"
    APROVAR = "aprovar"
    REJEITAR = "rejeitar"
    EXPORTAR = "exportar"
    IMPORTAR = "importar"
    CALCULAR = "calcular"
    VALIDAR = "validar"

class ModuloSistema(Enum):
    """Módulos do sistema auditáveis."""
    PRESCRICAO_VRT = "prescricao_vrt"
    COMPACTACAO = "compactacao"
    NEMATOIDES = "nematoides"
    FERTIRRIGACAO = "fertirrigacao"
    SENSORIAMENTO = "sensoriamento"
    MONITORAMENTO = "monitoramento"
    EXPORTACAO = "exportacao"
    CONFIGURACOES = "configuracoes"
    USUARIOS = "usuarios"
    PERMISSOES = "permissoes"

class AuditoriaRegistro:
    """
    Representa um registro de auditoria.
    Apenas dados, não lógica.
    """
    
    def __init__(self,
                 tipo_acao: TipoAcao,
                 modulo: ModuloSistema,
                 usuario: str,
                 acao: str,
                 dados_antes: Optional[Dict[str, Any]] = None,
                 dados_depois: Optional[Dict[str, Any]] = None,
                 ip: Optional[str] = None,
                 justificativa: Optional[str] = None):
        self.id = None
        self.tipo_acao = tipo_acao
        self.modulo = modulo
        self.usuario = usuario
        self.acao = acao
        self.dados_antes = dados_antes or {}
        self.dados_depois = dados_depois or {}
        self.ip = ip
        self.justificativa = justificativa
        self.data_registro = datetime.now()
        self.status = 'registrado'
        
    def __str__(self):
        return f"AuditoriaRegistro({self.tipo_acao.value}, {self.modulo.value}, {self.usuario}, {self.acao})"

class AuditorSistema:
    """
    Gerenciador de auditoria do sistema.
    Não contém lógica de negócio.
    """
    
    def __init__(self):
        self.registros: List[AuditoriaRegistro] = []
        self.historico_operacoes: Dict[str, List[AuditoriaRegistro]] = {}
        
    def registrar_operacao(self, registro: AuditoriaRegistro) -> str:
        """
        Registra operação na auditoria.
        Não valida, apenas registra.
        """
        # Gerar ID único
        registro.id = f"audit_{int(datetime.now().timestamp())}_{len(self.registros)}"
        
        # Adicionar aos registros
        self.registros.append(registro)
        
        # Adicionar ao histórico do usuário
        if registro.usuario not in self.historico_operacoes:
            self.historico_operacoes[registro.usuario] = []
        self.historico_operacoes[registro.usuario].append(registro)
        
        return registro.id
        
    def obter_registros(self, 
                       usuario: Optional[str] = None,
                       modulo: Optional[ModuloSistema] = None,
                       tipo_acao: Optional[TipoAcao] = None,
                       data_inicio: Optional[datetime] = None,
                       data_fim: Optional[datetime] = None) -> List[AuditoriaRegistro]:
        """
        Obtém registros de auditoria com filtros.
        """
        registros_filtrados = self.registros
        
        # Filtrar por usuário
        if usuario:
            registros_filtrados = [r for r in registros_filtrados if r.usuario == usuario]
            
        # Filtrar por módulo
        if modulo:
            registros_filtrados = [r for r in registros_filtrados if r.modulo == modulo]
            
        # Filtrar por tipo de ação
        if tipo_acao:
            registros_filtrados = [r for r in registros_filtrados if r.tipo_acao == tipo_acao]
            
        # Filtrar por data
        if data_inicio:
            registros_filtrados = [r for r in registros_filtrados if r.data_registro >= data_inicio]
            
        if data_fim:
            registros_filtrados = [r for r in registros_filtrados if r.data_registro <= data_fim]
            
        return registros_filtrados
        
    def obter_historico_usuario(self, usuario: str) -> List[AuditoriaRegistro]:
        """
        Obtém histórico de operações de um usuário.
        """
        return self.historico_operacoes.get(usuario, [])
        
    def gerar_relatorio(self, filtros: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Gera relatório de auditoria.
        """
        relatorio = {
            'total_registros': len(self.registros),
            'periodo': {
                'inicio': min(r.data_registro for r in self.registros) if self.registros else None,
                'fim': max(r.data_registro for r in self.registros) if self.registros else None
            },
            'por_usuario': {},
            'por_modulo': {},
            'por_tipo_acao': {}
        }
        
        # Agrupar por usuário
        for registro in self.registros:
            usuario = registro.usuario
            if usuario not in relatorio['por_usuario']:
                relatorio['por_usuario'][usuario] = 0
            relatorio['por_usuario'][usuario] += 1
            
        # Agrupar por módulo
        for registro in self.registros:
            modulo = registro.modulo.value
            if modulo not in relatorio['por_modulo']:
                relatorio['por_modulo'][modulo] = 0
            relatorio['por_modulo'][modulo] += 1
            
        # Agrupar por tipo de ação
        for registro in self.registros:
            tipo_acao = registro.tipo_acao.value
            if tipo_acao not in relatorio['por_tipo_acao']:
                relatorio['por_tipo_acao'][tipo_acao] = 0
            relatorio['por_tipo_acao'][tipo_acao] += 1
            
        return relatorio

class RegistroAuditoria:
    """
    Interface para registro de auditoria.
    Não contém lógica de negócio.
    """
    
    def __init__(self, auditoria: AuditorSistema):
        self.auditoria = auditoria
        
    def registrar(self, tipo_acao: TipoAcao, modulo: ModuloSistema, usuario: str, **kwargs) -> str:
        """
        Registra operação na auditoria.
        """
        registro = AuditoriaRegistro(
            tipo_acao=tipo_acao,
            modulo=modulo,
            usuario=usuario,
            **kwargs
        )
        return self.auditoria.registrar_operacao(registro)

# Instância global
auditor_sistema = AuditorSistema()
registro_auditoria = RegistroAuditoria(auditor_sistema)

# Funções utilitárias
def registrar_operacao_auditoria(tipo_acao: TipoAcao,
                                 modulo: ModuloSistema,
                                 usuario: str,
                                 acao: str,
                                 **kwargs) -> str:
    """
    Registra operação na auditoria.
    """
    return registro_auditoria.registrar(
        tipo_acao=tipo_acao,
        modulo=modulo,
        usuario=usuario,
        acao=acao,
        **kwargs
    )

def obter_registros_auditoria(usuario: Optional[str] = None,
                            modulo: Optional[ModuloSistema] = None,
                            tipo_acao: Optional[TipoAcao] = None) -> List[AuditoriaRegistro]:
    """
    Obtém registros de auditoria com filtros.
    """
    return auditor_sistema.obter_registros(
        usuario=usuario,
        modulo=modulo,
        tipo_acao=tipo_acao
    )