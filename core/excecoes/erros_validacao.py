"""
Precision VRT Solo — Erros de Validação

Exceções específicas para falhas na validação.
Não contém lógica de negócio.
"""

from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod

class ErroValidacao(Exception, ABC):
    """
    Classe base para erros de validação.
    """
    
    def __init__(self, mensagem: str, detalhes: Optional[Dict[str, Any]] = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.detalhes = detalhes or {}
        
    def __str__(self):
        return f"ErroValidacao: {self.mensagem}"
        
    def obter_detalhes(self) -> Dict[str, Any]:
        """
        Retorna detalhes do erro.
        """
        return self.detalhes.copy()

class ErroArquivoVazio(ErroValidacao):
    """
    Erro quando arquivo está vazio.
    """
    
    def __init__(self, caminho_arquivo: str):
        super().__init__(
            f"Arquivo está vazio: {caminho_arquivo}",
            {'caminho_arquivo': caminho_arquivo, 'tipo': 'arquivo_vazio'}
        )

class ErroArquivoCorrompido(ErroValidacao):
    """
    Erro quando arquivo está corrompido.
    """
    
    def __init__(self, caminho_arquivo: str, motivo: str):
        super().__init__(
            f"Arquivo corrompido: {caminho_arquivo} - {motivo}",
            {'caminho_arquivo': caminho_arquivo, 'motivo': motivo, 'tipo': 'arquivo_corrompido'}
        )

class ErroCampoObrigatorioAusente(ErroValidacao):
    """
    Erro quando campo obrigatório está ausente.
    """
    
    def __init__(self, campo: str, contexto: Optional[str] = None):
        mensagem = f"Campo obrigatório ausente: {campo}"
        if contexto:
            mensagem += f" (contexto: {contexto})"
            
        detalhes = {
            'campo': campo,
            'tipo': 'campo_obrigatorio_ausente'
        }
        if contexto:
            detalhes['contexto'] = contexto
            
        super().__init__(mensagem, detalhes)

class ErroColunaObrigatoriaAusente(ErroValidacao):
    """
    Erro quando coluna obrigatória está ausente em dados tabulares.
    """
    
    def __init__(self, coluna: str, linha: int = 0):
        mensagem = f"Coluna obrigatória ausente: {coluna}"
        if linha > 0:
            mensagem += f" (linha {linha})"
            
        detalhes = {
            'coluna': coluna,
            'linha': linha,
            'tipo': 'coluna_obrigatoria_ausente'
        }
        
        super().__init__(mensagem, detalhes)

class ErroDuplicidadeCampos(ErroValidacao):
    """
    Erro quando há duplicidade de campos.
    """
    
    def __init__(self, campos: List[str], linha: int):
        mensagem = f"Campos duplicados encontrados: {', '.join(campos)} (linha {linha})"
        
        detalhes = {
            'campos': campos,
            'linha': linha,
            'tipo': 'duplicidade_campos'
        }
        
        super().__init__(mensagem, detalhes)

class ErroTiposIncompativeis(ErroValidacao):
    """
    Erro quando tipos de dados são incompatíveis.
    """
    
    def __init__(self, campo: str, tipo_esperado: type, tipo_encontrado: type):
        mensagem = f"Tipo incompatível para campo '{campo}': esperado {tipo_esperado.__name__}, encontrado {tipo_encontrado.__name__}"
        
        detalhes = {
            'campo': campo,
            'tipo_esperado': tipo_esperado.__name__,
            'tipo_encontrado': tipo_encontrado.__name__,
            'tipo': 'tipos_incompativeis'
        }
        
        super().__init__(mensagem, detalhes)

class ErroCoordenadasInvalidas(ErroValidacao):
    """
    Erro quando coordenadas geográficas são inválidas.
    """
    
    def __init__(self, coordenada: str, valor: float, faixa_min: float, faixa_max: float):
        mensagem = f"Coordenada inválida: {coordenada} = {valor} (deve estar entre {faixa_min} e {faixa_max})"
        
        detalhes = {
            'coordenada': coordenada,
            'valor': valor,
            'faixa_min': faixa_min,
            'faixa_max': faixa_max,
            'tipo': 'coordenadas_invalidas'
        }
        
        super().__init__(mensagem, detalhes)

class ErroUnidadeInvalida(ErroValidacao):
    """
    Erro quando unidade de medida é inválida.
    """
    
    def __init__(self, unidade: str, campo: Optional[str] = None, linha: Optional[int] = None):
        mensagem = f"Unidade inválida: {unidade}"
        if campo:
            mensagem += f" (campo: {campo})"
        if linha:
            mensagem += f" (linha: {linha})"
            
        detalhes = {
            'unidade': unidade,
            'tipo': 'unidade_invalida'
        }
        if campo:
            detalhes['campo'] = campo
        if linha:
            detalhes['linha'] = linha
            
        super().__init__(mensagem, detalhes)

class ErroUnidadeNaoSuportada(ErroValidacao):
    """
    Erro quando unidade de medida não é suportada pelo sistema.
    """
    
    def __init__(self, unidade: str, campo: Optional[str] = None, linha: Optional[int] = None):
        mensagem = f"Unidade não suportada: {unidade}"
        if campo:
            mensagem += f" (campo: {campo})"
        if linha:
            mensagem += f" (linha: {linha})"
            
        detalhes = {
            'unidade': unidade,
            'tipo': 'unidade_nao_suportada'
        }
        if campo:
            detalhes['campo'] = campo
        if linha:
            detalhes['linha'] = linha
            
        super().__init__(mensagem, detalhes)

class ErroSemUnidadeExplicita(ErroValidacao):
    """
    Erro quando campo requer unidade explícita mas não tem.
    """
    
    def __init__(self, campo: str, valor: Union[int, float], linha: Optional[int] = None):
        mensagem = f"Campo '{campo}' requer unidade explícita: {valor} (sem unidade)"
        if linha:
            mensagem += f" (linha {linha})"
            
        detalhes = {
            'campo': campo,
            'valor': valor,
            'tipo': 'sem_unidade_explicita'
        }
        if linha:
            detalhes['linha'] = linha
            
        super().__init__(mensagem, detalhes)

class ErroValidacaoEstrutura(ErroValidacao):
    """
    Erro genérico de validação estrutural.
    """
    
    def __init__(self, mensagem: str, estrutura: Optional[Dict[str, Any]] = None):
        detalhes = {
            'tipo': 'validacao_estrutura'
        }
        if estrutura:
            detalhes['estrutura'] = estrutura
            
        super().__init__(mensagem, detalhes)

class ErroValidacaoUnidade(ErroValidacao):
    """
    Erro genérico de validação de unidades.
    """
    
    def __init__(self, mensagem: str, mapeamento: Optional[Dict[str, Any]] = None):
        detalhes = {
            'tipo': 'validacao_unidade'
        }
        if mapeamento:
            detalhes['mapeamento'] = mapeamento
            
        super().__init__(mensagem, detalhes)

class ErroValidacaoMetodologia(ErroValidacao):
    """
    Erro genérico de validação de metodologia.
    """
    
    def __init__(self, mensagem: str, metodologia: Optional[str] = None):
        detalhes = {
            'tipo': 'validacao_metodologia'
        }
        if metodologia:
            detalhes['metodologia'] = metodologia
            
        super().__init__(mensagem, detalhes)

# Validador global para lançamento de erros
class LancadorErrosValidacao:
    """
    Utilitário para lançar erros de validação consistentes.
    """
    
    @staticmethod
    def arquivo_vazio(caminho_arquivo: str):
        """Lança erro de arquivo vazio."""
        raise ErroArquivoVazio(caminho_arquivo)
        
    @staticmethod
    def arquivo_corrompido(caminho_arquivo: str, motivo: str):
        """Lança erro de arquivo corrompido."""
        raise ErroArquivoCorrompido(caminho_arquivo, motivo)
        
    @staticmethod
    def campo_obrigatorio_ausente(campo: str, contexto: Optional[str] = None):
        """Lança erro de campo obrigatório ausente."""
        raise ErroCampoObrigatorioAusente(campo, contexto)
        
    @staticmethod
    def coluna_obrigatoria_ausente(coluna: str, linha: int = 0):
        """Lança erro de coluna obrigatória ausente."""
        raise ErroColunaObrigatoriaAusente(coluna, linha)
        
    @staticmethod
    def duplicidade_campos(campos: List[str], linha: int):
        """Lança erro de duplicidade de campos."""
        raise ErroDuplicidadeCampos(campos, linha)
        
    @staticmethod
    def tipos_incompativeis(campo: str, tipo_esperado: type, tipo_encontrado: type):
        """Lança erro de tipos incompatíveis."""
        raise ErroTiposIncompativeis(campo, tipo_esperado, tipo_encontrado)
        
    @staticmethod
    def coordenadas_invalidas(coordenada: str, valor: float, faixa_min: float, faixa_max: float):
        """Lança erro de coordenadas inválidas."""
        raise ErroCoordenadasInvalidas(coordenada, valor, faixa_min, faixa_max)
        
    @staticmethod
    def unidade_invalida(unidade: str, campo: Optional[str] = None, linha: Optional[int] = None):
        """Lança erro de unidade inválida."""
        raise ErroUnidadeInvalida(unidade, campo, linha)
        
    @staticmethod
    def unidade_nao_suportada(unidade: str, campo: Optional[str] = None, linha: Optional[int] = None):
        """Lança erro de unidade não suportada."""
        raise ErroUnidadeNaoSuportada(unidade, campo, linha)
        
    @staticmethod
    def sem_unidade_explicita(campo: str, valor: Union[int, float], linha: Optional[int] = None):
        """Lança erro de sem unidade explícita."""
        raise ErroSemUnidadeExplicita(campo, valor, linha)

# Instância global
lancador_erros = LancadorErrosValidacao()

# Funções utilitárias
def validar_e_lancar_erro(valido: bool, erro_class, *args, **kwargs):
    """
    Valida condição e lança erro se falhar.
    """
    if not valido:
        raise erro_class(*args, **kwargs)