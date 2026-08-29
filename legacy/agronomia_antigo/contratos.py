"""
Contratos do módulo de Agronomia.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from core.tipos import ConfigBase, ResultadoBase


@dataclass
class ConfigAgronomia(ConfigBase):
    """
    Configuração para análise agronômica.
    Recebe dados de config/ como parâmetros.
    """
    metodo_id: str = "IAC_Graos"
    cultura: str = "soja"
    produtividade_alvo: float = 3.0
    teor_argila: float = 20.0
    profundidade_amostra_cm: float = 20.0


@dataclass
class ResultadoAgronomia(ResultadoBase):
    """
    Resultado da análise agronômica.
    """
    interpretacoes: Dict[str, Any] = field(default_factory=dict)
    classe_fertilidade: str = ""
    recomendacoes: Dict[str, Any] = field(default_factory=dict)
    balanco_nutricional: Dict[str, float] = field(default_factory=dict)
    config: Optional[ConfigAgronomia] = None


@dataclass
class InterpretacaoNutriente:
    nutriente: str = ""
    valor: float = 0.0
    unidade: str = ""
    classe: str = ""  # Baixo, Médio, Alto, Muito Alto
    metodo: str = ""