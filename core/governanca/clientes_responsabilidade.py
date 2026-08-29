"""
Precision VRT Solo — Gestão de Clientes e Responsabilidades

Implementa sistema de responsabilidades sobre clientes.
Não contém lógica de negócio.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

class TipoResponsavel(Enum):
    """Tipos de responsáveis por clientes."""
    CONSULTOR = "consultor"
    GERENTE = "gerente"
    SUPERVISOR = "supervisor"
    TECNICO = "tecnico"
    COMERCIAL = "comercial"
    OPERADOR = "operador"

class Cliente:
    """
    Representa um cliente do sistema com atributos básicos.
    """
    
    def __init__(self,
                 id_cliente: str,
                 nome: str,
                email: Optional[str] = None,
                telefone: Optional[str] = None,
                cnpj_cpf: Optional[str] = None,
                tipo: str = "comum"):
        self.id_cliente = id_cliente
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.cnpj_cpf = cnpj_cpf
        self.tipo = tipo
        self.criado_em = datetime.now()
        self.ativo = True
        self.responsaveis: List[ResponsavelCliente] = []
        
    def adicionar_responsavel(self, responsavel: 'ResponsavelCliente'):
        """
        Adiciona responsável ao cliente.
        """
        # Verificar se já existe
        if not any(r.usuario_id == responsavel.usuario_id for r in self.responsaveis):
            self.responsaveis.append(responsavel)
            
    def remover_responsavel(self, usuario_id: str):
        """
        Remove responsável do cliente.
        """
        self.responsaveis = [r for r in self.responsaveis if r.usuario_id != usuario_id]
        
    def obter_principal_responsavel(self) -> Optional['ResponsavelCliente']:
        """
        Obtém o responsável principal do cliente.
        """
        if not self.responsaveis:
            return None
            
        # Retorna o primeiro responsável como principal
        return self.responsaveis[0]
        
    def obter_todos_responsaveis(self) -> List['ResponsavelCliente']:
        """
        Obtém todos os responsáveis do cliente.
        """
        return self.responsaveis.copy()
        
    def pode_ser_operado_por(self, usuario_id: str) -> bool:
        """
        Verifica se usuário pode operar este cliente.
        """
        return any(r.usuario_id == usuario_id for r in self.responsaveis)

class ResponsavelCliente:
    """
    Responsável por um cliente específico.
    """
    
    def __init__(self,
                 usuario_id: str,
                 id_cliente: str,
                 tipo: TipoResponsavel,
                 data_inicio: datetime,
                 data_fim: Optional[datetime] = None,
                 limite_operacoes: Optional[Dict[str, int]] = None,
                 observacoes: Optional[str] = None):
        self.id = f"resp_{int(datetime.now().timestamp())}"
        self.usuario_id = usuario_id
        self.id_cliente = id_cliente
        self.tipo = tipo
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.limite_operacoes = limite_operacoes or {}
        self.observacoes = observacoes
        self.ativo = data_fim is None or data_fim > datetime.now()
        
    def pode_operar_cliente(self, usuario_id: str) -> bool:
        """
        Verifica se usuário pode operar cliente.
        """
        return (self.usuario_id == usuario_id and 
                self.ativo and 
                self.data_inicio <= datetime.now() <= (self.data_fim if self.data_fim else datetime.now()))
        
    def tem_limite_operacao(self, tipo_operacao: str, quantidade: int) -> bool:
        """
        Verifica se quantidade respeita o limite.
        """
        if tipo_operacao in self.limite_operacoes:
            return quantidade <= self.limite_operacoes[tipo_operacao]
        return True
        
    def definir_limite_operacao(self, tipo_operacao: str, quantidade: int):
        """
        Define limite para tipo de operação.
        """
        self.limite_operacoes[tipo_operacao] = quantidade

class ClienteGovernanca:
    """
    Gerenciamento centralizado de clientes e responsabilidades.
    """
    
    def __init__(self):
        self.clientes: Dict[str, Cliente] = {}
        self.responsaveis: Dict[str, ResponsavelCliente] = {}  # id -> ResponsavelCliente
        self.usuarios_clientes: Dict[str, List[str]] = {}  # usuario_id -> [cliente_ids]
        self.clientes_usuario: Dict[str, List[str]] = {}  # cliente_id -> [usuario_ids]
        
    def cadastrar_cliente(self, cliente: Cliente) -> str:
        """
        Cadastra novo cliente.
        """
        if cliente.id_cliente in self.clientes:
            return None  # Cliente já existe
            
        self.clientes[cliente.id_cliente] = cliente
        
        # Indexar responsáveis
        for responsavel in cliente.responsaveis:
            self.adicionar_responsavel(responsavel)
            
        return cliente.id_cliente
        
    def obter_cliente(self, id_cliente: str) -> Optional[Cliente]:
        """
        Obtém cliente pelo ID.
        """
        return self.clientes.get(id_cliente)
        
    def obter_cliente_por_usuario(self, usuario_id: str) -> List[Cliente]:
        """
        Obtém clientes que usuário pode operar.
        """
        cliente_ids = self.usuarios_clientes.get(usuario_id, [])
        return [self.clientes[cliente_id] for cliente_id in cliente_ids if cliente_id in self.clientes]
        
    def pode_operar_cliente(self, usuario_id: str, id_cliente: str) -> bool:
        """
        Verifica se usuário pode operar cliente específico.
        """
        cliente = self.obter_cliente(id_cliente)
        if not cliente:
            return False
            
        return cliente.pode_ser_operado_por(usuario_id)
        
    def adicionar_responsavel(self, responsavel: ResponsavelCliente) -> bool:
        """
        Adiciona responsável ao cliente e atualiza índices.
        """
        cliente = self.obter_cliente(responsavel.id_cliente)
        if not cliente:
            return False
            
        # Adicionar responsável ao cliente
        cliente.adicionar_responsavel(responsavel)
        
        # Adicionar aos índices
        if responsavel.usuario_id not in self.usuarios_clientes:
            self.usuarios_clientes[responsavel.usuario_id] = []
        if responsavel.id_cliente not in self.usuarios_clientes[responsavel.usuario_id]:
            self.usuarios_clientes[responsavel.usuario_id].append(responsavel.id_cliente)
            
        if responsavel.id_cliente not in self.clientes_usuario:
            self.clientes_usuario[responsavel.id_cliente] = []
        if responsavel.usuario_id not in self.clientes_usuario[responsavel.id_cliente]:
            self.clientes_usuario[responsavel.id_cliente].append(responsavel.usuario_id)
            
        self.responsaveis[responsavel.id] = responsavel
        
        return True
        
    def remover_responsavel(self, responsavel_id: str) -> bool:
        """
        Remove responsável do sistema.
        """
        responsavel = self.responsaveis.get(responsavel_id)
        if not responsavel:
            return False
            
        cliente = self.obter_cliente(responsavel.id_cliente)
        if cliente:
            cliente.remover_responsavel(responsavel.usuario_id)
            
        # Remover dos índices
        if responsavel.usuario_id in self.usuarios_clientes:
            if responsavel.id_cliente in self.usuarios_clientes[responsavel.usuario_id]:
                self.usuarios_clientes[responsavel.usuario_id].remove(responsavel.id_cliente)
                
        if responsavel.id_cliente in self.clientes_usuario:
            if responsavel.usuario_id in self.clientes_usuario[responsavel.id_cliente]:
                self.clientes_usuario[responsavel.id_cliente].remove(responsavel.usuario_id)
                
        del self.responsaveis[responsavel_id]
        
        return True
        
    def transferir_responsabilidade(self, id_cliente: str, usuario_saida: str, usuario_entrada: str, justificativa: str) -> bool:
        """
        Transfere responsabilidade de cliente entre usuários.
        """
        cliente = self.obter_cliente(id_cliente)
        if not cliente:
            return False
            
        # Verificar se usuário de saída é responsável
        if not cliente.pode_ser_operado_por(usuario_saida):
            return False
            
        # Remover responsável de saída
        cliente.remover_responsavel(usuario_saida)
        
        # Adicionar novo responsável
        novo_responsavel = ResponsavelCliente(
            usuario_id=usuario_entrada,
            id_cliente=id_cliente,
            tipo=TipoResponsavel.CONSULTOR,  # Tipo padrão para transferência
            data_inicio=datetime.now(),
            observacoes=f"Transferido de {usuario_saida}: {justificativa}"
        )
        
        self.adicionar_responsavel(novo_responsavel)
        
        return True
        
    def obter_operacoes_proibidas(self, usuario_id: str, cliente_id: str) -> List[str]:
        """
        Obtém lista de operações que usuário não pode executar no cliente.
        """
        cliente = self.obter_cliente(cliente_id)
        if not cliente or not cliente.pode_ser_operado_por(usuario_id):
            return ["todas"]  # Nenhuma operação permitida
            
        # Lista de operações críticas que requerem aprovação específica
        operacoes_proibidas = []
        
        # Obter responsável principal
        responsavel = cliente.obter_principal_responsavel()
        if responsavel and responsavel.usuario_id != usuario_id:
            operacoes_proibidas.extend([
                "realizar_venda",
                "editar_cadastro",
                "abrir_orcamento", 
                "gerar_contrato",
                "executar_atendimento",
                "alterar_informacoes"
            ])
            
        return operacoes_proibidas
        
    def gererar_historico_responsabilidades(self, cliente_id: str) -> List[Dict[str, Any]]:
        """
        Gera histórico de responsabilidades do cliente.
        """
        cliente = self.obter_cliente(cliente_id)
        if not cliente:
            return []
            
        historico = []
        
        for responsavel in cliente.responsaveis:
            historico.append({
                'id_responsavel': responsavel.id,
                'usuario_id': responsavel.usuario_id,
                'tipo': responsavel.tipo.value,
                'data_inicio': responsavel.data_inicio,
                'data_fim': responsavel.data_fim,
                'ativo': responsavel.ativo,
                'limite_operacoes': responsavel.limite_operacoes,
                'observacoes': responsavel.observacoes
            })
            
        return historico
        
    def validar_acao_cliente(self, usuario_id: str, cliente_id: str, acao: str, contexto: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Valida se usuário pode realizar ação específica no cliente.
        """
        resultado = {
            'permitido': False,
            'motivo': '',
            'operacoes_proibidas': [],
            'recomendacoes': []
        }
        
        # Verificar se usuário pode operar cliente
        if not self.pode_operar_cliente(usuario_id, cliente_id):
            resultado['motivo'] = 'Usuário não tem permissão para operar este cliente'
            resultado['operacoes_proibidas'] = ['todas']
            return resultado
            
        # Obter operações proibidas
        operacoes_proibidas = self.obter_operacoes_proibidas(usuario_id, cliente_id)
        resultado['operacoes_proibidas'] = operacoes_proibidas
        
        # Verificar se ação é permitida
        if acao in operacoes_proibidas:
            resultado['motivo'] = f'Ação "{acao}" é proibida para este usuário neste cliente'
            
            # Gerar recomendações
            cliente = self.obter_cliente(cliente_id)
            if cliente:
                responsavel = cliente.obter_principal_responsavel()
                if responsavel:
                    resultado['recomendacoes'].append(f'Contatar responsável principal: {responsavel.usuario_id}')
                    resultado['recomendacoes'].append(f'Solicitar autorização ao responsável')
        else:
            resultado['permitido'] = True
            resultado['motivo'] = 'Ação permitida'
            
        return resultado

# Instância global do gerenciamento de clientes
cliente_governanca = ClienteGovernanca()

def cadastrar_cliente(nome: str, usuario_responsavel: str, tipo_responsavel: TipoResponsavel = TipoResponsavel.CONSULTOR, **kwargs) -> str:
    """
    Função utilitária para cadastrar cliente.
    """
    cliente = Cliente(
        id_cliente=f"cliente_{int(datetime.now().timestamp())}",
        nome=nome,
        **kwargs
    )
    
    # Adicionar responsável inicial
    responsavel = ResponsavelCliente(
        usuario_id=usuario_responsavel,
        id_cliente=cliente.id_cliente,
        tipo=tipo_responsavel,
        data_inicio=datetime.now(),
        observacoes="Responsável inicial"
    )
    
    cliente.adicionar_responsavel(responsavel)
    cliente_governanca.cadastrar_cliente(cliente)
    
    return cliente.id_cliente