"""
Precision VRT Solo — Motor de Interpolação da Compactação

Implementa interpolação de dados de compactação sobre uma grade regular.
Utiliza métodos espaciais específicos para análise de compactação.
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

from ...tipos.geoespacial import Coordenada, Bounds
from ...tipos.base import ConfigBase, ResultadoBase
from ..compactacao.contratos import PontoAmostral, PerfilCompactacao


@dataclass
class ConfigInterpolacaoCompactacao(ConfigBase):
    """Configuração para interpolação de compactação."""
    
    # Parâmetros de interpolação
    metodo: str = "kriging"  # kriging, idw, natural_neighbor
    resolucao_grade: float = 50.0  # metros
    max_distancia: float = 100.0  # metros
    
    # Parâmetros do variograma (para kriging)
    variograma_modelo: str = "spherical"
    variograma_sill: float = 1.0
    variograma_range: float = 50.0
    variograma_nugget: float = 0.1
    
    # Parâmetros do IDW
    idw_power: float = 2.0
    
    def __post_init__(self):
        """Valida configuração."""
        if self.metodo not in ["kriging", "idw", "natural_neighbor"]:
            raise ValueError(f"Método de interpolação inválido: {self.metodo}")


@dataclass
class ResultadoInterpolacaoCompactacao:
    """Resultado da interpolação de compactação."""
    
    # Campos obrigatórios primeiro (sem valores padrão)
    valores_interpolados: np.ndarray
    coordenadas_grade: List[Tuple[float, float]]
    pontos_originais: List[PontoAmostral]
    configuracao_usada: ConfigInterpolacaoCompactacao
    
    # Campos opcionais (valores padrão)
    timestamp: datetime = field(default_factory=datetime.now)
    tempo_execucao_ms: float = 0.0
    config: Optional[ConfigBase] = None
    grade_regular: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte resultado para dicionário serializável."""
        resultado_base = super().to_dict()
        
        # Adicionar campos específicos
        resultado_base.update({
            "grade_regular": {
                "resolucao": self.configuracao_usada.resolucao_grade,
                "bounds": self.grade_regular.get("bounds"),
                "shape": self.valores_interpolados.shape
            },
            "estatisticas": {
                "minimo": float(np.min(self.valores_interpolados)),
                "maximo": float(np.max(self.valores_interpolados)),
                "media": float(np.mean(self.valores_interpolados)),
                "desvio_padrao": float(np.std(self.valores_interpolados))
            },
            "metodo": self.configuracao_usada.metodo,
            "pontos_originais": len(self.pontos_originais)
        })
        
        return resultado_base


class MotorInterpolacaoCompactacao:
    """
    Motor de interpolação específico para compactação do solo.
    
    Realiza interpolação de resistência à penetração sobre uma grade regular,
        considerando especificidades da análise de compactação.
    """
    
    def __init__(self, config: ConfigInterpolacaoCompactacao):
        self.config = config
        self.pontos_originais: List[PontoAmostral] = []
    
    def adicionar_ponto(self, ponto: PontoAmostral):
        """Adiciona ponto para interpolação."""
        self.pontos_originais.append(ponto)
    
    def adicionar_pontos(self, pontos: List[PontoAmostral]):
        """Adiciona múltiplos pontos para interpolação."""
        self.pontos_originais.extend(pontos)
    
    def interpolar(self, bounds: Bounds) -> ResultadoInterpolacaoCompactacao:
        """
        Realiza interpolação sobre uma grade regular.
        
        Args:
            bounds: Limites espaciais para interpolação
            
        Returns:
            Resultado com grade interpolada
        """
        if not self.pontos_originais:
            raise ValueError("Nenhum ponto adicionado para interpolação")
        
        # Gerar grade regular
        grade_info = self._gerar_grade_regular(bounds)
        coordenadas_grade = grade_info["coordenadas"]
        shape_grade = grade_info["shape"]
        
        # Extrair coordenadas e valores dos pontos
        coords_originais = np.array([
            [p.coordenada.longitude, p.coordenada.latitude] 
            for p in self.pontos_originais
        ])
        
        # Para interpolação, usamos a resistência máxima por ponto
        valores_originais = np.array([
            max(camada.resistencia_mpa for camada in p.camadas) 
            if p.camadas else 0.0 
            for p in self.pontos_originais
        ])
        
        # Realizar interpolação com base no método
        if self.config.metodo == "kriging":
            valores_interpolados = self._interpolar_kriging(
                coords_originais, valores_originais, coordenadas_grade
            )
        elif self.config.metodo == "idw":
            valores_interpolados = self._interpolar_idw(
                coords_originais, valores_originais, coordenadas_grade
            )
        else:  # natural_neighbor
            valores_interpolados = self._interpolar_natural_neighbor(
                coords_originais, valores_originais, coordenadas_grade
            )
        
        # Reshape para grade 2D
        valores_interpolados = valores_interpolados.reshape(shape_grade)
        
        return ResultadoInterpolacaoCompactacao(
            timestamp=grade_info["timestamp"],
            tempo_execucao_ms=0.0,  # Será preenchido posteriormente
            config=self.config,
            grade_regular=grade_info,
            valores_interpolados=valores_interpolados,
            coordenadas_grade=coordenadas_grade,
            pontos_originais=self.pontos_originais
        )
    
    def _gerar_grade_regular(self, bounds: Bounds) -> Dict[str, Any]:
        """Gera grade regular sobre os bounds especificados."""
        # Calcular número de pontos na grade
        res = self.config.resolucao_grade
        
        # Converter bounds para coordenadas
        min_lon, min_lat = bounds.min_lon, bounds.min_lat
        max_lon, max_lat = bounds.max_lon, bounds.max_lat
        
        # Número de pontos em cada dimensão
        n_lon = int((max_lon - min_lon) / res) + 1
        n_lat = int((max_lat - min_lat) / res) + 1
        
        # Gerar coordenadas da grade
        coordenadas = []
        for i in range(n_lat):
            for j in range(n_lon):
                lon = min_lon + j * res
                lat = min_lat + i * res
                coordenadas.append((lon, lat))
        
        return {
            "bounds": bounds,
            "resolucao": res,
            "shape": (n_lat, n_lon),
            "coordenadas": coordenadas,
            "timestamp": None  # Será preenchido no ResultadoBase
        }
    
    def _interpolar_kriging(self, coords_originais: np.ndarray, 
                           valores_originais: np.ndarray, 
                           coordenadas_grade: List[Tuple[float, float]]) -> np.ndarray:
        """Implementação simplificada de kriging."""
        # Versão simplificada - implementação real precisaria de bibliotecas como PyKrige
        n_pontos = len(coordenadas_grade)
        resultado = np.zeros(n_pontos)
        
        for i, (lon_grade, lat_grade) in enumerate(coordenadas_grade):
            # Calcular distâncias a todos os pontos originais
            distancias = np.sqrt(
                (coords_originais[:, 0] - lon_grade)**2 + 
                (coords_originais[:, 1] - lat_grade)**2
            )
            
            # Filtrar pontos dentro da distância máxima
            dentro_faixa = distancias <= self.config.max_distancia
            
            if np.any(dentro_faixa):
                # Ponderar inversamente pela distância
                pesos = 1.0 / (distancias[dentro_faixa] + 1e-10)
                pesos = pesos / np.sum(pesos)
                
                # Interpolar
                resultado[i] = np.sum(valores_originais[dentro_faixa] * pesos)
            else:
                # Se não houver pontos próximos, usar valor médio
                resultado[i] = np.mean(valores_originais)
        
        return resultado
    
    def _interpolar_idw(self, coords_originais: np.ndarray, 
                       valores_originais: np.ndarray, 
                       coordenadas_grade: List[Tuple[float, float]]) -> np.ndarray:
        """Implementação de Inverse Distance Weighting (IDW)."""
        n_pontos = len(coordenadas_grade)
        resultado = np.zeros(n_pontos)
        power = self.config.idw_power
        
        for i, (lon_grade, lat_grade) in enumerate(coordenadas_grade):
            # Calcular distâncias a todos os pontos originais
            distancias = np.sqrt(
                (coords_originais[:, 0] - lon_grade)**2 + 
                (coords_originais[:, 1] - lat_grade)**2
            )
            
            # Filtrar pontos dentro da distância máxima
            dentro_faixa = distancias <= self.config.max_distancia
            
            if np.any(dentro_faixa):
                # Ponderar inversamente pela distância elevada à potência
                pesos = 1.0 / (distancias[dentro_faixa]**power + 1e-10)
                pesos = pesos / np.sum(pesos)
                
                # Interpolar
                resultado[i] = np.sum(valores_originais[dentro_faixa] * pesos)
            else:
                # Se não houver pontos próximos, usar valor médio
                resultado[i] = np.mean(valores_originais)
        
        return resultado
    
    def _interpolar_natural_neighbor(self, coords_originais: np.ndarray, 
                                  valores_originais: np.ndarray, 
                                  coordenadas_grade: List[Tuple[float, float]]) -> np.ndarray:
        """Implementação simplificada de natural neighbor."""
        # Versão simplificada usando interpolação linear básica
        return self._interpolar_idw(coords_originais, valores_originais, coordenadas_grade)