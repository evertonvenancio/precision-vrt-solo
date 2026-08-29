"""
Precision VRT Solo — Schemas Comuns

Schemas genéricos usados em toda a API.
Sem regra de negócio, apenas tipos.
"""

from typing import Optional, Any, Dict, List
from pydantic import BaseModel

class PipelineRequest(BaseModel):
    """
    Request padrão para operações de pipeline.
    """
    configuracoes: Optional[Dict[str, Any]] = None
    arquivo_limite: Optional[str] = None
    arquivo_amostras: Optional[str] = None
    cultura: Optional[str] = None
    formula: Optional[str] = None
    formatos_saida: Optional[List[str]] = None

class PipelineResponse(BaseModel):
    """
    Response padrão para operações de pipeline.
    """
    sucesso: bool
    mensagem: str
    dados: Optional[Dict[str, Any]] = None
    arquivos_exportados: Optional[List[str]] = None

class UploadRequest(BaseModel):
    """
    Request para uploads de arquivos.
    """
    arquivo: str
    tipo: str = "padrao"

class ExportRequest(BaseModel):
    """
    Request para exportação.
    """
    dados_originais: Dict[str, Any]
    formatos: List[str]
    nome_arquivo_base: str
    configuracoes: Optional[Dict[str, Any]] = None

class AreaRequest(BaseModel):
    """
    Request para operações que envolvem área.
    """
    area_geojson_path: str
    configuracoes: Optional[Dict[str, Any]] = None