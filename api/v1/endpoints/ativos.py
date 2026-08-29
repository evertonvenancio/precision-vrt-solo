"""
Endpoints REST para Gestão de Ativos Patrimoniais, ROI e Ponto de Equilíbrio.

Rotas:
    POST /api/v1/ativos                         — Cadastrar ativo
    GET  /api/v1/ativos/{ativo_id}              — Buscar ativo por ID
    PUT  /api/v1/ativos/{ativo_id}              — Atualizar ativo
    DELETE /api/v1/ativos/{ativo_id}/baixa      — Baixar (desativar) ativo
    GET  /api/v1/ativos/tenant/{tenant_id}      — Listar ativos do tenant
    POST /api/v1/ativos/roi                     — Calcular ROI de um ativo
    POST /api/v1/ativos/ponto-equilibrio        — Calcular ponto de equilíbrio
"""

import logging
import uuid
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.ativos import (
    AtivoCreate,
    AtivoResponse,
    PontoEquilibrioRequest,
    PontoEquilibrioResponse,
    RoiAtivoRequest,
    RoiAtivoResponse,
)
from app.services.ativos_service import AtivosService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ativos", tags=["Ativos Patrimoniais"])


def get_ativos_service(db: Session = Depends(get_db)) -> AtivosService:
    """Fábrica do AtivosService para injeção via FastAPI Depends."""
    return AtivosService(db=db)


@router.post(
    "",
    response_model=AtivoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar ativo patrimonial",
    description=(
        "Cadastra um bem da empresa e calcula automaticamente a depreciação "
        "mensal pelo método linear: "
        "(valor_aquisicao - valor_residual) / (vida_util_anos × 12)."
    ),
)
def cadastrar_ativo(
    payload: AtivoCreate,
    service: AtivosService = Depends(get_ativos_service),
) -> AtivoResponse:
    try:
        ativo = service.cadastrar_ativo(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    return service._ativo_para_response(ativo)


@router.get(
    "/{ativo_id}",
    response_model=AtivoResponse,
    summary="Buscar ativo por ID",
    description="Retorna os dados completos de um ativo, incluindo depreciação acumulada e valor contábil atual.",
)
def buscar_ativo(
    ativo_id: uuid.UUID,
    service: AtivosService = Depends(get_ativos_service),
) -> AtivoResponse:
    try:
        ativo = service.buscar_ativo(ativo_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    return service._ativo_para_response(ativo)


@router.put(
    "/{ativo_id}",
    response_model=AtivoResponse,
    summary="Atualizar ativo patrimonial",
    description="Atualiza os dados do ativo e recalcula a depreciação mensal automaticamente.",
)
def atualizar_ativo(
    ativo_id: uuid.UUID,
    payload: AtivoCreate,
    service: AtivosService = Depends(get_ativos_service),
) -> AtivoResponse:
    try:
        ativo = service.atualizar_ativo(ativo_id, payload)
    except ValueError as exc:
        code = (
            status.HTTP_404_NOT_FOUND
            if "não encontrado" in str(exc)
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=code, detail=str(exc)) from exc
    return service._ativo_para_response(ativo)


@router.delete(
    "/{ativo_id}/baixa",
    response_model=AtivoResponse,
    summary="Baixar ativo (desativar)",
    description=(
        "Marca o ativo como baixado/descartado (ativo=False). "
        "O registro é mantido no banco para fins de histórico e auditoria."
    ),
)
def baixar_ativo(
    ativo_id: uuid.UUID,
    service: AtivosService = Depends(get_ativos_service),
) -> AtivoResponse:
    try:
        ativo = service.baixar_ativo(ativo_id)
    except ValueError as exc:
        code = (
            status.HTTP_404_NOT_FOUND
            if "não encontrado" in str(exc)
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=code, detail=str(exc)) from exc
    return service._ativo_para_response(ativo)


@router.get(
    "/tenant/{tenant_id}",
    response_model=List[AtivoResponse],
    summary="Listar ativos do tenant",
    description="Retorna todos os ativos patrimoniais do tenant, com filtros opcionais por categoria e status.",
)
def listar_ativos(
    tenant_id: uuid.UUID,
    categoria: Annotated[
        Optional[str],
        Query(description="Filtrar por categoria: veiculo | equipamento | imovel | ferramenta"),
    ] = None,
    apenas_ativos: Annotated[
        bool,
        Query(description="Se True, retorna apenas bens em uso (padrão: True)"),
    ] = True,
    service: AtivosService = Depends(get_ativos_service),
) -> List[AtivoResponse]:
    from models.ativos import CATEGORIAS_ATIVO

    if categoria and categoria not in CATEGORIAS_ATIVO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Categoria '{categoria}' inválida. Válidas: {list(CATEGORIAS_ATIVO)}",
        )

    try:
        ativos = service.listar_ativos_tenant(
            tenant_id=tenant_id,
            categoria=categoria,
            apenas_ativos=apenas_ativos,
        )
    except Exception as exc:
        logger.exception("Erro ao listar ativos tenant=%s: %s", tenant_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar ativos.",
        ) from exc

    return [service._ativo_para_response(a) for a in ativos]


@router.post(
    "/roi",
    response_model=RoiAtivoResponse,
    summary="Calcular ROI de um ativo",
    description=(
        "Calcula o Retorno sobre Investimento (ROI) de um ativo patrimonial "
        "com base no faturamento gerado pelo seu uso. "
        "ROI = (faturamento - depreciação_período) / valor_aquisicao × 100. "
        "Inclui estimativa de payback em meses."
    ),
)
def calcular_roi(
    request: RoiAtivoRequest,
    service: AtivosService = Depends(get_ativos_service),
) -> RoiAtivoResponse:
    try:
        resultado = service.calcular_roi_ativo(request)
    except ValueError as exc:
        code = (
            status.HTTP_404_NOT_FOUND
            if "não encontrado" in str(exc)
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=code, detail=str(exc)) from exc
    return resultado


@router.post(
    "/ponto-equilibrio",
    response_model=PontoEquilibrioResponse,
    summary="Calcular ponto de equilíbrio operacional",
    description=(
        "Calcula quantos serviços/mês precisam ser realizados para cobrir "
        "todos os custos fixos mensais da operação (salários, depreciação, "
        "aluguel, seguros, etc.). "
        "Fórmula: PE = custo_fixo / (ticket_medio × margem_variavel_pct / 100)."
    ),
)
def calcular_ponto_equilibrio(
    request: PontoEquilibrioRequest,
    service: AtivosService = Depends(get_ativos_service),
) -> PontoEquilibrioResponse:
    try:
        resultado = service.calcular_ponto_equilibrio(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    return resultado