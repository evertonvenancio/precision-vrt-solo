"""
Precision VRT Solo — Motor de Zoneamento de Fertirrigação

Biblioteca científica pura para zoneamento de soluções nutritivas.

Este módulo recebe camadas de dados de soluções e entrega zonas
com base em critérios específicos de população e nutrientes.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from ..fertirrigacao.contratos import (
    LeituraSolucao,
    AreaFertirrigacao,
    ConfigAnaliseSolucao
)

logger = logging.getLogger(__name__)


class AlgoritmoZoneamento(Enum):
    """Algoritmos de zoneamento suportados."""
    KMEANS = "kmeans"
    DBSCAN = "dbscan"
    AGLOMERATIVO = "aglomerativo"
    GAUSSIAN = "gaussian"


@dataclass
class ConfigZoneamentoFertirrigacao:
    """Configuração para zoneamento de soluções."""
    
    # Parâmetros de zoneamento
    algoritmo: AlgoritmoZoneamento = AlgoritmoZoneamento.KMEANS
    n_zonas: int = 3
    min_pontos_zona: int = 5
    
    # Parâmetros de análise
    parametros_clusuters: List[str] = field(default_factory=list)
    pesos_parametros: Dict[str, float] = field(default_factory=dict)
    
    # Parâmetros de qualidade
    tolerancia_intra_cluster: float = 0.1
    max_iteracoes: int = 100


@dataclass
class ZonaSolucao:
    """Zona de manejo classificada por soluções."""
    
    zona_id: int
    pontos_ids: List[str]
    centroide: Dict[str, float]
    caracteristicas: Dict[str, Any]
    recomendacoes: List[str]
    area_ha: float = 0.0
    perimetro_km: float = 0.0


@dataclass
class ResultadoZoneamentoFertirrigacao:
    """Resultado do zoneamento de soluções."""
    
    zonas: List[ZonaSolucao]
    qualidade_zoneamento: float
    estatisticas: Dict[str, Any]
    metodo_usado: str
    matriz_distancia: Optional[np.ndarray] = None


class MotorZoneamentoFertirrigacao:
    """Motor de zoneamento para soluções nutritivas."""
    
    def __init__(self):
        self.config = ConfigZoneamentoFertirrigacao()
        logger.info("MotorZoneamentoFertirrigacao inicializado")
    
    def zonar_solucoes(self, leituras: List[LeituraSolucao], 
                      area: AreaFertirrigacao,
                      config_analise: ConfigAnaliseSolucao,
                      mapa_interpolado: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Executar zoneamento de soluções.
        
        Args:
            leituras: Lista de leituras de solução
            area: Área de fertirrigação
            config_analise: Configuração de análise de soluções
            mapa_interpolado: Mapa interpolado opcional
        
        Returns:
            Lista de zonas de recomendação
        """
        logger.info(f"Iniciando zoneamento com algoritmo: {self.config.algoritmo.value}")
        
        # Validar dados de entrada
        self._validar_leituras(leituras)
        
        # Extrair características para clusterização
        dados_clusterizacao = self._extrair_caracteristicas(leituras)
        
        # Executar clusterização
        if self.config.algoritmo == AlgoritmoZoneamento.KMEANS:
            resultado = self._clusterizar_kmeans(dados_clusterizacao)
        elif self.config.algoritmo == AlgoritmoZoneamento.DBSCAN:
            resultado = self._clusterizar_dbscan(dados_clusterizacao)
        elif self.config.algoritmo == AlgoritmoZoneamento.AGLOMERATIVO:
            resultado = self._clusterizar_aglomerativo(dados_clusterizacao)
        elif self.config.algoritmo == AlgoritmoZoneamento.GAUSSIAN:
            resultado = self._clusterizar_gaussian(dados_clusterizacao)
        else:
            raise ValueError(f"Algoritmo não suportado: {self.config.algoritmo}")
        
        # Criar zonas com características
        zonas = self._criar_zonas(resultado, leituras, area)
        
        # Gerar recomendações para cada zona
        zonas_com_recomendacoes = self._adicionar_recomendacoes(zonas, leituras)
        
        logger.info(f"Zoneamento concluído: {len(zonas_com_recomendacoes)} zonas criadas")
        return zonas_com_recomendacoes
    
    def _validar_leituras(self, leituras: List[LeituraSolucao]) -> None:
        """Validar leituras para zoneamento."""
        if len(leituras) < self.config.min_pontos_zona:
            raise ValueError(
                f"Mínimo de {self.config.min_pontos_zona} pontos requeridos para zoneamento, "
                f"encontrados {len(leituras)}"
            )
    
    def _extrair_caracteristicas(self, leituras: List[LeituraSolucao]) -> np.ndarray:
        """Extrair características numéricas para clusterização."""
        logger.info("Extraindo características para clusterização")
        
        características = []
        
        for leitura in leituras:
            linha = []
            
            # Adicionar parâmetros configurados
            for parametro in self.config.parametros_clusuters:
                if hasattr(leitura, parametro):
                    valor = getattr(leitura, parametro)
                    if valor is None:
                        valor = 0.0  # Preencher valores nulos com zero
                    linha.append(valor)
                else:
                    linha.append(0.0)  # Parâmetro não encontrado
            
            características.append(linha)
        
        return np.array(características)
    
    def _clusterizar_kmeans(self, dados: np.ndarray) -> Dict[str, Any]:
        """Clusterizar usando K-means."""
        from sklearn.cluster import KMeans
        
        logger.info(f"Clusterizando K-means com {self.config.n_zonas} clusters")
        
        # Normalizar dados
        dados_normalizados = self._normalizar_dados(dados)
        
        # Executar K-means
        kmeans = KMeans(
            n_clusters=self.config.n_zonas,
            random_state=42,
            max_iter=self.config.max_iteracoes
        )
        
        labels = kmeans.fit_predict(dados_normalizados)
        
        return {
            "labels": labels,
            "centroids": kmeans.cluster_centers_,
            "inertia": kmeans.inertia_,
            "algoritmo": "kmeans"
        }
    
    def _clusterizar_dbscan(self, dados: np.ndarray) -> Dict[str, Any]:
        """Clusterizar usando DBSCAN."""
        from sklearn.cluster import DBSCAN
        
        logger.info("Clusterizando DBSCAN")
        
        # Normalizar dados
        dados_normalizados = self._normalizar_dados(dados)
        
        # Executar DBSCAN
        dbscan = DBSCAN(
            eps=0.5,
            min_samples=self.config.min_pontos_zona
        )
        
        labels = dbscan.fit_predict(dados_normalizados)
        
        # Remover rótulo de ruído (-1) se presente
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        
        return {
            "labels": labels,
            "n_clusters": n_clusters,
            "algoritmo": "dbscan"
        }
    
    def _clusterizar_aglomerativo(self, dados: np.ndarray) -> Dict[str, Any]:
        """Clusterizar usando clustering aglomerativo."""
        from sklearn.cluster import AgglomerativeClustering
        
        logger.info(f"Clusterizando aglomerativo com {self.config.n_zonas} clusters")
        
        # Normalizar dados
        dados_normalizados = self._normalizar_dados(dados)
        
        # Executar clustering aglomerativo
        clustering = AgglomerativeClustering(
            n_clusters=self.config.n_zonas,
            linkage='ward'
        )
        
        labels = clustering.fit_predict(dados_normalizados)
        
        return {
            "labels": labels,
            "algoritmo": "aglomerativo"
        }
    
    def _clusterizar_gaussian(self, dados: np.ndarray) -> Dict[str, Any]:
        """Clusterizar usando Gaussian Mixture."""
        from sklearn.mixture import GaussianMixture
        
        logger.info(f"Clusterizando Gaussian Mixture com {self.config.n_zonas} componentes")
        
        # Normalizar dados
        dados_normalizados = self._normalizar_dados(dados)
        
        # Executar Gaussian Mixture
        gmm = GaussianMixture(
            n_components=self.config.n_zonas,
            random_state=42,
            max_iter=self.config.max_iteracoes
        )
        
        labels = gmm.fit_predict(dados_normalizados)
        
        return {
            "labels": labels,
            "means": gmm.means_,
            "covariances": gmm.covariances_,
            "algoritmo": "gaussian"
        }
    
    def _normalizar_dados(self, dados: np.ndarray) -> np.ndarray:
        """Normalizar dados para clusterização."""
        from sklearn.preprocessing import StandardScaler
        
        scaler = StandardScaler()
        return scaler.fit_transform(dados)
    
    def _criar_zonas(self, resultado_clusterizacao: Dict[str, Any], 
                    leituras: List[LeituraSolucao],
                    area: AreaFertirrigacao) -> List[Dict[str, Any]]:
        """Criar zonas a partir dos resultados da clusterização."""
        logger.info("Criando zonas a partir dos clusters")
        
        labels = resultado_clusterizacao["labels"]
        zonas = {}
        
        # Agrupar leituras por cluster
        for i, leitura in enumerate(leituras):
            cluster_id = labels[i]
            
            if cluster_id not in zonas:
                zonas[cluster_id] = {
                    "zona_id": int(cluster_id) + 1,
                    "pontos_ids": [],
                    "caracteristicas": {},
                    "leituras": []
                }
            
            zonas[cluster_id]["pontos_ids"].append(leitura.ponto_id)
            zonas[cluster_id]["leituras"].append(leitura)
        
        # Calcar características médias de cada zona
        zonas_com_caracteristicas = []
        for cluster_id, dados_zona in zonas.items():
            caracteristicas_medias = self._calcular_caracteristicas_medias(dados_zona["leituras"])
            
            zona_final = {
                "zona_id": dados_zona["zona_id"],
                "pontos_ids": dados_zona["pontos_ids"],
                "caracteristicas": caracteristicas_medias,
                "area_ha": self._estimar_area_zona(len(dados_zona["leituras"]), area.area_ha),
                "leituras_originais": dados_zona["leituras"]
            }
            
            zonas_com_caracteristicas.append(zona_final)
        
        return zonas_com_caracteristicas
    
    def _calcular_caracteristicas_medias(self, leituras: List[LeituraSolucao]) -> Dict[str, float]:
        """Calcar características médias de uma zona."""
        caracteristicas = {}
        
        for parametro in self.config.parametros_clusuters:
            valores = []
            for leitura in leituras:
                if hasattr(leitura, parametro):
                    valor = getattr(leitura, parametro)
                    if valor is not None:
                        valores.append(valor)
            
            if valores:
                caracteristicas[parametro] = {
                    "min": min(valores),
                    "max": max(valores),
                    "media": np.mean(valores),
                    "mediana": np.median(valores),
                    "desvio_padrao": np.std(valores),
                    "coeficiente_variacao": np.std(valores) / np.mean(valores) * 100 if np.mean(valores) > 0 else 0
                }
            else:
                caracteristicas[parametro] = None
        
        return caracteristicas
    
    def _estimar_area_zona(self, n_pontos: int, area_total: float) -> float:
        """Estimar área de uma zona com base no número de pontos."""
        # Estimativa simplificada: área proporcional ao número de pontos
        return (n_pontos / 10) * area_total  # Ajuste conforme necessário
    
    def _adicionar_recomendacoes(self, zonas: List[Dict[str, Any]], 
                                leituras: List[LeituraSolucao]) -> List[Dict[str, Any]]:
        """Adicionar recomendações para cada zona."""
        logger.info("Adicionando recomendações para cada zona")
        
        zonas_com_recomendacoes = []
        
        for zona in zonas:
            # Analisar características da zona
            recomendacoes = self._gerar_recomendacoes_zona(zona, leituras)
            
            # Adicionar recomendações à zona
            zona_completa = zona.copy()
            zona_completa["recomendacoes"] = recomendacoes
            
            zonas_com_recomendacoes.append(zona_completa)
        
        return zonas_com_recomendacoes
    
    def _gerar_recomendacoes_zona(self, zona: Dict[str, Any], 
                                 leituras: List[LeituraSolucao]) -> List[str]:
        """Gerar recomendações específicas para uma zona."""
        recomendacoes = []
        caracteristicas = zona["caracteristas"]
        
        # Recomendações baseadas em CE
        if "ce_ds_m" in caracteristicas and caracteristicas["ce_ds_m"]:
            ce_media = caracteristicas["ce_ds_m"]["media"]
            
            if ce_media < 1.0:
                recomendacoes.append("CE abaixo do ideal: verificar necessidade de adição de nutrientes")
            elif ce_media > 3.0:
                recomendacoes.append("CE elevada: considerar diluição ou redução de fertilizantes")
            else:
                recomendacoes.append("CE dentro da faixa ideal para a cultura")
        
        # Recomendações baseadas em pH
        if "ph" in caracteristicas and caracteristicas["ph"]:
            ph_media = caracteristicas["ph"]["media"]
            
            if ph_media < 6.0:
                recomendacoes.append("pH ácido: considerar calagem ou correção de acidez")
            elif ph_media > 7.5:
                recomendacoes.append("pH alcalino: considerar acidificação ou correção de alcalinidade")
            else:
                recomendacoes.append("pH dentro da faixa ideal para a cultura")
        
        # Recomendações baseadas em nutrientes
        for nutriente in ["no3_mg_L", "k_mg_L", "ca_mg_L", "mg_mg_L"]:
            if nutriente in caracteristicas and caracteristicas[nutriente]:
                media = caracteristicas[nutriente]["media"]
                
                if media < 50:  # Limite genérico
                    recomendacoes.append(f"{nutriente} baixo: considerar adição de fertilizante")
                elif media > 500:  # Limite genérico
                    recomendacoes.append(f"{nutriente} elevado: verificar necessidade de redução")
        
        return recomendacoes