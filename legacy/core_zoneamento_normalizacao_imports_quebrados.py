"""
Precision VRT Solo — Normalização do Módulo de Zoneamento

Orquestrador de normalização. Recebe matriz de features, retorna matriz normalizada.
Implementação pura com numpy, sem dependências externas.
"""

import logging
from typing import Dict, List, Optional

import numpy as np

from .utils.matriz import aplicar_pesos_features
from ..exceptions import ConfiguracaoError

logger = logging.getLogger(__name__)

__all__ = [
    'Normalizador',
]


class Normalizador:
    """
    Classe para normalização de features antes do clustering.
    
    Suporta:
    - Min-Max scaling para [0, 1]
    - Z-score standardization (média 0, desvio 1)
    - Aplicação de pesos por feature antes da normalização
    """
    
    def __init__(self, metodo: str = "minmax"):
        """
        Inicializa o normalizador.
        
        Args:
            metodo: Método de normalização ("minmax", "zscore", "none")
            
        Raises:
            ConfiguracaoError: Se método não for suportado
        """
        self.metodo = metodo.lower()
        self._validar_metodo()
        
        logger.info(f"Normalizador inicializado com método: {self.metodo}")
    
    def _validar_metodo(self):
        """Valida se o método de normalização é suportado."""
        metodos_suportados = ["minmax", "zscore", "none"]
        if self.metodo not in metodos_suportados:
            raise ConfiguracaoError(
                f"Método de normalização inválido: {self.metodo}. "
                f"Suportados: {metodos_suportados}"
            )
    
    def ajustar(self, X: np.ndarray) -> np.ndarray:
        """
        Aplica a normalização escolhida.
        
        Args:
            X: Array numpy 2D de features
            
        Returns:
            Array numpy 2D normalizado
        """
        if X.size == 0:
            logger.warning("Array vazio: normalização não aplicada")
            return X.copy()
        
        logger.debug(f"Aplicando normalização {self.metodo} em array shape {X.shape}")
        
        if self.metodo == "minmax":
            from .utils.matriz import escalonar_min_max
            return escalonar_min_max(X)
        
        elif self.metodo == "zscore":
            from .utils.matriz import padronizar_zscore
            return padronizar_zscore(X)
        
        elif self.metodo == "none":
            # Retorna cópia para garantir consistência
            return X.copy()
    
    def ajustar_com_pesos(self, X: np.ndarray, pesos: Optional[Dict[str, float]], colunas: List[str]) -> np.ndarray:
        """
        Aplica pesos por feature ANTES da normalização.
        Se pesos for None, comportamento idêntico a ajustar().
        
        Args:
            X: Array numpy 2D de features
            pesos: Dicionário com pesos por feature (nome -> peso)
            colunas: Lista de nomes das colunas na ordem do array
            
        Returns:
            Array numpy 2D normalizado com pesos aplicados
        """
        if X.size == 0:
            logger.warning("Array vazio: normalização não aplicada")
            return X.copy()
        
        # Se não houver pesos, usar normalização simples
        if pesos is None or len(pesos) == 0:
            return self.ajustar(X)
        
        logger.debug(f"Aplicando pesos e normalização {self.metodo}")
        
        # Aplicar pesos
        X_com_pesos = aplicar_pesos_features(X, pesos, colunas)
        
        # Aplicar normalização
        return self.ajustar(X_com_pesos)
    
    def get_config(self) -> Dict[str, str]:
        """
        Retorna a configuração atual do normalizador.
        
        Returns:
            Dicionário com configuração
        """
        return {
            "metodo": self.metodo
        }