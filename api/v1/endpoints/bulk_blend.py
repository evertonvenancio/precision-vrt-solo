"""
Endpoints REST para Bulk Blend & Misturas de Fertilizantes.

Rotas:
    POST /api/v1/bulk_blend/calcular    -- Calcular mistura otimizada
    GET  /api/v1/bulk_blend/fertilizantes -- Listar catalogo de fertilizantes
"""

import logging
from typing import Dict, List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from core.otimizacao.bulk_blend import (
    FertilizanteDisponivel,
    OtimizadorBulkBlend,
    RecomendacaoNutricional,
)
from config.fertilizantes_fisicos import CatalogoFertilizantes

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bulk_blend", tags=["Bulk Blend & Misturas"])


# =========================================================================
# Schemas Pydantic
# =========================================================================

class FertilizanteEntrada(BaseModel):
    """Fertilizante disponivel para o calculo de mistura."""
    nome: str = Field(..., description="Identificador do fertilizante (ex: UREIA, MAP, MOP)")
    custo_kg: float = Field(..., gt=0, description="Custo por kg em R$")
    composicao: Dict[str, float] = Field(..., description='Teores percentuais (ex: {"N": 45.0, "P2O5": 0.0})')
    sgn: float = Field(..., gt=0, description="Size Guide Number em mm")
    densidade: float = Field(..., gt=0, description="Densidade aparente em kg/L")
    inclusao_min_pct: float = Field(0.0, ge=0, le=100, description="Percentual minimo na mistura")
    inclusao_max_pct: float = Field(100.0, ge=0, le=100, description="Percentual maximo na mistura")


class RecomendacaoEntrada(BaseModel):
    """Demanda nutricional do talhao para calculo da mistura."""
    n_kg_ha: float = Field(..., ge=0, description="Nitrogenio desejado (kg/ha)")
    p2o5_kg_ha: float = Field(..., ge=0, description="Fosforo desejado (kg/ha)")
    k2o_kg_ha: float = Field(..., ge=0, description="Potassio desejado (kg/ha)")
    area_ha: float = Field(..., gt=0, description="Area do talhao em hectares")


class LoteSaida(BaseModel):
    """Lote gerado para aplicacao."""
    lote: int
    total_kg: float
    composicao: Dict[str, float]


class ResultadoSaida(BaseModel):
    """Resultado da otimizacao de mistura."""
    composicao: Dict[str, float] = Field(..., description="Quantidade de cada fertilizante em kg")
    custo_total: float = Field(..., description="Custo total da mistura em R$")
    nutrientes_totais: Dict[str, float] = Field(..., description="Nutrientes totais fornecidos em kg")
    pct_inclusao: Dict[str, float] = Field(..., description="Percentual de cada fertilizante na mistura")
    metodo: str = Field(..., description="Metodo usado: 'pulp' ou 'heuristico'")
    status: str = Field(..., description="Status: 'Optimal', 'Heuristico' ou 'Falha'")
    compatibilidade: float = Field(..., description="Nota de compatibilidade fisica (0 a 100)")
    lotes: List[LoteSaida] = Field(..., description="Lotes gerados para aplicacao")


class FertilizanteCatalogoSaida(BaseModel):
    """Fertilizante do catalogo padrao."""
    codigo: str
    nome: str
    composicao: Dict[str, float]
    densidade_aparente: float
    sgn: float
    custo_kg: float
    inclusao_max_pct: float
    inclusao_min_pct: float


class CalcularRequest(BaseModel):
    """Payload para calculo de mistura."""
    recomendacao: RecomendacaoEntrada
    fertilizantes: List[FertilizanteEntrada]
    usar_pulp: bool = Field(True, description="Usar otimizacao via PuLP se disponivel")
    capacidade_lote_kg: float = Field(5000.0, gt=0, description="Capacidade maxima de cada lote em kg")


# =========================================================================
# Endpoints
# =========================================================================

@router.post(
    "/calcular",
    response_model=ResultadoSaida,
    status_code=status.HTTP_200_OK,
    summary="Calcular mistura otimizada de fertilizantes",
    description=(
        "Recebe a demanda nutricional do talhao e a lista de fertilizantes disponiveis, "
        "e retorna a composicao otimizada da mistura com menor custo. "
        "Usa Programacao Linear (PuLP) como metodo principal, com fallback heuristico."
    ),
)
async def calcular_mistura(payload: CalcularRequest) -> ResultadoSaida:
    """Calcula a mistura de fertilizantes otimizada para a demanda informada."""
    try:
        # Converte entrada -> objetos de dominio
        recomendacao = RecomendacaoNutricional(
            n_kg_ha=payload.recomendacao.n_kg_ha,
            p2o5_kg_ha=payload.recomendacao.p2o5_kg_ha,
            k2o_kg_ha=payload.recomendacao.k2o_kg_ha,
            area_ha=payload.recomendacao.area_ha,
        )

        fertilizantes = [
            FertilizanteDisponivel(
                nome=f.nome,
                custo_kg=f.custo_kg,
                composicao=f.composicao,
                sgn=f.sgn,
                densidade=f.densidade,
                inclusao_min_pct=f.inclusao_min_pct,
                inclusao_max_pct=f.inclusao_max_pct,
            )
            for f in payload.fertilizantes
        ]

        if not fertilizantes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="E necessario informar pelo menos um fertilizante disponivel.",
            )

        # Executa otimizacao
        otimizador = OtimizadorBulkBlend(
            fertilizantes=fertilizantes,
            usar_pulp=payload.usar_pulp,
            capacidade_lote_kg=payload.capacidade_lote_kg,
        )
        resultado = otimizador.otimizar(recomendacao)

        if resultado.status == "Falha":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Nao foi possivel calcular uma mistura viavel com os fertilizantes informados.",
            )

        return ResultadoSaida(
            composicao=resultado.composicao,
            custo_total=resultado.custo_total,
            nutrientes_totais=resultado.nutrientes_totais,
            pct_inclusao=resultado.pct_inclusao,
            metodo=resultado.metodo,
            status=resultado.status,
            compatibilidade=resultado.compatibilidade,
            lotes=[LoteSaida(**lote) for lote in resultado.lotes],
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Erro ao calcular mistura: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao calcular mistura: {str(exc)}",
        )


@router.get(
    "/fertilizantes",
    response_model=List[FertilizanteCatalogoSaida],
    status_code=status.HTTP_200_OK,
    summary="Listar catalogo de fertilizantes",
    description="Retorna o catalogo padrao de fertilizantes granulados disponiveis para blending.",
)
async def listar_fertilizantes() -> List[FertilizanteCatalogoSaida]:
    """Lista todos os fertilizantes do catalogo padrao."""
    try:
        catalogo = CatalogoFertilizantes()
        fertilizantes = catalogo.listar_todos()

        return [
            FertilizanteCatalogoSaida(
                codigo=f.codigo,
                nome=f.nome,
                composicao=f.composicao,
                densidade_aparente=f.densidade_aparente,
                sgn=f.sgn,
                custo_kg=f.custo_kg,
                inclusao_max_pct=f.inclusao_max_pct,
                inclusao_min_pct=f.inclusao_min_pct,
            )
            for f in fertilizantes
        ]

    except Exception as exc:
        logger.exception("Erro ao listar fertilizantes: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao carregar catalogo: {str(exc)}",
        )
