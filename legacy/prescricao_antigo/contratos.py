"""
Precision VRT Solo — Contratos de Dados do Módulo de Prescrição

Dataclasses, enums e modelos de dados para prescrição agronômica.
Estruturas puras de dados — sem constantes agronômicas.
"""

from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from enum import Enum

# Importar as classes base do core.tipos
from core.tipos import ConfigBase, ResultadoBase


__all__ = [
    "StatusNutriente",
    "TipoCorretivo",
    "ResultadoNutriente",
    "ResultadoCorretivo",
    "PrescricaoZona",
    "ResumoPrescricao",
    "NotasTecnicas",
    "ConfigPrescricao",
    "ResultadoPrescricao",
]


# =============================================================================
# ENUMS
# =============================================================================

class StatusNutriente(Enum):
    """Status de disponibilidade do nutriente no solo."""
    ADEQUADO = "Adequado"
    BAIXO = "Baixo"
    MEDIO = "Medio"
    ALTO = "Alto"
    MUITO_BAIXO = "Muito baixo"
    NECESSITA_ADUBACAO = "Necessita adubacao"
    BLOQUEADO = "Bloqueado"


class TipoCorretivo(Enum):
    """Tipos de corretivos de solo."""
    CALAGEM = "calagem"
    GESSAGEM = "gessagem"


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class ResultadoNutriente:
    """Resultado de prescrição para um nutriente específico."""
    dose: float = 0.0
    status: str = ""
    forma: str = ""
    bloqueado: bool = False
    alerta: Optional[str] = None
    unidade: str = "kg_ha"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dose_kg_ha" if self.unidade == "kg_ha" else "dose_t_ha": round(self.dose, 3),
            "status": self.status,
            "forma": self.forma,
            "bloqueado": self.bloqueado,
            "alerta": self.alerta,
        }


@dataclass
class ResultadoCorretivo:
    """Resultado de prescrição para um corretivo de solo."""
    dose_t_ha: float = 0.0
    status: str = ""
    metodo: str = ""
    meta: float = 0.0
    criterio: str = ""
    observacao: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dose_t_ha": round(self.dose_t_ha, 2),
            "status": self.status,
            "metodo": self.metodo,
            "meta_v_percent": self.meta,
            "criterio": self.criterio,
            "observacao": self.observacao,
        }


@dataclass
class PrescricaoZona:
    """Prescrição completa para uma zona de manejo."""
    zona_id: str = ""
    calagem: ResultadoCorretivo = field(default_factory=ResultadoCorretivo)
    gessagem: ResultadoCorretivo = field(default_factory=ResultadoCorretivo)
    nitrogenio: ResultadoNutriente = field(default_factory=lambda: ResultadoNutriente(forma="N"))
    fosforo: ResultadoNutriente = field(default_factory=lambda: ResultadoNutriente(forma="P2O5"))
    potassio: ResultadoNutriente = field(default_factory=lambda: ResultadoNutriente(forma="K2O"))
    calcio: ResultadoNutriente = field(default_factory=lambda: ResultadoNutriente(forma="Ca"))
    magnesio: ResultadoNutriente = field(default_factory=lambda: ResultadoNutriente(forma="Mg"))
    enxofre: ResultadoNutriente = field(default_factory=lambda: ResultadoNutriente(forma="S"))
    boro: ResultadoNutriente = field(default_factory=lambda: ResultadoNutriente(forma="B"))
    cobre: ResultadoNutriente = field(default_factory=lambda: ResultadoNutriente(forma="Cu"))
    ferro: ResultadoNutriente = field(default_factory=lambda: ResultadoNutriente(forma="Fe"))
    manganes: ResultadoNutriente = field(default_factory=lambda: ResultadoNutriente(forma="Mn"))
    zinco: ResultadoNutriente = field(default_factory=lambda: ResultadoNutriente(forma="Zn"))
    custo_estimado_ha: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "calagem": self.calagem.to_dict(),
            "gessagem": self.gessagem.to_dict(),
            "nitrogenio": self.nitrogenio.to_dict(),
            "fosforo": self.fosforo.to_dict(),
            "potassio": self.potassio.to_dict(),
            "calcio": self.calcio.to_dict(),
            "magnesio": self.magnesio.to_dict(),
            "enxofre": self.enxofre.to_dict(),
            "boro": self.boro.to_dict(),
            "cobre": self.cobre.to_dict(),
            "ferro": self.ferro.to_dict(),
            "manganes": self.manganes.to_dict(),
            "zinco": self.zinco.to_dict(),
            "custo_estimado_ha": round(self.custo_estimado_ha, 2),
        }


@dataclass
class ResumoPrescricao:
    """Resumo executivo da prescrição."""
    n_zonas: int = 0
    custo_medio_ha: float = 0.0
    custo_min_ha: float = 0.0
    custo_max_ha: float = 0.0
    economia_vrt: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_zonas": self.n_zonas,
            "custo_medio_ha": round(self.custo_medio_ha, 2),
            "custo_min_ha": round(self.custo_min_ha, 2),
            "custo_max_ha": round(self.custo_max_ha, 2),
            "economia_vrt": round(self.economia_vrt, 2),
        }


@dataclass
class NotasTecnicas:
    """Notas técnicas complementares à prescrição."""
    embasamento: str = ""
    bibliografia: str = ""
    referencia_legal: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "embasamento": self.embasamento,
            "bibliografia": self.bibliografia,
            "referencia_legal": self.referencia_legal,
        }


@dataclass
class ConfigPrescricao(ConfigBase):
    """Configuração da prescrição."""
    cultura: str = "soja"
    produtividade: float = 3.0
    teor_argila: float = 20.0
    metodo_id: str = "IAC_Graos"
    safra: Optional[str] = None
    safras: List[str] = field(default_factory=list)
    mapas_auxiliares: Dict[str, Any] = field(default_factory=dict)
    eficiencia_n: float = 0.6
    eficiencia_p2o5: float = 0.2
    eficiencia_k2o: float = 0.5
    eficiencia_ca: float = 0.8
    eficiencia_mg: float = 0.8
    eficiencia_s: float = 0.8
    eficiencia_micro: float = 0.1
    preco_n: float = 5.0
    preco_p2o5: float = 3.0
    preco_k2o: float = 2.5
    preco_ca: float = 0.5
    preco_mg: float = 1.0
    preco_s: float = 2.0
    preco_micro: float = 10.0
    preco_cal: float = 100.0
    preco_gesso: float = 80.0
    prnt_percent: float = 67.0
    guardrail_p_max: float = 40.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cultura": self.cultura,
            "produtividade": self.produtividade,
            "teor_argila": self.teor_argila,
            "metodo_id": self.metodo_id,
            "safra": self.safra,
            "safras": self.safras,
            "mapas_auxiliares": self.mapas_auxiliares,
            "eficiencia_n": self.eficiencia_n,
            "eficiencia_p2o5": self.eficiencia_p2o5,
            "eficiencia_k2o": self.eficiencia_k2o,
            "eficiencia_ca": self.eficiencia_ca,
            "eficiencia_mg": self.eficiencia_mg,
            "eficiencia_s": self.eficiencia_s,
            "eficiencia_micro": self.eficiencia_micro,
            "preco_n": self.preco_n,
            "preco_p2o5": self.preco_p2o5,
            "preco_k2o": self.preco_k2o,
            "preco_ca": self.preco_ca,
            "preco_mg": self.preco_mg,
            "preco_s": self.preco_s,
            "preco_micro": self.preco_micro,
            "preco_cal": self.preco_cal,
            "preco_gesso": self.preco_gesso,
            "prnt_percent": self.prnt_percent,
            "guardrail_p_max": self.guardrail_p_max,
        }


@dataclass
class ResultadoPrescricao(ResultadoBase):
    """Resultado da prescrição."""
    prescricoes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    resumo: Dict[str, Any] = field(default_factory=dict)
    notas_tecnicas: Dict[str, Any] = field(default_factory=dict)
    status: str = "sucesso"
    mensagens: List[str] = field(default_factory=list)
    config: Optional[ConfigPrescricao] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prescricoes": self.prescricoes,
            "resumo": self.resumo,
            "notas_tecnicas": self.notas_tecnicas,
            "status": self.status,
            "mensagens": self.mensagens,
            "config": self.config,
            **super().to_dict(),
        }