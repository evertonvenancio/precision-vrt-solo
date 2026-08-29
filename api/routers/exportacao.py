"""
Precision VRT Solo — Router de Exportação

Endpoints HTTP para exportação de dados.
Chama exclusivamente o Service correspondente.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, HTTPException
from pathlib import Path

from api.dependencies import (
    validar_parametros_obrigatorios,
    success_response,
    error_response
)
from schemas.comum import ExportRequest
from api.responses import sucesso, erro

from app.services import exportacao_service

router = APIRouter()

# Instância do service
exportacao_service = exportacao_service.ExportacaoService()

@router.post("/PDF")
def exportar_pdf(
    dados_originais: Dict[str, Any],
    nome_arquivo_base: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Exporta dados em formato PDF.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "dados_originais": dados_originais,
            "nome_arquivo_base": nome_arquivo_base
        }, ["dados_originais", "nome_arquivo_base"])
        
        # Chamar service
        resultado = exportacao_service.exportar_pdf(
            dados_originais,
            nome_arquivo_base,
            configuracoes
        )
        
        return success_response(resultado, "Exportação PDF realizada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao exportar PDF", str(e))

@router.post("/CSV")
def exportar_csv(
    dados_originais: Dict[str, Any],
    nome_arquivo_base: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Exporta dados em formato CSV.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "dados_originais": dados_originais,
            "nome_arquivo_base": nome_arquivo_base
        }, ["dados_originais", "nome_arquivo_base"])
        
        # Chamar service
        resultado = exportacao_service.exportar_csv(
            dados_originais,
            nome_arquivo_base,
            configuracoes
        )
        
        return success_response(resultado, "Exportação CSV realizada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao exportar CSV", str(e))

@router.post("/Excel")
def exportar_excel(
    dados_originais: Dict[str, Any],
    nome_arquivo_base: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Exporta dados em formato Excel.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "dados_originais": dados_originais,
            "nome_arquivo_base": nome_arquivo_base
        }, ["dados_originais", "nome_arquivo_base"])
        
        # Chamar service
        resultado = exportacao_service.exportar_excel(
            dados_originais,
            nome_arquivo_base,
            configuracoes
        )
        
        return success_response(resultado, "Exportação Excel realizada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao exportar Excel", str(e))

@router.post("/GeoJSON")
def exportar_geojson(
    dados_originais: Dict[str, Any],
    nome_arquivo_base: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Exporta dados em formato GeoJSON.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "dados_originais": dados_originais,
            "nome_arquivo_base": nome_arquivo_base
        }, ["dados_originais", "nome_arquivo_base"])
        
        # Chamar service
        resultado = exportacao_service.exportar_geojson(
            dados_originais,
            nome_arquivo_base,
            configuracoes
        )
        
        return success_response(resultado, "Exportação GeoJSON realizada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao exportar GeoJSON", str(e))

@router.post("/Shapefile")
def exportar_shapefile(
    dados_originais: Dict[str, Any],
    nome_arquivo_base: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Exporta dados em formato Shapefile.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "dados_originais": dados_originais,
            "nome_arquivo_base": nome_arquivo_base
        }, ["dados_originais", "nome_arquivo_base"])
        
        # Chamar service
        resultado = exportacao_service.exportar_shapefile(
            dados_originais,
            nome_arquivo_base,
            configuracoes
        )
        
        return success_response(resultado, "Exportação Shapefile realizada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao exportar Shapefile", str(e))

@router.post("/GeoTIFF")
def exportar_geotiff(
    dados_originais: Dict[str, Any],
    nome_arquivo_base: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Exporta dados em formato GeoTIFF.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "dados_originais": dados_originais,
            "nome_arquivo_base": nome_arquivo_base
        }, ["dados_originais", "nome_arquivo_base"])
        
        # Chamar service
        resultado = exportacao_service.exportar_geotiff(
            dados_originais,
            nome_arquivo_base,
            configuracoes
        )
        
        return success_response(resultado, "Exportação GeoTIFF realizada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao exportar GeoTIFF", str(e))

@router.post("/ISOXML")
def exportar_isoxml(
    dados_originais: Dict[str, Any],
    nome_arquivo_base: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Exporta dados em formato ISOXML.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "dados_originais": dados_originais,
            "nome_arquivo_base": nome_arquivo_base
        }, ["dados_originais", "nome_arquivo_base"])
        
        # Chamar service
        resultado = exportacao_service.exportar_isoxml(
            dados_originais,
            nome_arquivo_base,
            configuracoes
        )
        
        return success_response(resultado, "Exportação ISOXML realizada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao exportar ISOXML", str(e))

@router.post("/KML")
def exportar_kml(
    dados_originais: Dict[str, Any],
    nome_arquivo_base: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Exporta dados em formato KML.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "dados_originais": dados_originais,
            "nome_arquivo_base": nome_arquivo_base
        }, ["dados_originais", "nome_arquivo_base"])
        
        # Chamar service
        resultado = exportacao_service.exportar_kml(
            dados_originais,
            nome_arquivo_base,
            configuracoes
        )
        
        return success_response(resultado, "Exportação KML realizada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao exportar KML", str(e))

@router.post("/KMZ")
def exportar_kmz(
    dados_originais: Dict[str, Any],
    nome_arquivo_base: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Exporta dados em formato KMZ.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "dados_originais": dados_originais,
            "nome_arquivo_base": nome_arquivo_base
        }, ["dados_originais", "nome_arquivo_base"])
        
        # Chamar service
        resultado = exportacao_service.exportar_kmz(
            dados_originais,
            nome_arquivo_base,
            configuracoes
        )
        
        return success_response(resultado, "Exportação KMZ realizada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao exportar KMZ", str(e))

@router.post("/exportar-multiplos")
def exportar_multiplos(
    dados_originais: Dict[str, Any],
    formatos: list,
    nome_arquivo_base: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Exporta dados em múltiplos formatos simultaneamente.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "dados_originais": dados_originais,
            "formatos": formatos,
            "nome_arquivo_base": nome_arquivo_base
        }, ["dados_originais", "formatos", "nome_arquivo_base"])
        
        # Chamar service
        resultado = exportacao_service.exportar_multiplos(
            dados_originais,
            formatos,
            nome_arquivo_base,
            configuracoes
        )
        
        return success_response(resultado, "Exportação múltipla realizada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao exportar múltiplos formatos", str(e))