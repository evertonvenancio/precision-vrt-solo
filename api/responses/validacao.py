"""
Precision VRT Solo — Respostas de Validação

Respostas padrão de validação da API.
Formato unificado.
"""

from typing import Optional, List
from pydantic import BaseModel

class ValidationErrorResponse(BaseModel):
    """
    Resposta padrão de erro de validação.
    """
    success: bool = False
    message: str
    errors: Optional[List[str]] = None
    field: Optional[str] = None
    timestamp: Optional[str] = None

def validation_error_response(
    message: str,
    errors: Optional[List[str]] = None,
    field: Optional[str] = None
) -> ValidationErrorResponse:
    """
    Cria resposta de erro de validação.
    
    Args:
        message: Mensagem de erro
        errors: Lista de erros específicos
        field: Campo com erro
        
    Returns:
        Resposta de erro de validação formatada
    """
    from datetime import datetime
    timestamp = datetime.now().isoformat()
    
    return ValidationErrorResponse(
        message=message,
        errors=errors,
        field=field,
        timestamp=timestamp
    )