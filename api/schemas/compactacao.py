"""
Precision VRT Solo — Schema de Compactação

Schemas de entrada e saída para compactação.
Contém apenas tipos, sem regra de negócio.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class ImportarCompactacaoRequest(BaseModel):
    """
    Request para importação de compactação.
    """
    arquivo_limite: str
    arquivo_amostras: str
    configuracoes: Optional[Dict[str, Any]] = None

class InterpolarCompactacaoRequest(BaseModel):
    """
    Request para interpolação de dados.
    """
    arquivo_limite: str
    arquivo_amostras: str
    configuracoes: Optional[Dict[str, Any]] = None

class ZonearCompactacaoRequest(BaseModel):
    """
    Request para zoneamento de área.
    """
    arquivo_limite: str
    arquivo_interpolado: str
    configuracoes: Optional[Dict[str, Any]] = None

class GerarMapaRequest(BaseModel):
    """
    Request para geração de mapa.
    """
    arquivo_limite: str
    arquivo_zoneamento: str
    configuracoes: Optional[Dict[str, Any]] = None

class ExportarResultadosRequest(BaseModel):
    """
    Request para exportação de resultados.
    """
    dados_compactacao: Dict[str, Any]
    formatos: List[str]
    nome_arquivo_base: str
    configuracoes: Optional[Dict[str, Any]] = None

class PipelineCompletoCompactacaoRequest(BaseModel):
    """
    Request para pipeline completo de compactação.
    """
    arquivo_limite: str
    arquivo_amostras: str
    configuracoes: Optional[Dict[str, Any]] = None

class CompactacaoResponse(BaseModel):
    """
    Response padrão para operações de compactação.
    """
    sucesso: bool
    mensagem: str
    dados: Optional[Dict[str, Any]] = None
    arquivos_exportados: Optional[List[str]] = None

class MapaResponse(BaseModel):
    """
    Response para geração de mapa.
    """
    sucesso: bool
    mensagem: str
    mapa: Optional[Dict[str, Any]] = None

class ResultadosResponse(BaseModel):
    """
    Response para resultados de compactação.
    """
    sucesso: bool
    mensagem: str
    resultados: Optional[Dict[str, Any]] = None