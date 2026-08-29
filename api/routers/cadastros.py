"""
Precision VRT Solo — Router de Cadastros

Endpoints HTTP para cadastros do sistema.
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

@router.get("/culturas")
def listar_culturas():
    """
    Lista todas as culturas cadastradas.
    """
    try:
        # Placeholder - em produção viria de um service
        culturas = [
            {"id": 1, "nome": "Milho", "tipo": "Cereais"},
            {"id": 2, "nome": "Soja", "tipo": "Grãos"},
            {"id": 3, "nome": "Café", "tipo": "Perene"}
        ]
        
        return success_response(culturas, "Culturas obtidas com sucesso")
        
    except Exception as e:
        return error_response("Erro ao obter culturas", str(e))

@router.post("/culturas")
def cadastrar_cultura(cultura: Dict[str, Any]):
    """
    Cadastra nova cultura.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "cultura": cultura
        }, ["cultura"])
        
        # Placeholder - em produção chamaria service
        resultado = {"id": 4, "status": "cadastrado"}
        
        return success_response(resultado, "Cultura cadastrada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao cadastrar cultura", str(e))

@router.get("/usuarios")
def listar_usuarios():
    """
    Lista todos os usuários cadastrados.
    """
    try:
        # Placeholder - em produção viria de um service
        usuarios = [
            {"id": 1, "nome": "João Silva", "email": "joao@exemplo.com", "perfil": "admin"},
            {"id": 2, "nome": "Maria Santos", "email": "maria@exemplo.com", "perfil": "usuario"}
        ]
        
        return success_response(usuarios, "Usuários obtidos com sucesso")
        
    except Exception as e:
        return error_response("Erro ao obter usuários", str(e))

@router.post("/usuarios")
def cadastrar_usuario(usuario: Dict[str, Any]):
    """
    Cadastra novo usuário.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "usuario": usuario
        }, ["usuario"])
        
        # Placeholder - em produção chamaria service
        resultado = {"id": 3, "status": "cadastrado"}
        
        return success_response(resultado, "Usuário cadastrado com sucesso")
        
    except Exception as e:
        return error_response("Erro ao cadastrar usuário", str(e))