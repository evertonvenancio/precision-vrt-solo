"""
Precision VRT Solo — Router de CRM

Endpoints HTTP para gestão de clientes.
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

@router.get("/clientes")
def listar_clientes():
    """
    Lista todos os clientes cadastrados.
    """
    try:
        # Placeholder - em produção viria de um service
        clientes = [
            {"id": 1, "nome": "Fazenda ABC", "contato": "João Silva", "telefone": "(11) 9999-1111"},
            {"id": 2, "nome": "Agro Tech", "contato": "Maria Santos", "telefone": "(21) 9999-2222"},
            {"id": 3, "nome": "Terra Brasil", "contato": "Pedro Oliveira", "telefone": "(31) 9999-3333"}
        ]
        
        return success_response(clientes, "Clientes obtidos com sucesso")
        
    except Exception as e:
        return error_response("Erro ao obter clientes", str(e))

@router.post("/clientes")
def cadastrar_cliente(cliente: Dict[str, Any]):
    """
    Cadastra novo cliente.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "cliente": cliente
        }, ["cliente"])
        
        # Placeholder - em produção chamaria service
        resultado = {"id": 4, "status": "cadastrado"}
        
        return success_response(resultado, "Cliente cadastrado com sucesso")
        
    except Exception as e:
        return error_response("Erro ao cadastrar cliente", str(e))

@router.get("/oportunidades")
def listar_oportunidades():
    """
    Lista todas as oportunidades de negócio.
    """
    try:
        # Placeholder - em produção viria de um service
        oportunidades = [
            {"id": 1, "cliente": "Fazenda ABC", "valor": 25000.00, "status": "Em Negociação"},
            {"id": 2, "cliente": "Agro Tech", "valor": 18000.00, "status": "Proposta Enviada"},
            {"id": 3, "cliente": "Terra Brasil", "valor": 32000.00, "status": "Ganho"}
        ]
        
        return success_response(oportunidades, "Oportunidades obtidas com sucesso")
        
    except Exception as e:
        return error_response("Erro ao obter oportunidades", str(e))

@router.post("/oportunidades")
def criar_oportunidade(oportunidade: Dict[str, Any]):
    """
    Cria nova oportunidade de negócio.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "oportunidade": oportunidade
        }, ["oportunidade"])
        
        # Placeholder - em produção chamaria service
        resultado = {"id": 4, "status": "criada"}
        
        return success_response(resultado, "Oportunidade criada com sucesso")
        
    except Exception as e:
        return error_response("Erro ao criar oportunidade", str(e))

@router.get("/contatos")
def listar_contatos():
    """
    Lista todos os contatos dos clientes.
    """
    try:
        # Placeholder - em produção viria de um service
        contatos = [
            {"id": 1, "cliente": "Fazenda ABC", "nome": "João Silva", "cargo": "Gerente", "email": "joao@fazendaabc.com"},
            {"id": 2, "cliente": "Agro Tech", "nome": "Maria Santos", "cargo": "Diretora", "email": "maria@agrotech.com"},
            {"id": 3, "cliente": "Terra Brasil", "nome": "Pedro Oliveira", "cargo": "Dono", "email": "pedro@terrabrasil.com"}
        ]
        
        return success_response(contatos, "Contatos obtidos com sucesso")
        
    except Exception as e:
        return error_response("Erro ao obter contatos", str(e))

@router.post("/contatos")
def cadastrar_contato(contato: Dict[str, Any]):
    """
    Cadastra novo contato.
    """
    try:
        # Validação de parâmetros
        validar_parametros_obrigatorios({
            "contato": contato
        }, ["contato"])
        
        # Placeholder - em produção chamaria service
        resultado = {"id": 4, "status": "cadastrado"}
        
        return success_response(resultado, "Contato cadastrado com sucesso")
        
    except Exception as e:
        return error_response("Erro ao cadastrar contato", str(e))