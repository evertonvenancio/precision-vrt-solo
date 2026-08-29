"""
Precision VRT Solo — Normalização e Cálculo de Métricas

Classes utilitárias para normalização e cálculo de métricas do zoneamento.
"""

import numpy as np
from typing import List, Dict, Any

from ..exceptions import ConfiguracaoError


class Normalizador:
    """Classe para normalização de dados."""
    
    def __init__(self, metodo: str = "minmax"):
        """
        Inicializa o normalizador.
        
        Args:
            metodo: Método de normalização ('minmax', 'zscore')
        """
        self.metodo = metodo
        if metodo not in ["minmax", "zscore"]:
            raise ConfiguracaoError(f"Método de normalização inválido: {metodo}")
    
    def normalizar(self, dados: np.ndarray) -> np.ndarray:
        """
        Normaliza os dados usando o método selecionado.
        
        Args:
            dados: Array numpy de entrada
            
        Returns:
            Array numpy normalizado
        """
        if self.metodo == "minmax":
            return (dados - np.min(dados)) / (np.max(dados) - np.min(dados) + 1e-10)
        elif self.metodo == "zscore":
            return (dados - np.mean(dados)) / (np.std(dados) + 1e-10)
        else:
            raise ConfiguracaoError(f"Método não implementado: {self.metodo}")


class CalculadorMetricas:
    """Classe para cálculo de métricas de qualidade do zoneamento."""
    
    @staticmethod
    def calcular_inercia_intra(clusters: Dict[int, np.ndarray]) -> float:
        """
        Calcula a inércia intra-cluster (soma das distâncias dentro dos clusters).
        
        Args:
            clusters: Dicionário com clusters (índice -> array de pontos)
            
        Returns:
            Valor da inércia intra-cluster
        """
        inercia = 0.0
        for cluster_id, pontos in clusters.items():
            if len(pontos) > 1:
                centroide = np.mean(pontos, axis=0)
                distancias = np.linalg.norm(pontos - centroide, axis=1)
                inercia += np.sum(distancias**2)
        return inercia
    
    @staticmethod
    def calcular_silhueta_media(dados: np.ndarray, clusters: Dict[int, np.ndarray]) -> float:
        """
        Calcula o coeficiente de silhueta médio.
        
        Args:
            dados: Array numpy com todos os pontos
            clusters: Dicionário com clusters
            
        Returns:
            Coeficiente de silhueta médio
        """
        # Implementação simplificada do coeficiente de silhueta
        # Note: Esta é uma versão simplificada para demonstração
        n_clusters = len(clusters)
        if n_clusters < 2:
            return 1.0  # Silhueta máxima quando há apenas um cluster
        
        # Calcular centroides
        centroides = []
        for cluster_id in clusters:
            centroides.append(np.mean(clusters[cluster_id], axis=0))
        centroides = np.array(centroides)
        
        # Calcular distâncias inter-cluster
        distancias_inter = np.linalg.norm(centroides[:, np.newaxis] - centroides[np.newaxis, :], axis=2)
        
        # Silhueta simplificada (distância média ao centroide mais próximo)
        silhueta_media = 0.0
        n_pontos = 0
        
        for i, ponto in enumerate(dados):
            # Calcular distâncias para todos os centroides
            distancias_centroides = np.linalg.norm(ponto - centroides, axis=1)
            
            # Encontrar cluster mais próximo
            cluster_mais_proximo = np.argmin(distancias_centroides)
            distancia_cluster = distancias_centroides[cluster_mais_proximo]
            
            # Encontrar segundo cluster mais próximo
            distancias_copy = distancias_centroides.copy()
            distancias_copy[cluster_mais_proximo] = np.inf
            cluster_segundo_mais_proximo = np.argmin(distancias_copy)
            distancia_segundo_cluster = distancias_copy[cluster_segundo_mais_proximo]
            
            # Calcular silhueta do ponto
            if distancias_inter[cluster_mais_proximo, cluster_segundo_mais_proximo] > 0:
                silhueta_ponto = (distancia_segundo_cluster - distancia_cluster) / max(distancia_cluster, distancia_segundo_cluster)
                silhueta_media += silhueta_ponto
                n_pontos += 1
        
        return silhueta_media / max(n_pontos, 1)
    
    @staticmethod
    def calcular_indice_calinski_harabasz(dados: np.ndarray, clusters: Dict[int, np.ndarray]) -> float:
        """
        Calcula o índice de Calinski-Harabasz (ratio of between-cluster dispersion to within-cluster dispersion).
        
        Args:
            dados: Array numpy com todos os pontos
            clusters: Dicionário com clusters
            
        Returns:
            Valor do índice de Calinski-Harabasz
        """
        k = len(clusters)
        n = len(dados)
        
        if k < 2:
            return np.inf
        
        # Calcular centroides
        centroides = []
        tamanhos_clusters = []
        for cluster_id in clusters:
            centroides.append(np.mean(clusters[cluster_id], axis=0))
            tamanhos_clusters.append(len(clusters[cluster_id]))
        centroides = np.array(centroides)
        tamanhos_clusters = np.array(tamanhos_clusters)
        
        # Calcular centroide global
        centroide_global = np.mean(dados, axis=0)
        
        # Calcular dispersão entre clusters (BCSS)
        bcss = 0.0
        for i, (centroide, tamanho) in enumerate(zip(centroides, tamanhos_clusters)):
            distancia = np.linalg.norm(centroide - centroide_global)**2
            bcss += tamanho * distancia
        
        # Calcular dispersão dentro dos clusters (WCSS)
        wcss = 0.0
        for cluster_id, pontos in clusters.items():
            centroide = centroides[cluster_id]
            for ponto in pontos:
                distancia = np.linalg.norm(ponto - centroide)**2
                wcss += distancia
        
        if wcss == 0:
            return np.inf
        
        return (bcss / (k - 1)) / (wcss / (n - k))