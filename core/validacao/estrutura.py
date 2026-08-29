"""
Precision VRT Solo — Validação Estrutural

Responsável pela validação estrutural de arquivos e dados.
Sem lógica de negócio.
"""

import os
from typing import Any, Dict, List, Optional, Union
from abc import ABC, abstractmethod

class BaseValidadorEstrutural(ABC):
    """
    Classe base para validação estrutural.
    Contém apenas atributos e métodos de infraestrutura.
    """
    
    def __init__(self, dados: Any):
        self.dados = dados
        self.erros: List[str] = []
        self.validado: bool = False
        
    @abstractmethod
    def validar(self) -> bool:
        """
        Método abstrato para validação.
        Deve ser implementado por cada validador específico.
        """
        pass

class ArquivoVazio(BaseValidadorEstrutural):
    """
    Validador para verificar se arquivo está vazio.
    Apenas infraestrutura de validação.
    """
    
    def __init__(self, caminho_arquivo: str):
        super().__init__(None)
        self.caminho_arquivo = caminho_arquivo
        
    def validar(self) -> bool:
        """
        Verifica apenas se arquivo tem conteúdo.
        Não remove processamento.
        """
        try:
            tamanho = os.path.getsize(self.caminho_arquivo)
            if tamanho == 0:
                self.erros.append("Arquivo está vazio")
                self.validado = False
                return False
            self.validado = True
            return True
        except Exception as e:
            self.erros.append(f"Erro ao verificar arquivo vazio: {e}")
            self.validado = False
            return False

class ArquivoCorrompido(BaseValidadorEstrutural):
    """
    Validador para verificar se arquivo está corrompido.
    Apenas infraestrutura de validação.
    """
    
    def __init__(self, caminho_arquivo: str):
        super().__init__(None)
        self.caminho_arquivo = caminho_arquivo
        
    def validar(self) -> bool:
        """
        Verifica apenas se arquivo pode ser lido.
        Não analisa conteúdo.
        """
        try:
            with open(self.caminho_arquivo, 'rb') as f:
                f.read(1)  # Tentar ler 1 byte
            self.validado = True
            return True
        except Exception as e:
            self.erros.append(f"Arquivo corrompido: {e}")
            self.validado = False
            return False

class CampoObrigatorio(BaseValidadorEstrutural):
    """
    Validador para campos obrigatórios.
    Apenas infraestrutura de validação.
    """
    
    def __init__(self, dados: Dict[str, Any], campos_obrigatorios: List[str]):
        super().__init__(dados)
        self.campos_obrigatorios = campos_obrigatorios
        
    def validar(self) -> bool:
        """
        Verifica apenas se campos obrigatórios existem.
        Não valida valores.
        """
        try:
            if self.dados is None:
                self.erros.append("Dados não fornecidos")
                self.validado = False
                return False
                
            for campo in self.campos_obrigatorios:
                if campo not in self.dados:
                    self.erros.append(f"Campo obrigatório ausente: {campo}")
                    self.validado = False
                    return False
                    
            self.validado = True
            return True
        except Exception as e:
            self.erros.append(f"Erro na validação de campos obrigatórios: {e}")
            self.validado = False
            return False

class ColunaObrigatoria(BaseValidadorEstrutural):
    """
    Validador para colunas obrigatórias em dados tabulares.
    Apenas infraestrutura de validação.
    """
    
    def __init__(self, dados: List[Dict[str, Any]], colunas_obrigatorias: List[str]):
        super().__init__(dados)
        self.colunas_obrigatorias = colunas_obrigatorias
        
    def validar(self) -> bool:
        """
        Verifica apenas se colunas obrigatórias existem.
        Não valida dados.
        """
        try:
            if not self.dados:
                self.erros.append("Dados não fornecidos")
                self.validado = False
                return False
                
            # Verificar se pelo menos um registro existe
            if len(self.dados) == 0:
                self.erros.append("Nenhum registro encontrado")
                self.validado = False
                return False
                
            # Verificar colunas no primeiro registro
            primeiro_registro = self.dados[0]
            for coluna in self.colunas_obrigatorias:
                if coluna not in primeiro_registro:
                    self.erros.append(f"Coluna obrigatória ausente: {coluna}")
                    self.validado = False
                    return False
                    
            self.validado = True
            return True
        except Exception as e:
            self.erros.append(f"Erro na validação de colunas obrigatórias: {e}")
            self.validado = False
            return False

class DuplicidadeCampos(BaseValidadorEstrutural):
    """
    Validador para duplicidade de campos.
    Apenas infraestrutura de validação.
    """
    
    def __init__(self, dados: List[Dict[str, Any]]):
        super().__init__(dados)
        
    def validar(self) -> bool:
        """
        Verifica apenas se há campos duplicados.
        Não remove duplicatas.
        """
        try:
            if not self.dados:
                self.validado = True
                return True
                
            campos_encontrados = set()
            for i, registro in enumerate(self.dados):
                for campo in registro.keys():
                    if campo in campos_encontrados:
                        self.erros.append(f"Campo duplicado encontrado na linha {i+1}: {campo}")
                        self.validado = False
                        return False
                    campos_encontrados.add(campo)
                    
            self.validado = True
            return True
        except Exception as e:
            self.erros.append(f"Erro na validação de duplicidade: {e}")
            self.validado = False
            return False

class TiposIncompativeis(BaseValidadorEstrutural):
    """
    Validador para tipos de dados incompatíveis.
    Apenas infraestrutura de validação.
    """
    
    def __init__(self, dados: Dict[str, Any], tipos_esperados: Dict[str, type]):
        super().__init__(dados)
        self.tipos_esperados = tipos_esperados
        
    def validar(self) -> bool:
        """
        Verifica apenas se tipos são compatíveis.
        Não converte tipos.
        """
        try:
            if self.dados is None:
                self.validado = True
                return True
                
            for campo, tipo_esperado in self.tipos_esperados.items():
                if campo in self.dados:
                    valor = self.dados[campo]
                    if not isinstance(valor, tipo_esperado):
                        self.erros.append(f"Tipo incompatível para campo {campo}: esperado {tipo_esperado.__name__}, encontrado {type(valor).__name__}")
                        self.validado = False
                        return False
                        
            self.validado = True
            return True
        except Exception as e:
            self.erros.append(f"Erro na validação de tipos: {e}")
            self.validado = False
            return False

class CoordenadasInvalidas(BaseValidadorEstrutural):
    """
    Validador para coordenadas geográficas.
    Apenas infraestrutura de validação.
    """
    
    def __init__(self, coordenadas: Dict[str, float]):
        super().__init__(coordenadas)
        
    def validar(self) -> bool:
        """
        Verifica apenas se coordenadas estão em faixas válidas.
        Não processa coordenadas.
        """
        try:
            if self.dados is None:
                self.erros.append("Coordenadas não fornecidas")
                self.validado = False
                return False
                
            # Verificar latitude
            if 'latitude' in self.dados:
                lat = self.dados['latitude']
                if not (-90 <= lat <= 90):
                    self.erros.append(f"Latitude inválida: {lat}")
                    self.validado = False
                    return False
                    
            # Verificar longitude
            if 'longitude' in self.dados:
                lon = self.dados['longitude']
                if not (-180 <= lon <= 180):
                    self.erros.append(f"Longitude inválida: {lon}")
                    self.validado = False
                    return False
                    
            self.validado = True
            return True
        except Exception as e:
            self.erros.append(f"Erro na validação de coordenadas: {e}")
            self.validado = False
            return False

# Validador principal que orquestra todos os validadores
class ValidadorEstrutural:
    """
    Validador principal que combina múltiplos validadores.
    Apenas infraestrutura de orquestração.
    """
    
    def __init__(self):
        self.validadores: List[BaseValidadorEstrutural] = []
        
    def adicionar_validador(self, validador: BaseValidadorEstrutural):
        """
        Apenas adiciona validador à lista.
        Não executa validação.
        """
        self.validadores.append(validador)
        
    def validar_todos(self) -> bool:
        """
        Executa todos os validadores.
        Não inicia processamento se falhar.
        """
        try:
            for validador in self.validadores:
                if not validador.validar():
                    return False
            return True
        except Exception as e:
            self.erros = [f"Erro na orquestração de validação: {e}"]
            return False