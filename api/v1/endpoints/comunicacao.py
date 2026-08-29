"""Endpoints HTTP da Central de Comunicação."""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from models.comunicacao import CanalEnvio
from schemas.comunicacao import (
    DispararAniversariosResponse,
    EnviarDocumentoRequest,
    EnviarDocumentoResponse,
)
from app.services.comunicacao_service import ComunicacaoService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/comunicacao", tags=["Comunicação"])


def _resolver_documento(documento_id: int) -> tuple[str, str]:
    """Resolve documento_id em (caminho_pdf, assunto_padrao)."""
    pdf_path = f"/var/precision_vrt/documentos/{documento_id}.pdf"
    if not Path(pdf_path).is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento {documento_id} não encontrado.",
        )
    return pdf_path, f"Documento Precision VRT #{documento_id}"


@router.post(
    "/enviar-documento",
    response_model=EnviarDocumentoResponse,
    status_code=status.HTTP_200_OK,
    summary="Envia laudo/orçamento via WhatsApp ou E-mail.",
)
def enviar_documento(
    payload: EnviarDocumentoRequest,
    db: Session = Depends(get_db),
) -> EnviarDocumentoResponse:
    pdf_path, assunto_padrao = _resolver_documento(payload.documento_id)
    service = ComunicacaoService(db=db)

    mensagem = payload.mensagem or (
        f"Olá! Segue em anexo o documento solicitado (#{payload.documento_id})."
    )
    assunto = payload.assunto or assunto_padrao

    if payload.canal == CanalEnvio.WHATSAPP:
        resultado = service.enviar_whatsapp(
            numero_destino=payload.destino,
            mensagem=mensagem,
            pdf_path=pdf_path,
            tipo_documento=payload.tipo_documento,
            documento_id=payload.documento_id,
        )
    elif payload.canal == CanalEnvio.EMAIL:
        resultado = service.enviar_email(
            destino=payload.destino,
            assunto=assunto,
            corpo=mensagem,
            anexo_path=pdf_path,
            tipo_documento=payload.tipo_documento,
            documento_id=payload.documento_id,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Canal inválido: {payload.canal}",
        )

    if not resultado.sucesso:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=resultado.detalhe,
        )

    return EnviarDocumentoResponse(
        sucesso=True,
        canal=payload.canal,
        destinatario=payload.destino,
        detalhe=resultado.detalhe,
    )


@router.post(
    "/aniversarios/disparar",
    response_model=DispararAniversariosResponse,
    summary="Dispara parabéns para os aniversariantes do dia.",
)
def disparar_aniversarios(
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    sincrono: bool = False,
) -> DispararAniversariosResponse:
    service = ComunicacaoService(db=db)

    if sincrono:
        stats = service.disparar_parabens_automatico()
        return DispararAniversariosResponse(**stats)

    background.add_task(service.disparar_parabens_automatico)
    return DispararAniversariosResponse(
        total=0, enviados=0, falhas=0, ja_enviados_hoje=0
    )