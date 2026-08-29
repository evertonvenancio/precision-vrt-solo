"""
Schemas Pydantic v2 para o módulo de Cruzamento Solo x Planta.

Define DTOs para:
- Entradas de cruzamento (camadas solo e planta)
- Alertas de diagnóstico agronômico
- Resultados consolidados do cruzamento
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


# ===================== ENUMS =====================

class TipoVariavelPlanta(str, Enum):
    """Tipos de variável de resposta da planta."""

    NDVI = "ndvi"
    PRODUTIVIDADE = "produtividade"


class ClasseFertilidade(str, Enum):
    """Classe de fertilidade da zona de solo."""

    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"
    DESCONHECIDA = "desconhecida"


class ClasseDesempenhPlanta(str, Enum):
    """Classe de desempenho da planta na zona."""

    ALTO = "alto"
    MEDIO = "medio"
    BAIXO = "baixo"


class NivelAlerta(str, Enum):
    """Nível de criticidade do alerta diagnóstico."""

    INFORMATIVO = "informativo"
    ATENCAO = "atencao"
    CRITICO = "critico"


class TipoDiagnostico(str, Enum):
    """Tipo de diagnóstico inferido pelo motor."""

    LIMITACAO_FISICA = "limitacao_fisica"
    LIMITACAO_NUTRICIONAL = "limitacao_nutricional"
    ANOMALIA = "anomalia"
    EFICIENCIA_ADEQUADA = "eficiencia_adequada"
    INCONCLUSIVO = "inconclusivo"


# ===================== SCHEMAS DE ENTRADA =====================

class EntradaCruzamento(BaseModel):
    """
    Schema de entrada para execução do cruzamento espacial.

    Contém os dois GeoJSONs (solo e planta) e parâmetros de controle.
    """

    geojson_solo: dict[str, Any] = Field(
        ...,
        description="GeoJSON FeatureCollection com zonas de solo e atributos químicos",
    )
    geojson_planta: dict[str, Any] = Field(
        ...,
        description="GeoJSON FeatureCollection com zonas de NDVI ou produtividade",
    )
    tipo_variavel_planta: TipoVariavelPlanta = Field(
        default=TipoVariavelPlanta.NDVI,
        description="Tipo da variável de resposta da planta",
    )
    campo_valor_planta: Optional[str] = Field(
        None,
        description="Nome do campo de valor na camada de planta (detectado automaticamente se None)",
    )
    campo_zona_id: str = Field(
        default="zona_id",
        description="Nome do campo de ID das zonas de solo",
    )
    nome_talhao: Optional[str] = Field(
        None,
        max_length=100,
        description="Nome do talhão para identificação",
    )
    safra: Optional[str] = Field(
        None,
        max_length=20,
        description="Safra de referência (ex: 2025/26)",
    )

    @model_validator(mode="after")
    def validar_geojsons(self) -> "EntradaCruzamento":
        """Valida estrutura básica dos GeoJSONs."""
        for campo, nome in [
            (self.geojson_solo, "geojson_solo"),
            (self.geojson_planta, "geojson_planta"),
        ]:
            if campo.get("type") != "FeatureCollection":
                raise ValueError(
                    f"'{nome}' deve ser um GeoJSON do tipo FeatureCollection."
                )
            if not campo.get("features"):
                raise ValueError(f"'{nome}' não contém features.")
        return self


# ===================== SCHEMAS DE DIAGNÓSTICO =====================

class AlertaDiagnostico(BaseModel):
    """
    Alerta diagnóstico gerado para uma zona de cruzamento.

    Cada alerta representa uma situação detectada pelo motor de regras
    a partir da combinação de fertilidade do solo e desempenho da planta.
    """

    zona_id: Any = Field(
        ...,
        description="Identificador da zona de solo analisada",
    )
    classificacao_solo: ClasseFertilidade = Field(
        ...,
        description="Classe de fertilidade do solo nesta zona",
    )
    classificacao_planta: ClasseDesempenhPlanta = Field(
        ...,
        description="Classe de desempenho da planta predominante na zona",
    )
    tipo_diagnostico: TipoDiagnostico = Field(
        ...,
        description="Tipo de diagnóstico inferido",
    )
    nivel_alerta: NivelAlerta = Field(
        ...,
        description="Nível de criticidade do alerta",
    )
    mensagem_alerta: str = Field(
        ...,
        description="Mensagem detalhada do diagnóstico para o agrônomo",
    )
    acao_recomendada: str = Field(
        ...,
        description="Ação prática recomendada para resolução",
    )
    modulo_relacionado: Optional[str] = Field(
        None,
        description="Módulo do sistema para ação complementar (ex: modulo_compactacao)",
    )
    area_ha: float = Field(
        default=0.0,
        ge=0,
        description="Área da zona em hectares",
    )
    atributos_solo: dict[str, Any] = Field(
        default_factory=dict,
        description="Atributos de solo da zona (ph, p, k, v, mo)",
    )


class EstatisticasCruzamento(BaseModel):
    """Estatísticas resumidas do cruzamento."""

    total_zonas: int = Field(description="Total de zonas de solo analisadas")
    area_total_ha: float = Field(description="Área total do talhão em ha")

    # Distribuição de fertilidade
    zonas_fertilidade_alta: int = Field(default=0)
    zonas_fertilidade_media: int = Field(default=0)
    zonas_fertilidade_baixa: int = Field(default=0)

    # Distribuição de planta
    zonas_planta_alto: int = Field(default=0)
    zonas_planta_medio: int = Field(default=0)
    zonas_planta_baixo: int = Field(default=0)

    # Diagnósticos
    alertas_limitacao_fisica: int = Field(default=0)
    alertas_limitacao_nutricional: int = Field(default=0)
    alertas_anomalia: int = Field(default=0)
    alertas_eficiencia_adequada: int = Field(default=0)

    # Porcentagens
    area_limitacao_fisica_ha: float = Field(default=0.0)
    area_limitacao_nutricional_ha: float = Field(default=0.0)


class ResultadoCruzamento(BaseModel):
    """
    DTO de saída completo do cruzamento Solo x Planta.

    Contém o GeoJSON resultante, alertas diagnósticos e estatísticas.
    """

    sucesso: bool = Field(description="Indica se o processamento foi bem-sucedido")
    mensagem: str = Field(description="Mensagem de status do processamento")

    # Metadados
    nome_talhao: Optional[str] = None
    safra: Optional[str] = None
    tipo_variavel_planta: str

    # GeoJSON da intersecção
    geojson_resultado: Optional[dict[str, Any]] = Field(
        None,
        description="GeoJSON com as zonas cruzadas e atributos agregados",
    )

    # Alertas por zona
    alertas: list[AlertaDiagnostico] = Field(
        default_factory=list,
        description="Lista de alertas diagnósticos por zona de solo",
    )

    # Estatísticas gerais
    estatisticas: Optional[EstatisticasCruzamento] = None

    # Erros de processamento
    erros: list[str] = Field(default_factory=list)

    @property
    def tem_alertas_criticos(self) -> bool:
        """Verifica se há alertas de nível crítico."""
        return any(a.nivel_alerta == NivelAlerta.CRITICO for a in self.alertas)

    @property
    def alertas_por_tipo(self) -> dict[str, list[AlertaDiagnostico]]:
        """Agrupa alertas por tipo de diagnóstico."""
        grupos: dict[str, list[AlertaDiagnostico]] = {}
        for alerta in self.alertas:
            tipo = alerta.tipo_diagnostico.value
            grupos.setdefault(tipo, []).append(alerta)
        return grupos

    model_config = {"from_attributes": True}


# ===================== SCHEMAS DE CLASSIFICAÇÃO =====================

class AtributosSolo(BaseModel):
    """Atributos químicos de uma zona de solo."""

    ph: Optional[float] = Field(None, ge=0, le=14, description="pH em água")
    p_mg_dm3: Optional[float] = Field(None, ge=0, description="Fósforo disponível mg/dm³")
    k_mg_dm3: Optional[float] = Field(None, ge=0, description="Potássio trocável mg/dm³")
    v_percent: Optional[float] = Field(None, ge=0, le=100, description="Saturação de bases %")
    mo_percent: Optional[float] = Field(None, ge=0, description="Matéria orgânica %")
    ca_cmolc_dm3: Optional[float] = Field(None, ge=0, description="Cálcio trocável cmolc/dm³")
    mg_cmolc_dm3: Optional[float] = Field(None, ge=0, description="Magnésio trocável cmolc/dm³")
    al_cmolc_dm3: Optional[float] = Field(None, ge=0, description="Alumínio tóxico cmolc/dm³")

    def to_dict(self) -> dict:
        """Retorna apenas campos com valores."""
        return {k: v for k, v in self.model_dump().items() if v is not None}


class RegraAplicada(BaseModel):
    """Registro de qual regra diagnóstica foi aplicada."""

    numero_regra: int
    nome_regra: str
    condicao: str
    resultado: str
