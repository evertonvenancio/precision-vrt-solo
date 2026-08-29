
"""
Precision VRT Solo — Modelo Fiscal

Implementa modelos de dados para gestão de documentos fiscais e notas fiscais.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class ProvedorFiscal(Enum):
    """Provedores de serviços fiscais."""
    PLUGNOTAS = "plugnotas"
    ENOTAS = "enotas"
    NFE = "nfe"
    NFS = "nfs"
    SAT = "sat"
    DFE = "dfe"

class StatusNota(Enum):
    """Status das notas fiscais."""
    rascunho = "rascunho"
    emitida = "emitida"
    autorizada = "autorizada"
    cancelada = "cancelada"
    denegada = "denegada"
    inutilizada = "inutilizada"

class NotaFiscal:
    """
    Representa uma nota fiscal.
    """
    
    def __init__(self,
                 id: UUID,
                 tenant_id: UUID,
                 orcamento_id: UUID,
                 provedor: ProvedorFiscal,
                 status: StatusNota,
                 numero_nota: Optional[str] = None,
                 serie: Optional[str] = None,
                 chave_acesso: Optional[str] = None,
                 xml_content: Optional[str] = None,
                 pdf_content: Optional[str] = None,
                 dados_adicionais: Optional[dict] = None):
        self.id = id
        self.tenant_id = tenant_id
        self.orcamento_id = orcamento_id
        self.provedor = provedor
        self.status = status
        self.numero_nota = numero_nota
        self.serie = serie
        self.chave_acesso = chave_acesso
        self.xml_content = xml_content
        self.pdf_content = pdf_content
        self.dados_adicionais = dados_adicionais or {}
        self.criado_em = datetime.now()
        self.atualizado_em = datetime.now()
        
    def to_dict(self) -> dict:
        """
        Converte para dicionário.
        """
        return {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'orcamento_id': str(self.orcamento_id),
            'provedor': self.provedor.value,
            'status': self.status.value,
            'numero_nota': self.numero_nota,
            'serie': self.serie,
            'chave_acesso': self.chave_acesso,
            'xml_content': self.xml_content,
            'pdf_content': self.pdf_content,
            'dados_adicionais': self.dados_adicionais,
            'criado_em': self.criado_em.isoformat(),
            'atualizado_em': self.atualizado_em.isoformat()
        }

class FiscalError(Exception):
    """
    Exceção personalizada para erros na camada fiscal.
    """
    pass
