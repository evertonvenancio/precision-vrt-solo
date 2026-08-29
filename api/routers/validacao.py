"""
Precision VRT Solo — Router de Validação

Endpoints HTTP para validação de dados.
Chama exclusivamente o Service correspondente.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, HTTPException, File
from pathlib import Path

from api.dependencies import (
    validar_parametros_obrigatorios,
    validar_arquivo_upload,
    success_response,
    error_response
)
from schemas.comum import PipelineRequest, PipelineResponse
from api.responses import sucesso, erro

from app.services import validacao_service

router = APIRouter()

# Instância do service
validacao_service = validacao_service.ValidacaoService()

@router.post("/validar-arquivo")
def validar_arquivo_endpoint(
    arquivo: UploadFile = File(...),
    tipo: str = "padrao"
):
    """
    Valida arquivo recebido via upload.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "arquivo": arquivo.filename,
            "tipo": tipo
        }, ["arquivo", "tipo"])
        
        # Validação de arquivo
        resultado_validacao = validar_arquivo_upload(arquivo)
        
        return success_response(resultado_validacao, "Arquivo validado com sucesso")
        
    except Exception as e:
        return error_response("Erro ao validar arquivo", str(e))

@router.post("/validar-parametros")
def validar_parametros_endpoint(
    parametros: Dict[str, Any],
    campos_obrigatorios: list
):
    """
    Valida parâmetros recebidos na requisição.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "parametros": parametros,
            "campos_obrigatorios": campos_obrigatorios
        }, ["parametros", "campos_obrigatorios"])
        
        # Chamar service
        resultado = validacao_service.validar_parametros_obrigatorios(
            parametros,
            campos_obrigatorios
        )
        
        return success_response(resultado, "Parâmetros validados com sucesso")
        
    except Exception as e:
        return error_response("Erro ao validar parâmetros", str(e))

@router.post("/validar-geojson")
def validar_geojson(
    arquivo_geojson: UploadFile = File(...),
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Valida arquivo GeoJSON.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "arquivo_geojson": arquivo_geojson.filename
        }, ["arquivo_geojson"])
        
        # Validação de arquivo
        arquivo_geojson_validado = validar_arquivo_upload(arquivo_geojson)
        
        # Salvar arquivo temporariamente para validação
        with open(arquivo_geojson.filename, "wb") as buffer:
            buffer.write(arquivo_geojson.file.read())
        
        # Chamar service
        resultado = validacao_service.validar_formato_geojson(arquivo_geojson.filename)
        
        # Limpar arquivo temporário
        Path(arquivo_geojson.filename).unlink(missing_ok=True)
        
        return success_response(resultado, "GeoJSON validado com sucesso")
        
    except Exception as e:
        # Limpar arquivo temporário em caso de erro
        if arquivo_geojson.filename:
            Path(arquivo_geojson.filename).unlink(missing_ok=True)
        return error_response("Erro ao validar GeoJSON", str(e))

@router.post("/validar-formato")
def validar_formato_arquivo(
    arquivo: UploadFile = File(...),
    formatos_permitidos: list = None
):
    """
    Valida formato do arquivo.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "arquivo": arquivo.filename,
            "formatos_permitidos": formatos_permitidos
        }, ["arquivo"])
        
        # Validação de arquivo
        arquivo_validado = validar_arquivo_upload(arquivo)
        
        # Chamar service
        if formatos_permitidos:
            resultado = validacao_service.validar_formato_arquivo(
                arquivo.filename,
                formatos_permitidos
            )
        else:
            # Formatos padrão
            resultado = validacao_service.validar_formato_arquivo(
                arquivo.filename,
                ['JPG', 'JPEG', 'PNG', 'TIF', 'TIFF', 'CSV', 'XLS', 'XLSX', 'PDF', 'TXT', 'JSON']
            )
        
        return success_response(resultado, "Formato de arquivo validado com sucesso")
        
    except Exception as e:
        return error_response("Erro ao validar formato", str(e))

@router.post("/validar-dados")
def validar_dados(
    dados: Dict[str, Any],
    tipo_validacao: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Valida dados de acordo com o tipo especificado.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "dados": dados,
            "tipo_validacao": tipo_validacao
        }, ["dados", "tipo_validacao"])
        
        # Chamar service
        resultado = validacao_service.validar_dados(
            dados,
            tipo_validacao,
            configuracoes
        )
        
        return success_response(resultado, "Dados validados com sucesso")
        
    except Exception as e:
        return error_response("Erro ao validar dados", str(e))

@router.post("/validar-pipeline")
def validar_pipeline(
    pipeline_request: Dict[str, Any]
):
    """
    Valida estrutura de pipeline.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "pipeline_request": pipeline_request
        }, ["pipeline_request"])
        
        # Chamar service
        resultado = validacao_service.validar_pipeline(pipeline_request)
        
        return success_response(resultado, "Pipeline validado com sucesso")
        
    except Exception as e:
        return error_response("Erro ao validar pipeline", str(e))