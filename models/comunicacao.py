
"""
Precision VRT Solo — Modelo de Comunicação

Implementa modelos de dados para gestão de comunicação e envio de documentos.
"""

from typing import Any, Dict
from datetime import datetime
from enum import Enum

class CanalEnvio(Enum):
    """Canais de comunicação disponíveis."""
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SMS = "sms"
    NOTIFICACAO = "notificacao"

class StatusEnvio(Enum):
    """Status de envio de documentos."""
    PENDENTE = "pendente"
    ENVIADO = "enviado"
    FALHA = "falha"
    RETRY = "retry"
    CANCELADO = "cancelado"

class TipoDocumento(Enum):
    """Tipos de documentos para envio."""
    LAUDO = "laudo"
    ORCAMENTO = "orcamento"
    FATURA = "fatura"
    RECIBO = "recibo"
    PROPOSTA = "proposta"
    CONTRATO = "contrato"
    NOTIFICACAO = "notificacao"

class LogEnvio:
    """
    Registro de logs de envio de documentos.
    """
    
    def __init__(self,
                 log_id: int,
                 canal: CanalEnvio,
                 status: StatusEnvio,
                 tipo_documento: TipoDocumento,
                 destinatario: str,
                 assunto: str = None,
                 documento_id: int = None,
                 referencia_id: int = None,
                 erro: str = None,
                 resposta_api: Dict[str, Any] = None,
                 enviado_em: datetime = None):
        self.log_id = log_id
        self.canal = canal
        self.status = status
        self.tipo_documento = tipo_documento
        self.destinatario = destinatario
        self.assunto = assunto
        self.documento_id = documento_id
        self.referencia_id = referencia_id
        self.erro = erro
        self.resposta_api = resposta_api or {}
        self.enviado_em = enviado_em or datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte para dicionário.
        """
        return {
            'log_id': self.log_id,
            'canal': self.canal.value,
            'status': self.status.value,
            'tipo_documento': self.tipo_documento.value,
            'destinatario': self.destinatario,
            'assunto': self.assunto,
            'documento_id': self.documento_id,
            'referencia_id': self.referencia_id,
            'erro': self.erro,
            'resposta_api': self.resposta_api,
            'enviado_em': self.enviado_em.isoformat()
        }

class Aniversariante:
    """
    Pessoa que faz aniversário.
    """
    
    def __init__(self, id: int, nome: str, tipo: str, email: str = None, telefone: str = None):
        self.id = id
        self.nome = nome
        self.tipo = tipo  # 'cliente' ou 'funcionario'
        self.email = email
        self.telefone = telefone
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte para dicionário.
        """
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'email': self.email,
            'telefone': self.telefone
        }
