"""
Precision VRT Solo — Contratos do CORE

Contratos compartilhados do CORE.
"""

from typing import Any, Dict, List, Optional
from enum import Enum

class ContratoBase:
    """Classe base para contratos."""
    pass


class ContratoExecucao(ContratoBase):
    """Contrato para execuções de processos."""
    
    def __init__(self, acao: str, recurso: str, usuario_id: str = None):
        self.acao = acao
        self.recurso = recurso
        self.usuario_id = usuario_id
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "acao": self.acao,
            "recurso": self.recurso,
            "usuario_id": self.usuario_id
        }


class PerfilZona(ContratoBase):
    """Perfil de zona para contratos."""
    
    def __init__(self, zona_id: str, perfil: Dict[str, Any]):
        self.zona_id = zona_id
        self.perfil = perfil
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "zona_id": self.zona_id,
            "perfil": self.perfil
        }


class MetricaQualidadeEnum(Enum):
    """Métricas de qualidade."""
    SILHOUETTE = "silhouette"
    DAVIES_BOULDIN = "davies_bouldin"
    CALINSKI = "calinski"
    INERCIA = "inercia"