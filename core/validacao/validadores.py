"""
Precision VRT Solo — Validadores Globais

Validadores genéricos para uso em toda a infraestrutura.
Sem lógica de negócio.
"""

from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod

class ValidadorCampos:
    """
    Validador genérico de campos.
    Não faz lógica de negócio.
    """
    
    def __init__(self, regras: Dict[str, Any]):
        self.regras = regras
        
    def validar_campos(self, dados: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Valida campos conforme regras.
        Retorna erros, não corrige.
        """
        erros = {}
        
        for campo, regra in self.regras.items():
            if campo in dados:
                valor = dados[campo]
                erros_campos = self._validar_campo(campo, valor, regra)
                if erros_campos:
                    erros[campo] = erros_campos
            elif regra.get('obrigatorio', False):
                erros[campo] = [f"Campo obrigatório ausente: {campo}"]
                
        return erros
        
    def _validar_campo(self, campo: str, valor: Any, regra: Dict[str, Any]) -> List[str]:
        """
        Valida campo individualmente.
        """
        erros = []
        
        # Validação de tipo
        if 'tipo' in regra:
            if not isinstance(valor, regra['tipo']):
                erros.append(f"Tipo inválido para {campo}: esperado {regra['tipo'].__name__}, encontrado {type(valor).__name__}")
                
        # Validação de obrigatório
        if regra.get('obrigatorio', False) and valor is None:
            erros.append(f"Campo obrigatório não pode ser nulo: {campo}")
            
        # Validação de valores permitidos
        if 'permitido' in regra and valor not in regra['permitido']:
            erros.append(f"Valor não permitido para {campo}: {valor}")
            
        # Validação de tamanho mínimo
        if 'min_length' in regra and len(str(valor)) < regra['min_length']:
            erros.append(f"Valor para {campo} deve ter no mínimo {regra['min_length']} caracteres")
            
        # Validação de tamanho máximo
        if 'max_length' in regra and len(str(valor)) > regra['max_length']:
            erros.append(f"Valor para {campo} deve ter no máximo {regra['max_length']} caracteres")
            
        # Validação de valor mínimo
        if 'min_value' in regra and isinstance(valor, (int, float)) and valor < regra['min_value']:
            erros.append(f"Valor para {campo} deve ser no mínimo {regra['min_value']}")
            
        # Validação de valor máximo
        if 'max_value' in regra and isinstance(valor, (int, float)) and valor > regra['max_value']:
            erros.append(f"Valor para {campo} deve ser no máximo {regra['max_value']}")
            
        return erros

class ValidadorArquivos:
    """
    Validador genérico de arquivos.
    Não faz lógica de negócio.
    """
    
    def __init__(self):
        self.extensoes_suportadas = {
            'csv': 'text/csv',
            'pdf': 'application/pdf',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'geojson': 'application/geo+json',
            'tif': 'image/tiff',
            'tiff': 'image/tiff',
            'kml': 'application/vnd.google-earth.kml+xml',
            'kmz': 'application/vnd.google-earth.kmz'
        }
        
    def validar_arquivo(self, caminho_arquivo: str) -> Dict[str, List[str]]:
        """
        Valida arquivo genérico.
        Retorna erros, não corrige.
        """
        erros = {}
        
        try:
            import os
            import mimetypes
            
            # Verificar se arquivo existe
            if not os.path.exists(caminho_arquivo):
                erros['arquivo'] = [f"Arquivo não encontrado: {caminho_arquivo}"]
                return erros
                
            # Verificar extensão
            nome_arquivo = os.path.basename(caminho_arquivo)
            extensao = os.path.splitext(nome_arquivo)[1].lower().lstrip('.')
            
            if extensao not in self.extensoes_suportadas:
                erros['extensao'] = [f"Extensão não suportada: .{extensao}"]
                return erros
                
            # Verificar tamanho do arquivo
            tamanho = os.path.getsize(caminho_arquivo)
            if tamanho == 0:
                erros['tamanho'] = ["Arquivo está vazio"]
            elif tamanho > 100 * 1024 * 1024:  # 100MB
                erros['tamanho'] = ["Arquivo excede tamanho máximo permitido (100MB)"]
                
        except Exception as e:
            erros['geral'] = [f"Erro na validação do arquivo: {e}"]
            
        return erros

class ValidadorCoordenadas:
    """
    Validador genérico de coordenadas.
    Não faz lógica de negócio.
    """
    
    def validar_coordenadas(self, coordenadas: Dict[str, float]) -> List[str]:
        """
        Valida coordenadas geográficas.
        """
        erros = []
        
        if 'latitude' in coordenadas:
            lat = coordenadas['latitude']
            if not (-90 <= lat <= 90):
                erros.append(f"Latitude inválida: {lat} (deve estar entre -90 e 90)")
                
        if 'longitude' in coordenadas:
            lon = coordenadas['longitude']
            if not (-180 <= lon <= 180):
                erros.append(f"Longitude inválida: {lon} (deve estar entre -180 e 180)")
                
        if 'altitude' in coordenadas:
            alt = coordenadas['altitude']
            if alt < -500 or alt > 10000:  # Valores razoáveis
                erros.append(f"Altitude inválida: {alt} (deve estar entre -500 e 10000 metros)")
                
        return erros
        
    def validar_geometria(self, geometria: Dict[str, Any]) -> List[str]:
        """
        Valida estrutura de geometria.
        """
        erros = []
        
        if not isinstance(geometria, dict):
            erros.append("Geometria deve ser um dicionário")
            return erros
            
        if 'type' not in geometria:
            erros.append("Geometria deve ter campo 'type'")
            
        if 'coordinates' not in geometria:
            erros.append("Geometria deve ter campo 'coordinates'")
            
        # Validação básica de tipos de geometria
        tipo_geometria = geometria.get('type', '')
        tipos_validos = ['Point', 'LineString', 'Polygon', 'MultiPoint', 'MultiLineString', 'MultiPolygon']
        
        if tipo_geometria not in tipos_validos:
            erros.append(f"Tipo de geometria inválido: {tipo_geometria}")
            
        return erros

class ValidadorMetadados:
    """
    Validador genérico de metadados.
    Não faz lógica de negócio.
    """
    
    def __init__(self):
        self.metadados_obrigatorios = [
            'criado_em', 'criado_por', 'formato', 'versao'
        ]
        
    def validar_metadados(self, metadados: Dict[str, Any]) -> List[str]:
        """
        Valida metadados básicos.
        """
        erros = []
        
        for campo_obrigatorio in self.metadados_obrigatorios:
            if campo_obrigatorio not in metadados:
                erros.append(f"Metadado obrigatório ausente: {campo_obrigatorio}")
                
        # Validação de data
        if 'criado_em' in metadados:
            try:
                from datetime import datetime
                if not isinstance(metadados['criado_em'], (datetime, str)):
                    erros.append("Metadado 'criado_em' deve ser data ou string")
            except:
                erros.append("Metadado 'criado_em' inválido")
                
        return erros

# Instâncias globais
validador_campos = ValidadorCampos({})
validador_arquivos = ValidadorArquivos()
validador_coordenadas = ValidadorCoordenadas()
validador_metadados = ValidadorMetadados()

# Funções utilitárias
def configurar_regras_validacao_campos(regras: Dict[str, Any]) -> None:
    """
    Configura regras para validador de campos.
    """
    global validador_campos
    validador_campos = ValidadorCampos(regras)

def validar_dados_completos(dados: Dict[str, Any], metadados: Optional[Dict[str, Any]] = None) -> Dict[str, List[str]]:
    """
    Valida dados completos (dados + metadados).
    """
    erros = {}
    
    # Validar campos
    erros_campos = validador_campos.validar_campos(dados)
    if erros_campos:
        erros['campos'] = erros_campos
        
    # Validar metadados (se fornecidos)
    if metadados:
        erros_metadados = validador_metadados.validar_metadados(metadados)
        if erros_metadados:
            erros['metadados'] = erros_metadados
            
    return erros