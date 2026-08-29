"""
Endpoints REST para consulta de previsao e analise de janela de aplicacao.
Sintaxe classica do FastAPI (sem Annotated) para compatibilidade total.
"""

import logging
from functools import lru_cache
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from config.clima_config import clima_config
from schemas.clima import JanelaAplicacaoResponseSchema, PrevisaoResponseSchema
from app.services.clima_service import ClimaService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clima", tags=["Clima"])


# ---------------------------------------------------------------------------
# Injecao de dependencia do servico
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _api_key() -> str:
    """Le a chave da API de clima."""
    # Chave fixa para testes:
    return "a5097499242c0b7b4618af23e671fd9f"


def get_clima_service() -> ClimaService:
    """Fabrica do ClimaService para injecao via FastAPI Depends.

    Returns:
        Instancia configurada do ClimaService.
    """
    return ClimaService(api_key=_api_key(), config=clima_config)

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/previsao",
    response_model=PrevisaoResponseSchema,
    summary="Previsao climatica por localizacao",
    description=(
        "Retorna a previsao do tempo para os proximos dias a partir das "
        "coordenadas geograficas ou do nome da cidade informada. "
        "Se a cidade for informada, o sistema resolve lat/lon automaticamente "
        "via Geocoding API. Resultados sao cacheados por ate 1 hora."
    ),
)
def get_previsao(
    lat: Optional[float] = Query(
        None,
        description="Latitude do ponto de interesse",
        ge=-90,
        le=90,
    ),
    lon: Optional[float] = Query(
        None,
        description="Longitude do ponto de interesse",
        ge=-180,
        le=180,
    ),
    cidade: Optional[str] = Query(
        None,
        description="Nome da cidade para busca automatica de coordenadas (ex: Londrina, PR)",
        min_length=2,
        max_length=100,
    ),
    service: ClimaService = Depends(get_clima_service),
) -> PrevisaoResponseSchema:
    """Busca e retorna previsao climatica em formato padronizado.

    Aceita coordenadas diretas (lat/lon) ou nome de cidade.
    Se a cidade for informada, resolve lat/lon via Geocoding API.

    Args:
        lat: Latitude do talhao ou propriedade.
        lon: Longitude do talhao ou propriedade.
        cidade: Nome da cidade para resolucao automatica de coordenadas.
        service: Instancia injetada do ClimaService.

    Returns:
        PrevisaoResponseSchema com lista de dias previstos.

    Raises:
        HTTPException 400: Parametros invalidos ou cidade nao encontrada.
        HTTPException 422: Parametros fora dos limites (FastAPI valida automaticamente).
        HTTPException 503: Falha interna inesperada ao chamar servico externo.
    """
    # Validacao: precisa de cidade OU lat+lon
    if cidade is None and (lat is None or lon is None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe o nome da cidade (cidade=...) ou as coordenadas (lat=...&lon=...).",
        )

    # Se cidade informada, resolver coordenadas
    if cidade is not None:
        try:
            lat, lon = service.buscar_coordenadas_por_cidade(cidade)
        except ValueError as exc:
            logger.warning("Cidade nao encontrada: %s -- %s", cidade, exc)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except Exception as exc:
            logger.exception("Erro ao resolver cidade '%s': %s", cidade, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Erro ao buscar coordenadas da cidade. Tente novamente mais tarde.",
            ) from exc

    try:
        resultado = service.buscar_previsao(lat=lat, lon=lon)
    except Exception as exc:
        logger.exception("Erro inesperado em /previsao: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servico de clima temporariamente indisponivel.",
        ) from exc

    return resultado


@router.get(
    "/alertas",
    response_model=JanelaAplicacaoResponseSchema,
    summary="Analise de janela de aplicacao agronomica",
    description=(
        "Cruza os dados de previsao do tempo com os limites agronomicos "
        "configurados para o tipo de insumo informado. Retorna se e seguro "
        "realizar a aplicacao hoje e uma lista detalhada de alertas."
    ),
)
def get_alertas(
    lat: Optional[float] = Query(
        None,
        description="Latitude do talhao",
        ge=-90,
        le=90,
    ),
    lon: Optional[float] = Query(
        None,
        description="Longitude do talhao",
        ge=-180,
        le=180,
    ),
    cidade: Optional[str] = Query(
        None,
        description="Nome da cidade para resolucao automatica de coordenadas",
        min_length=2,
        max_length=100,
    ),
    tipo_aplicacao: str = Query(
        "ureia",
        description=(
            "Tipo de insumo a analisar. Valores aceitos: "
            + ", ".join(f"'{k}'" for k in clima_config.TIPOS_APLICACAO_VALIDOS)
        ),
        min_length=2,
        max_length=50,
    ),
    service: ClimaService = Depends(get_clima_service),
) -> JanelaAplicacaoResponseSchema:
    """Gera analise de janela de aplicacao para o insumo e localizacao dados.

    Args:
        lat: Latitude do talhao.
        lon: Longitude do talhao.
        cidade: Nome da cidade para resolucao automatica de coordenadas.
        tipo_aplicacao: Tipo de insumo (ureia, foliar, herbicida).
        service: Instancia injetada do ClimaService.

    Returns:
        JanelaAplicacaoResponseSchema com decisao e alertas detalhados.

    Raises:
        HTTPException 400: Tipo de aplicacao nao reconhecido ou parametros invalidos.
        HTTPException 404: Cidade nao encontrada.
        HTTPException 503: Falha inesperada ao chamar servico externo.
    """
    # Validacao: precisa de cidade OU lat+lon
    if cidade is None and (lat is None or lon is None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe o nome da cidade (cidade=...) ou as coordenadas (lat=...&lon=...).",
        )

    tipo_norm = tipo_aplicacao.lower().strip()
    if tipo_norm not in clima_config.TIPOS_APLICACAO_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Tipo de aplicacao '{tipo_aplicacao}' nao reconhecido. "
                f"Valores validos: {list(clima_config.TIPOS_APLICACAO_VALIDOS.keys())}"
            ),
        )

    # Se cidade informada, resolver coordenadas
    if cidade is not None:
        try:
            lat, lon = service.buscar_coordenadas_por_cidade(cidade)
        except ValueError as exc:
            logger.warning("Cidade nao encontrada: %s -- %s", cidade, exc)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except Exception as exc:
            logger.exception("Erro ao resolver cidade '%s': %s", cidade, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Erro ao buscar coordenadas da cidade. Tente novamente mais tarde.",
            ) from exc

    try:
        resultado = service.gerar_alertas_aplicacao(
            lat=lat, lon=lon, tipo_aplicacao=tipo_norm
        )
    except Exception as exc:
        logger.exception("Erro inesperado em /alertas: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servico de clima temporariamente indisponivel.",
        ) from exc

    return resultado


@router.get(
    "/historico",
    response_model=PrevisaoResponseSchema,
    summary="Historico climatico para auditoria de laudo",
    description=(
        "Retorna dados climaticos dos ultimos dias para fins de auditoria "
        "juridica do laudo. Confirma as condicoes vigentes na data de emissao."
    ),
)
def get_historico(
    lat: Optional[float] = Query(
        None,
        description="Latitude",
        ge=-90,
        le=90,
    ),
    lon: Optional[float] = Query(
        None,
        description="Longitude",
        ge=-180,
        le=180,
    ),
    cidade: Optional[str] = Query(
        None,
        description="Nome da cidade para resolucao automatica de coordenadas",
        min_length=2,
        max_length=100,
    ),
    service: ClimaService = Depends(get_clima_service),
) -> PrevisaoResponseSchema:
    """Busca historico climatico para auditoria.

    Args:
        lat: Latitude do talhao.
        lon: Longitude do talhao.
        cidade: Nome da cidade para resolucao automatica de coordenadas.
        service: Instancia injetada do ClimaService.

    Returns:
        PrevisaoResponseSchema com os dias historicos.

    Raises:
        HTTPException 400: Parametros invalidos.
        HTTPException 404: Cidade nao encontrada.
        HTTPException 503: Falha inesperada ao chamar servico externo.
    """
    # Validacao: precisa de cidade OU lat+lon
    if cidade is None and (lat is None or lon is None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe o nome da cidade (cidade=...) ou as coordenadas (lat=...&lon=...).",
        )

    # Se cidade informada, resolver coordenadas
    if cidade is not None:
        try:
            lat, lon = service.buscar_coordenadas_por_cidade(cidade)
        except ValueError as exc:
            logger.warning("Cidade nao encontrada: %s -- %s", cidade, exc)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except Exception as exc:
            logger.exception("Erro ao resolver cidade '%s': %s", cidade, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Erro ao buscar coordenadas da cidade. Tente novamente mais tarde.",
            ) from exc

    try:
        resultado = service.buscar_historico(lat=lat, lon=lon)
    except Exception as exc:
        logger.exception("Erro inesperado em /historico: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servico de clima temporariamente indisponivel.",
        ) from exc

    return resultado

