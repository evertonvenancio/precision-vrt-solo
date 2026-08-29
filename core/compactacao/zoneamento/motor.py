"""
Precision VRT Solo — Motor de Zoneamento da Compactação

Biblioteca científica pura para zoneamento de compactação agrícola.

Recebe camadas de dados de compactação e entrega zonas
com base em critérios específicos de resistência do solo.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from ...tipos.geoespacial import Bounds
from ...tipos.base import ConfigBase, ResultadoBase
from ..compactacao.contratos import PontoAmostral, PerfilCompactacao
from ..interpolacao.motor import ResultadoInterpolacaoCompactacao


class MetodoZoneamento(Enum):
    """Métodos disponíveis para zoneamento."""
    KMEANS = "kmeans"
    DBSCAN = "dbscan"
    AGLOMERATIVO = "aglomerativo"


class EstrategiaFusao(Enum):
    """Estratégias para fusão de zonas."""
    MANUAL = "manual"
    AUTOMATICO = "automatico"


@dataclass
class ConfigZoneamentoCompactacao(ConfigBase):
    """Configuração para zoneamento de compactação."""
    
    # Parâmetros de zoneamento
    metodo: MetodoZoneamento = MetodoZoneamento.KMEANS
    n_zonas: int = 5
    estrategia_fusao: EstrategiaFusao = EstrategiaFusao.MANUAL
    
    # Parâmetros dos algoritmos
    dbscan_eps: float = 50.0  # metros
    dbscan_min_samples: int = 3
    
    # Parâmetros de qualidade
    minimo_pontos_zona: int = 5
    maximo_variancia_zona: float = 0.3
    
    # Thresholds de classificação
    threshold_impedimento: float = 2.5  # MPa
    threshold_restricao: float = 2.0   # MPa
    
    def __post_init__(self):
        """Valida configuração."""
        if self.metodo == MetodoZoneamento.DBSCAN and self.n_zonas > 0:
            raise ValueError("Para DBSCAN, n_zonas deve ser 0 (automático)")
        
        if self.metodo != MetodoZoneamento.DBSCAN and self.n_zonas <= 0:
            raise ValueError("Para KMeans/Aglomerativo, n_zonas deve ser > 0")


@dataclass
class ZonaCompactacao:
    """Representa uma zona de compactação."""
    
    id: int
    pontos: List[Tuple[float, float]]  # coordenadas
    resistencia_media: float
    resistencia_min: float
    resistencia_max: float
    classificacao_predominante: str
    area_ha: float
    centroid_lon: float
    centroid_lat: float
    
    def calcular_similaridade(self, outra_zona: "ZonaCompactacao") -> float:
        """Calcula similaridade entre duas zonas."""
        # Similaridade baseada em resistência média e variação
        diff_resistencia = abs(self.resistencia_media - outra_zona.resistencia_media)
        diff_variancia = abs((self.resistencia_max - self.resistencia_min) - 
                           (outra_zona.resistencia_max - outra_zona.resistencia_min))
        
        # Normalizar (0 a 1, onde 1 é mais similar)
        res_similar = 1.0 - min(diff_resistencia / 2.0, 1.0)
        var_similar = 1.0 - min(diff_variancia / 2.0, 1.0)
        
        return (res_similar + var_similar) / 2.0


@dataclass
class ResultadoZoneamentoCompactacao:
    """Resultado do zoneamento de compactação."""
    
    # Campos obrigatórios primeiro
    zonas: List[ZonaCompactacao]
    matriz_similaridade: np.ndarray
    classificacao_predominante: str
    percentual_impedimento: float
    percentual_restricao: float
    percentual_apto: float
    recomendacao_geral: str
    
    # Campos opcionais
    mapa_final: Optional[Dict[str, Any]] = None
    zonas_suavizadas: Optional[List[ZonaCompactacao]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte resultado para dicionário serializável."""
        return {
            "total_zonas": len(self.zonas),
            "classificacao_predominante": self.classificacao_predominante,
            "percentuais": {
                "impedimento": self.percentual_impedimento,
                "restricao": self.percentual_restricao,
                "apto": self.percentual_apto
            },
            "recomendacao_geral": self.recomendacao_geral,
            "zonas": [
                {
                    "id": z.id,
                    "resistencia_media": z.resistencia_media,
                    "resistencia_min": z.resistencia_min,
                    "resistencia_max": z.resistance_max,
                    "classificacao_predominante": z.classificacao_predominante,
                    "area_ha": z.area_ha,
                    "centroid": [z.centroid_lon, z.centroid_lat]
                }
                for z in self.zonas
            ],
            "estatisticas": {
                "resistencia_media_global": np.mean([z.resistencia_media for z in self.zonas]),
                "area_total_ha": sum(z.area_ha for z in self.zonas)
            }
        }


class MotorZoneamentoCompactacao:
    """
    Motor de zoneamento específico para compactação do solo.
    
    Implementa algoritmos de clusterização para criar zonas homogêneas
    de compactação com base em resistência à penetração.
    """
    
    def __init__(self, config: ConfigZoneamentoCompactacao):
        self.config = config
        self.pontos_originais: List[Tuple[float, float, float]] = []  # (lon, lat, resistencia)
        self.resultado: Optional[ResultadoZoneamentoCompactacao] = None
    
    def adicionar_dados_interpolacao(self, resultado_interpolacao: ResultadoInterpolacaoCompactacao):
        """Adiciona dados interpolados para zoneamento."""
        # Extrair coordenadas e valores da grade interpolada
        lon_lat_coords = resultado_interpolacao.coordenadas_grade
        valores_grade = resultado_interpolacao.valores_interpolados.flatten()
        
        # Criar lista de pontos (lon, lat, resistencia)
        pontos = []
        for i, (lon, lat) in enumerate(lon_lat_coords):
            if i < len(valores_grade):
                resistencia = valores_grade[i]
                if not np.isnan(resistencia):  # Ignorar valores NaN
                    pontos.append((lon, lat, resistencia))
        
        self.pontos_originais = pontos
    
    def zonear(self) -> ResultadoZoneamentoCompactacao:
        """
        Executa o zoneamento dos dados.
        
        Returns:
            Resultado com zonas criadas
        """
        if not self.pontos_originais:
            raise ValueError("Nenhum dado disponível para zoneamento")
        
        # Preparar dados para clusterização
        dados = np.array([
            [ponto[0], ponto[1], ponto[2]]  # lon, lat, resistencia
            for ponto in self.pontos_originais
        ])
        
        # Executar algoritmo de clusterização
        if self.config.metodo == MetodoZoneamento.KMEANS:
            zonas = self._zonear_kmeans(dados)
        elif self.config.metodo == MetodoZoneamento.DBSCAN:
            zonas = self._zonear_dbscan(dados)
        else:  # AGLOMERATIVO
            zonas = self._zonear_aglomerativo(dados)
        
        # Calcular estatísticas gerais
        stats = self._calcular_estatisticas_gerais(zonas)
        
        # Criar resultado
        self.resultado = ResultadoZoneamentoCompactacao(
            timestamp=None,  # Será preenchido no ResultadoBase
            tempo_execucao_ms=0.0,
            config=self.config,
            zonas=zonas,
            matriz_similaridade=self._calcular_matriz_similaridade(zonas),
            classificacao_predominante=stats["classificacao_predominante"],
            percentual_impedimento=stats["percentual_impedimento"],
            percentual_restricao=stats["percentual_restricao"],
            percentual_apto=stats["percentual_apto"],
            recomendacao_geral=stats["recomendacao_geral"]
        )
        
        return self.resultado
    
    def _zonear_kmeans(self, dados: np.ndarray) -> List[ZonaCompactacao]:
        """Zoneamento usando K-Means."""
        from sklearn.cluster import KMeans
        
        # Extrair coordenadas e resistências
        coords = dados[:, :2]  # lon, lat
        resistencias = dados[:, 2]  # resistencia
        
        # Aplicar K-Me nas coordenadas espaciais
        kmeans = KMeans(n_clusters=self.config.n_zonas, random_state=42)
        labels = kmeans.fit_predict(coords)
        
        # Criar zonas
        zonas = []
        for i in range(self.config.n_zonas):
            pontos_zona = dados[labels == i]
            
            if len(pontos_zona) < self.config.minimo_pontos_zona:
                continue  # Ignorar zonas muito pequenas
            
            resistencia_zona = pontos_zona[:, 2]
            lon_zona = pontos_zona[:, 0]
            lat_zona = pontos_zona[:, 1]
            
            zona = self._criar_zona(
                id=i,
                lon_coords=lon_zona,
                lat_coords=lat_zona,
                resistencias=resistencia_zona
            )
            zonas.append(zona)
        
        return zonas
    
    def _zonear_dbscan(self, dados: np.ndarray) -> List[ZonaCompactacao]:
        """Zoneamento usando DBSCAN."""
        from sklearn.cluster import DBSCAN
        
        # Extrair coordenadas
        coords = dados[:, :2]  # lon, lat
        
        # Converter epsilon de metros para graus (aproximação)
        eps_graus = self.config.dbscan_eps / 111320.0  # 1 grau ≈ 111.32 km
        
        # Aplicar DBSCAN
        dbscan = DBSCAN(eps=eps_graus, min_samples=self.config.dbscan_min_samples)
        labels = dbscan.fit_predict(coords)
        
        # Ignar pontos de ruído (label = -1)
        unique_labels = set(labels) - {-1}
        
        zonas = []
        for label in unique_labels:
            pontos_zona = dados[labels == label]
            
            if len(pontos_zona) < self.config.minimo_pontos_zona:
                continue
            
            resistencia_zona = pontos_zona[:, 2]
            lon_zona = pontos_zona[:, 0]
            lat_zona = pontos_zona[:, 1]
            
            zona = self._criar_zona(
                id=label,
                lon_coords=lon_zona,
                lat_coords=lat_zona,
                resistencias=resistencia_zona
            )
            zonas.append(zona)
        
        return zonas
    
    def _zonear_aglomerativo(self, dados: np.ndarray) -> List[ZonaCompactacao]:
        """Zoneamento usando clustering aglomerativo."""
        from sklearn.cluster import AgglomerativeClustering
        
        # Extrair coordenadas
        coords = dados[:, :2]  # lon, lat
        
        # Aplicar clustering aglomerativo
        clustering = AgglomerativeClustering(
            n_clusters=self.config.n_zonas,
            linkage='ward'
        )
        labels = clustering.fit_predict(coords)
        
        # Criar zonas
        zonas = []
        for i in range(self.config.n_zonas):
            pontos_zona = dados[labels == i]
            
            if len(pontos_zona) < self.config.minimo_pontos_zona:
                continue
            
            resistencia_zona = pontos_zona[:, 2]
            lon_zona = pontos_zona[:, 0]
            lat_zona = pontos_zona[:, 1]
            
            zona = self._criar_zona(
                id=i,
                lon_coords=lon_zona,
                lat_coords=lat_zona,
                resistencias=resistencia_zona
            )
            zonas.append(zona)
        
        return zonas
    
    def _criar_zona(self, id: int, lon_coords: np.ndarray, 
                   lat_coords: np.ndarray, resistencias: np.ndarray) -> ZonaCompactacao:
        """Cria uma zona a partir de coordenadas e resistências."""
        # Calcular estatísticas
        resistencia_media = np.mean(resistencias)
        resistencia_min = np.min(resistencias)
        resistencia_max = np.max(resistencias)
        
        # Determinar classificação predominante
        classificacao = self._classificar_resistencia(resistencia_media)
        
        # Calcular área (aproximada)
        area_ha = self._calcular_area_ha(lon_coords, lat_coords)
        
        # Calcular centróide
        centroid_lon = np.mean(lon_coords)
        centroid_lat = np.mean(lat_coords)
        
        return ZonaCompactacao(
            id=id,
            pontos=list(zip(lon_coords, lat_coords)),
            resistencia_media=resistencia_media,
            resistencia_min=resistencia_min,
            resistencia_max=resistencia_max,
            classificacao_predominante=classificacao,
            area_ha=area_ha,
            centroid_lon=centroid_lon,
            centroid_lat=centroid_lat
        )
    
    def _classificar_resistencia(self, resistencia: float) -> str:
        """Classifica resistência com base nos thresholds."""
        if resistencia >= self.config.threshold_impedimento:
            return "impedimento_severo"
        elif resistance >= self.config.threshold_restricao:
            return "restricao"
        else:
            return "apto"
    
    def _calcular_area_ha(self, lon_coords: np.ndarray, lat_coords: np.ndarray) -> float:
        """Calcula área aproximada da zona em hectares."""
        # Usar método simples de cálculo de área poligonal
        # Converte para metros usando aproximação de graus
        lon_meters = np.diff(lon_coords) * 111320.0
        lat_meters = np.diff(lat_coords) * 111320.0
        
        # Calcular área usando aproximação retangular
        area_m2 = np.sum(np.abs(lon_meters) * np.abs(lat_meters))
        return area_m2 / 10000.0  # converter para hectares
    
    def _calcular_estatisticas_gerais(self, zonas: List[ZonaCompactacao]) -> Dict[str, Any]:
        """Calcula estatísticas gerais das zonas."""
        if not zonas:
            return {
                "classificacao_predominante": "sem_dados",
                "percentual_impedimento": 0.0,
                "percentual_restricao": 0.0,
                "percentual_apto": 0.0,
                "recomendacao_geral": "Sem dados disponíveis"
            }
        
        total_area = sum(z.area_ha for z in zonas)
        
        # Calcular percentuais por classificação
        areas_impedimento = sum(z.area_ha for z in zonas 
                               if z.classificacao_predominante == "impedimento_severo")
        areas_restricao = sum(z.area_ha for z in zonas 
                            if z.classificacao_predominante == "restricao")
        areas_apto = sum(z.area_ha for z in zonas 
                        if z.classificacao_predominante == "apto")
        
        percentual_impedimento = (areas_impedimento / total_area) * 100 if total_area > 0 else 0
        percentual_restricao = (areas_restricao / total_area) * 100 if total_area > 0 else 0
        percentual_apto = (areas_apto / total_area) * 100 if total_area > 0 else 0
        
        # Determinar classificação predominante
        if percentual_impedimento >= 30:
            classificacao_predominante = "impedimento_severo"
        elif percentual_restricao >= 50:
            classificacao_predominante = "restricao"
        else:
            classificacao_predominante = "apto"
        
        # Gerar recomendação
        if percentual_impedimento >= 30:
            recomendacao = "Escarificação mecanizada recomendada para todo o talhão."
        elif percentual_restricao >= 50:
            recomendacao = "Escarificação localizada nos pontos críticos."
        else:
            recomendacao = "Manutenção do manejo atual com monitoramento."
        
        return {
            "classificacao_predominante": classificacao_predominante,
            "percentual_impedimento": round(percentual_impedimento, 1),
            "percentual_restricao": round(percentual_restricao, 1),
            "percentual_apto": round(percentual_apto, 1),
            "recomendacao_geral": recomendacao
        }
    
    def _calcular_matriz_similaridade(self, zonas: List[ZonaCompactacao]) -> np.ndarray:
        """Calcula matriz de similaridade entre zonas."""
        n_zonas = len(zonas)
        matriz = np.zeros((n_zonas, n_zonas))
        
        for i in range(n_zonas):
            for j in range(n_zonas):
                if i == j:
                    matriz[i, j] = 1.0  # Auto-similaridade
                else:
                    matriz[i, j] = zonas[i].calcular_similaridade(zonas[j])
        
        return matriz
    
    def suavizar_zonas(self, threshold_similaridade: float = 0.8) -> List[ZonaCompactacao]:
        """
        Aplica suavização nas zonas com base na similaridade.
        
        Args:
            threshold_similaridade: Limite de similaridade para fusão
            
        Returns:
            Lista de zonas suavizadas
        """
        if self.resultado is None:
            raise ValueError("Zoneamento ainda não executado")
        
        zonas = self.resultado.zonas.copy()
        zonas_suavizadas = []
        
        # Para cada zona, procurar zonas similares para fusão
        i = 0
        while i < len(zonas):
            zona_atual = zonas[i]
            zonas_similares = [zona_atual]
            
            j = i + 1
            while j < len(zonas):
                zona_comparar = zonas[j]
                similaridade = zona_atual.calcular_similaridade(zona_comparar)
                
                if similaridade >= threshold_similaridade:
                    zonas_similares.append(zona_comparar)
                    del zonas[j]  # Remover zona que será fundida
                else:
                    j += 1
            
            # Criar zona fundida
            zona_fundida = self._fundir_zonas(zonas_similares)
            zonas_suavizadas.append(zona_fundida)
            i += 1
        
        # Atualizar resultado
        self.resultado.zonas_suavizadas = zonas_suavizadas
        
        return zonas_suavizadas
    
    def _fundir_zonas(self, zonas: List[ZonaCompactacao]) -> ZonaCompactacao:
        """Fundir múltiplas zonas em uma única."""
        # Combinar todos os pontos
        todos_pontos = []
        for zona in zonas:
            todos_pontos.extend(zona.pontos)
        
        lon_coords = np.array([p[0] for p in todos_pontos])
        lat_coords = np.array([p[1] for p in todos_pontos])
        resistencias = np.array([p[2] for p in todos_pontos])
        
        # Criar nova zona com dados combinados
        return self._criar_zona(
            id=max(z.id for z in zonas),
            lon_coords=lon_coords,
            lat_coords=lat_coords,
            resistencias=resistencias
        )