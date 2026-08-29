"""
Precision VRT Solo — API Endpoints do Modulo Prescricao

Orquestra o pipeline completo de Prescricao VRT:
  Upload -> Parse -> Merge -> Interpolacao -> Zoneamento -> Prescricao -> Exportacao
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from core.prescricao_vrt.exportacao import Exportador, MetadadosExportacao
from core.prescricao_vrt.interpolacao import InterpoladorSolo
from core.prescricao_vrt.prescricao import MotorPrescricao
from core.prescricao_vrt.zoneamento import Zoneador
from db.database import get_db
from app.services.geo_parser_service import parse_upload
from utils.geojson import gdf_para_geojson_dict, validar_geojson

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/prescricao", tags=["Prescricao"])


@router.post("/upload")
async def upload_prescricao(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Recebe arquivo geografico (CSV, XLSX, ZIP/SHP, TIF, GeoJSON).

    Identifica automaticamente se sao pontos (amostras) ou poligonos (talhao).
    """
    logger.info("[PRESCRICAO_UPLOAD] Recebido arquivo: %s", file.filename)

    try:
        resultado = parse_upload(file)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[PRESCRICAO_UPLOAD] Erro no parse do arquivo %s", file.filename)
        raise HTTPException(status_code=422, detail=f"Erro ao processar arquivo: {e}")

    tipo = resultado.tipo
    gdf_pontos = resultado.gdf_pontos
    gdf_poligono = resultado.gdf_poligono
    df = resultado.df
    crs = resultado.crs
    metadados = resultado.metadados

    logger.info(
        "[PRESCRICAO_UPLOAD] Parse concluido: tipo=%s | registros=%d | CRS=%s",
        tipo, metadados.total_registros, crs,
    )

    if tipo == "poligono":
        logger.info("[PRESCRICAO_UPLOAD] Poligono detectado. Salvando geometria do talhao.")
        return {
            "status": "sucesso",
            "tipo": "poligono",
            "mensagem": "Poligono de talhao recebido e validado. Prosseguir para vinculacao do talhao.",
            "registros": metadados.total_registros,
            "crs": crs,
            "geometria_tipo": str(gdf_poligono.geom_type.iloc[0]) if gdf_poligono is not None and not gdf_poligono.empty else None,
        }

    if tipo == "pontos":
        logger.info("[PRESCRICAO_UPLOAD] Pontos detectados. Enviando para pipeline de Krigagem.")
        return {
            "status": "sucesso",
            "tipo": "pontos",
            "mensagem": "Amostras georreferenciadas recebidas. Prosseguir para Krigagem e Zoneamento.",
            "registros": metadados.total_registros,
            "crs": crs,
            "colunas": metadados.colunas_padronizadas,
        }

    if tipo == "tabular":
        logger.info(
            "[PRESCRICAO_UPLOAD] Amostras sem coordenadas detectadas. "
            "Aguardando GeoJSON/SHP para merge."
        )
        return {
            "status": "sucesso",
            "tipo": "amostras_sem_coords",
            "mensagem": "Amostras recebidas (sem coordenadas). Faca upload do GeoJSON/SHP com pontos para vincular.",
            "registros": metadados.total_registros,
            "colunas": metadados.colunas_padronizadas,
        }

    if tipo == "ambos":
        logger.info("[PRESCRICAO_UPLOAD] Arquivo contem pontos e poligonos.")
        return {
            "status": "sucesso",
            "tipo": "ambos",
            "mensagem": "Arquivo contem pontos e poligonos. Processar conforme necessario.",
            "registros": metadados.total_registros,
            "crs": crs,
            "colunas": metadados.colunas_padronizadas,
        }

    logger.error("[PRESCRICAO_UPLOAD] Tipo geometrico desconhecido: %s", tipo)
    raise HTTPException(status_code=422, detail=f"Tipo geometrico nao reconhecido: {tipo}")


@router.post("/processar")
async def processar_prescricao(
    arquivo_amostras: UploadFile = File(
        ..., description="CSV/XLSX com ponto_id + dados quimicos"
    ),
    arquivo_limite: UploadFile = File(
        ..., description="GeoJSON ou ZIP/SHP com poligono do talhao + pontos com ponto_id"
    ),
    cultura: str = Form("soja", description="Cultura (ex: soja, milho, cafe)"),
    produtividade: float = Form(3.0, description="Produtividade alvo"),
    n_zonas: int = Form(4, description="Numero de zonas de manejo"),
    metodo: str = Form("IAC_Graos", description="Metodologia (ex: IAC_Graos, CFSEMG_Geral)"),
    safra: str = Form("", description="Safra selecionada (ex: 2025/2026, 2026). Aceita qualquer valor."),
    safras_adicionais: str = Form("", description="Safras adicionais separadas por virgula (opcional)"),
    db: Session = Depends(get_db),
):
    """Pipeline completo de Prescricao VRT.

    Recebe:
      - arquivo_amostras: XLSX/CSV com ponto_id + dados de analise de solo
      - arquivo_limite: GeoJSON/SHP com poligono do talhao + pontos das amostras

    Retorna:
      - GeoJSON de limite e zonas (serializavel)
      - Prescricao por zona
      - Area em hectares
      - Perfis por zona
      - Estatisticas de zoneamento
    """
    logger.info(
        "[PRESCRICAO_PROCESSAR] Iniciando pipeline VRT | cultura=%s | zonas=%d | safra=%s",
        cultura, n_zonas, safra or "nao informada",
    )

    # Processar lista de safras
    lista_safras: List[str] = []
    if safra:
        lista_safras.append(safra)
    if safras_adicionais:
        lista_safras.extend([s.strip() for s in safras_adicionais.split(",") if s.strip()])

    # --- PASSO 1: Parse do XLSX de amostras ---
    try:
        resultado_amostras = parse_upload(arquivo_amostras)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[PRESCRICAO_PROCESSAR] Erro ao parsear amostras: %s", e)
        raise HTTPException(status_code=422, detail=f"Erro ao processar arquivo de amostras: {e}")

    if resultado_amostras.tipo != "tabular":
        raise HTTPException(
            status_code=422,
            detail=(
                "Arquivo de amostras deve ser CSV/XLSX com ponto_id (sem lat/long). "
                f"Tipo detectado: {resultado_amostras.tipo}"
            ),
        )

    df_amostras = resultado_amostras.df
    if df_amostras is None or df_amostras.empty:
        raise HTTPException(status_code=422, detail="Arquivo de amostras vazio ou invalido")

    logger.info(
        "[PRESCRICAO_PROCESSAR] Amostras: %d registros | colunas=%s",
        len(df_amostras), resultado_amostras.metadados.colunas_padronizadas,
    )

    # --- PASSO 2: Parse do GeoJSON/SHP de limite ---
    try:
        resultado_limite = parse_upload(arquivo_limite)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[PRESCRICAO_PROCESSAR] Erro ao parsear limite: %s", e)
        raise HTTPException(status_code=422, detail=f"Erro ao processar arquivo de limite: {e}")

    gdf_limite = resultado_limite.gdf_poligono
    gdf_pontos_limite = resultado_limite.gdf_pontos

    if gdf_limite is None and gdf_pontos_limite is None:
        raise HTTPException(
            status_code=422,
            detail="Arquivo de limite nao contem dados geometricos validos",
        )

    logger.info(
        "[PRESCRICAO_PROCESSAR] Limite: poligonos=%s | pontos=%s",
        len(gdf_limite) if gdf_limite is not None else 0,
        len(gdf_pontos_limite) if gdf_pontos_limite is not None else 0,
    )

    # --- PASSO 3: Merge amostras + coordenadas ---
    try:
        if gdf_pontos_limite is not None and not gdf_pontos_limite.empty:
            # Merge usando o metodo do geo_parser_service
            resultado_merge = parse_upload(arquivo_amostras, merge_com=resultado_limite)
            gdf_pontos = resultado_merge.gdf_pontos
        else:
            # Se nao ha pontos no limite, usar apenas os dados tabulares
            gdf_pontos = gdf_pontos_limite
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[PRESCRICAO_PROCESSAR] Erro no merge: %s", e)
        raise HTTPException(status_code=422, detail=f"Erro ao vincular amostras com coordenadas: {e}")

    if gdf_pontos is None or gdf_pontos.empty:
        raise HTTPException(
            status_code=422,
            detail="Nao foi possivel vincular amostras com coordenadas. Verifique o arquivo de limite.",
        )

    logger.info(
        "[PRESCRICAO_PROCESSAR] Merge concluido: %d pontos georreferenciados",
        len(gdf_pontos),
    )

    # --- PASSO 4: Interpolacao ---
    interpolador = InterpoladorSolo()
    try:
        resultados_interp = interpolador.interpolar_talhao(gdf_pontos)
    except Exception as e:
        logger.exception("[PRESCRICAO_PROCESSAR] Erro na interpolacao: %s", e)
        raise HTTPException(status_code=500, detail=f"Erro na interpolacao: {e}")

    n_atributos = len(resultados_interp.get("atributos", {}))
    logger.info(
        "[PRESCRICAO_PROCESSAR] Interpolacao concluida: %d atributos",
        n_atributos,
    )

    if n_atributos == 0:
        raise HTTPException(status_code=422, detail="Nenhum atributo valido para interpolacao")

    # --- PASSO 5: Zoneamento ---
    zoneador = Zoneador(n_zonas=n_zonas)
    try:
        resultados_zona = zoneador.zonear(resultados_interp)
    except Exception as e:
        logger.exception("[PRESCRICAO_PROCESSAR] Erro no zoneamento: %s", e)
        raise HTTPException(status_code=500, detail=f"Erro no zoneamento: {e}")

    n_zonas_geradas = resultados_zona["estatisticas"]["n_zonas"]
    logger.info(
        "[PRESCRICAO_PROCESSAR] Zoneamento concluido: %d zonas",
        n_zonas_geradas,
    )

    # --- PASSO 6: Prescricao ---
    motor = MotorPrescricao(
        cultura=cultura,
        produtividade=produtividade,
        metodo_id=metodo,
        safra=safra if safra else None,
        safras=lista_safras if lista_safras else None,
    )
    try:
        prescricoes = motor.prescrever_todas_zonas(resultados_zona["perfis"])
    except Exception as e:
        logger.exception("[PRESCRICAO_PROCESSAR] Erro na prescricao: %s", e)
        raise HTTPException(status_code=500, detail=f"Erro na prescricao: {e}")

    logger.info(
        "[PRESCRICAO_PROCESSAR] Prescricao concluida: %d zonas",
        prescricoes["resumo"]["n_zonas"],
    )

    # --- PASSO 7: Exportacao ---
    exportador = Exportador()

    gdf_zonas = exportador.raster_para_zonas_poligonos(
        resultados_zona["raster_zonas"],
        resultados_interp["grid_x"],
        resultados_interp["grid_y"],
    )

    gdf_prescricao = exportador.adicionar_prescricao(gdf_zonas, prescricoes)

    # Calcular area
    try:
        gdf_prescricao_proj = gdf_prescricao.to_crs("EPSG:3857")
        area_total_ha = float(gdf_prescricao_proj.geometry.area.sum() / 10000)
    except Exception as e:
        logger.warning("[PRESCRICAO_PROCESSAR] Erro ao calcular area: %s. Usando 0.", e)
        area_total_ha = 0.0

    # GeoJSON de limite (poligono)
    geojson_limite = {"type": "FeatureCollection", "features": []}
    if gdf_limite is not None and not gdf_limite.empty:
        poligonos = gdf_limite[gdf_limite.geom_type.isin(["Polygon", "MultiPolygon"])]
        if not poligonos.empty:
            geojson_limite = gdf_para_geojson_dict(poligonos)

    # GeoJSON de zonas
    geojson_zonas = gdf_para_geojson_dict(gdf_prescricao)

    # Validar GeoJSONs gerados
    if not validar_geojson(geojson_limite):
        logger.warning("[PRESCRICAO_PROCESSAR] GeoJSON de limite invalido")
        geojson_limite = {"type": "FeatureCollection", "features": []}

    if not validar_geojson(geojson_zonas):
        logger.error("[PRESCRICAO_PROCESSAR] GeoJSON de zonas invalido")
        raise HTTPException(status_code=500, detail="Erro ao gerar GeoJSON de zonas")

    # Preparar metadados
    metadados_export = MetadadosExportacao(
        cultura=cultura,
        metodologia=metodo,
        safra=safra if safra else None,
        safras=lista_safras,
        camadas_utilizadas=["analise_solo", "limite_talhao"],
        parametros_processamento={
            "n_zonas": n_zonas,
            "produtividade_alvo": produtividade,
            "metodo": metodo,
        },
    )

    logger.info(
        "[PRESCRICAO_PROCESSAR] Pipeline concluido | Area: %.2f ha | Zonas: %d | "
        "Features limite: %d | Features zonas: %d",
        area_total_ha,
        len(gdf_zonas),
        len(geojson_limite.get("features", [])),
        len(geojson_zonas.get("features", [])),
    )

    return {
        "status": "sucesso",
        "area_hectares": round(area_total_ha, 4),
        "n_zonas": len(gdf_zonas),
        "cultura": cultura,
        "produtividade_alvo": produtividade,
        "metodo": metodo,
        "safra": safra,
        "safras": lista_safras,
        "geojson_limite": geojson_limite,
        "geojson_zonas": geojson_zonas,
        "prescricoes": prescricoes["prescricoes"],
        "resumo": prescricoes["resumo"],
        "notas_tecnicas": prescricoes.get("notas_tecnicas", {}),
        "perfis_zonas": resultados_zona["perfis"],
        "estatisticas_zoneamento": resultados_zona["estatisticas"],
        "metricas_qualidade": resultados_zona.get("metricas_qualidade", {}),
        "atributos_usados": resultados_zona.get("atributos_usados", []),
    }
