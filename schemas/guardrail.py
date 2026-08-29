"""
Schemas Pydantic para o sistema de Guardrails (Seguranca Juridica e Agronomica).

Define os modelos de dados para validacao de prescricoes, resultados de
bloqueio/alarme e relatorios de conformidade.

Typical usage:
    >>> from schemas.guardrail import GuardrailResult, GuardrailReport
    >>> resultado = GuardrailResult(
    ...     nutriente_afetado="P2O5",
    ...     severidade="BLOCK",
    ...     mensagem="Teor de P muito alto",
    ...     regra_id="ENV_P_MAX"
    ... )
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class SeveridadeGuardrail(str, Enum):
    """Niveis de severidade do guardrail.

    Attributes:
        BLOCK: Impede o calculo do nutriente. Gera registro no laudo.
        WARNING: Permite o calculo com justificativa manual obrigatoria.
        INFO: Apenas informativo tecnico.
    """
    BLOCK = "BLOCK"
    WARNING = "WARNING"
    INFO = "INFO"


class GuardrailResult(BaseModel):
    """Resultado individual de uma validacao de guardrail.

    Representa uma unica violacao detectada para um nutriente ou parametro.

    Attributes:
        nutriente_afetado: Sigla do nutriente afetado (ex: "P2O5", "CaO", "N").
            Pode ser "GERAL" para regras que afetam multiplos nutrientes.
        severidade: Nivel de severidade (BLOCK, WARNING, INFO).
        mensagem: Mensagem descritiva para o usuario.
        regra_id: Identificador unico da regra (ex: "ENV_P_MAX", "SAT_BASES_V").
        valor_atual: Valor medido/detectado que disparou o guardrail.
        valor_limite: Valor limite configurado para a regra.
        zona_id: Identificador da zona/talhao afetada (opcional).
        justificativa: Justificativa manual do agronomo (preenchido em WARNING).
        metadata: Dados adicionais especificos da regra.
    """
    nutriente_afetado: str = Field(..., description="Nutriente ou parametro afetado")
    severidade: SeveridadeGuardrail = Field(..., description="Nivel de severidade")
    mensagem: str = Field(..., description="Mensagem descritiva para o usuario")
    regra_id: str = Field(..., description="ID unico da regra que disparou")
    valor_atual: Optional[float] = Field(None, description="Valor medido que disparou")
    valor_limite: Optional[float] = Field(None, description="Valor limite configurado")
    zona_id: Optional[str] = Field(None, description="ID da zona/talhao")
    justificativa: Optional[str] = Field(None, description="Justificativa manual do agronomo")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados extras")

    @field_validator("nutriente_afetado")
    @classmethod
    def _validar_nutriente(cls, v: str) -> str:
        """Normaliza o nutriente para maiusculas."""
        return v.strip().upper()

    def to_dict(self) -> Dict[str, Any]:
        """Serializa para dicionario Python nativo."""
        return self.model_dump()

    def is_bloqueante(self) -> bool:
        """Retorna True se a severidade for BLOCK."""
        return self.severidade == SeveridadeGuardrail.BLOCK

    def is_warning(self) -> bool:
        """Retorna True se a severidade for WARNING."""
        return self.severidade == SeveridadeGuardrail.WARNING


class GuardrailReport(BaseModel):
    """Relatorio completo de validacao de guardrails para uma prescricao.

    Agrega todos os resultados de validacao e fornece metodos para
    consultar bloqueios, warnings e status geral.

    Attributes:
        prescricao_id: ID da prescricao validada.
        zona_id: ID da zona/talhao.
        resultados: Lista de todos os GuardrailResult detectados.
        data_validacao: Data/hora da validacao.
        status_geral: Status consolidado ("APROVADO", "APROVADO_COM_RESSALVAS", "BLOQUEADO").
        nutrientes_bloqueados: Lista de nutrientes com bloqueio ativo.
        nutrientes_com_warning: Lista de nutrientes com warning ativo.
    """
    prescricao_id: int = Field(..., description="ID da prescricao")
    zona_id: Optional[str] = Field(None, description="ID da zona/talhao")
    resultados: List[GuardrailResult] = Field(default_factory=list)
    data_validacao: datetime = Field(default_factory=datetime.now)
    status_geral: str = Field("APROVADO", description="Status consolidado")
    nutrientes_bloqueados: List[str] = Field(default_factory=list)
    nutrientes_com_warning: List[str] = Field(default_factory=list)

    @field_validator("status_geral")
    @classmethod
    def _validar_status(cls, v: str) -> str:
        """Valida que o status esta entre os permitidos."""
        permitidos = {"APROVADO", "APROVADO_COM_RESSALVAS", "BLOQUEADO"}
        if v not in permitidos:
            raise ValueError(f"Status deve ser um de: {permitidos}")
        return v

    def adicionar_resultado(self, resultado: GuardrailResult) -> None:
        """Adiciona um resultado e atualiza status consolidado."""
        self.resultados.append(resultado)
        self._atualizar_status()

    def _atualizar_status(self) -> None:
        """Recalcula o status geral baseado nos resultados."""
        tem_block = any(r.is_bloqueante() for r in self.resultados)
        tem_warning = any(r.is_warning() for r in self.resultados)

        if tem_block:
            self.status_geral = "BLOQUEADO"
        elif tem_warning:
            self.status_geral = "APROVADO_COM_RESSALVAS"
        else:
            self.status_geral = "APROVADO"

        # Atualizar listas de nutrientes
        self.nutrientes_bloqueados = list(set(
            r.nutriente_afetado for r in self.resultados if r.is_bloqueante()
        ))
        self.nutrientes_com_warning = list(set(
            r.nutriente_afetado for r in self.resultados if r.is_warning()
        ))

    def tem_bloqueio(self, nutriente: Optional[str] = None) -> bool:
        """Verifica se ha bloqueios. Se nutriente especificado, verifica apenas para ele."""
        if nutriente:
            return any(
                r.nutriente_afetado == nutriente.upper() and r.is_bloqueante()
                for r in self.resultados
            )
        return any(r.is_bloqueante() for r in self.resultados)

    def tem_warning(self, nutriente: Optional[str] = None) -> bool:
        """Verifica se ha warnings. Se nutriente especificado, verifica apenas para ele."""
        if nutriente:
            return any(
                r.nutriente_afetado == nutriente.upper() and r.is_warning()
                for r in self.resultados
            )
        return any(r.is_warning() for r in self.resultados)

    def get_por_severidade(self, severidade: SeveridadeGuardrail) -> List[GuardrailResult]:
        """Filtra resultados por severidade."""
        return [r for r in self.resultados if r.severidade == severidade]

    def get_por_nutriente(self, nutriente: str) -> List[GuardrailResult]:
        """Filtra resultados por nutriente afetado."""
        return [r for r in self.resultados if r.nutriente_afetado == nutriente.upper()]

    def get_por_regra(self, regra_id: str) -> List[GuardrailResult]:
        """Filtra resultados por ID da regra."""
        return [r for r in self.resultados if r.regra_id == regra_id]

    def nutrientes_liberados(self) -> List[str]:
        """Retorna nutrientes que NAO tem bloqueio."""
        todos = set(r.nutriente_afetado for r in self.resultados)
        bloqueados = set(self.nutrientes_bloqueados)
        return list(todos - bloqueados)

    def to_dict(self) -> Dict[str, Any]:
        """Serializa relatorio para dicionario."""
        return self.model_dump()

    def resumo_texto(self) -> str:
        """Gera resumo textual do relatorio."""
        linhas = [
            f"Relatorio Guardrails - Prescricao {self.prescricao_id}",
            f"Status: {self.status_geral}",
            f"Data: {self.data_validacao.strftime('%d/%m/%Y %H:%M')}",
            f"Total de alertas: {len(self.resultados)}",
            f"Bloqueios: {len(self.nutrientes_bloqueados)}",
            f"Warnings: {len(self.nutrientes_com_warning)}",
        ]
        if self.nutrientes_bloqueados:
            linhas.append(f"Nutrientes bloqueados: {', '.join(self.nutrientes_bloqueados)}")
        if self.nutrientes_com_warning:
            linhas.append(f"Nutrientes com warning: {', '.join(self.nutrientes_com_warning)}")
        return "\n".join(linhas)


class DadosAmostra(BaseModel):
    """Modelo de dados de amostra de solo para validacao.

    Representa os dados laboratoriais de uma amostra de solo que serao
    validados pelos guardrails.

    Attributes:
        ph: pH do solo (agua ou CaCl2).
        fosforo_mg: Teor de fosforo em mg/dm3 (Mehlich ou outro extrator).
        potassio_mg: Teor de potassio em mg/dm3.
        calcio_cmol: Teor de calcio em cmolc/dm3.
        magnesio_cmol: Teor de magnesio em cmolc/dm3.
        aluminio_cmol: Teor de aluminio em cmolc/dm3 (opcional).
        h_al_cmol: Acidez potencial em cmolc/dm3 (opcional).
        argila_pct: Teor de argila em percentual.
        areia_pct: Teor de areia em percentual (opcional).
        silte_pct: Teor de silte em percentual (opcional).
        ctc: Capacidade de troca cationica (opcional).
        v_pct: Saturacao por bases em percentual (opcional).
        m_pct: Saturacao por aluminio em percentual (opcional).
        zona_id: Identificador da zona/talhao.
        amostra_id: Identificador da amostra.
    """
    ph: float = Field(..., ge=0.0, le=14.0, description="pH do solo")
    fosforo_mg: float = Field(..., ge=0.0, description="Fosforo em mg/dm3")
    potassio_mg: float = Field(..., ge=0.0, description="Potassio em mg/dm3")
    calcio_cmol: float = Field(..., ge=0.0, description="Calcio em cmolc/dm3")
    magnesio_cmol: float = Field(..., ge=0.0, description="Magnesio em cmolc/dm3")
    aluminio_cmol: Optional[float] = Field(None, ge=0.0, description="Aluminio em cmolc/dm3")
    h_al_cmol: Optional[float] = Field(None, ge=0.0, description="Acidez potencial cmolc/dm3")
    argila_pct: float = Field(..., ge=0.0, le=100.0, description="Argila em %")
    areia_pct: Optional[float] = Field(None, ge=0.0, le=100.0, description="Areia em %")
    silte_pct: Optional[float] = Field(None, ge=0.0, le=100.0, description="Silte em %")
    ctc: Optional[float] = Field(None, ge=0.0, description="CTC cmolc/dm3")
    v_pct: Optional[float] = Field(None, ge=0.0, le=100.0, description="Saturacao por bases %")
    m_pct: Optional[float] = Field(None, ge=0.0, le=100.0, description="Saturacao por Al %")
    zona_id: Optional[str] = Field(None, description="ID da zona")
    amostra_id: Optional[str] = Field(None, description="ID da amostra")

    @property
    def saturacao_bases(self) -> Optional[float]:
        """Calcula saturacao por bases (V%) se CTC estiver disponivel."""
        if self.ctc and self.ctc > 0:
            bases = self.calcio_cmol + self.magnesio_cmol
            if self.potassio_mg:
                # Converter K mg/dm3 para cmolc/dm3 (aprox: /390)
                k_cmol = self.potassio_mg / 390.0
                bases += k_cmol
            return (bases / self.ctc) * 100.0
        return self.v_pct

    @property
    def relacao_k_ca_mg(self) -> Optional[float]:
        """Calcula relacao K/(Ca+Mg) em cmolc/dm3."""
        ca_mg = self.calcio_cmol + self.magnesio_cmol
        if ca_mg > 0 and self.potassio_mg > 0:
            k_cmol = self.potassio_mg / 390.0
            return k_cmol / ca_mg
        return None

    @property
    def soma_bases(self) -> float:
        """Soma de bases em cmolc/dm3 (Ca + Mg + K)."""
        k_cmol = self.potassio_mg / 390.0 if self.potassio_mg else 0.0
        return self.calcio_cmol + self.magnesio_cmol + k_cmol

    def to_dict(self) -> Dict[str, Any]:
        """Serializa para dicionario."""
        return self.model_dump()

