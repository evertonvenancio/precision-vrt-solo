"""
Precision VRT Solo — Router de Fertirrigação

Endpoints HTTP para recomendação de fertirrigação.
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

from app.services import fertirrigacao_service

router = APIRouter()

# Instância do service
fertirrigacao_service = fertirrigacao_service.FertirrigacaoService()

@router.post("/importar")
def importar_arquivos(
    arquivo_limite: UploadFile = File(...),
    arquivo_amostras: UploadFile = File(...),
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Importa arquivos para recomendação de fertirrigação.
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
        resultado = fertirrigacao_service.importar_arquivos(
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
    Processa interpolação de dados (opcional).
    """
    try:
        # Validação de parâmetros (opcional)
        if arquivo_limite.filename and arquivo_amostras.filename:
            validar_parametros_obrigatorios({
                "arquivo_limite": arquivo_limite.filename,
                "arquivo_amostras": arquivo_amostras.filename
            }, ["arquivo_limite", "arquivo_amostras"])
            
            # Validação de arquivos
            arquivo_limite_validado = validar_arquivo_upload(arquivo_limite)
            arquivo_amostras_validado = validar_arquivo_upload(arquivo_amostras)
            
            # Chamar service
            resultado = fertirrigacao_service.processar_interpolacao(
                arquivo_limite.filename,
                arquivo_amostras.filename,
                configuracoes
            )
        else:
            # Chamar service sem interpolação
            resultado = {}
        
        return success_response(resultado, "Interpolação processada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao processar interpolação", str(e))

@router.post("/recomendar")
def recomendar_fertirrigacao(
    cultura: str,
    arquivo_limite: UploadFile = File(...),
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Realiza recomendação de fertirrigação.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "arquivo_limite": arquivo_limite.filename,
            "cultura": cultura
        }, ["arquivo_limite", "cultura"])
        
        # Validação de arquivos
        arquivo_limite_validado = validar_arquivo_upload(arquivo_limite)
        
        # Chamar service
        resultado = fertirrigacao_service.processar_recomendacao(
            arquivo_limite.filename,
            cultura,
            configuracoes
        )
        
        return success_response(resultado, "Recomendação realizada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao realizar recomendação", str(e))

@router.post("/exportar")
def exportar_resultados(
    dados_fertirrigacao: Dict[str, Any],
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
            "dados_fertirrigacao": "dados",
            "formatos": formatos,
            "nome_arquivo_base": nome_arquivo_base
        }, ["dados_fertirrigacao", "formatos", "nome_arquivo_base"])
        
        # Chamar service
        resultado = fertirrigacao_service.exportar_resultados(
            dados_fertirrigacao,
            formatos,
            nome_arquivo_base,
            configuracoes
        )
        
        return success_response(resultado, "Exportação realizada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao exportar resultados", str(e))

@router.post("/pipeline-completo")
def pipeline_completo(
    cultura: str,
    arquivo_limite: UploadFile = File(...),
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Executa pipeline completo de fertirrigação.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "arquivo_limite": arquivo_limite.filename,
            "cultura": cultura
        }, ["arquivo_limite", "cultura"])
        
        # Validação de arquivos
        arquivo_limite_validado = validar_arquivo_upload(arquivo_limite)
        
        # Chamar service - pipeline completo
        resultado = fertirrigacao_service.processar_recomendacao(
            arquivo_limite.filename,
            cultura,
            configuracoes
        )
        
        return success_response(resultado, "Pipeline completo executado com sucesso")
        
    except Exception as e:
        return error_response("Erro ao executar pipeline completo", str(e))