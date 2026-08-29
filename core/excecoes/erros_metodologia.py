"""
Precision VRT Solo — Erros de Metodologia

Exceções específicas para falhas na gestão de metodologias.
Não contém lógica de negócio.
"""

from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod

class ErroMetodologia(Exception, ABC):
    """
    Classe base para erros de metodologia.
    """
    
    def __init__(self, mensagem: str, detalhes: Optional[Dict[str, Any]] = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.detalhes = detalhes or {}
        
    def __str__(self):
        return f"ErroMetodologia: {self.mensagem}"
        
    def obter_detalhes(self) -> Dict[str, Any]:
        """
        Retorna detalhes do erro.
        """
        return self.detalhes.copy()

class ErroMetodologiaNaoEncontrada(ErroMetodologia):
    """
    Erro quando metodologia não é encontrada.
    """
    
    def __init__(self, nome_metodologia: str):
        super().__init__(
            f"Metodologia não encontrada: {nome_metodologia}",
            {'nome_metodologia': nome_metodologia, 'tipo': 'metodologia_nao_encontrada'}
        )

class ErroMetodologiaInvalida(ErroMetodologia):
    """
    Erro quando metodologia é inválida.
    """
    
    def __init__(self, nome_metodologia: str, erros: List[str]):
        mensagem = f"Metodologia inválida: {nome_metodologia}"
        if erros:
            mensagem += f" - {', '.join(erros)}"
            
        super().__init__(
            mensagem,
            {
                'nome_metodologia': nome_metodologia,
                'erros': erros,
                'tipo': 'metodologia_invalida'
            }
        )

class ErroMetodologiaPadrao(ErroMetodologia):
    """
    Erro quando metodologia padrão não pode ser alterada diretamente.
    """
    
    def __init__(self, nome_metodologia: str):
        super().__init__(
            f"Metodologia padrão não pode ser alterada diretamente: {nome_metodologia}. Use fluxo de autorização.",
            {
                'nome_metodologia': nome_metodologia,
                'tipo': 'metodologia_padrao'
            }
        )

class ErroMetodologiaExcepcional(ErroMetodologia):
    """
    Erro quando metodologia excepcional requer autorização.
    """
    
    def __init__(self, nome_metodologia: str, motivo: str):
        mensagem = f"Metodologia excepcional requer autorização: {nome_metodologia}"
        if motivo:
            mensagem += f" - {motivo}"
            
        super().__init__(
            mensagem,
            {
                'nome_metodologia': nome_metodologia,
                'motivo': motivo,
                'tipo': 'metodologia_excepcional'
            }
        )

class ErroStatusMetodologiaInvalido(ErroMetodologia):
    """
    Erro quando status da metodologia é inválido.
    """
    
    def __init__(self, status_atual: str, status_permitidos: List[str]):
        mensagem = f"Status inválido: {status_atual}. Status permitidos: {', '.join(status_permitidos)}"
        
        super().__init__(
            mensagem,
            {
                'status_atual': status_atual,
                'status_permitidos': status_permitidos,
                'tipo': 'status_metodologia_invalido'
            }
        )

class ErroMetodologiaJaExiste(ErroMetodologia):
    """
    Erro quando metodologia já existe.
    """
    
    def __init__(self, nome_metodologia: str):
        super().__init__(
            f"Metodologia já existe: {nome_metodologia}",
            {
                'nome_metodologia': nome_metodologia,
                'tipo': 'metodologia_ja_existe'
            }
        )

class ErroMetodologiaDependencia(ErroMetodologia):
    """
    Erro quando metodologia possui dependências não resolvidas.
    """
    
    def __init__(self, nome_metodologia: str, dependencias: List[str]):
        mensagem = f"Metodologia possui dependências não resolvidas: {nome_metodologia}"
        if dependencias:
            mensagem += f" - {', '.join(dependencias)}"
            
        super().__init__(
            mensagem,
            {
                'nome_metodologia': nome_metodologia,
                'dependencias': dependencias,
                'tipo': 'metodologia_dependencia'
            }
        )

class ErroMetodologiaParametroObrigatorio(ErroMetodologia):
    """
    Erro quando parâmetro obrigatório não está presente na metodologia.
    """
    
    def __init__(self, nome_metodologia: str, parametro: str):
        super().__init__(
            f"Parâmetro obrigatório ausente na metodologia '{nome_metodologia}': {parametro}",
            {
                'nome_metodologia': nome_metodologia,
                'parametro': parametro,
                'tipo': 'metodologia_parametro_obrigatorio'
            }
        )

class ErroMetodologiaParametroInvalido(ErroMetodologia):
    """
    Erro quando parâmetro da metodologia é inválido.
    """
    
    def __init__(self, nome_metodologia: str, parametro: str, valor: Any, motivo: str):
        mensagem = f"Parâmetro inválido na metodologia '{nome_metodologia}': {parametro} = {valor} - {motivo}"
        
        super().__init__(
            mensagem,
            {
                'nome_metodologia': nome_metodologia,
                'parametro': parametro,
                'valor': valor,
                'motivo': motivo,
                'tipo': 'metodologia_parametro_invalido'
            }
        )

class ErroMetodologiaVersao(ErroMetodologia):
    """
    Erro quando versão da metodologia é inválida.
    """
    
    def __init__(self, nome_metodologia: str, versao_atual: int, versao_solicitada: int):
        mensagem = f"Versão inválida para metodologia '{nome_metodologia}': solicitada {versao_solicitada}, disponível {versao_atual}"
        
        super().__init__(
            mensagem,
            {
                'nome_metodologia': nome_metodologia,
                'versao_atual': versao_atual,
                'versao_solicitada': versao_solicitada,
                'tipo': 'metodologia_versao'
            }
        )

class ErroMetodologiaNaoPadrao(ErroMetodologia):
    """
    Erro quando operação requer metodologia padrão mas é excepcional.
    """
    
    def __init__(self, nome_metodologia: str):
        super().__init__(
            f"Operação requer metodologia padrão, mas '{nome_metodologia}' é excepcional",
            {
                'nome_metodologia': nome_metodologia,
                'tipo': 'metodologia_nao_padrao'
            }
        )

class ErroMetodologiaNaoExcepcional(ErroMetodologia):
    """
    Erro quando operação requer metodologia excepcional mas é padrão.
    """
    
    def __init__(self, nome_metodologia: str):
        super().__init__(
            f"Operação requer metodologia excepcional, mas '{nome_metodologia}' é padrão",
            {
                'nome_metodologia': nome_metodologia,
                'tipo': 'metodologia_nao_excepcional'
            }
        )

class ErroMetodologiaConflito(ErroMetodologia):
    """
    Erro quando há conflito entre metodologias.
    """
    
    def __init__(self, nome_metodologia1: str, nome_metodologia2: str, motivo: str):
        mensagem = f"Conflito entre metodologias '{nome_metodologia1}' e '{nome_metodologia2}': {motivo}"
        
        super().__init__(
            mensagem,
            {
                'nome_metodologia1': nome_metodologia1,
                'nome_metodologia2': nome_metodologia2,
                'motivo': motivo,
                'tipo': 'metodologia_conflito'
            }
        )

# Validador global para lançamento de erros de metodologia
class LancadorErrosMetodologia:
    """
    Utilitário para lançar erros de metodologia consistentes.
    """
    
    @staticmethod
    def metodologia_nao_encontrada(nome_metodologia: str):
        """Lança erro de metodologia não encontrada."""
        raise ErroMetodologiaNaoEncontrada(nome_metodologia)
        
    @staticmethod
    def metodologia_invalida(nome_metodologia: str, erros: List[str]):
        """Lança erro de metodologia inválida."""
        raise ErroMetodologiaInvalida(nome_metodologia, erros)
        
    @staticmethod
    def metodologia_padrao(nome_metodologia: str):
        """Lança erro de metodologia padrão."""
        raise ErroMetodologiaPadrao(nome_metodologia)
        
    @staticmethod
    def metodologia_excepcional(nome_metodologia: str, motivo: str = ""):
        """Lança erro de metodologia excepcional."""
        raise ErroMetodologiaExcepcional(nome_metodologia, motivo)
        
    @staticmethod
    def status_metodologia_invalido(status_atual: str, status_permitidos: List[str]):
        """Lança erro de status inválido."""
        raise ErroStatusMetodologiaInvalido(status_atual, status_permitidos)
        
    @staticmethod
    def metodologia_ja_existe(nome_metodologia: str):
        """Lança erro de metodologia já existe."""
        raise ErroMetodologiaJaExiste(nome_metodologia)
        
    @staticmethod
    def metodologia_dependencia(nome_metodologia: str, dependencias: List[str]):
        """Lança erro de dependência não resolvida."""
        raise ErroMetodologiaDependencia(nome_metodologia, dependencias)
        
    @staticmethod
    def metodologia_parametro_obrigatorio(nome_metodologia: str, parametro: str):
        """Lança erro de parâmetro obrigatório ausente."""
        raise ErroMetodologiaParametroObrigatorio(nome_metodologia, parametro)
        
    @staticmethod
    def metodologia_parametro_invalido(nome_metodologia: str, parametro: str, valor: Any, motivo: str):
        """Lança erro de parâmetro inválido."""
        raise ErroMetodologiaParametroInvalido(nome_metodologia, parametro, valor, motivo)
        
    @staticmethod
    def metodologia_versao(nome_metodologia: str, versao_atual: int, versao_solicitada: int):
        """Lança erro de versão inválida."""
        raise ErroMetodologiaVersao(nome_metodologia, versao_atual, versao_solicitada)
        
    @staticmethod
    def metodologia_nao_padrao(nome_metodologia: str):
        """Lança erro de metodologia não padrão."""
        raise ErroMetodologiaNaoPadrao(nome_metodologia)
        
    @staticmethod
    def metodologia_nao_excepcional(nome_metodologia: str):
        """Lança erro de metodologia não excepcional."""
        raise ErroMetodologiaNaoExcepcional(nome_metodologia)
        
    @staticmethod
    def metodologia_conflito(nome_metodologia1: str, nome_metodologia2: str, motivo: str):
        """Lança erro de conflito entre metodologias."""
        raise ErroMetodologiaConflito(nome_metodologia1, nome_metodologia2, motivo)

# Instância global
lancador_erros_metodologia = LancadorErrosMetodologia()

# Funções utilitárias
def validar_metodologia_e_lancar_erro(valido: bool, erro_class, *args, **kwargs):
    """
    Valida condição de metodologia e lança erro se falhar.
    """
    if not valido:
        raise erro_class(*args, **kwargs)

def formatar_mensagem_metodologia(nome_metodologia: str, operacao: str, detalhes: Optional[str] = None) -> str:
    """
    Formata mensagem de erro de metodologia.
    """
    mensagem = f"Falha na operação '{operacao}' na metodologia '{nome_metodologia}'"
    if detalhes:
        mensagem += f": {detalhes}"
    return mensagem