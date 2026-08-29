"""
Precision VRT Solo — Tipos Geoespaciais Puros do CORE

Tipos geoespaciais básicos sem dependência de geopandas.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Coordenada:
    """Coordenada geográfica ou projetada. Imutável."""
    x: float
    y: float
    z: float | None = None
    
    def __post_init__(self):
        if not (-180 <= self.x <= 180 and -90 <= self.y <= 90):
            # Se fora de faixa geográfica, assume coordenada projetada — não validar
            pass


@dataclass(frozen=True)
class Bounds:
    """Envelope espacial. Imutável."""
    minx: float
    miny: float
    maxx: float
    maxy: float
    
    @property
    def width(self) -> float:
        return self.maxx - self.minx
    
    @property
    def height(self) -> float:
        return self.maxy - self.miny
    
    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass(frozen=True)
class ResolucaoEspacial:
    """Resolução de grade em metros. Imutável."""
    x_metros: float
    y_metros: float | None = None  # Se None, assume isotrópico (x_metros)
    
    @property
    def isotropica(self) -> bool:
        return self.y_metros is None or self.y_metros == self.x_metros


@dataclass(frozen=True)
class AffineTransform:
    """Transformação affine GDAL-style: (a, b, c, d, e, f)."""
    a: float  # resolução x
    b: float  # rotação x (0)
    c: float  # origem x (minx)
    d: float  # rotação y (0)
    e: float  # resolução y (negativo)
    f: float  # origem y (maxy)
    
    @classmethod
    def from_bounds_resolucao(cls, bounds: Bounds, resolucao: ResolucaoEspacial) -> "AffineTransform":
        """Constrói affine a partir de bounds e resolução."""
        a = resolucao.x_metros
        e = -resolucao.y_metros if resolucao.y_metros else -resolucao.x_metros
        
        return cls(
            a=a, b=0.0, c=bounds.minx,
            d=0.0, e=e, f=bounds.maxy
        )
    
    def to_tuple(self) -> tuple[float, float, float, float, float, float]:
        return (self.a, self.b, self.c, self.d, self.e, self.f)