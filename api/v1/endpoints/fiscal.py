"""Endpoints fiscais (emissão de pré-nota via PlugNotas / eNotas)."""
from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from db.database import get_db
from models.fiscal import ProvedorFiscal, StatusNota
from app.services.fiscal_service import FiscalError, FiscalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fiscal", tags=["fiscal"])


class EmitirNotaRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    orcamento_id: UUID


class NotaFiscalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    orcamento_id: UUID
    provedor: ProvedorFiscal
    status: StatusNota
    protocolo: Optional[str]
    numero_nota: Optional[str]
    link_danfe: Optional[str]
    link_xml: Optional[str]
    valor_total: Optional[float]
    mensagem_sefaz: Optional[str]


@router.post(
    "/emitir-nota",
    response_model=NotaFiscalOut,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Gera uma pré-nota a partir de um orçamento e envia ao provedor.",
)
def emitir_nota(
    payload: EmitirNotaRequest,
    db: Session = Depends(get_db),
) -> NotaFiscalOut:
    svc = FiscalService(db)
    try:
        nota = svc.gerar_pre_nota(payload.orcamento_id)
    except FiscalError as exc:
        logger.warning("Falha ao emitir nota para %s: %s", payload.orcamento_id, exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return NotaFiscalOut.model_validate(nota)