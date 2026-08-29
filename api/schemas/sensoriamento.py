"""
Precision VRT Solo — Schema de Sensoriamento

Schemas de entrada e saída para sensoriamento por satélite.
Contém apenas tipos, sem regra de negócio.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class SatelitesResponse(BaseModel):
    """
    Response para listagem de satélites.
    """
    sucesso: bool
    mensagem: str
    satelites: Optional[List[Dict[str, Any]]] = None

class IndicesSensoresRequest(BaseModel):
    """
    Request para obtenção de índices de sensores.
    """
    satelite: str
    configuracoes: Optional[Dict[str, Any]] = None

class IndicesResponse(BaseModel):
    """
    Response para índices de sensores.
    """
    sucesso: bool
    mensagem: str
    indices: Optional[List[Dict[str, Any]]] = None

class BaixarImagensRequest(BaseModel):
    """
    Request para download de imagens.
    """
    satelite: str
    indices: List[str]
    area_geojson: str
    configuracoes: Optional[Dict[str, Any]] = None

class ImagensResponse(BaseModel):
    """
    Response para download de imagens.
    """
    sucesso: bool
    mensagem: str
    imagens: Optional[List[str]] = None

class GerarMapasRequest(BaseModel):
    """
    Request para geração de mapas.
    """
    arquivo_imagens: str
    indices: List[str]
    configuracoes: Optional[Dict[str, Any]] = None

class MapasResponse(BaseModel):
    """
    Response para geração de mapas.
    """
    sucesso: bool
    mensagem: str
    mapas: Optional[List[Dict[str, Any]]] = None

class HistoricoRequest(BaseModel):
    """
    Request para histórico de imagens.
    """
    area_geojson: str
    periodo_inicio: str
    periodo_fim: str
    satelite: Optional[str] = None
    configuracoes: Optional[Dict[str, Any]] = None

class HistoricoResponse(BaseModel):
    """
    Response para histórico de imagens.
    """
    sucesso: bool
    mensagem: str
    historico: Optional[List[Dict[str, Any]]] = None

class PipelineCompletoSensoriamentoRequest(BaseModel):
    """
    Request para pipeline completo de sensoriamento.
    """
    area_geojson: str
    satelite: str
    indices: List[str]
    periodo_inicio: str
    periodo_fim: str
    configuracoes: Optional[Dict[str, Any]] = None

class SensoriamentoResponse(BaseModel):
    """
    Response padrão para operações de sensoriamento.
    """
    sucesso: bool
    mensagem: str
    dados: Optional[Dict[str, Any]] = None
    arquivos_exportados: Optional[List[str]] = None