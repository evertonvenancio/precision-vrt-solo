"""
Precision VRT Solo — Protocols Genéricos do CORE

Interfaces compartilhadas entre módulos do CORE.
"""

from typing import Protocol, Any, runtime_checkable


@runtime_checkable
class Orquestravel(Protocol):
    """
    Protocol para classes que orquestram processamento (motores).
    Ex: Zoneador, Prescritor, Interpolador, Exportador, Agronomo, Otimizador.
    """
    def executar(self, *args: Any, **kwargs: Any) -> Any: ...


@runtime_checkable
class Exportavel(Protocol):
    """
    Protocol para resultados que podem ser exportados.
    """
    def to_dict(self) -> dict[str, Any]: ...
    
    @property
    def timestamp(self) -> Any: ...


@runtime_checkable
class Cacheavel(Protocol):
    """
    Protocol para objetos que podem ser cacheados.
    """
    def hash_entrada(self) -> str: ...


@runtime_checkable
class Validavel(Protocol):
    """
    Protocol para configs que podem ser validadas.
    """
    def validar(self) -> None: ...


@runtime_checkable
class Metrico(Protocol):
    """
    Protocol para resultados que possuem métricas de qualidade.
    """
    @property
    def metricas(self) -> dict[str, float]: ...