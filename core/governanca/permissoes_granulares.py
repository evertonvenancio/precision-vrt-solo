"""
Precision VRT Solo — Permissões Granulares

Implementa sistema de permissões granulares parametrizável.
Não contém regras fixas.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from .hierarquia import Cargo, PerfilGovernanca

class RecursoSistema(Enum):
    """Recursos do sistema controlados por permissões."""
    DADOS = "dados"
    CLIENTES = "clientes"
    FINANCEIRO = "financeiro"
    CRM = "crm"
    PATRIMONIO = "patrimonio"
    CONFIGURACOES = "configuracoes"
    USUARIOS = "usuarios"
    RELATORIOS = "relatorios"
    INTEGRACOES = "integracoes"
    METODOLOGIAS = "metodologias"
    OPERACOES = "operacoes"

class OperacaoSistema(Enum):
    """Operações do sistema controladas por permissões."""
    VISUALIZAR = "visualizar"
    CRIAR = "criar"
    EDITAR = "editar"
    EXCLUIR = "excluir"
    EXPORTAR = "exportar"
    IMPORTAR = "importar"
    APROVAR = "aprovar"
    REJEITAR = "rejeitar"
    ALTERAR_METODOLOGIA = "alterar_metodologia"
    ALTERAR_PARAMETROS = "alterar_parametros"
    ALTERAR_PRECOS = "alterar_precos"
    ALTERAR_PRODUTOS = "alterar_produtos"
    ALTERAR_CONFIGURACOES = "alterar_configuracoes"
    CADASTRAR_USUARIOS = "cadastrar_usuarios"
    LIBERAR_DESCONTOS = "liberar_descontos"
    LIBERAR_VENDAS = "liberar_vendas"
    LIBERAR_CLIENTES = "liberar_clientes"
    LIBERAR_PATRIMONIO = "liberar_patrimonio"
    LIBERAR_FINANCEIRO = "liberar_financeiro"
    LIBERAR_RH = "liberar_rh"
    LIBERAR_CRM = "liberar_crm"
    LIBERAR_INTEGRACOES = "liberar_integracoes"
    LIBERAR_MODULOS = "liberar_modulos"

class PermissaoGranular:
    """
    Permissão granular individual.
    """
    
    def __init__(self,
                 recurso: RecursoSistema,
                 operacao: OperacaoSistema,
                 cliente_id: Optional[str] = None,
                 modulo: Optional[str] = None,
                 restricoes: Optional[Dict[str, Any]] = None):
        self.id = None
        self.recurso = recurso
        self.operacao = operacao
        self.cliente_id = cliente_id
        self.modulo = modulo
        self.restricoes = restricoes or {}
        self.criado_em = datetime.now()
        self.ativo = True
        
    def __str__(self):
        modulo_str = f" no módulo {self.modulo}" if self.modulo else ""
        cliente_str = f" do cliente {self.cliente_id}" if self.cliente_id else ""
        return f"PermissaoGranular({self.recurso.value}, {self.operacao.value}{modulo_str}{cliente_str})"
        
    def aplica_se(self, recurso: RecursoSistema, operacao: OperacaoSistema, cliente_id: Optional[str] = None, modulo: Optional[str] = None) -> bool:
        """
        Verifica se permissão se aplica ao contexto informado.
        """
        # Verificar recurso e operação
        if self.recurso != recurso or self.operacao != operacao:
            return False
            
        # Verificar cliente
        if self.cliente_id and self.cliente_id != cliente_id:
            return False
            
        # Verificar módulo
        if self.modulo and self.modulo != modulo:
            return False
            
        return True
        
    def verifica_restricoes(self, contexto: Dict[str, Any]) -> bool:
        """
        Verifica se contexto atende às restrições da permissão.
        """
        for chave, valor_restricao in self.restricoes.items():
            if chave in contexto:
                contexto_valor = contexto[chave]
                # Verificar tipo e valor
                if isinstance(valor_restricao, dict):
                    # Restrição complexa (ex: limite máximo)
                    if 'max' in valor_restricao and contexto_valor > valor_restricao['max']:
                        return False
                    if 'min' in valor_restricao and contexto_valor < valor_restricao['min']:
                        return False
                    if 'permitido' in valor_restricao and contexto_valor not in valor_restricao['permitido']:
                        return False
                else:
                    # Restrição simples (ex: valor exato)
                    if contexto_valor != valor_restricao:
                        return False
                        
        return True

class MatrizPermissoes:
    """
    Matriz de permissões granulares do sistema.
    """
    
    def __init__(self):
        self.permissoes: List[PermissaoGranular] = []
        self.permissoes_por_usuario: Dict[str, List[PermissaoGranular]] = {}
        self.permissoes_por_cargo: Dict[Cargo, List[PermissaoGranular]] = {}
        self.permissoes_por_cliente: Dict[str, List[PermissaoGranular]] = {}
        
    def adicionar_permissao(self, permissao: PermissaoGranular, usuario_id: Optional[str] = None, cargo: Optional[Cargo] = None, cliente_id: Optional[str] = None):
        """
        Adiciona permissão à matriz.
        """
        permissao.id = f"perm_{int(datetime.now().timestamp())}_{len(self.permissoes)}"
        self.permissoes.append(permissao)
        
        # Indexar por usuário
        if usuario_id:
            if usuario_id not in self.permissoes_por_usuario:
                self.permissoes_por_usuario[usuario_id] = []
            self.permissoes_por_usuario[usuario_id].append(permissao)
            
        # Indexar por cargo
        if cargo:
            if cargo not in self.permissoes_por_cargo:
                self.permissoes_por_cargo[cargo] = []
            self.permissoes_por_cargo[cargo].append(permissao)
            
        # Indexar por cliente
        if cliente_id:
            if cliente_id not in self.permissoes_por_cliente:
                self.permissoes_por_cliente[cliente_id] = []
            self.permissoes_por_cliente[cliente_id].append(permissao)
            
    def remover_permissao(self, permissao_id: str):
        """
        Remove permissão da matriz.
        """
        # Remover da lista principal
        self.permissoes = [p for p in self.permissoes if p.id != permissao_id]
        
        # Remover dos índices
        for usuario_permissoes in self.permissoes_por_usuario.values():
            usuario_permissoes[:] = [p for p in usuario_permissoes if p.id != permissao_id]
            
        for cargo_permissoes in self.permissoes_por_cargo.values():
            cargo_permissoes[:] = [p for p in cargo_permissoes if p.id != permissao_id]
            
        for cliente_permissoes in self.permissoes_por_cliente.values():
            cliente_permissoes[:] = [p for p in cliente_permissoes if p.id != permissao_id]
            
    def obter_permissoes_usuario(self, usuario_id: str) -> List[PermissaoGranular]:
        """
        Obtém permissões de um usuário específico.
        """
        return self.permissoes_por_usuario.get(usuario_id, []).copy()
        
    def obter_permissoes_cargo(self, cargo: Cargo) -> List[PermissaoGranular]:
        """
        Obtém permissões de um cargo específico.
        """
        return self.permissoes_por_cargo.get(cargo, []).copy()
        
    def obter_permissoes_cliente(self, cliente_id: str) -> List[PermissaoGranular]:
        """
        Obtém permissões de um cliente específico.
        """
        return self.permissoes_por_cliente.get(cliente_id, []).copy()
        
    def pode_executar(self, usuario_id: str, recurso: RecursoSistema, operacao: OperacaoSistema, cliente_id: Optional[str] = None, modulo: Optional[str] = None, contexto: Optional[Dict[str, Any]] = None) -> bool:
        """
        Verifica se usuário pode executar operação no recurso informado.
        """
        # Obter permissões do usuário
        permissoes_usuario = self.obter_permissoes_usuario(usuario_id)
        
        # Buscar permissão que se aplica ao contexto
        for permissao in permissoes_usuario:
            if permissao.aplica_se(recurso, operacao, cliente_id, modulo):
                # Verificar restrições se contexto fornecido
                if contexto is None or permissao.verifica_restricoes(contexto):
                    return True
                    
        return False
        
    def obter_permissoes_recurso(self, usuario_id: str, recurso: RecursoSistema) -> List[OperacaoSistema]:
        """
        Obtém todas as operações que um usuário pode executar em um recurso.
        """
        permissoes_usuario = self.obter_permissoes_usuario(usuario_id)
        operacoes_validas = []
        
        for permissao in permissoes_usuario:
            if permissao.recurso == recurso and permissao.aplica_se(recurso, permissao.operacao, permissao.cliente_id, permissao.modulo):
                operacoes_validas.append(permissao.operacao)
                
        return list(set(operacoes_validas))  # Remover duplicatas
        
    def pode_operar_cliente(self, usuario_id: str, cliente_id: str) -> bool:
        """
        Verifica se usuário pode operar cliente específico.
        """
        # Se usuário tem permissão global ou específica para o cliente
        permissoes_usuario = self.obter_permissoes_usuario(usuario_id)
        
        for permissao in permissoes_usuario:
            if permissao.recurso == RecursoSistema.CLIENTES and permissao.aplica_se(RecursoSistema.CLIENTES, OperacaoSistema.VISUALIZAR, cliente_id):
                return True
                
        return False

class ValidadorPermissoes:
    """
    Validador de permissões para operações.
    """
    
    def __init__(self, matriz_permissoes: MatrizPermissoes):
        self.matriz = matriz_permissoes
        
    def validar_acesso(self, usuario_id: str, recurso: RecursoSistema, operacao: OperacaoSistema, cliente_id: Optional[str] = None, modulo: Optional[str] = None, contexto: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Valida acesso do usuário a operação específica.
        """
        resultado = {
            'permitido': False,
            'motivo': '',
            'permissoes_relacionadas': [],
            'recomendacoes': []
        }
        
        # Verificar se usuário tem permissão
        if self.matriz.pode_executar(usuario_id, recurso, operacao, cliente_id, modulo, contexto):
            resultado['permitido'] = True
            resultado['motivo'] = 'Permissão concedida'
        else:
            resultado['motivo'] = 'Permissão negada'
            
            # Obter permissões relacionadas para recomendações
            permissoes_usuario = self.matriz.obter_permissoes_usuario(usuario_id)
            for permissao in permissoes_usuario:
                if permissao.recurso == recurso:
                    resultado['permissoes_relacionadas'].append(str(permissao))
                    
            # Gerar recomendações
            if operacao == OperacaoSistema.APROVAR:
                resultado['recomendacoes'].append('Solicite aprovação de usuário superior')
            elif operacao == OperacaoSistema.EXCLUIR:
                resultado['recomendacoes'].append('Requer confirmação de supervisão')
                
        return resultado

# Instância global
matriz_permissoes = MatrizPermissoes()
validador_permissoes = ValidadorPermissoes(matriz_permissoes)

# Funções utilitárias
def adicionar_permissao_usuario(usuario_id: str, recurso: RecursoSistema, operacao: OperacaoSistema, cliente_id: Optional[str] = None, modulo: Optional[str] = None, restricoes: Optional[Dict[str, Any]] = None):
    """
    Adiciona permissão específica para usuário.
    """
    permissao = PermissaoGranular(recurso, operacao, cliente_id, modulo, restricoes)
    matriz_permissoes.adicionar_permissao(permissao, usuario_id)
    return permissao
    
def adicionar_permissao_cargo(cargo: Cargo, recurso: RecursoSistema, operacao: OperacaoSistema, cliente_id: Optional[str] = None, modulo: Optional[str] = None, restricoes: Optional[Dict[str, Any]] = None):
    """
    Adiciona permissão específica para cargo.
    """
    permissao = PermissaoGranular(recurso, operacao, cliente_id, modulo, restricoes)
    matriz_permissoes.adicionar_permissao(permissao, cargo=cargo)
    return permissao
    
def definir_permissao_padrao_cargo(cargo: Cargo):
    """
    Define permissões padrão para um cargo.
    """
    perfil_padrao = obter_perfil_padrao(cargo)
    
    for permissao_str in perfil_padrao.permissoes:
        # Converter string para enum
        try:
            operacao = OperacaoSistema(permissao_str)
            adicionar_permissao_cargo(cargo, RecursoSistema.OPERACOES, operacao)
        except ValueError:
            # Permissão personalizada
            adicionar_permissao_cargo(cargo, RecursoSistema.OPERACOES, OperacaoSistema.VISUALIZAR)

# Configurar permissões padrão para todos os cargos
from .hierarquia import obter_perfil_padrao

for cargo in Cargo:
    definir_permissao_padrao_cargo(cargo)