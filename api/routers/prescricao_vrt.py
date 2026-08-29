"""
Precision VRT Solo — Router de Prescrição VRT

Endpoints HTTP para prescrição VRT.
Chama exclusivamente o Service correspondente.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, File, UploadFile, HTTPException
from pathlib import Path

from api.dependencies import (
    validar_parametros_obrigatorios,
    validar_arquivo_upload,
    success_response,
    error_response,
    get_validation_service
)
from schemas.comum import PipelineRequest, PipelineResponse
from api.responses import sucesso, erro

from app.services import prescricao_vrt_service

router = APIRouter()

# Instância do service
prescricao_service = prescricao_vrt_service.PrescricaoVrtService()

@router.post("/importar")
def importar_arquivos(
    arquivo_limite: UploadFile = File(...),
    arquivo_amostras: UploadFile = File(...),
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Importa arquivos para processamento de prescrição VRT.
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
        resultado = prescricao_service.importar_arquivos(
            arquivo_limite.filename,
            arquivo_amostras.filename,
            configuracoes
        )
        
        return success_response(resultado, "Arquivos importados com sucesso")
        
    except Exception as e:
        return error_response("Erro ao importar arquivos", str(e))

@router.post("/interpolar")
def interpolar_solo(
    arquivo_limite: UploadFile = File(...),
    arquivo_amostras: UploadFile = File(...),
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Processa interpolação de dados de solo.
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
        resultado = prescricao_service.processar_interpolacao(
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
        resultado = prescricao_service.processar_zoneamento(
            arquivo_limite.filename,
            configuracoes
        )
        
        return success_response(resultado, "Zoneamento realizado com sucesso")
        
    except Exception as e:
        return error_response("Erro ao realizar zoneamento", str(e))

@router.post("/prescrever")
def prescrever_fertilizantes(
    cultura: str,
    formula: str,
    arquivo_limite: UploadFile = File(...),
    arquivo_zoneamento: UploadFile = File(...),
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Realiza prescrição de fertilizantes.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "arquivo_limite": arquivo_limite.filename,
            "arquivo_zoneamento": arquivo_zoneamento.filename,
            "cultura": cultura,
            "formula": formula
        }, ["arquivo_limite", "arquivo_zoneamento", "cultura", "formula"])
        
        # Validação de arquivos
        arquivo_limite_validado = validar_arquivo_upload(arquivo_limite)
        arquivo_zoneamento_validado = validar_arquivo_upload(arquivo_zoneamento)
        
        # Chamar service
        resultado = prescricao_service.processar_prescricao(
            arquivo_limite.filename,
            arquivo_zoneamento.filename,
            cultura,
            formula,
            configuracoes
        )
        
        return success_response(resultado, "Prescrição realizada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao realizar prescrição", str(e))

@router.post("/exportar")
def exportar_prescricao(
    dados_prescricao: Dict[str, Any],
    formatos: list,
    nome_arquivo_base: str,
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Exporta prescrição em múltiplos formatos.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "dados_prescricao": "dados",
            "formatos": formatos,
            "nome_arquivo_base": nome_arquivo_base
        }, ["dados_prescricao", "formatos", "nome_arquivo_base"])
        
        # Chamar service
        resultado = prescricao_service._exportar_resultados(dados_prescricao)
        
        return success_response(resultado, "Exportação realizada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao exportar prescrição", str(e))

@router.post("/pipeline-completo")
def pipeline_completo(
    cultura: str,
    formula: str,
    arquivo_limite: UploadFile = File(...),
    arquivo_amostras: UploadFile = File(...),
    configuracoes: Optional[Dict[str, Any]] = None
):
    """
    Executa pipeline completo de prescrição VRT.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "arquivo_limite": arquivo_limite.filename,
            "arquivo_amostras": arquivo_amostras.filename,
            "cultura": cultura,
            "formula": formula
        }, ["arquivo_limite", "arquivo_amostras", "cultura", "formula"])
        
        # Validação de arquivos
        arquivo_limite_validado = validar_arquivo_upload(arquivo_limite)
        arquivo_amostras_validado = validar_arquivo_upload(arquivo_amostras)
        
        # Chamar service - pipeline completo
        resultado = prescricao_service.processar_prescricao(
            arquivo_limite.filename,
            arquivo_amostras.filename,
            cultura,
            formula,
            configuracoes
        )
        
        return success_response(resultado, "Pipeline completo executado com sucesso")
        
    except Exception as e:
        return error_response("Erro ao executar pipeline completo", str(e))

@router.get("/culturas/disponiveis")
def obter_culturas_disponiveis():
    """
    Retorna lista de culturas disponíveis.
    """
    try:
        culturas = prescricao_service.obter_culturas_disponiveis()
        return success_response(culturas, "Culturas obtidas com sucesso")
        
    except Exception as e:
        return error_response("Erro ao obter culturas", str(e))

@router.get("/formulas/disponiveis")
def obter_formulas_disponiveis(cultura: str):
    """
    Retorna lista de fórmulas disponíveis para uma cultura.
    """
    try:
        # Validação de parâmetros
        if not cultura:
            return error_response("Cultura não especificada")
        
        formulas = prescricao_service.obter_formulas_disponiveis(cultura)
        return success_response(formulas, "Fórmulas obtidas com sucesso")
        
    except Exception as e:
        return error_response("Erro ao obter fórmulas", str(e))

@router.get("/configuracoes/padrao")
def obter_configuracoes_padrao(cultura: str, formula: str):
    """
    Retorna configurações padrão para cultura e fórmula.
    """
    try:
        # Validação de parâmetros
        if not cultura or not formula:
            return error_response("Cultura e fórmula são obrigatórios")
        
        configuracoes = prescricao_service.obter_configuracoes_padrao(cultura, formula)
        return success_response(configuracoes, "Configurações obtidas com sucesso")
        
    except Exception as e:
        return error_response("Erro ao obter configurações", str(e))