"""
Precision VRT Solo — Algoritmos Base para Clustering

Interface abstrata e protocolo para algoritmos de clustering.
"""

import abc
import time
from typing import Any, Dict

import geopandas as gpd
import numpy as np

from ..configuracao import ConfigZoneamento
from ..contratos import AlgoritmoClusteringProtocol, ResultadoZoneamento
from ..exceptions import AlgoritmoError, ValidacaoError
from ..validacao import extrair_features, validar_configuracao, verificar_nan_inf


class BaseAlgoritmoClustering(AlgoritmoClusteringProtocol, abc.ABC):
    """
    Classe abstrata base para implementações de algoritmos de clustering.
    
    Implementa o protocolo AlgoritmoClusteringProtocol e fornece
    a estrutura comum para todos os algoritmos.
    """
    
    def __init__(self, config: ConfigZoneamento):
        """
        Inicializa o algoritmo com configuração.
        
        Args:
            config: Configuração de zoneamento
        """
        self.config = config
    
    @property
    @abc.abstractmethod
    def nome(self) -> str:
        """Nome do algoritmo."""
        pass
    
    @abc.abstractmethod
    def _fit(self, X: np.ndarray) -> np.ndarray:
        """
        Método abstrato que executa o algoritmo de clustering.
        
        Args:
            X: Matriz de features (amostras × características)
            
        Returns:
            Array de labels (inteiros começando em 0)
        """
        pass
    
    def executar(self, gdf: gpd.GeoDataFrame, config: ConfigZoneamento, X_normalizado: np.ndarray = None) -> ResultadoZoneamento:
        """
        Executa o algoritmo de clustering.
        
        Args:
            gdf: GeoDataFrame com dados de entrada
            config: Configuração de zoneamento
            X_normalizado: Array numpy com features pré-normalizadas (opcional)
                           Se None, extrai e normaliza internamente
            
        Returns:
            Resultado do zoneamento
            
        Raises:
            ValidacaoError: Se os dados ou configuração forem inválidos
            AlgoritmoError: Se ocorrer erro no algoritmo
        """
        import logging
        logging.basicConfig(level=logging.INFO)
        
        try:
            # Validar dados e configuração
            from ..validacao import validar_geodataframe
            validar_geodataframe(gdf)
            validar_configuracao(config, gdf)
            
            # Extrair features (se X_normalizado não fornecido)
            if X_normalizado is None:
                X = extrair_features(gdf, config)
                # Verificar NaN/Inf
                verificar_nan_inf(X)
            else:
                # Usar X fornecido (já validado externamente)
                X = X_normalizado
            
            # Medir tempo de execução
            start_time = time.time()
            
            # Executar algoritmo
            labels = self._fit(X)
            
            end_time = time.time()
            tempo_execucao_ms = (end_time - start_time) * 1000
            
            # Adicionar coluna zona ao GeoDataFrame (labels + 1 para começar em 1)
            gdf_resultado = gdf.copy()
            gdf_resultado['zona'] = labels + 1
            
            # Calcular número de zonas efetivas
            n_zonas_efetivas = len(np.unique(labels))
            
            # Criar resultado
            resultado = ResultadoZoneamento(
                gdf=gdf_resultado,
                algoritmo=config.algoritmo,
                n_zonas_efetivas=n_zonas_efetivas,
                config=config,
                tempo_execucao_ms=tempo_execucao_ms
            )
            
            return resultado
            
        except Exception as e:
            raise AlgoritmoError(f"Erro ao executar {self.nome}: {str(e)}")
    
    def estatisticas(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do algoritmo.
        
        Returns:
            Dicionário com estatísticas básicas
        """
        return {
            "algoritmo": self.nome,
            "configuracao": self.config.__dict__,
            "parametros": {
                "n_zonas": self.config.n_zonas,
                "random_state": self.config.random_state
            }
        }