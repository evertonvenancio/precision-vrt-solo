"""Schemas Pydantic da Central de Comunicação."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from models.comunicacao import CanalEnvio, StatusEnvio, TipoDocumento  # type: ignore[import-not-found]


class EnviarDocumentoRequest(BaseModel):
    """Payload do endpoint ``POST /comunicacao/enviar-documento``."""

    documento_id: int = Field(..., gt=0, description="ID do laudo ou orçamento.")
    canal: CanalEnvio = Field(..., description="Canal de envio: ``whatsapp`` ou ``email``.")
    destino: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Telefone (E.164, ex.: +5511999999999) ou e-mail.",
    )
    tipo_documento: TipoDocumento = Field(default=TipoDocumento.LAUDO)
    assunto: str | None = Field(default=None, max_length=500)
    mensagem: str | None = Field(default=None)

    @field_validator("destino")
    @classmethod
    def _strip(cls, v: str) -> str:
        return v.strip()


class EnviarDocumentoResponse(BaseModel):
    """Resposta do endpoint de envio."""

    sucesso: bool
    canal: CanalEnvio
    destinatario: str
    log_id: int | None = None
    detalhe: str | None = None


class LogEnvioOut(BaseModel):
    """Saída pública de um registro de log."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    canal: CanalEnvio
    status: StatusEnvio
    tipo_documento: TipoDocumento
    destinatario: str
    assunto: str | None
    documento_id: int | None
    referencia_id: int | None
    erro: str | None
    resposta_api: dict[str, Any] | None
    enviado_em: datetime


class AniversarianteOut(BaseModel):
    """Pessoa que faz aniversário hoje."""

    id: int
    nome: str
    tipo: str = Field(description="``cliente`` ou ``funcionario``.")
    email: str | None = Field(default=None, pattern=r"^[^@]+@[^@]+\.[^@]+$")
    telefone: str | None = None


class DispararAniversariosResponse(BaseModel):
    """Resposta da rotina de aniversários."""

    total: int
    enviados: int
    falhas: int
    ja_enviados_hoje: int
