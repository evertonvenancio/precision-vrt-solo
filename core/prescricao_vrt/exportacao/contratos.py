"""
Precision VRT Solo — Contratos de Dados do Módulo de Exportação

Dataclasses, enums e modelos de dados para exportação.
Estruturas puras de dados — sem constantes de configuração.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Importar as classes base do core.tipos
from core.tipos import ConfigBase, ResultadoBase

from .configuracao import FormatoExportacao

__all__ = [
    "MetadadosExportacao",
    "ConfigExportacao",
]


@dataclass
class MetadadosExportacao:
    """Metadados do processo de exportacao."""
    cultura: str = ""
    metodologia: str = ""
    safra: Optional[str] = None
    safras: List[str] = field(default_factory=list)
    camadas_utilizadas: List[str] = field(default_factory=list)
    indices_espectrais: List[str] = field(default_factory=list)
    parametros_processamento: Dict[str, Any] = field(default_factory=dict)
    data_processamento: Optional[str] = None
    versao_sistema: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cultura": self.cultura,
            "metodologia": self.metodologia,
            "safra": self.safra,
            "safras": self.safras,
            "camadas_utilizadas": self.camadas_utilizadas,
            "indices_espectrais": self.indices_espectrais,
            "parametros_processamento": self.parametros_processamento,
            "data_processamento": self.data_processamento,
            "versao_sistema": self.versao_sistema,
        }


@dataclass
class ConfigExportacao(ConfigBase):
    """Configuracao de exportacao."""
    output_dir: str = "data/output"
    formato_padrao: FormatoExportacao = FormatoExportacao.GEOJSON
    crs_saida: str = "EPSG:4326"
    incluir_metadados: bool = True
    incluir_prescricoes: bool = True
    incluir_estatisticas: bool = True
    simplificar_geometria: bool = True
    tolerancia_simplificacao: float = 0.00001

    def to_dict(self) -> Dict[str, Any]:
        return {
            "output_dir": self.output_dir,
            "formato_padrao": self.formato_padrao,
            "crs_saida": self.crs_saida,
            "incluir_metadados": self.incluir_metadados,
            "incluir_prescricoes": self.incluir_prescricoes,
            "incluir_estatisticas": self.incluir_estatisticas,
            "simplificar_geometria": self.simplificar_geometria,
            "tolerancia_simplificacao": self.tolerancia_simplificacao,
        }


@dataclass
class ResultadoExportacao(ResultadoBase):
    """Resultado da exportação."""
    arquivos_exportados: Optional[Dict[str, str]] = None
    formatos_suportados: List[str] = field(default_factory=list)
    metadados: Optional[Dict[str, Any]] = None
    status: str = "sucesso"
    mensagens: List[str] = field(default_factory=list)
    config: Optional[ConfigExportacao] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "arquivos_exportados": self.arquivos_exportados,
            "formatos_suportados": self.formatos_suportados,
            "metadados": self.metadados,
            "status": self.status,
            "mensagens": self.mensagens,
            "config": self.config,
            **super().to_dict(),
        }