"""
Precision VRT Solo — Algoritmo DBSCAN

Stub para implementação futura na etapa Zx.
"""

from .base import BaseAlgoritmoClustering


class DBSCANAlgoritmo(BaseAlgoritmoClustering):
    """
    Stub para implementação do algoritmo DBSCAN.
    
    Será implementado na etapa Zx.
    """
    
    @property
    def nome(self) -> str:
        """Nome do algoritmo."""
        return "DBSCAN"
    
    def _fit(self, X):
        """
        Método stub que levanta NotImplementedError.
        
        Args:
            X: Matriz de features
            
        Raises:
            NotImplementedError: Implementação virá na etapa Zx
        """
        raise NotImplementedError(
            "Algoritmo DBSCAN ainda não foi implementado. "
            "A implementação completa será adicionada na etapa Zx do projeto."
        )