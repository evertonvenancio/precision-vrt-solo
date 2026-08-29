"""
Precision VRT Solo — Hierarquia de Cargos e Perfis

Implementa hierarquia parametrizável para governança corporativa.
Não contém regras fixas.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

class Cargo(Enum):
    """Tipos de cargos do sistema."""
    DESENVOLVEDOR = "desenvolvedor"
    PROPRIETARIO = "proprietario"
    ADMINISTRADOR = "administrador"
    DIRETOR = "diretor"
    GERENTE = "gerente"
    SUPERVISOR = "supervisor"
    CONSULTOR = "consultor"
    TECNICO = "tecnico"
    FINANCEIRO = "financeiro"
    RH = "rh"
    COMERCIAL = "comercial"
    OPERADOR = "operador"
    CLIENTE = "cliente"

class Hierarquia:
    """
    Gerencia hierarquia de cargos parametrizável.
    Não contém regras fixas.
    """
    
    def __init__(self):
        self.cargos: Dict[Cargo, List[Cargo]] = {}
        self.perfis: Dict[str, 'PerfilGovernanca'] = {}
        self.niveis: Dict[Cargo, int] = {}
        
    def definir_relacionamento(self, cargo_pai: Cargo, cargo_filho: List[Cargo]):
        """
        Define relacionamento de hierarquia entre cargos.
        Não valida, apenas define.
        """
        self.cargos[cargo_pai] = cargo_filho
        
    def definir_niveis(self, cargos_niveis: Dict[Cargo, int]):
        """
        Define níveis hierárquicos.
        """
        self.niveis = cargos_niveis
        
    def obter_cargos_superiores(self, cargo: Cargo) -> List[Cargo]:
        """
        Obtém cargos superiores ao cargo informado.
        """
        superiores = []
        
        for cargo_pai, cargos_filhos in self.cargos.items():
            if cargo in cargos_filhos:
                superiores.append(cargo_pai)
                # Recursivamente obter superiores do pai
                superiores.extend(self.obter_cargos_superiores(cargo_pai))
                
        return list(set(superiores))  # Remover duplicatas
        
    def obter_cargos_inferiores(self, cargo: Cargo) -> List[Cargo]:
        """
        Obtém cargos inferiores ao cargo informado.
        """
        if cargo not in self.cargos:
            return []
            
        inferiores = self.cargos[cargo].copy()
        
        # Recursivamente obter inferiores dos filhos
        for filho in self.cargos[cargo]:
            inferiores.extend(self.obter_cargos_inferiores(filho))
            
        return list(set(inferiores))  # Remover duplicatas
        
    def pode_autorizar(self, cargo_autorizador: Cargo, cargo_solicitante: Cargo) -> bool:
        """
        Verifica se cargo pode autorizar operação de outro cargo.
        """
        return cargo_solicitante in self.obter_cargos_inferiores(cargo_autorizador)
        
    def obter_nivel(self, cargo: Cargo) -> int:
        """
        Obtém nível hierárquico do cargo.
        """
        return self.niveis.get(cargo, 0)
        
    def obter_todos_cargos(self) -> List[Cargo]:
        """
        Obtém todos os cargos definidos.
        """
        return list(Cargo)

class PerfilGovernanca:
    """
    Perfil de governança parametrizável.
    """
    
    def __init__(self,
                 nome: str,
                 cargo: Cargo,
                 permissoes: List[str],
                 limite_operacoes: Optional[Dict[str, int]] = None,
                 cliente_id: Optional[str] = None,
                 criado_por: Optional[str] = None):
        self.id = None
        self.nome = nome
        self.cargo = cargo
        self.permissoes = permissoes or []
        self.limite_operacoes = limite_operacoes or {}
        self.cliente_id = cliente_id
        self.criado_em = datetime.now()
        self.atualizado_em = datetime.now()
        self.criado_por = criado_por
        self.status = 'ativo'
        self.customizado = False
        
    def adicionar_permissao(self, permissao: str):
        """
        Adiciona permissão ao perfil.
        """
        if permissao not in self.permissoes:
            self.permissoes.append(permissao)
            self.atualizado_em = datetime.now()
            self.customizado = True
            
    def remover_permissao(self, permissao: str):
        """
        Remove permissão do perfil.
        """
        if permissao in self.permissoes:
            self.permissoes.remove(permissao)
            self.atualizado_em = datetime.now()
            self.customizado = True
            
    def definir_limite_operacao(self, operacao: str, limite: int):
        """
        Define limite para operação específica.
        """
        self.limite_operacoes[operacao] = limite
        self.atualizado_em = datetime.now()
        self.customizado = True
        
    def pode_executar(self, operacao: str) -> bool:
        """
        Verifica se perfil pode executar operação.
        """
        return operacao in self.permissoes
        
    def pode_executar_cliente(self, cliente_id: str) -> bool:
        """
        Verifica se perfil pode operar cliente específico.
        """
        return self.cliente_id is None or self.cliente_id == cliente_id
        
    def pode_executar_limite(self, operacao: str, quantidade: int) -> bool:
        """
        Verifica se operação respeita limite.
        """
        if operacao in self.limite_operacoes:
            return quantidade <= self.limite_operacoes[operacao]
        return True

class CargoSistema:
    """
    Representa cargo no sistema com configurações específicas.
    """
    
    def __init__(self, 
                 cargo: Cargo,
                 nome_exibicao: str,
                 descricao: Optional[str] = None,
                 permissoes_padrao: Optional[List[str]] = None,
                 limite_operacoes: Optional[Dict[str, int]] = None):
        self.cargo = cargo
        self.nome_exibicao = nome_exibicao
        self.descricao = descricao
        self.permissoes_padrao = permissoes_padrao or []
        self.limite_operacoes = limite_operacoes or {}
        self.ativo = True
        
    def obter_permissoes_padrao(self) -> List[str]:
        """
        Obtém permissões padrão do cargo.
        """
        return self.permissoes_padrao.copy()
        
    def obter_limite_operacoes(self) -> Dict[str, int]:
        """
        Obtém limites de operações do cargo.
        """
        return self.limite_operacoes.copy()

# Instância global da hierarquia
hierarquia_sistema = Hierarquia()

# Funções utilitárias para configuração inicial
def configurar_hierarquia_padrao():
    """
    Configura hierarquia padrão do sistema.
    """
    # Definir relacionamentos hierárquicos
    hierarquia_sistema.definir_relacionamento(
        Cargo.ADMINISTRADOR,
        [Cargo.DIRETOR, Cargo.GERENTE, Cargo.COMERCIAL]
    )
    
    hierarquia_sistema.definir_relacionamento(
        Cargo.DIRETOR,
        [Cargo.GERENTE, Cargo.SUPERVISOR, Cargo.FINANCEIRO, Cargo.RH]
    )
    
    hierarquia_sistema.definir_relacionamento(
        Cargo.GERENTE,
        [Cargo.SUPERVISOR, Cargo.TECNICO, Cargo.OPERADOR]
    )
    
    hierarquia_sistema.definir_relacionamento(
        Cargo.SUPERVISOR,
        [Cargo.TECNICO, Cargo.OPERADOR]
    )
    
    hierarquia_sistema.definir_relacionamento(
        Cargo.TECNICO,
        [Cargo.OPERADOR]
    )
    
    # Definir níveis hierárquicos
    niveis = {
        Cargo.ADMINISTRADOR: 10,
        Cargo.DIRETOR: 9,
        Cargo.GERENTE: 8,
        Cargo.SUPERVISOR: 7,
        Cargo.CONSULTOR: 6,
        Cargo.TECNICO: 5,
        Cargo.OPERADOR: 4,
        Cargo.FINANCEIRO: 8,
        Cargo.RH: 7,
        Cargo.COMERCIAL: 6,
        Cargo.PROPRIETARIO: 11,
        Cargo.DESENVOLVEDOR: 5,
        Cargo.CLIENTE: 1
    }
    
    hierarquia_sistema.definir_niveis(niveis)

def obter_perfil_padrao(cargo: Cargo) -> PerfilGovernanca:
    """
    Obtém perfil padrão para um cargo.
    """
    perfis_padrao = {
        Cargo.ADMINISTRADOR: PerfilGovernanca(
            "Administrador",
            Cargo.ADMINISTRADOR,
            ["visualizar", "criar", "editar", "excluir", "exportar", "importar", "aprovar", "rejeitar", "alterar_metodologia", "alterar_parametros", "alterar_precos", "alterar_produtos", "alterar_configuracoes", "cadastrar_usuarios", "liberar_descontos", "liberar_vendas", "liberar_clientes", "liberar_patrimonio", "liberar_financeiro", "liberar_rh", "liberar_crm", "liberar_integracoes", "liberar_modulos"],
            {"operacoes_criticas": 100, "vendas_diarias": 1000}
        ),
        Cargo.DIRETOR: PerfilGovernanca(
            "Diretor",
            Cargo.DIRETOR,
            ["visualizar", "criar", "editar", "aprovar", "rejeitar", "alterar_metodologia", "alterar_parametros", "liberar_descontos", "liberar_vendas"],
            {"operacoes_criticas": 50, "vendas_diarias": 500}
        ),
        Cargo.GERENTE: PerfilGovernanca(
            "Gerente",
            Cargo.GERENTE,
            ["visualizar", "criar", "editar", "exportar", "alterar_parametros", "liberar_descontos"],
            {"operacoes_criticas": 20, "vendas_diarias": 100}
        ),
        Cargo.SUPERVISOR: PerfilGovernanca(
            "Supervisor",
            Cargo.SUPERVISOR,
            ["visualizar", "criar", "editar", "exportar"],
            {"operacoes_criticas": 10, "vendas_diarias": 50}
        ),
        Cargo.CONSULTOR: PerfilGovernanca(
            "Consultor",
            Cargo.CONSULTOR,
            ["visualizar", "criar", "exportar"],
            {"operacoes_criticas": 5, "vendas_diarias": 20}
        ),
        Cargo.TECNICO: PerfilGovernanca(
            "Técnico",
            Cargo.TECNICO,
            ["visualizar", "criar"],
            {"operacoes_criticas": 2, "vendas_diarias": 10}
        ),
        Cargo.OPERADOR: PerfilGovernanca(
            "Operador",
            Cargo.OPERADOR,
            ["visualizar"],
            {"operacoes_criticas": 1, "vendas_diarias": 5}
        )
    }
    
    return perfis_padrao.get(cargo, PerfilGovernanca("Padrao", cargo, ["visualizar"]))

# Configurar hierarquia padrão na inicialização
configurar_hierarquia_padrao()