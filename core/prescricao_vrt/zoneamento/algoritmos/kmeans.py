"""
Precision VRT Solo — Algoritmo K-Means para Zoneamento

Implementação completa do algoritmo K-Means para clustering.
"""

import logging
from typing import Any, Dict

import numpy as np
from sklearn.cluster import KMeans

from .base import BaseAlgoritmoClustering
from ..configuracao import ConfigZoneamento


class KMeansAlgoritmo(BaseAlgoritmoClustering):
    """
    Implementação do algoritmo K-Means para zoneamento.
    
    Utiliza sklearn.cluster.KMeans com tratamento específico
    para casos de edge cases.
    """
    
    @property
    def nome(self) -> str:
        """Nome do algoritmo."""
        return "K-Means"
    
    def _fit(self, X: np.ndarray) -> np.ndarray:
        """
        Executa o K-Means clustering.
        
        Args:
            X: Matriz de features (amostras × características)
            
        Returns:
            Array de labels (inteiros começando em 0)
        """
        # Tratar caso especial: n_zonas > número de amostras
        if self.config.n_zonas > len(X):
            logging.warning(
                f"n_zonas ({self.config.n_zonas}) > número de amostras ({len(X)}). "
                f"Reduzindo para {len(X)} zonas."
            )
            n_clusters = len(X)
        else:
            n_clusters = self.config.n_zonas
        
        # Criar e treinar modelo K-Means
        modelo = KMeans(
            n_clusters=n_clusters,
            random_state=self.config.random_state,
            n_init='auto',  # Evite warning no sklearn versão recente
            max_iter=300   # Limite de iterações
        )
        
        # Ajustar o modelo
        labels = modelo.fit_predict(X)
        
        # Retornar labels
        return labels
    
    def estatisticas(self) -> Dict[str, Any]:
        """
        Retorna estatísticas específicas do K-Means.
        
        Returns:
            Dicionário com estatísticas do algoritmo
        """
        stats = super().estatisticas()
        
        # Adicionar métricas específicas do K-Means
        # (Nota: para acessar estas métricas, seria necessário manter o modelo)
        stats["tipo"] = "K-Means"
        stats["métricas"] = {
            "algoritmo": "K-Means",
            "n_clusters": self.config.n_zonas,
            "random_state": self.config.random_state
        }
        
        return stats