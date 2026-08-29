"""
Precision VRT Solo — Algoritmos de Interpolação

Implementações de algoritmos espaciais para interpolação.
"""

from .rbf import interpolar_rbf
from .idw import interpolar_idw

__all__ = ["interpolar_rbf", "interpolar_idw"]