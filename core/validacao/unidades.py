"""
Precision VRT Solo — Validação de Unidades

Responsável pela identificação e normalização de unidades de medida.
Não faz conversões, apenas identifica unidades.
"""

from typing import Dict, List, Optional, Union, Any
from abc import ABC, abstractmethod

# Unidades canônicas definidas pelo sistema
UNIDADES_CANONICAS = {
    'cmolc/dm3': 'cmolc/dm3',
    'mmolc/dm3': 'mmolc/dm3', 
    'mg/dm3': 'mg/dm3',
    'ppm': 'ppm',
    '%': 'porcentagem',
    'g/dm3': 'g/dm3',
    'kg/ha': 'kg/ha',
    't/ha': 't/ha',
    'cm': 'cm',
    'm': 'm',
    'ha': 'ha',
    'km2': 'km2'
}

class IdentificadorUnidades:
    """
    Identifica unidades de medida em dados.
    Não faz conversões, apenas identifica.
    """
    
    def __init__(self):
        self.padroes_reconhecidos = {
            'cmolc/dm3': ['cmolc/dm3', 'cmolc/dm³', 'cmolc/dm^3'],
            'mmolc/dm3': ['mmolc/dm3', 'mmolc/dm³', 'mmolc/dm^3'],
            'mg/dm3': ['mg/dm3', 'mg/dm³', 'mg/dm^3'],
            'ppm': ['ppm', 'mg/kg'],
            '%': ['%', 'porcentagem'],
            'g/dm3': ['g/dm3', 'g/dm³', 'g/dm^3'],
            'kg/ha': ['kg/ha', 'kg/ha-1'],
            't/ha': ['t/ha', 't/ha-1'],
            'cm': ['cm', 'centimetro'],
            'm': ['m', 'metro'],
            'ha': ['ha', 'hectare'],
            'km2': ['km2', 'km²', 'km^2']
        }
        
    def identificar_unidade(self, valor: Any, contexto: Optional[str] = None) -> Optional[str]:
        """
        Identifica unidade de medida em um valor.
        Não deduz, não assume, não inventa unidades.
        """
        if valor is None:
            return None
            
        # Se for string, tentar identificar padrão
        if isinstance(valor, str):
            valor_limpo = valor.strip().lower()
            
            for unidade_canonica, padroes in self.padroes_reconhecidos.items():
                for padrao in padroes:
                    if padrao in valor_limpo:
                        return unidade_canonica
                        
        # Se for numérico, sem unidade explícita
        elif isinstance(valor, (int, float)):
            # Sem unidade explícita - não pode deduzir
            if contexto:
                return None  # Informa que não tem unidade no contexto
            return None
            
        return None
        
    def validar_unidade(self, unidade: str) -> bool:
        """
        Verifica se unidade é suportada pelo sistema.
        """
        return unidade in UNIDADES_CANONICAS
        
    def get_unidades_suportadas(self) -> List[str]:
        """
        Retorna lista de unidades suportadas.
        """
        return list(UNIDADES_CANONICAS.keys())

class ValidadorUnidades:
    """
    Valida unidades de medida em dados.
    Não faz conversões.
    """
    
    def __init__(self):
        self.identificador = IdentificadorUnidades()
        
    def validar_dados_com_unidades(self, dados: Dict[str, Any], mapeamento_unidades: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Valida unidades em dados estruturados.
        Retorna erros, não corrige.
        """
        erros = {}
        
        for campo, unidade_esperada in mapeamento_unidades.items():
            if campo in dados:
                valor = dados[campo]
                unidade_encontrada = self.identificador.identificar_unidade(valor)
                
                # Se unidade encontrada não corresponde à esperada
                if unidade_encontrada and unidade_encontrada != unidade_esperada:
                    erros[campo] = [
                        f"Unidade inválida: esperado {unidade_esperada}, encontrado {unidade_encontrada}"
                    ]
                # Se unidade não for suportada
                elif unidade_encontrada and not self.identificador.validar_unidade(unidade_encontrada):
                    erros[campo] = [
                        f"Unidade não suportada: {unidade_encontrada}"
                    ]
                # Se não tem unidade e é obrigatório
                elif unidade_esperada and unidade_encontrada is None and isinstance(valor, (int, float)):
                    erros[campo] = [
                        f"Campo requer unidade explícita: {campo}={valor} (sem unidade)"
                    ]
                    
        return erros
        
    def validar_linha_com_unidade(self, linha: int, dados: Dict[str, Any], nutrientes: Dict[str, Any]) -> List[str]:
        """
        Valida unidades específicas para linhas de dados.
        Relata erros exatos (linha, coluna, nutriente).
        """
        erros = []
        
        for nutriente, unidade_esperada in nutrientes.items():
            if nutriente in dados:
                valor = dados[nutriente]
                unidade_encontrada = self.identificador.identificar_unidade(valor)
                
                # Validação estrita: sem unidade não é permitido
                if unidade_encontrada is None and isinstance(valor, (int, float)):
                    erros.append(
                        f"Linha {linha}: nutriente '{nutriente}' não tem unidade - valor: {valor}"
                    )
                # Validação de unidade incorreta
                elif unidade_encontrada and unidade_encontrada != unidade_esperada:
                    erros.append(
                        f"Linha {linha}: nutriente '{nutriente}' unidade inválida - esperado: {unidade_esperada}, encontrado: {unidade_encontrada}"
                    )
                # Unidade não suportada
                elif unidade_encontrada and not self.identificador.validar_unidade(unidade_encontrada):
                    erros.append(
                        f"Linha {linha}: nutriente '{nutriente}' unidade não suportada: {unidade_encontrada}"
                    )
                    
        return erros

class NormalizadorUnidades:
    """
    Prepara unidades para normalização.
    Não faz conversões, apenas prepara estrutura.
    """
    
    def __init__(self):
        self.unidades_canonicas = UNIDADES_CANONICAS
        
    def prepara_normalizacao(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepara estrutura para normalização.
        Não executa conversões.
        """
        estrutura_normalizacao = {
            'dados_originais': dados,
            'unidades_identificadas': {},
            'unidades_canonicas': self.unidades_canonicas,
            'conversoes_necessarias': {},
            'dados_normalizados': None  # Será preenchido após conversão
        }
        
        # Identificar unidades existentes
        for chave, valor in dados.items():
            unidade = IdentificadorUnidades().identificar_unidade(valor)
            if unidade:
                estrutura_normalizacao['unidades_identificadas'][chave] = unidade
                
        return estrutura_normalizacao
        
    def verifica_conversao_necessaria(self, unidade_original: str, unidade_alvo: str) -> bool:
        """
        Verifica se conversão é necessária.
        Não executa conversão.
        """
        return unidade_original != unidade_alvo and unidade_original in self.unidades_canonicas

class UnidadeCanonica:
    """
    Representa uma unidade canônica do sistema.
    Apenas dados, não lógica.
    """
    
    def __init__(self, nome: str, simbolo: str, descricao: str = ""):
        self.nome = nome
        self.simbolo = simbolo
        self.descricao = descricao
        
    def __str__(self):
        return f"{self.nome} ({self.simbolo})"

# Instâncias globais para uso da infraestrutura
identificador_unidades = IdentificadorUnidades()
validador_unidades = ValidadorUnidades()
normalizador_unidades = NormalizadorUnidades()

# Constantes de unidades
cmolc_dm3 = 'cmolc/dm3'
mmolc_dm3 = 'mmolc/dm3'
mg_dm3 = 'mg/dm3'
ppm = 'ppm'
porcentagem = '%'
g_dm3 = 'g/dm3'
kg_ha = 'kg/ha'
t_ha = 't/ha'