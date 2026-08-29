"""
Precision VRT Solo — Schema de Fertirrigação

Schemas de entrada e saída para recomendação de fertirrigação.
Contém apenas tipos, sem regra de negócio.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class ImportarFertirrigacaoRequest(BaseModel):
    """
    Request para importação de dados de fertirrigação.
    """
    arquivo_limite: str
    arquivo_amostras: str
    configuracoes: Optional[Dict[str, Any]] = None

class InterpolarFertirrigacaoRequest(BaseModel):
    """
    Request para interpolação de dados (opcional).
    """
    arquivo_limite: str
    arquivo_amostras: str
    configuracoes: Optional[Dict[str, Any]] = None

class RecomendarFertirrigacaoRequest(BaseModel):
    """
    Request para recomendação de fertirrigação.
    """
    arquivo_limite: str
    cultura: str
    configuracoes: Optional[Dict[str, Any]] = None

class ExportarResultadosFertirrigacaoRequest(BaseModel):
    """
    Request para exportação de resultados de fertirrigação.
    """
    dados_fertirrigacao: Dict[str, Any]
    formatos: List[str]
    nome_arquivo_base: str
    configuracoes: Optional[Dict[str, Any]] = None

class PipelineCompletoFertirrigacaoRequest(BaseModel):
    """
    Request para pipeline completo de fertirrigação.
    """
    arquivo_limite: str
    cultura: str
    configuracoes: Optional[Dict[str, Any]] = None

class FertirrigacaoResponse(BaseModel):
    """
    Response padrão para operações de fertirrigação.
    """
    sucesso: bool
    mensagem: str
    dados: Optional[Dict[str, Any]] = None
    arquivos_exportados: Optional[List[str]] = None

class RecomendacaoResponse(BaseModel):
    """
    Response para recomendação de fertirrigação.
    """
    sucesso: bool
    mensagem: str
    recomendacoes: Optional[Dict[str, Any]] = None

class ResultadosFertirrigacaoResponse(BaseModel):
    """
    Response para resultados de fertirrigação.
    """
    sucesso: bool
    mensagem: str
    resultados: Optional[Dict[str, Any]] = None