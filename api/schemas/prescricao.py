"""
Precision VRT Solo — Schema de Prescrição VRT

Schemas de entrada e saída para prescrição VRT.
Contém apenas tipos, sem regra de negócio.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class ImportarPrescricaoRequest(BaseModel):
    """
    Request para importação de prescrição.
    """
    arquivo_limite: str
    arquivo_amostras: str
    configuracoes: Optional[Dict[str, Any]] = None

class InterpolarPrescricaoRequest(BaseModel):
    """
    Request para interpolação de prescrição.
    """
    arquivo_limite: str
    arquivo_amostras: str
    configuracoes: Optional[Dict[str, Any]] = None

class ZonearPrescricaoRequest(BaseModel):
    """
    Request para zoneamento de prescrição.
    """
    arquivo_limite: str
    arquivo_interpolado: str
    configuracoes: Optional[Dict[str, Any]] = None

class PrescreverFertilizanteRequest(BaseModel):
    """
    Request para prescrição de fertilizantes.
    """
    arquivo_limite: str
    arquivo_zoneamento: str
    cultura: str
    formula: str
    configuracoes: Optional[Dict[str, Any]] = None

class ExportarPrescricaoRequest(BaseModel):
    """
    Request para exportação de prescrição.
    """
    dados_prescricao: Dict[str, Any]
    formatos: List[str]
    nome_arquivo_base: str
    configuracoes: Optional[Dict[str, Any]] = None

class PipelineCompletoPrescricaoRequest(BaseModel):
    """
    Request para pipeline completo de prescrição.
    """
    arquivo_limite: str
    arquivo_amostras: str
    cultura: str
    formula: str
    configuracoes: Optional[Dict[str, Any]] = None

class PrescricaoResponse(BaseModel):
    """
    Response padrão para operações de prescrição.
    """
    sucesso: bool
    mensagem: str
    dados: Optional[Dict[str, Any]] = None
    arquivos_exportados: Optional[List[str]] = None

class CulturaResponse(BaseModel):
    """
    Response para listagem de culturas.
    """
    sucesso: bool
    mensagem: str
    culturas: Optional[List[Dict[str, Any]]] = None

class FormulaResponse(BaseModel):
    """
    Response para listagem de fórmulas.
    """
    sucesso: bool
    mensagem: str
    formulas: Optional[List[Dict[str, Any]]] = None

class ConfiguracaoResponse(BaseModel):
    """
    Response para configurações padrão.
    """
    sucesso: bool
    mensagem: str
    configuracoes: Optional[Dict[str, Any]] = None