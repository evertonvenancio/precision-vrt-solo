"""
Precision VRT Solo — Respostas de Sucesso

Respostas padrão de sucesso da API.
Formato unificado.
"""

from typing import Any, Optional
from pydantic import BaseModel

class SuccessResponse(BaseModel):
    """
    Resposta padrão de sucesso.
    """
    success: bool = True
    message: str
    data: Optional[Any] = None
    timestamp: Optional[str] = None

def success_response(
    data: Any = None,
    message: str = "Operação realizada com sucesso"
) -> SuccessResponse:
    """
    Cria resposta de sucesso.
    
    Args:
        data: Dados da resposta
        message: Mensagem de sucesso
        
    Returns:
        Resposta de sucesso formatada
    """
    from datetime import datetime
    timestamp = datetime.now().isoformat()
    
    return SuccessResponse(
        message=message,
        data=data,
        timestamp=timestamp
    )