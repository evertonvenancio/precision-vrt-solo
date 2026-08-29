"""
Endpoints REST para Vendas e Baixa de Títulos Financeiros.

Rotas:
    POST /api/v1/vendas/avista          — Registrar venda à vista
    POST /api/v1/vendas/prazo           — Registrar venda a prazo (parcelas)
    GET  /api/v1/vendas/{venda_id}      — Buscar venda com títulos
    POST /api/v1/titulos/baixa          — Registrar pagamento de um título
    GET  /api/v1/titulos/cliente/{id}   — Listar títulos de um cliente
    POST /api/v1/titulos/sync-atrasados — Sincronizar status de títulos vencidos
"""

import logging
import uuid
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.vendas import (
    BaixaPagamentoRequest,
    BaixaPagamentoResponse,
    VendaCreate,
    VendaPrazoCreate,
    VendaResponse,
)
from app.services.vendas_service import VendasService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Vendas e Títulos"])


def get_vendas_service(db: Session = Depends(get_db)) -> VendasService:
    """Fábrica do VendasService para injeção via FastAPI Depends."""
    return VendasService(db=db)


@router.post(
    "/api/v1/vendas/avista",
    response_model=VendaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar venda à vista",
    description=(
        "Cria uma venda e gera automaticamente 1 título financeiro RECEBER "
        "com data de vencimento igual a hoje. "
        "O orçamento referenciado deve estar em status 'aprovado' ou 'faturado'."
    ),
)
def registrar_venda_avista(
    payload: VendaCreate,
    service: VendasService = Depends(get_vendas_service),
) -> VendaResponse:
    try:
        venda = service.registrar_venda_avista(payload)
    except ValueError as exc:
        _raise_erro_negocio(exc)
    return _venda_para_response(venda)


@router.post(
    "/api/v1/vendas/prazo",
    response_model=VendaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar venda a prazo",
    description=(
        "Cria uma venda e gera N títulos RECEBER com datas de vencimento "
        "individuais por parcela. Ideal para negociações vinculadas à safra/"
        "colheita onde o vencimento coincide com a entrega da produção. "
        "A soma das parcelas deve ser igual ao valor líquido do orçamento."
    ),
)
def registrar_venda_prazo(
    payload: VendaPrazoCreate,
    service: VendasService = Depends(get_vendas_service),
) -> VendaResponse:
    try:
        venda = service.registrar_venda_prazo(payload)
    except ValueError as exc:
        _raise_erro_negocio(exc)
    return _venda_para_response(venda)


@router.get(
    "/api/v1/vendas/{venda_id}",
    response_model=VendaResponse,
    summary="Buscar venda por ID",
    description="Retorna a venda com todos os títulos financeiros vinculados.",
)
def buscar_venda(
    venda_id: uuid.UUID,
    service: VendasService = Depends(get_vendas_service),
) -> VendaResponse:
    try:
        venda = service.buscar_venda(venda_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    return _venda_para_response(venda)


@router.post(
    "/api/v1/titulos/baixa",
    response_model=BaixaPagamentoResponse,
    status_code=status.HTTP_200_OK,
    summary="Registrar pagamento (baixa) de um título",
    description=(
        "Marca um título financeiro como pago. "
        "Se o valor pago for menor que o valor original, um título residual "
        "é gerado automaticamente com o saldo devedor. "
        "Atualiza o status da venda para 'concluida' quando todos os títulos "
        "estiverem quitados."
    ),
)
def baixar_titulo(
    request: BaixaPagamentoRequest,
    service: VendasService = Depends(get_vendas_service),
) -> BaixaPagamentoResponse:
    try:
        resultado = service.baixar_titulo(request)
    except ValueError as exc:
        _raise_erro_negocio(exc)
    return resultado


@router.get(
    "/api/v1/titulos/cliente/{cliente_id}",
    summary="Listar títulos financeiros de um cliente",
    description=(
        "Retorna todos os títulos financeiros de um cliente, com filtros "
        "opcionais por status e tipo (RECEBER/PAGAR)."
    ),
)
def listar_titulos_cliente(
    cliente_id: uuid.UUID,
    status_filtro: Annotated[
        Optional[str],
        Query(
            alias="status",
            description="Filtrar por status: pendente | pago | atrasado | cancelado",
        ),
    ] = None,
    tipo: Annotated[
        Optional[str],
        Query(description="Filtrar por tipo: RECEBER | PAGAR"),
    ] = None,
    service: VendasService = Depends(get_vendas_service),
) -> List[dict]:
    STATUSES_VALIDOS = {"pendente", "pago", "atrasado", "cancelado"}
    TIPOS_VALIDOS = {"RECEBER", "PAGAR"}

    if status_filtro and status_filtro not in STATUSES_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status inválido: '{status_filtro}'. Válidos: {sorted(STATUSES_VALIDOS)}",
        )
    if tipo and tipo not in TIPOS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo inválido: '{tipo}'. Válidos: {sorted(TIPOS_VALIDOS)}",
        )

    try:
        titulos = service.listar_titulos_cliente(
            cliente_id=cliente_id,
            status=status_filtro,
            tipo=tipo,
        )
    except Exception as exc:
        logger.exception("Erro ao listar títulos do cliente %s: %s", cliente_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar títulos.",
        ) from exc

    return [
        {
            "id": str(t.id),
            "tipo": t.tipo,
            "valor_original": str(t.valor_original),
            "valor_liquidado": str(t.valor_liquidado) if t.valor_liquidado else None,
            "data_vencimento": t.data_vencimento.isoformat(),
            "data_pagamento": t.data_pagamento.isoformat() if t.data_pagamento else None,
            "status": t.status,
            "metodo_pagamento": t.metodo_pagamento,
            "parcela": f"{t.parcela_numero}/{t.parcela_total}"
            if t.parcela_numero and t.parcela_total
            else None,
            "esta_vencido": t.esta_vencido,
        }
        for t in titulos
    ]


@router.post(
    "/api/v1/titulos/sync-atrasados",
    summary="Sincronizar status de títulos vencidos",
    description=(
        "Atualiza para 'atrasado' todos os títulos com status 'pendente' e "
        "data_vencimento anterior a hoje. Deve ser chamado por um job agendado "
        "(cron diário). Requer autenticação de administrador."
    ),
)
def sincronizar_atrasados(
    tenant_id: Annotated[uuid.UUID, Query(description="UUID do tenant a sincronizar")],
    service: VendasService = Depends(get_vendas_service),
) -> dict:
    try:
        atualizados = service.sincronizar_status_atrasados(tenant_id)
    except Exception as exc:
        logger.exception("Erro ao sincronizar atrasados tenant=%s: %s", tenant_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao sincronizar títulos.",
        ) from exc

    return {"tenant_id": str(tenant_id), "titulos_atualizados": atualizados}


def _raise_erro_negocio(exc: Exception) -> None:
    """Converte ValueError de regra de negócio em HTTPException 400."""
    msg = str(exc)
    http_status = (
        status.HTTP_404_NOT_FOUND if "não encontrad" in msg.lower()
        else status.HTTP_400_BAD_REQUEST
    )
    raise HTTPException(status_code=http_status, detail=msg) from exc


def _venda_para_response(venda) -> VendaResponse:
    """Converte instância de Venda para VendaResponse."""
    from schemas.vendas import TituloFinanceiroResponse

    titulos_resp = []
    for t in venda.titulos:
        titulos_resp.append(
            TituloFinanceiroResponse(
                id=t.id,
                tenant_id=t.tenant_id,
                cliente_id=t.cliente_id,
                orcamento_id=t.orcamento_id,
                venda_id=t.venda_id,
                tipo=t.tipo,
                valor_original=t.valor_original,
                valor_liquidado=t.valor_liquidado,
                data_emissao=t.data_emissao,
                data_vencimento=t.data_vencimento,
                data_pagamento=t.data_pagamento,
                status=t.status,
                metodo_pagamento=t.metodo_pagamento,
                parcela_numero=t.parcela_numero,
                parcela_total=t.parcela_total,
                saldo_residual=t.saldo_residual,
                esta_vencido=t.esta_vencido,
                criado_em=t.criado_em,
                atualizado_em=t.atualizado_em,
            )
        )

    return VendaResponse(
        id=venda.id,
        tenant_id=venda.tenant_id,
        orcamento_id=venda.orcamento_id,
        cliente_id=venda.cliente_id,
        valor_total=venda.valor_total,
        tipo_venda=venda.tipo_venda,
        status=venda.status,
        total_liquidado=venda.total_liquidado,
        esta_quitada=venda.esta_quitada,
        criado_em=venda.criado_em,
        titulos=titulos_resp,
    )