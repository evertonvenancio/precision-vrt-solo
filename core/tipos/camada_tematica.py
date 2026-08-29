
"""
Precision VRT Solo - Camada Tématica (Compatibilidade)

Classe base para camadas temáticas do sistema VRT.
"""

from typing import Dict, Any, Optional, List
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon
from enum import Enum

class TipoCamada(Enum):
    """Tipos de camadas temáticas."""
    INDICE_ESPECTRAL = "indice_espectral"
    AMOSTRAGEM = "amostragem"
    LIMITES_TALHAO = "limites_talhao"
    PREVISAO = "previsao"
    RESULTADO = "resultado"

class TipoIndice(Enum):
    """Tipos de índices espectrais."""
    NDVI = "ndvi"
    EVI = "evi"
    SAVI = "savi"
    GNDVI = "gndvi"
    NDRE = "ndre"

class CamadaTematica:
    """
    Classe base para camadas temáticas do sistema VRT.
    Implementação simplificada para compatibilidade.
    """
    
    def __init__(self, nome: str, tipo: TipoCamada, geometria: gpd.GeoDataFrame, crs: Optional[str] = None):
        """
        Inicializa uma camada temática.
        
        Args:
            nome: Nome da camada
            tipo: Tipo da camada
            geometria: GeoDataFrame com os dados
            crs: Sistema de coordenadas
        """
        self.nome = nome
        self.tipo = tipo
        self.geometria = geometria
        self.crs = crs or geometria.crs if geometria is not None else None
        self.metadados = {}
        
    def adicionar_metadados(self, chave: str, valor: Any):
        """Adiciona metadados à camada."""
        self.metadados[chave] = valor
        
    def obter_metadados(self, chave: str) -> Any:
        """Obtém metadados da camada."""
        return self.metadados.get(chave)
        
    def __repr__(self) -> str:
        return f"CamadaTematica(nome='{self.nome}', tipo={self.tipo.value}, crs={self.crs})"

# Funções utilitárias para compatibilidade
def criar_camada_indice_espectral(nome: str, geometria: gpd.GeoDataFrame, 
                                  tipo_indice: TipoIndice = TipoIndice.NDVI) -> CamadaTematica:
    """
    Cria uma camada de índice espectral.
    
    Args:
        nome: Nome da camada
        geometria: GeoDataFrame com os dados
        tipo_indice: Tipo de índice
        
    Returns:
        CamadaTematica
    """
    camada = CamadaTematica(nome, TipoCamada.INDICE_ESPECTRAL, geometria)
    camada.adicionar_metadados('tipo_indice', tipo_indice.value)
    return camada

def criar_camada_amostragem(nome: str, geometria: gpd.GeoDataFrame) -> CamadaTematica:
    """
    Cria uma camada de amostragem.
    
    Args:
        nome: Nome da camada
        geometria: GeoDataFrame com os dados
        
    Returns:
        CamadaTematica
    """
    return CamadaTematica(nome, TipoCamada.AMOSTRAGEM, geometria)

def criar_camada_limites_talhao(nome: str, geometria: gpd.GeoDataFrame) -> CamadaTematica:
    """
    Cria uma camada de limites de talhão.
    
    Args:
        nome: Nome da camada
        geometria: GeoDataFrame com os dados
        
    Returns:
        CamadaTematica
    """
    return CamadaTematica(nome, TipoCamada.LIMITES_TALHAO, geometria)

# Interface para compatibilidade
class CamadaTematicaInterface:
    """
    Interface para camadas temáticas (compatibilidade com imports antigos).
    """
    pass

# Instância para compatibilidade
FabricaCamadasTematicas = {
    'indice_espectral': criar_camada_indice_espectral,
    'amostragem': criar_camada_amostragem,
    'limites_talhao': criar_camada_limites_talhao
}

__all__ = [
    'CamadaTematica',
    'CamadaTematicaInterface',
    'TipoCamada',
    'TipoIndice',
    'FabricaCamadasTematicas',
    'criar_camada_indice_espectral',
    'criar_camada_amostragem',
    'criar_camada_limites_talhao'
]
