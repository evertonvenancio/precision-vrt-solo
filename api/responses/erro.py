"""
Precision VRT Solo — Respostas de Erro

Respostas padrão de erro da API.
Formato unificado.
"""

from typing import Optional
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """
    Resposta padrão de erro.
    """
    success: bool = False
    message: str
    error: Optional[str] = None
    timestamp: Optional[str] = None
    code: Optional[int] = None

def error_response(
    message: str,
    error: Optional[str] = None,
    code: Optional[int] = None
) -> ErrorResponse:
    """
    Cria resposta de erro.
    
    Args:
        message: Mensagem de erro
        error: Detalhe técnico do erro
        code: Código do erro
        
    Returns:
        Resposta de erro formatada
    """
    from datetime import datetime
    timestamp = datetime.now().isoformat()
    
    return ErrorResponse(
        message=message,
        error=error,
        code=code,
        timestamp=timestamp
    )