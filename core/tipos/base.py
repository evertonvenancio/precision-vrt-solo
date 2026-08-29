"""
Precision VRT Solo — Tipos Base do CORE

Classes base, mixins e metaclasses leves para todo o sistema.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Protocol, Optional
import hashlib
import json
import uuid


@dataclass
class ConfigBase:
    """
    Classe base para todas as ConfigXxx do core.
    Fornece serialização/deserialização padrão.
    """
    
    def to_dict(self) -> dict[str, Any]:
        """Serializa para dict. Dataclasses aninhadas são convertidas recursivamente."""
        result = {}
        for key, value in asdict(self).items():
            if isinstance(value, ConfigBase):
                result[key] = value.to_dict()
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, dados: dict[str, Any]) -> "ConfigBase":
        """Desserializa de dict. Subclasses devem sobrescrever se têm campos complexos."""
        # Para a base, apenas cria a instância com os dados diretos
        return cls(**dados)
    
    def hash_parametros(self) -> str:
        """
        Gera hash SHA256 determinístico da config.
        Útil para cache e auditoria.
        Ordena chaves, usa json.dumps com default=str.
        """
        dict_data = self.to_dict()
        json_str = json.dumps(dict_data, sort_keys=True, default=str, ensure_ascii=False)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()


@dataclass
class ResultadoBase:
    """
    Classe base para todos os ResultadoXxx do core.
    """
    timestamp: datetime = field(default_factory=datetime.now)
    tempo_execucao_ms: float = 0.0
    config: Optional[ConfigBase] = None
    
    def to_dict(self) -> dict[str, Any]:
        """Serialização com tratamento de datetime."""
        result = {}
        for key, value in asdict(self).items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, ConfigBase):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result
    
    def hash_resultado(self) -> str:
        """Hash SHA256 do resultado serializado."""
        dict_data = self.to_dict()
        json_str = json.dumps(dict_data, sort_keys=True, default=str, ensure_ascii=False)
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()


class IdentificavelMixin:
    """Mixin que adiciona id único (UUID4 ou timestamp+random)."""
    id: str = field(default_factory=str)


class TimestampMixin:
    """Mixin que adiciona created_at e updated_at."""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class Serializavel(Protocol):
    """Protocol para qualquer coisa que pode ser serializada para dict."""
    def to_dict(self) -> dict[str, Any]: ...
    
    @classmethod
    def from_dict(cls, dados: dict[str, Any]) -> Any: ...