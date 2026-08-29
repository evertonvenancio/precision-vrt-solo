"""
Precision VRT Solo — Contratos de Dados do Módulo de Interpolação

Dataclasses, enums e modelos de dados para interpolação espacial.
Estruturas puras de dados — sem constantes de configuração.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Importar as classes base do core.tipos
from core.tipos import ConfigBase, ResultadoBase

__all__ = [
    "EstatisticaInterpolacao",
    "ConfigInterpolacao",
]


@dataclass
class EstatisticaInterpolacao:
    """Estatisticas de um atributo interpolado."""
    minimo: float = 0.0
    maximo: float = 0.0
    media: float = 0.0
    mediana: float = 0.0
    desvio: float = 0.0
    variancia: float = 0.0
    q1: float = 0.0
    q3: float = 0.0
    iqr: float = 0.0
    coef_variacao: float = 0.0
    n_pontos_validos: int = 0
    n_pontos_interpolados: int = 0
    pct_cobertura: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "minimo": self.minimo,
            "maximo": self.maximo,
            "media": self.media,
            "mediana": self.mediana,
            "desvio": self.desvio,
            "variancia": self.variancia,
            "q1": self.q1,
            "q3": self.q3,
            "iqr": self.iqr,
            "coef_variacao": self.coef_variacao,
            "n_pontos_validos": self.n_pontos_validos,
            "n_pontos_interpolados": self.n_pontos_interpolados,
            "pct_cobertura": self.pct_cobertura,
        }


@dataclass
class ConfigInterpolacao(ConfigBase):
    """Configuracao da interpolacao."""
    resolucao_m: int = 10
    funcao_rbf: str = "thin_plate_spline"
    suavizacao: float = 0.0
    metodo: str = "rbf"
    normalizar_coords: bool = True
    tratar_outliers: bool = True
    limite_outlier_std: float = 3.0
    preencher_nulos: bool = True
    max_iter: int = 1000
    tolerancia: float = 1e-6

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resolucao_m": self.resolucao_m,
            "funcao_rbf": self.funcao_rbf,
            "suavizacao": self.suavizacao,
            "metodo": self.metodo,
            "normalizar_coords": self.normalizar_coords,
            "tratar_outliers": self.tratar_outliers,
            "limite_outlier_std": self.limite_outlier_std,
            "preencher_nulos": self.preencher_nulos,
            "max_iter": self.max_iter,
            "tolerancia": self.tolerancia,
        }


@dataclass
class ResultadoInterpolacao(ResultadoBase):
    """Resultado da interpolação espacial."""
    grid_x: Optional[Any] = None
    grid_y: Optional[Any] = None
    coordenadas: Optional[Dict[str, float]] = None
    atributos: Optional[Dict[str, Dict[str, Any]]] = None
    atributos_interpolados: Optional[List[str]] = None
    estatisticas: Optional[Dict[str, Dict[str, Any]]] = None
    configuracao: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grid_x": self.grid_x,
            "grid_y": self.grid_y,
            "coordenadas": self.coordenadas,
            "atributos": self.atributos,
            "atributos_interpolados": self.atributos_interpolados,
            "estatisticas": self.estatisticas,
            "configuracao": self.configuracao,
            **super().to_dict(),
        }