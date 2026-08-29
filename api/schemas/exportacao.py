"""
Precision VRT Solo — Schema de Exportação

Schemas de entrada e saída para exportação de dados.
Contém apenas tipos, sem regra de negócio.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class ExportarPDFRequest(BaseModel):
    """
    Request para exportação em PDF.
    """
    dados_originais: Dict[str, Any]
    nome_arquivo_base: str
    configuracoes: Optional[Dict[str, Any]] = None

class ExportarCSVRequest(BaseModel):
    """
    Request para exportação em CSV.
    """
    dados_originais: Dict[str, Any]
    nome_arquivo_base: str
    configuracoes: Optional[Dict[str, Any]] = None

class ExportarExcelRequest(BaseModel):
    """
    Request para exportação em Excel.
    """
    dados_originais: Dict[str, Any]
    nome_arquivo_base: str
    configuracoes: Optional[Dict[str, Any]] = None

class ExportarGeoJSONRequest(BaseModel):
    """
    Request para exportação em GeoJSON.
    """
    dados_originais: Dict[str, Any]
    nome_arquivo_base: str
    configuracoes: Optional[Dict[str, Any]] = None

class ExportarShapefileRequest(BaseModel):
    """
    Request para exportação em Shapefile.
    """
    dados_originais: Dict[str, Any]
    nome_arquivo_base: str
    configuracoes: Optional[Dict[str, Any]] = None

class ExportarGeoTIFFRequest(BaseModel):
    """
    Request para exportação em GeoTIFF.
    """
    dados_originais: Dict[str, Any]
    nome_arquivo_base: str
    configuracoes: Optional[Dict[str, Any]] = None

class ExportarISOXMLRequest(BaseModel):
    """
    Request para exportação em ISOXML.
    """
    dados_originais: Dict[str, Any]
    nome_arquivo_base: str
    configuracoes: Optional[Dict[str, Any]] = None

class ExportarKMLRequest(BaseModel):
    """
    Request para exportação em KML.
    """
    dados_originais: Dict[str, Any]
    nome_arquivo_base: str
    configuracoes: Optional[Dict[str, Any]] = None

class ExportarKMZRequest(BaseModel):
    """
    Request para exportação em KMZ.
    """
    dados_originais: Dict[str, Any]
    nome_arquivo_base: str
    configuracoes: Optional[Dict[str, Any]] = None

class ExportarMultiplosRequest(BaseModel):
    """
    Request para exportação múltipla.
    """
    dados_originais: Dict[str, Any]
    formatos: List[str]
    nome_arquivo_base: str
    configuracoes: Optional[Dict[str, Any]] = None

class ExportacaoResponse(BaseModel):
    """
    Response padrão para operações de exportação.
    """
    sucesso: bool
    mensagem: str
    arquivo: Optional[str] = None
    formato: Optional[str] = None

class ExportacaoMultiplosResponse(BaseModel):
    """
    Response para exportação múltipla.
    """
    sucesso: bool
    mensagem: str
    arquivos: Optional[List[str]] = None