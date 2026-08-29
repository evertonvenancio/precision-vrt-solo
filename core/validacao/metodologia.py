"""
Precision VRT Solo — Validação de Metodologias

Responsável pela gestão de metodologias.
Não contém lógica de negócio.
"""

from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod

class Metodologia:
    """
    Representa uma metodologia do sistema.
    Apenas dados, não lógica.
    """
    
    def __init__(self, 
                 nome: str,
                 status: str = "rascunho",
                 descricao: Optional[str] = None,
                 referencia: Optional[str] = None,
                 parametros: Optional[Dict[str, Any]] = None):
        self.nome = nome
        self.status = status  # rascunho, revisao, aprovado
        self.descricao = descricao
        self.referencia = referencia
        self.parametros = parametros or {}
        self.criado_em = None
        self.atualizado_em = None
        
    def __str__(self):
        return f"Metodologia({self.nome}, {self.status})"

class MetodologiaPadrao(Metodologia):
    """
    Metodologia padrão do sistema.
    Apenas dados, não lógica.
    """
    
    def __init__(self, 
                 nome: str,
                 status: str = "aprovado",
                 descricao: Optional[str] = None,
                 referencia: Optional[str] = None,
                 parametros: Optional[Dict[str, Any]] = None):
        super().__init__(nome, status, descricao, referencia, parametros)
        self.tipo = "padrao"

class MetodologiaExcepcional(Metodologia):
    """
    Metodologia excepcional.
    Apenas dados, não lógica.
    """
    
    def __init__(self, 
                 nome: str,
                 status: str = "revisao",
                 descricao: Optional[str] = None,
                 referencia: Optional[str] = None,
                 parametros: Optional[Dict[str, Any]] = None):
        super().__init__(nome, status, descricao, referencia, parametros)
        self.tipo = "excepcional"

class ValidadorMetodologia:
    """
    Valida metodologias.
    Não altera, apenas valida.
    """
    
    def __init__(self):
        self.status_permitidos = ["rascunho", "revisao", "aprovado"]
        
    def validar_metodologia(self, metodologia: Metodologia) -> List[str]:
        """
        Valida metodologia.
        Retorna erros, não corrige.
        """
        erros = []
        
        # Validar nome
        if not metodologia.nome or not isinstance(metodologia.nome, str):
            erros.append("Nome da metodologia é obrigatório")
            
        # Validar status
        if metodologia.status not in self.status_permitidos:
            erros.append(f"Status inválido: {metodologia.status}. Status permitidos: {self.status_permitidos}")
            
        # Validar parâmetros obrigatórios para metodologia padrão
        if isinstance(metodologia, MetodologiaPadrao):
            if not metodologia.parametros:
                erros.append("Metodologia padrão deve ter parâmetros")
                
        return erros

class GerenciadorMetodologias:
    """
    Gerencia metodologias do sistema.
    Não contém lógica de negócio.
    """
    
    def __init__(self):
        self.metodologias: Dict[str, Metodologia] = {}
        self.validador = ValidadorMetodologia()
        
    def adicionar_metodologia(self, metodologia: Metodologia) -> bool:
        """
        Adiciona metodologia.
        Não faz validação de negócio.
        """
        # Validar primeiro
        erros = self.validador.validar_metodologia(metodologia)
        if erros:
            return False
            
        self.metodologias[metodologia.nome] = metodologia
        return True
        
    def obter_metodologia(self, nome: str) -> Optional[Metodologia]:
        """
        Obtém metodologia pelo nome.
        """
        return self.metodologias.get(nome)
        
    def listar_metodologias(self) -> List[Metodologia]:
        """
        Lista todas as metodologias.
        """
        return list(self.metodologias.values())
        
    def remover_metodologia(self, nome: str) -> bool:
        """
        Remove metodologia.
        """
        if nome in self.metodologias:
            del self.metodologias[nome]
            return True
        return False

# Instância global para uso da infraestrutura
gerenciador_metodologias = GerenciadorMetodologias()

# Métodos utilitários
def criar_metodologia_padrao(nome: str, 
                            descricao: Optional[str] = None,
                            referencia: Optional[str] = None,
                            parametros: Optional[Dict[str, Any]] = None) -> MetodologiaPadrao:
    """
    Cria metodologia padrão.
    Apenas infraestrutura.
    """
    return MetodologiaPadrao(nome, "aprovado", descricao, referencia, parametros)

def criar_metodologia_excepcional(nome: str,
                                 descricao: Optional[str] = None,
                                 referencia: Optional[str] = None,
                                 parametros: Optional[Dict[str, Any]] = None) -> MetodologiaExcepcional:
    """
    Cria metodologia excepcional.
    Apenas infraestrutura.
    """
    return MetodologiaExcepcional(nome, "revisao", descricao, referencia, parametros)

def obter_metodologia_padrao() -> Optional[MetodologiaPadrao]:
    """
    Obtém metodologia padrão do sistema.
    """
    for metodologia in gerenciador_metodologias.metodologias.values():
        if isinstance(metodologia, MetodologiaPadrao):
            return metodologia
    return None