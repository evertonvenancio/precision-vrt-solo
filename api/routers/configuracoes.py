"""
Precision VRT Solo — Router de Configurações

Endpoints HTTP para configurações do sistema.
Chama exclusivamente o Service correspondente.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter

from api.dependencies import (
    validar_parametros_obrigatorios,
    success_response,
    error_response
)
from api.responses import sucesso, erro

router = APIRouter()

@router.get("/obter-configuracoes")
def obter_configuracoes():
    """
    Retorna todas as configurações do sistema.
    """
    try:
        # Placeholder - em produção viria de um service
        configuracoes = {
            "tema": "claro",
            "idioma": "pt-br",
            "formato_data": "DD/MM/YYYY",
            "coordenadas": "EPSG:4326"
        }
        
        return success_response(configuracoes, "Configurações obtidas com sucesso")
        
    except Exception as e:
        return error_response("Erro ao obter configurações", str(e))

@router.post("/atualizar-configuracoes")
def atualizar_configuracoes(
    configuracoes: Dict[str, Any]
):
    """
    Atualiza configurações do sistema.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "configuracoes": configuracoes
        }, ["configuracoes"])
        
        # Placeholder - em produção chamaria service
        resultado = {"status": "atualizado"}
        
        return success_response(resultado, "Configurações atualizadas com sucesso")
        
    except Exception as e:
        return error_response("Erro ao atualizar configurações", str(e))