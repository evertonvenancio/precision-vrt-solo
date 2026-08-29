"""
Precision VRT Solo — Router de Monitoramento

Endpoints HTTP para monitoramento de áreas.
Chama exclusivamente o Service correspondente.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, File, UploadFile, HTTPException
from pathlib import Path

from api.dependencies import (
    validar_parametros_obrigatorios,
    validar_arquivo_upload,
    success_response,
    error_response
)
from schemas.comum import PipelineRequest, PipelineResponse
from api.responses import sucesso, erro

from app.services import monitoramento_service

router = APIRouter()

# Instância do service
monitoramento_service = monitoramento_service.MonitoramentoService()

@router.post("/comparacao")
def comparar_areas(
    area_geojson_1: str,
    area_geojson_2: str,
    periodo_1: str,
    periodo_2: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Compara duas áreas em diferentes períodos.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "area_geojson_1": area_geojson_1,
            "area_geojson_2": area_geojson_2,
            "periodo_1": periodo_1,
            "periodo_2": periodo_2
        }, ["area_geojson_1", "area_geojson_2", "periodo_1", "periodo_2"])
        
        # Chamar service
        resultado = monitoramento_service.comparar_areas(
            area_geojson_1,
            area_geojson_2,
            periodo_1,
            periodo_2,
            configuracoes
        )
        
        return success_response(resultado, "Comparação realizada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao comparar áreas", str(e))

@router.post("/historico")
def obter_historico(
    area_geojson: str,
    periodo_inicio: str,
    periodo_fim: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Obtém histórico de monitoramento de uma área.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "area_geojson": area_geojson,
            "periodo_inicio": periodo_inicio,
            "periodo_fim": periodo_fim
        }, ["area_geojson", "periodo_inicio", "periodo_fim"])
        
        # Chamar service
        resultado = monitoramento_service.obter_historico(
            area_geojson,
            periodo_inicio,
            periodo_fim,
            configuracoes
        )
        
        return success_response(resultado, "Histórico obtido com sucesso")
        
    except Exception as e:
        return error_response("Erro ao obter histórico", str(e))

@router.post("/alertas")
def gerar_alertas(
    area_geojson: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Gera alertas para monitoramento.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "area_geojson": area_geojson
        }, ["area_geojson"])
        
        # Chamar service
        resultado = monitoramento_service.gerar_alertas(
            area_geojson,
            configuracoes
        )
        
        return success_response(resultado, "Alertas gerados com sucesso")
        
    except Exception as e:
        return error_response("Erro ao gerar alertas", str(e))

@router.post("/relatorio")
def gerar_relatorio(
    area_geojson: str,
    periodo_inicio: str,
    periodo_fim: str,
    formatos: list,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Gera relatório de monitoramento.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "area_geojson": area_geojson,
            "periodo_inicio": periodo_inicio,
            "periodo_fim": periodo_fim,
            "formatos": formatos
        }, ["area_geojson", "periodo_inicio", "periodo_fim", "formatos"])
        
        # Chamar service
        resultado = monitoramento_service.gerar_relatorio(
            area_geojson,
            periodo_inicio,
            periodo_fim,
            formatos,
            configuracoes
        )
        
        return success_response(resultado, "Relatório gerado com sucesso")
        
    except Exception as e:
        return error_response("Erro ao gerar relatório", str(e))

@router.post("/pipeline-completo")
def pipeline_completo(
    area_geojson: str,
    periodo_inicio: str,
    periodo_fim: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Executa pipeline completo de monitoramento.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "area_geojson": area_geojson,
            "periodo_inicio": periodo_inicio,
            "periodo_fim": periodo_fim
        }, ["area_geojson", "periodo_inicio", "periodo_fim"])
        
        # Chamar service - pipeline completo
        resultado = monitoramento_service.processar_monitoramento_completo(
            area_geojson,
            periodo_inicio,
            periodo_fim,
            configuracoes
        )
        
        return success_response(resultado, "Pipeline completo executado com sucesso")
        
    except Exception as e:
        return error_response("Erro ao executar pipeline completo", str(e))