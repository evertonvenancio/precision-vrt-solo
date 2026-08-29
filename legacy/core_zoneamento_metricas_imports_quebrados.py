"""
Precision VRT Solo — Métricas do Módulo de Zoneamento

Orquestrador de métricas de qualidade para clustering.
Integração de todas as métricas individuais em uma interface unificada.
"""

import logging
from typing import Dict

import numpy as np
import geopandas as gpd

from .contratos import MetricaQualidadeEnum
from ..utilitarios.utils import media
from ..qualidade import (
    calcular_silhouette,
    calcular_davies_bouldin,
    calcular_calinski,
    calcular_inercia,
    calcular_homogeneidade_media
)

logger = logging.getLogger(__name__)

__all__ = [
    'CalculadorMetricas',
]


class CalculadorMetricas:
    """
    Classe orquestradora para cálculo de todas as métricas de qualidade do clustering.
    
    Suporta métricas internas (silhouette, Davies-Bouldin, Calinski, inércia)
    e métricas personalizadas (homogeneidade intra-zona).
    """
    
    def __init__(self):
        """Inicializa o calculador de métricas."""
        self.metricas_disponiveis = {
            MetricaQualidadeEnum.SILHOUETTE: calcular_silhouette,
            MetricaQualidadeEnum.DAVIES_BOULDIN: calcular_davies_bouldin,
            MetricaQualidadeEnum.CALINSKI: calcular_calinski,
            MetricaQualidadeEnum.INERCIA: calcular_inercia,
        }
        
        logger.info("Calculador de métricas inicializado")
    
    def calcular_todas(self, X: np.ndarray, labels: np.ndarray, gdf: gpd.GeoDataFrame, colunas: list[str]) -> Dict[str, float]:
        """
        Executa todas as métricas disponíveis.
        Retorna dict com chaves 'silhouette', 'davies_bouldin', 'calinski', 'inercia', 'homogeneidade_media'.
        
        Args:
            X: Array numpy com dados normalizados
            labels: Array numpy com rótulos de zona (começando em 0 para métricas)
            gdf: GeoDataFrame com dados e coluna 'zona'
            colunas: Lista de colunas de features para análise
            
        Returns:
            Dicionário com todas as métricas calculadas
            
        Raises:
            ValueError: Se parâmetros forem inválidos
        """
        if X.ndim != 2:
            raise ValueError("X deve ser array 2D")
        
        if len(labels) != X.shape[0]:
            raise ValueError("Número de labels deve corresponder ao número de linhas de X")
        
        logger.info("Calculando todas as métricas de qualidade")
        
        metricas_resultado = {}
        
        # Calcular métricas internas
        for enum_key, funcao_calculo in self.metricas_disponiveis.items():
            try:
                metrica_nome = enum_key.value.lower()
                valor = funcao_calculo(X, labels)
                metricas_resultado[metrica_nome] = valor
                logger.debug(f"{metrica_nome}: {valor:.4f}")
            except Exception as e:
                logger.warning(f"Erro ao calcular {enum_key.value}: {e}")
                metricas_resultado[metrica_nome] = 0.0
        
        # Calcular homogeneidade intra-zona (requer GeoDataFrame)
        try:
            homogeneidade_media = calcular_homogeneidade_media(gdf, colunas)
            metricas_resultado['homogeneidade_media'] = homogeneidade_media
            logger.debug(f"homogeneidade_media: {homogeneidade_media:.4f}%")
        except Exception as e:
            logger.warning(f"Erro ao calcular homogeneidade: {e}")
            metricas_resultado['homogeneidade_media'] = 0.0
        
        # Adicionar metadados
        metricas_resultado['n_amostras'] = int(X.shape[0])
        metricas_resultado['n_features'] = int(X.shape[1])
        metricas_resultado['n_clusters'] = int(len(np.unique(labels)))
        
        logger.info(f"Métricas calculadas: {len(metricas_resultado)} métricas")
        return metricas_resultado
    
    def get_disponiveis(self) -> list[str]:
        """
        Retorna lista de todas as métricas disponíveis.
        
        Returns:
            Lista de nomes das métricas disponíveis
        """
        return list(self.metricas_disponiveis.keys())
    
    def calcular_individuais(self, X: np.ndarray, labels: np.ndarray, 
                           metricas_selecionadas: list[str] = None) -> Dict[str, float]:
        """
        Calcula apenas métricas individuais selecionadas.
        
        Args:
            X: Array numpy com dados normalizados
            labels: Array numpy com rótulos de zona
            metricas_selecionadas: Lista de nomes das métricas a calcular
                                    (None para todas)
            
        Returns:
            Dicionário com métricas calculadas
        """
        if metricas_selecionadas is None:
            metricas_selecionadas = self.get_disponiveis()
        
        resultado = {}
        
        for metrica_nome in metricas_selecionadas:
            # Encontrar enum correspondente
            enum_key = None
            for enum_val, nome in [(e, e.value.lower()) for e in MetricaQualidadeEnum]:
                if nome == metrica_nome.lower():
                    enum_key = enum_val
                    break
            
            if enum_key and enum_key in self.metricas_disponiveis:
                try:
                    valor = self.metricas_disponiveis[enum_key](X, labels)
                    resultado[metrica_nome] = valor
                except Exception as e:
                    logger.warning(f"Erro ao calcular {metrica_nome}: {e}")
                    resultado[metrica_nome] = 0.0
            else:
                logger.warning(f"Métrica não disponível: {metrica_nome}")
        
        return resultado