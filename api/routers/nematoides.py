"""
Precision VRT Solo — Router de Nematoides

Endpoints HTTP para análise de nematoides.
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

from app.services import nematoides_service

router = APIRouter()

# Instância do service
nematoides_service = nematoides_service.NematoidesService()

@router.post("/importar")
def importar_arquivos(
    arquivo_limite: UploadFile = File(...),
    arquivo_amostras: UploadFile = File(...),
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Importa arquivos para análise de nematoides.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "arquivo_limite": arquivo_limite.filename,
            "arquivo_amostras": arquivo_amostras.filename
        }, ["arquivo_limite", "arquivo_amostras"])
        
        # Validação de arquivos
        arquivo_limite_validado = validar_arquivo_upload(arquivo_limite)
        arquivo_amostras_validado = validar_arquivo_upload(arquivo_amostras)
        
        # Chamar service
        resultado = nematoides_service.importar_arquivos(
            arquivo_limite.filename,
            arquivo_amostras.filename,
            configuracoes
        )
        
        return success_response(resultado, "Arquivos importados com sucesso")
        
    except Exception as e:
        return error_response("Erro ao importar arquivos", str(e))

@router.post("/interpolar")
def interpolar_dados(
    arquivo_limite: UploadFile = File(...),
    arquivo_amostras: UploadFile = File(...),
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Processa interpolação de dados de nematoides.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "arquivo_limite": arquivo_limite.filename,
            "arquivo_amostras": arquivo_amostras.filename
        }, ["arquivo_limite", "arquivo_amostras"])
        
        # Validação de arquivos
        arquivo_limite_validado = validar_arquivo_upload(arquivo_limite)
        arquivo_amostras_validado = validar_arquivo_upload(arquivo_amostras)
        
        # Chamar service
        resultado = nematoides_service.processar_interpolacao(
            arquivo_limite.filename,
            arquivo_amostras.filename,
            configuracoes
        )
        
        return success_response(resultado, "Interpolação realizada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao processar interpolação", str(e))

@router.post("/zonear")
def zonear_area(
    arquivo_limite: UploadFile = File(...),
    arquivo_interpolado: UploadFile = File(...),
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Realiza zoneamento da área.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "arquivo_limite": arquivo_limite.filename,
            "arquivo_interpolado": arquivo_interpolado.filename
        }, ["arquivo_limite", "arquivo_interpolado"])
        
        # Validação de arquivos
        arquivo_limite_validado = validar_arquivo_upload(arquivo_limite)
        arquivo_interpolado_validado = validar_arquivo_upload(arquivo_interpolado)
        
        # Chamar service
        resultado = nematoides_service.processar_zoneamento(
            arquivo_limite.filename,
            configuracoes
        )
        
        return success_response(resultado, "Zoneamento realizado com sucesso")
        
    except Exception as e:
        return error_response("Erro ao realizar zoneamento", str(e))

@router.post("/mapa")
def gerar_mapa(
    arquivo_limite: UploadFile = File(...),
    arquivo_zoneamento: UploadFile = File(...),
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Gera mapa da área.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "arquivo_limite": arquivo_limite.filename,
            "arquivo_zoneamento": arquivo_zoneamento.filename
        }, ["arquivo_limite", "arquivo_zoneamento"])
        
        # Validação de arquivos
        arquivo_limite_validado = validar_arquivo_upload(arquivo_limite)
        arquivo_zoneamento_validado = validar_arquivo_upload(arquivo_zoneamento)
        
        # Chamar service
        resultado = nematoides_service.gerar_mapa(
            arquivo_limite.filename,
            arquivo_zoneamento.filename,
            configuracoes
        )
        
        return success_response(resultado, "Mapa gerado com sucesso")
        
    except Exception as e:
        return error_response("Erro ao gerar mapa", str(e))

@router.post("/exportar")
def exportar_resultados(
    dados_nematoides: Dict[str, Any],
    formatos: list,
    nome_arquivo_base: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Exporta resultados em múltiplos formatos.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "dados_nematoides": "dados",
            "formatos": formatos,
            "nome_arquivo_base": nome_arquivo_base
        }, ["dados_nematoides", "formatos", "nome_arquivo_base"])
        
        # Chamar service
        resultado = nematoides_service.exportar_resultados(
            dados_nematoides,
            formatos,
            nome_arquivo_base,
            configuracoes
        )
        
        return success_response(resultado, "Exportação realizada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao exportar resultados", str(e))

@router.post("/pipeline-completo")
def pipeline_completo(
    arquivo_limite: UploadFile = File(...),
    arquivo_amostras: UploadFile = File(...),
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Executa pipeline completo de análise de nematoides.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "arquivo_limite": arquivo_limite.filename,
            "arquivo_amostras": arquivo_amostras.filename
        }, ["arquivo_limite", "arquivo_amostras"])
        
        # Validação de arquivos
        arquivo_limite_validado = validar_arquivo_upload(arquivo_limite)
        arquivo_amostras_validado = validar_arquivo_upload(arquivo_amostras)
        
        # Chamar service - pipeline completo
        resultado = nematoides_service.processar_analise(
            arquivo_limite.filename,
            arquivo_amostras.filename,
            configuracoes
        )
        
        return success_response(resultado, "Pipeline completo executado com sucesso")
        
    except Exception as e:
        return error_response("Erro ao executar pipeline completo", str(e))