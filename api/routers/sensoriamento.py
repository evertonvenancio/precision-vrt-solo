"""
Precision VRT Solo — Router de Sensoriamento

Endpoints HTTP para sensoriamento por satélite.
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

from app.services import sensoriamento_service

router = APIRouter()

# Instância do service
sensoriamento_service = sensoriamento_service.SensoriamentoService()

@router.post("/satelites")
def listar_satelites():
    """
    Lista satélites disponíveis para sensoriamento.
    """
    try:
        satelites = sensoriamento_service.obter_satelites_disponiveis()
        return success_response(satelites, "Satélites obtidos com sucesso")
        
    except Exception as e:
        return error_response("Erro ao obter satélites", str(e))

@router.post("/indices")
def obter_indices_sensores(
    satelite: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Obtém índices disponíveis para um satélite.
    """
    try:
        # Validação de parâmetros
        if not satelite:
            return error_response("Satélite não especificado")
        
        indices = sensoriamento_service.obter_indices_disponiveis(satelite)
        return success_response(indices, "Índices obtidos com sucesso")
        
    except Exception as e:
        return error_response("Erro ao obter índices", str(e))

@router.post("/download")
def baixar_imagens(
    satelite: str,
    indices: list,
    area_geojson: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Baixa imagens de satélite.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "satelite": satelite,
            "indices": indices,
            "area_geojson": area_geojson
        }, ["satelite", "indices", "area_geojson"])
        
        # Chamar service
        resultado = sensoriamento_service.baixar_imagens(
            satelite,
            indices,
            area_geojson,
            configuracoes
        )
        
        return success_response(resultado, "Imagens baixadas com sucesso")
        
    except Exception as e:
        return error_response("Erro ao baixar imagens", str(e))

@router.post("/mapas")
def gerar_mapas(
    indices: list,
    arquivo_imagens: UploadFile = File(...),
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Gera mapas a partir de imagens de satélite.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "arquivo_imagens": arquivo_imagens.filename,
            "indices": indices
        }, ["arquivo_imagens", "indices"])
        
        # Validação de arquivos
        arquivo_imagens_validado = validar_arquivo_upload(arquivo_imagens)
        
        # Chamar service
        resultado = sensoriamento_service.gerar_mapas(
            arquivo_imagens.filename,
            indices,
            configuracoes
        )
        
        return success_response(resultado, "Mapas gerados com sucesso")
        
    except Exception as e:
        return error_response("Erro ao gerar mapas", str(e))

@router.post("/historico")
def obter_historico(
    area_geojson: str,
    periodo_inicio: str,
    periodo_fim: str,
    satelite: str = None,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Obtém histórico de imagens de satélite.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "area_geojson": area_geojson,
            "periodo_inicio": periodo_inicio,
            "periodo_fim": periodo_fim
        }, ["area_geojson", "periodo_inicio", "periodo_fim"])
        
        # Chamar service
        resultado = sensoriamento_service.obter_historico(
            area_geojson,
            periodo_inicio,
            periodo_fim,
            satelite,
            configuracoes
        )
        
        return success_response(resultado, "Histórico obtido com sucesso")
        
    except Exception as e:
        return error_response("Erro ao obter histórico", str(e))

@router.post("/pipeline-completo")
def pipeline_completo(
    area_geojson: str,
    satelite: str,
    indices: list,
    periodo_inicio: str,
    periodo_fim: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Executa pipeline completo de sensoriamento.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "area_geojson": area_geojson,
            "satelite": satelite,
            "indices": indices,
            "periodo_inicio": periodo_inicio,
            "periodo_fim": periodo_fim
        }, ["area_geojson", "satelite", "indices", "periodo_inicio", "periodo_fim"])
        
        # Chamar service - pipeline completo
        resultado = sensoriamento_service.processar_sensoriamento_completo(
            area_geojson,
            satelite,
            indices,
            periodo_inicio,
            periodo_fim,
            configuracoes
        )
        
        return success_response(resultado, "Pipeline completo executado com sucesso")
        
    except Exception as e:
        return error_response("Erro ao executar pipeline completo", str(e))