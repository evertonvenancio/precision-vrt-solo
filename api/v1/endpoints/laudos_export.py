"""Endpoints para download e listagem de laudos exportados."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.laudo_export_service import obter_caminho_laudo, listar_laudos_disponiveis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/laudos", tags=["Laudos e Exportacoes"])


@router.get(
    "/download/{nome_arquivo}",
    summary="Download de laudo exportado (PDF, CSV, Shapefile).",
)
def download_laudo(
    nome_arquivo: str,
    db: Session = Depends(get_db),
):
    """Retorna o arquivo de laudo solicitado com validacao de path traversal.

    Args:
        nome_arquivo: Nome do arquivo (ex: laudo_123.pdf).

    Returns:
        FileResponse com o arquivo binario.

    Raises:
        HTTPException 404: Se o arquivo nao existir ou for invalido.
    """
    logger.info("Solicitacao de download: %s", nome_arquivo)

    try:
        caminho = obter_caminho_laudo(nome_arquivo)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro inesperado ao localizar laudo %s: %s", nome_arquivo, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar solicitacao de download."
        )

    return FileResponse(
        path=str(caminho),
        filename=caminho.name,
        media_type="application/octet-stream",
    )


@router.get(
    "/listar",
    summary="Listar laudos disponiveis para download.",
)
def listar_laudos(
    db: Session = Depends(get_db),
):
    """Lista todos os laudos disponiveis no diretorio de exportacoes.

    Returns:
        Lista de dicts com metadados dos arquivos.
    """
    logger.info("Listando laudos disponiveis")
    return {"laudos": listar_laudos_disponiveis()}