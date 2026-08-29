"""
Precision VRT Solo — Dependências da API

Dependências FastAPI para a camada de API.
Responsável por gerenciar injeção de dependências e validações.
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, UploadFile, File
from pathlib import Path

from api.responses import sucesso, erro, validacao
from app.services import validacao_service

# Instância do serviço de validação
validation_service = validacao_service.ValidacaoService()

def get_validation_service() -> validacao_service.ValidacaoService:
    """
    Dependência para injetar o serviço de validação.
    
    Returns:
        Instância do ValidacaoService
    """
    return validation_service

def validar_arquivo_upload(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Valida arquivo recebido via upload.
    
    Args:
        file: Arquivo recebido via upload
        
    Returns:
        Resultado da validação
        
    Raises:
        HTTPException: Se arquivo for inválido
    """
    try:
        # Validar se arquivo foi enviado
        resultado = validation_service.validar_existencia_arquivo(
            file.filename, 
            obrigatorio=True
        )
        
        if not resultado['valid']:
            raise HTTPException(
                status_code=400,
                detail=resultado['error']
            )
        
        # Validar formato
        resultado_formato = validation_service.validar_formato_arquivo(
            file.filename,
            ['JPG', 'JPEG', 'PNG', 'TIF', 'TIFF', 'CSV', 'XLS', 'XLSX', 'PDF', 'TXT', 'JSON']
        )
        
        if not resultado_formato['valid']:
            raise HTTPException(
                status_code=400,
                detail=resultado_formato['error']
            )
        
        return {
            "success": True,
            "message": "Arquivo válido",
            "filename": file.filename,
            "content_type": file.content_type
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao validar arquivo: {str(e)}"
        )

def validar_parametros_obrigatorios(params: Dict[str, Any], campos_obrigatorios: list) -> Dict[str, Any]:
    """
    Valida parâmetros obrigatórios da requisição.
    
    Args:
        params: Parâmetros da requisição
        campos_obrigatorios: Lista de campos obrigatórios
        
    Returns:
        Resultado da validação
        
    Raises:
        HTTPException: Se parâmetros forem inválidos
    """
    try:
        resultado = validation_service.validar_parametros_obrigatorios(
            params, 
            campos_obrigatorios
        )
        
        if not resultado['valid']:
            raise HTTPException(
                status_code=400,
                detail=resultado['error']
            )
        
        return resultado
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao validar parâmetros: {str(e)}"
        )

def validar_geojson(arquivo_path: str) -> Dict[str, Any]:
    """
    Valida arquivo GeoJSON.
    
    Args:
        arquivo_path: Caminho do arquivo GeoJSON
        
    Returns:
        Resultado da validação
        
    Raises:
        HTTPException: Se GeoJSON for inválido
    """
    try:
        resultado = validation_service.validar_formato_geojson(arquivo_path)
        
        if not resultado['valid']:
            raise HTTPException(
                status_code=400,
                detail=resultado['error']
            )
        
        return resultado
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao validar GeoJSON: {str(e)}"
        )

def success_response(data: Any = None, message: str = "Operação realizada com sucesso") -> Dict[str, Any]:
    """
    Resposta padrão de sucesso.
    
    Args:
        data: Dados da resposta
        message: Mensagem de sucesso
        
    Returns:
        Resposta padrão de sucesso
    """
    return {
        "success": True,
        "message": message,
        "data": data
    }

def error_response(message: str, error: str = None, status_code: int = 500) -> Dict[str, Any]:
    """
    Resposta padrão de erro.
    
    Args:
        message: Mensagem de erro
        error: Detalhe técnico do erro
        status_code: Código HTTP do erro
        
    Returns:
        Resposta padrão de erro
    """
    return {
        "success": False,
        "message": message,
        "error": error
    }