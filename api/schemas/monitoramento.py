"""
Precision VRT Solo — Schema de Monitoramento

Schemas de entrada e saída para monitoramento de áreas.
Contém apenas tipos, sem regra de negócio.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class CompararAreasRequest(BaseModel):
    """
    Request para comparação de áreas.
    """
    area_geojson_1: str
    area_geojson_2: str
    periodo_1: str
    periodo_2: str
    configuracoes: Optional[Dict[str, Any]] = None

class CompararAreasResponse(BaseModel):
    """
    Response para comparação de áreas.
    """
    sucesso: bool
    mensagem: str
    comparacao: Optional[Dict[str, Any]] = None

class HistoricoRequest(BaseModel):
    """
    Request para histórico de monitoramento.
    """
    area_geojson: str
    periodo_inicio: str
    periodo_fim: str
    configuracoes: Optional[Dict[str, Any]] = None

class HistoricoResponse(BaseModel):
    """
    Response para histórico de monitoramento.
    """
    sucesso: bool
    mensagem: str
    historico: Optional[List[Dict[str, Any]]] = None

class AlertasRequest(BaseModel):
    """
    Request para geração de alertas.
    """
    area_geojson: str
    configuracoes: Optional[Dict[str, Any]] = None

class AlertasResponse(BaseModel):
    """
    Response para geração de alertas.
    """
    sucesso: bool
    mensagem: str
    alertas: Optional[List[Dict[str, Any]]] = None

class RelatorioRequest(BaseModel):
    """
    Request para geração de relatório.
    """
    area_geojson: str
    periodo_inicio: str
    periodo_fim: str
    formatos: List[str]
    configuracoes: Optional[Dict[str, Any]] = None

class RelatorioResponse(BaseModel):
    """
    Response para geração de relatório.
    """
    sucesso: bool
    mensagem: str
    relatorio: Optional[Dict[str, Any]] = None

class PipelineCompletoMonitoramentoRequest(BaseModel):
    """
    Request para pipeline completo de monitoramento.
    """
    area_geojson: str
    periodo_inicio: str
    periodo_fim: str
    configuracoes: Optional[Dict[str, Any]] = None

class MonitoramentoResponse(BaseModel):
    """
    Response padrão para operações de monitoramento.
    """
    sucesso: bool
    mensagem: str
    dados: Optional[Dict[str, Any]] = None
    arquivos_exportados: Optional[List[str]] = None