"""
Precision VRT Solo — Schema de Nematoides

Schemas de entrada e saída para análise de nematoides.
Contém apenas tipos, sem regra de negócio.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class ImportarNematoidesRequest(BaseModel):
    """
    Request para importação de análise de nematoides.
    """
    arquivo_limite: str
    arquivo_amostras: str
    configuracoes: Optional[Dict[str, Any]] = None

class InterpolarNematoidesRequest(BaseModel):
    """
    Request para interpolação de dados de nematoides.
    """
    arquivo_limite: str
    arquivo_amostras: str
    configuracoes: Optional[Dict[str, Any]] = None

class ZonearNematoidesRequest(BaseModel):
    """
    Request para zoneamento de área.
    """
    arquivo_limite: str
    arquivo_interpolado: str
    configuracoes: Optional[Dict[str, Any]] = None

class GerarMapaNematoidesRequest(BaseModel):
    """
    Request para geração de mapa de nematoides.
    """
    arquivo_limite: str
    arquivo_zoneamento: str
    configuracoes: Optional[Dict[str, Any]] = None

class ExportarResultadosNematoidesRequest(BaseModel):
    """
    Request para exportação de resultados de nematoides.
    """
    dados_nematoides: Dict[str, Any]
    formatos: List[str]
    nome_arquivo_base: str
    configuracoes: Optional[Dict[str, Any]] = None

class PipelineCompletoNematoidesRequest(BaseModel):
    """
    Request para pipeline completo de análise de nematoides.
    """
    arquivo_limite: str
    arquivo_amostras: str
    configuracoes: Optional[Dict[str, Any]] = None

class NematoidesResponse(BaseModel):
    """
    Response padrão para operações de nematoides.
    """
    sucesso: bool
    mensagem: str
    dados: Optional[Dict[str, Any]] = None
    arquivos_exportados: Optional[List[str]] = None

class MapaNematoidesResponse(BaseModel):
    """
    Response para geração de mapa de nematoides.
    """
    sucesso: bool
    mensagem: str
    mapa: Optional[Dict[str, Any]] = None

class ResultadosNematoidesResponse(BaseModel):
    """
    Response para resultados de análise de nematoides.
    """
    sucesso: bool
    mensagem: str
    resultados: Optional[Dict[str, Any]] = None