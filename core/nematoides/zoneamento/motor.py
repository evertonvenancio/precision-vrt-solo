"""
Precision VRT Solo — Motor de Zoneamento de Nematoides

Biblioteca científica pura para zoneamento de risco de nematoides.

Recebe camadas de dados de nematoides e entrega zonas
com base em critérios de risco populacional.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering

from ...tipos.geoespacial import Bounds
from ...tipos.base import ConfigBase, ResultadoBase
from ..nematoides.contratos import (
    ZonaRiscoNematoides,
    PontoAmostraNematoides,
    ConfigZoneamentoNematoides,
    ResultadoZoneamentoNematoides,
    NivelRiscoNematoides
)


class AlgoritmoZoneamento(Enum):
    """Algoritmos disponíveis para zoneamento."""
    KMEANS = "kmeans"
    DBSCAN = "dbscan"
    AGLOMERATIVO = "aglomerativo"


@dataclass
class ConfigZoneamentoCientifico(ConfigBase):
    """Configuração científica para zoneamento de nematoides."""
    algoritmo: AlgoritmoZoneamento = AlgoritmoZoneamento.KMEANS
    n_zonas: int = 5
    limite_distancia: float = 50.0  # metros
    metodo_agrupamento: str = "ward"
    metrica_distancia: str = "euclidean"
    linkage: str = "ward"
    densidade_minima: int = 3  # amostras mínimas por zona


@dataclass
class EstatisticaZona:
    """Estatísticas de uma zona individual."""
    zona_id: int
    centroide: Tuple[float, float]
    n_amostras: int
    populacao_media: float
    populacao_maxima: float
    populacao_minima: float
    desvio_padrao: float
    intervalo_confianca_95: Tuple[float, float]
    especies_detectadas: List[str]
    pontos_pertencentes: List[int]  # índices das amostras


class MotorZoneamentoNematoides:
    """
    Motor de zoneamento científico para nematoides.
    
    Implementa algoritmos de clustering avançados para identificar
    zonas de risco com base em populações de nematoides.
    """
    
    def __init__(self, config: ConfigZoneamentoNematoides):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Converter para configuração científica
        self.config_cientifico = ConfigZoneamentoCientifico(
            algoritmo=AlgoritmoZoneamento(config.algoritmo),
            n_zonas=config.n_zonas,
            limite_distancia=100.0,  # padrão
            metodo_agrupamento=config.metodo_agrupamento
        )
    
    def gerar_zoneamento(self, amostras: List[PontoAmostraNematoides],
                       bounds: Optional[Bounds] = None) -> ResultadoZoneamentoNematoides:
        """
        Realiza zoneamento científico de risco de nematoides.
        
        Args:
            amostras: Lista de amostras de nematoides
            bounds: Limites espaciais da área
            
        Returns:
            Zoneamento completo com estatísticas
        """
        if not amostras:
            raise ValueError("Nenhuma amostra fornecida para zoneamento")
        
        self.logger.info(f"Iniciando zoneamento com {len(amostras)} amostras")
        
        # Preparar dados para clustering
        dados_preparados = self._preparar_dados_clustering(amostras)
        
        # Executar algoritmo de clustering
        if self.config_cientifico.algoritmo == AlgoritmoZoneamento.KMEANS:
            clusters = self._executar_kmeans(dados_preparados)
        elif self.config_cientifico.algoritmo == AlgoritmoZoneamento.DBSCAN:
            clusters = self._executar_dbscan(dados_preparados)
        elif self.config_cientifico.algoritmo == AlgoritmoZoneamento.AGLOMERATIVO:
            clusters = self._executar_aglomerativo(dados_preparados)
        else:
            raise ValueError(f"Algoritmo não suportado: {self.config_cientifico.algoritmo}")
        
        # Calcular estatísticas por zona
        zonas_estatisticas = self._calcular_estatisticas_zonas(
            amostras, clusters, dados_preparados
        )
        
        # Gerar mapa de zonas
        mapa_zonas = self._gerar_mapa_zonas(zonas_estatisticas, bounds)
        
        # Calcular estatísticas gerais
        estatisticas_gerais = self._calcular_estatisticas_gerais(zonas_estatisticas)
        
        # Criar zonas de risco
        zonas_risco = self._criar_zonas_risco(zonas_estatisticas)
        
        return ResultadoZoneamentoNematoides(
            zonas_risco=zonas_risco,
            mapa_zonas=mapa_zonas,
            configuracao_usada=self.config,
            estatisticas_gerais=estatisticas_gerais
        )
    
    def _preparar_dados_clustering(self, amostras: List[PontoAmostraNematoides]) -> np.ndarray:
        """
        Prepara dados para clustering normalizando atributos.
        
        Args:
            amostras: Lista de amostras
            
        Returns:
            Array numpy com dados normalizados
        """
        # Extrair coordenadas e populações
        coordenadas = np.array([[a.coordenada.x, a.coordenada.y] for a in amostras])
        populacoes = np.array([a.populacao_nematoides_100g_solo for a in amostras])
        
        # Normalizar populações (escala 0-1)
        populacoes_norm = (populacoes - populacoes.min()) / (populacoes.max() - populacoes.min() + 1e-6)
        
        # Combinar coordenadas e populações normalizadas
        # Ponderação: 40% coordenada, 60% população
        dados = np.column_stack([
            coordenadas[:, 0] * 0.4,  # x ponderado
            coordenadas[:, 1] * 0.4,  # y ponderado  
            populacoes_norm * 0.6     # população ponderada
        ])
        
        return dados
    
    def _executar_kmeans(self, dados: np.ndarray) -> np.ndarray:
        """Executa algoritmo K-means."""
        kmeans = KMeans(
            n_clusters=self.config_cientifico.n_zonas,
            random_state=42,
            init='k-means++'
        )
        
        clusters = kmeans.fit_predict(dados)
        self.logger.info(f"K-means concluído. {len(np.unique(clusters))} clusters formados")
        
        return clusters
    
    def _executar_dbscan(self, dados: np.ndarray) -> np.ndarray:
        """Executa algoritmo DBSCAN."""
        dbscan = DBSCAN(
            eps=self.config_cientifico.limite_distancia / 1000.0,  # converter para unidades dos dados
            min_samples=self.config_cientifico.densidade_minima,
            metric=self.config_cientifico.metrica_distancia
        )
        
        clusters = dbscan.fit_predict(dados)
        n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
        self.logger.info(f"DBSCAN concluído. {n_clusters} clusters formados")
        
        return clusters
    
    def _executar_aglomerativo(self, dados: np.ndarray) -> np.ndarray:
        """Executa algoritmo aglomerativo."""
        clustering = AgglomerativeClustering(
            n_clusters=self.config_cientifico.n_zonas,
            linkage=self.config_cientifico.linkage,
            affinity=self.config_cientifico.metrica_distancia
        )
        
        clusters = clustering.fit_predict(dados)
        self.logger.info(f"Clustering aglomerativo concluído. {len(np.unique(clusters))} clusters formados")
        
        return clusters
    
    def _calcular_estatisticas_zonas(self, amostras: List[PontoAmostraNematoides],
                                   clusters: np.ndarray, dados: np.ndarray) -> List[EstatisticaZona]:
        """
        Calcula estatísticas detalhadas por zona.
        
        Args:
            amostras: Lista original de amostras
            clusters: Resultados do clustering
            dados: Dados normalizados
            
        Returns:
            Lista de estatísticas por zona
        """
        zonas_estatisticas = []
        n_amostras = len(amostras)
        
        # Processar cada cluster
        for cluster_id in np.unique(clusters):
            if cluster_id == -1:  # Ponto ruído (DBSCAN)
                continue
                
            # Encontrar amostras do cluster
            mask = clusters == cluster_id
            indices_amostras = np.where(mask)[0]
            
            # Extrair dados do cluster
            amostras_cluster = [amostras[i] for i in indices_amostras]
            populacoes_cluster = [a.populacao_nematoides_100g_solo for a in amostras_cluster]
            
            # Calcular centroide (em coordenadas originais)
            coordenadas = np.array([[a.coordenada.x, a.coordenada.y] for a in amostras_cluster])
            centroide = (np.mean(coordenadas[:, 0]), np.mean(coordenadas[:, 1]))
            
            # Calcular estatísticas
            populacao_media = np.mean(populacoes_cluster)
            populacao_maxima = np.max(populacoes_cluster)
            populacao_minima = np.min(populacoes_cluster)
            desvio_padrao = np.std(populacoes_cluster, ddof=1)
            
            # Intervalo de confiança 95%
            from scipy import stats
            ic_media = stats.t.interval(0.95, len(populacoes_cluster)-1, 
                                       loc=populacao_media, scale=desvio_padrao/np.sqrt(len(populacoes_cluster)))
            
            # Detectar espécies
            especies = list(set(a.especie_predominante.value for a in amostras_cluster if a.especie_predominante))
            
            estatistica = EstatisticaZona(
                zona_id=cluster_id,
                centroide=centroide,
                n_amostras=len(amostras_cluster),
                populacao_media=populacao_media,
                populacao_maxima=populacao_maxima,
                populacao_minima=populacao_minima,
                desvio_padrao=desvio_padrao,
                intervalo_confianca_95=ic_media,
                especies_detectadas=especies,
                pontos_pertencentes=indices_amostras.tolist()
            )
            
            zonas_estatisticas.append(estatistica)
        
        return zonas_estatisticas
    
    def _gerar_mapa_zonas(self, zonas_estatisticas: List[EstatisticaZona],
                         bounds: Optional[Bounds]) -> np.ndarray:
        """
        Gera mapa de zonas para visualização.
        
        Args:
            zonas_estatisticas: Lista de estatísticas por zona
            bounds: Limites da área
            
        Returns:
            Mapa de zonas
        """
        if bounds is None:
            # Usar limites das amostras
            all_x = [z.centroide[0] for z in zonas_estatisticas]
            all_y = [z.centroide[1] for z in zonas_estatisticas]
            bounds = Bounds(min(min(all_x), min(all_y)), max(max(all_x), max(all_y)))
        
        # Criar grade para o mapa
        resolucao = 10.0  # metros
        nx = int((bounds.maxx - bounds.minx) / resolucao) + 1
        ny = int((bounds.maxy - bounds.miny) / resolucao) + 1
        
        mapa_zonas = np.zeros((ny, nx), dtype=int)
        
        # Preencher mapa com informações das zonas
        for zona in zonas_estatisticas:
            # Criar máscara circular em torno do centroide
            centro_x, centro_y = zona.centroide
            
            for i in range(ny):
                for j in range(nx):
                    x = bounds.minx + j * resolucao
                    y = bounds.miny + i * resolucao
                    
                    dist = np.sqrt((x - centro_x)**2 + (y - centro_y)**2)
                    
                    # Atribuir zona se estiver dentro do raio de influência
                    if dist < 50.0:  # raio de influência de 50 metros
                        mapa_zonas[i, j] = zona.zona_id
        
        return mapa_zonas
    
    def _calcular_estatisticas_gerais(self, zonas_estatisticas: List[EstatisticaZona]) -> Dict[str, Any]:
        """Calcula estatísticas gerais do zoneamento."""
        if not zonas_estatisticas:
            return {}
        
        total_amostras = sum(z.n_amostras for z in zonas_estatisticas)
        total_populacao = sum(z.populacao_media * z.n_amostras for z in zonas_estatisticas)
        
        populacoes = [z.populacao_media for z in zonas_estatisticas]
        desvios = [z.desvio_padrao for z in zonas_estatisticas]
        
        return {
            "total_zonas": len(zonas_estatisticas),
            "total_amostras": total_amostras,
            "populacao_global": total_populacao / total_amostras if total_amostras > 0 else 0,
            "populacao_maxima_zona": max(populacoes),
            "populacao_minima_zona": min(populacoes),
            "desvio_padrao_global": np.std(populacoes),
            "especies_detectadas_total": list(set(
                esp for zona in zonas_estatisticas for esp in zona.especies_detectadas
            ))
        }
    
    def _criar_zonas_risco(self, zonas_estatisticas: List[EstatisticaZona]) -> List[ZonaRiscoNematoides]:
        """Cria zonas de risco a partir das estatísticas."""
        zonas_risco = []
        
        for estatistica in zonas_estatisticas:
            # Classificar risco da zona
            from ..nematoides.motor import MotorNematoides
            motor_nematoides = MotorNematoides()
            risco_classificacao = motor_nematoides.classificar_risco(estatistica.populacao_media)
            
            # Gerar recomendação
            recomendacao = motor_nematoides.gerar_recomendacao_manejo(risco_classificacao)
            
            zona_risco = ZonaRiscoNematoides(
                zona_id=estatistica.zona_id,
                risco_classificacao=risco_classificacao,
                populacao_media=estatistica.populacao_media,
                populacao_maxima=estatistica.populacao_maxima,
                generos_detectados=[especie for especie in estatistica.especies_detectadas],
                recomendacao_manejo=recomendacao,
                area_hectares=estatistica.n_amostras * 2.0,  # estimativa
                correlacao_produtividade_risko=0.0,  # placeholder
                prioridade_acao="PENDENTE"  # placeholder
            )
            
            zonas_risco.append(zona_risco)
        
        return zonas_risco