"""
Precision VRT Solo — Serviço de Validação

Serviço responsável apenas por validação básica de parâmetros.
Nunca contém regras agronômicas ou lógica de negócio.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import re
import json

logger = logging.getLogger(__name__)


class ValidacaoService:
    """
    Serviço de validação básica.
    Responsável apenas por verificar:
    - parâmetros obrigatórios
    - existência de arquivos
    - formatos suportados
    
    NUNCA valida regras agronômicas.
    """
    
    def __init__(self):
        self.formatos_suportados = {
            # Formatos de imagem
            'JPG', 'JPEG', 'PNG', 'TIF', 'TIFF', 'GIF', 'BMP',
            # Formatos de vetor
            'SHP', 'KML', 'KMZ', 'GEOJSON',
            # Formatos de dados
            'CSV', 'XLS', 'XLSX', 'PDF', 'TXT', 'JSON'
        }
        
        self.fontes_dados_suportadas = {
            'SATÉLITE', 'DRONE', 'SENSOR_TERRESTRE', 'ARQUIVO_LOCAL'
        }
    
    def validar_parametros_obrigatorios(self, 
                                       parametros: Dict[str, Any],
                                       campos_obrigatorios: List[str]) -> Dict[str, Any]:
        """
        Verifica se todos os parâmetros obrigatórios estão presentes.
        
        Args:
            parametros: Dicionário de parâmetros a serem validados
            campos_obrigatorios: Lista de campos obrigatórios
            
        Returns:
            Resultado da validação
        """
        try:
            ausentes = []
            
            for campo in campos_obrigatorios:
                if campo not in parametros or parametros[campo] is None:
                    ausentes.append(campo)
            
            if ausentes:
                return {
                    'valid': False,
                    'error': f'Campos obrigatórios ausentes: {", ".join(ausentes)}',
                    'ausentes': ausentes,
                    'mensagem': 'Faltam parâmetros obrigatórios'
                }
            
            return {
                'valid': True,
                'mensagem': 'Todos os parâmetros obrigatórios estão presentes'
            }
            
        except Exception as e:
            logger.error(f"Erro ao validar parâmetros: {e}")
            return {
                'valid': False,
                'error': str(e),
                'mensagem': 'Falha na validação de parâmetros'
            }
    
    def validar_existencia_arquivo(self, 
                                 caminho_arquivo: str,
                                 obrigatorio: bool = True) -> Dict[str, Any]:
        """
        Verifica se o arquivo existe e é acessível.
        
        Args:
            caminho_arquivo: Caminho do arquivo a ser validado
            obrigatorio: Se True, falha se arquivo não existir
            
        Returns:
            Resultado da validação
        """
        try:
            if not caminho_arquivo:
                if obrigatorio:
                    return {
                        'valid': False,
                        'error': 'Caminho do arquivo não especificado',
                        'mensagem': 'Caminho do arquivo é obrigatório'
                    }
                else:
                    return {
                        'valid': True,
                        'mensagem': 'Arquivo opcional não especificado'
                    }
            
            if not Path(caminho_arquivo).exists():
                if obrigatorio:
                    return {
                        'valid': False,
                        'error': f'Arquivo não encontrado: {caminho_arquivo}',
                        'mensagem': 'Arquivo obrigatório não encontrado'
                    }
                else:
                    return {
                        'valid': True,
                        'mensagem': 'Arquivo opcional não encontrado (aceitável)'
                    }
            
            # Verificar se pode ser lido
            try:
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    f.read(100)  # Ler apenas para verificar acesso
            except Exception as e:
                return {
                    'valid': False,
                    'error': f'Arquivo não pode ser lido: {e}',
                    'mensagem': 'Arquivo encontrado mas inacessível'
                }
            
            return {
                'valid': True,
                'caminho': caminho_arquivo,
                'mensagem': 'Arquivo existe e é acessível'
            }
            
        except Exception as e:
            logger.error(f"Erro ao validar arquivo: {e}")
            return {
                'valid': False,
                'error': str(e),
                'mensagem': 'Falha na validação do arquivo'
            }
    
    def validar_formato_arquivo(self, 
                              arquivo_path: str,
                              formatos_esperados: List[str]) -> Dict[str, Any]:
        """
        Verifica se o arquivo possui formato suportado.
        
        Args:
            arquivo_path: Caminho do arquivo a ser validado
            formatos_esperados: Lista de formatos esperados
            
        Returns:
            Resultado da validação
        """
        try:
            if not arquivo_path:
                return {
                    'valid': False,
                    'error': 'Caminho do arquivo não especificado',
                    'mensagem': 'Caminho do arquivo é obrigatório'
                }
            
            path = Path(arquivo_path)
            
            if not path.exists():
                return {
                    'valid': False,
                    'error': f'Arquivo não encontrado: {arquivo_path}',
                    'mensagem': 'Arquivo não existe'
                }
            
            # Extrair extensão
            extensao = path.suffix.upper().replace('.', '')
            
            if extensao not in formatos_esperados:
                return {
                    'valid': False,
                    'error': f'Formato não suportado: {extensao}. Esperado: {", ".join(formatos_esperados)}',
                    'mensagem': 'Formato de arquivo inválido'
                }
            
            return {
                'valid': True,
                'extensao': extensao,
                'mensagem': f'Formato suportado: {extensao}'
            }
            
        except Exception as e:
            logger.error(f"Erro ao validar formato: {e}")
            return {
                'valid': False,
                'error': str(e),
                'mensagem': 'Falha na validação do formato'
            }
    
    def validar_formato_geojson(self, geojson_path: str) -> Dict[str, Any]:
        """
        Valida se o arquivo é um GeoJSON válido.
        
        Args:
            geojson_path: Caminho do arquivo GeoJSON
            
        Returns:
            Resultado da validação
        """
        try:
            resultado = self.validar_existencia_arquivo(geojson_path)
            if not resultado['valid']:
                return resultado
            
            import json
            
            with open(geojson_path, 'r', encoding='utf-8') as f:
                try:
                    dados = json.load(f)
                except json.JSONDecodeError as e:
                    return {
                        'valid': False,
                        'error': f'JSON inválido: {e}',
                        'mensagem': 'Arquivo não é um JSON válido'
                    }
            
            # Verificar estrutura básica do GeoJSON
            if not isinstance(dados, dict):
                return {
                    'valid': False,
                    'error': 'GeoJSON deve ser um objeto JSON',
                    'mensagem': 'Arquivo não tem estrutura de GeoJSON'
                }
            
            if 'type' not in dados:
                return {
                    'valid': False,
                    'error': 'GeoJSON deve ter campo "type"',
                    'mensagem': 'Arquivo não é um GeoJSON válido'
                }
            
            return {
                'valid': True,
                'type': dados['type'],
                'mensagem': 'Arquivo GeoJSON válido'
            }
            
        except Exception as e:
            logger.error(f"Erro ao validar GeoJSON: {e}")
            return {
                'valid': False,
                'error': str(e),
                'mensagem': 'Falha na validação do GeoJSON'
            }
    
    def validar_formatos_genericos(self, 
                                  arquivo_path: str,
                                  formatos_genericos: List[str] = None) -> Dict[str, Any]:
        """
        Valida formatos genéricos (não específicos como GeoJSON).
        
        Args:
            arquivo_path: Caminho do arquivo
            formatos_genericos: Lista de formatos genéricos
            
        Returns:
            Resultado da validação
        """
        if formatos_genericos is None:
            formatos_genericos = ['CSV', 'XLS', 'XLSX', 'PDF', 'TXT', 'JSON']
        
        return self.validar_formato_arquivo(arquivo_path, formatos_genericos)
    
    def validar_campo_json(self, 
                          valor: Any,
                          campo: str,
                          esperado_type: type = None) -> Dict[str, Any]:
        """
        Valida campo JSON básico.
        
        Args:
            valor: Valor a ser validado
            campo: Nome do campo
            esperado_type: Tipo esperado (opcional)
            
        Returns:
            Resultado da validação
        """
        try:
            if valor is None:
                return {
                    'valid': False,
                    'error': f'Campo {campo} é nulo',
                    'mensagem': 'Campo obrigatório nulo'
                }
            
            if esperado_type and not isinstance(valor, esperado_type):
                return {
                    'valid': False,
                    'error': f'Campo {campo} deve ser do tipo {esperado_type.__name__}',
                    'mensagem': 'Tipo de campo inválido'
                }
            
            return {
                'valid': True,
                'mensagem': f'Campo {campo} válido'
            }
            
        except Exception as e:
            logger.error(f"Erro ao validar campo JSON: {e}")
            return {
                'valid': False,
                'error': str(e),
                'mensagem': 'Falha na validação do campo'
            }
    
    def validar_dados_csv_basico(self, csv_path: str) -> Dict[str, Any]:
        """
        Valida estrutura básica de arquivo CSV.
        
        Args:
            csv_path: Caminho do arquivo CSV
            
        Returns:
            Resultado da validação
        """
        try:
            resultado = self.validar_existencia_arquivo(csv_path)
            if not resultado['valid']:
                return resultado
            
            import csv
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                try:
                    reader = csv.reader(f)
                    primeira_linha = next(reader, None)
                    
                    if not primeira_linha:
                        return {
                            'valid': False,
                            'error': 'Arquivo CSV está vazio',
                            'mensagem': 'Arquivo CSV não tem cabeçalho'
                        }
                    
                    return {
                        'valid': True,
                        'colunas': len(primeira_linha),
                        'mensagem': 'Arquivo CSV válido'
                    }
                    
                except Exception as e:
                    return {
                        'valid': False,
                        'error': f'Erro ao ler CSV: {e}',
                        'mensagem': 'Arquivo CSV inválido'
                    }
                    
        except Exception as e:
            logger.error(f"Erro ao validar CSV: {e}")
            return {
                'valid': False,
                'error': str(e),
                'mensagem': 'Falha na validação do CSV'
            }