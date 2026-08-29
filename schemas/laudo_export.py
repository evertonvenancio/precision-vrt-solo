"""Schemas (DTOs) para exportação de laudos.

Fase 5 - Parte 2: Exportação de Laudos (PDF Profissional, Cartão de Cabine,
ISOBUS XML).
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class FormatoExportacao(str, Enum):
    """Formatos suportados de exportação de laudo."""

    PDF_PROFISSIONAL = "pdf_profissional"
    CARTAO_CABINE = "cartao_cabine"
    ISOBUS_XML = "isobus_xml"


class OpcoesPDF(BaseModel):
    """Opções de personalização do PDF Profissional.

    Attributes:
        incluir_capa: Inclui capa com logo da empresa (white-label).
        incluir_art: Inclui ficha técnica do Responsável Técnico (ART/RT).
        incluir_mapa: Renderiza o mapa de zonas no PDF.
        incluir_metodologia: Inclui descrição da metodologia utilizada.
        exibir_custo: Exibe coluna de custo estimado por zona.
        idioma: Código ISO 639-1 do idioma (pt, en, es).
    """

    model_config = ConfigDict(extra="forbid")

    incluir_capa: bool = True
    incluir_art: bool = True
    incluir_mapa: bool = True
    incluir_metodologia: bool = True
    exibir_custo: bool = False
    idioma: str = Field(default="pt", min_length=2, max_length=5)


class OpcoesCartaoCabine(BaseModel):
    """Opções do Cartão de Cabine (A5)."""

    model_config = ConfigDict(extra="forbid")

    unidade_dose: str = Field(default="kg/ha", max_length=16)
    incluir_qrcode: bool = True


class OpcoesISOBUS(BaseModel):
    """Opções de exportação ISOBUS / ISO 11783 (TaskData)."""

    model_config = ConfigDict(extra="forbid")

    versao_iso: str = Field(default="4", description="Versão do TaskData (3 ou 4).")
    cliente_id_externo: Optional[str] = Field(
        default=None,
        description="ID do cliente no terminal/console (CTR).",
    )
    fazenda_id_externo: Optional[str] = Field(
        default=None,
        description="ID da fazenda (FRM) no terminal.",
    )


class ExportarLaudoRequest(BaseModel):
    """Requisição de exportação de um laudo de prescrição."""

    model_config = ConfigDict(extra="forbid")

    prescricao_id: UUID
    formato: FormatoExportacao
    opcoes_pdf: Optional[OpcoesPDF] = None
    opcoes_cartao: Optional[OpcoesCartaoCabine] = None
    opcoes_isobus: Optional[OpcoesISOBUS] = None


class ArquivoExportado(BaseModel):
    """Metadados do arquivo gerado."""

    model_config = ConfigDict(from_attributes=True)

    prescricao_id: UUID
    formato: FormatoExportacao
    caminho: str = Field(description="Caminho absoluto do arquivo no storage.")
    nome_arquivo: str
    mime_type: str
    tamanho_bytes: int
    gerado_em: datetime


class ZonaPrescricaoDTO(BaseModel):
    """Representação de uma zona de manejo para renderização."""

    model_config = ConfigDict(from_attributes=True)

    numero: int
    nome: str
    cor_hex: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    area_ha: float
    dose: float
    unidade: str = "kg/ha"
    insumo: str
    custo_estimado: Optional[float] = None


class PrescricaoCompletaDTO(BaseModel):
    """DTO agregando os dados necessários para renderizar um laudo."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    titulo: str
    talhao: str
    fazenda: str
    cliente: str
    cultura: str
    safra: str
    area_total_ha: float
    metodologia: str
    responsavel_tecnico_nome: str
    responsavel_tecnico_registro: str
    responsavel_tecnico_art: Optional[str] = None
    logo_path: Optional[str] = None
    mapa_path: Optional[str] = None
    zonas: List[ZonaPrescricaoDTO]
    criado_em: datetime
