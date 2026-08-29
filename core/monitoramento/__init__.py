"""
Precision VRT Solo — Módulo de Monitoramento Completo

Implementa sistema completo de monitoramento temporal da área agrícola.
Permite comparar imagens ao longo do tempo, detectar mudanças
e registrar histórico da evolução vegetacional.

Estrutura:
- monitoramento/        # Motor principal e pipeline
- imagens/             # Gerenciamento de imagens
- comparacao/          # Análise temporal e tendências
- alertas/             # Sistema de alertas pré-configurado
- processamento/       # Pipeline de processamento de imagens
- exportacao/          # Exportação em múltiplos formatos
- agronomia/           # Análise agronômica estruturada

Funcionalidades:
- Comparação temporal de imagens satélite/drone
- Detecção de alterações espectrais
- Registro histórico de evolução
- Exportação de dados processados (PDF, CSV, Excel, GeoJSON, Shapefile, GeoTIFF)
- Arquitetura independente dos demais módulos
- Baseado em código legado extraído e adaptado

Dependências:
- core/tipos/ (estruturas de dados compartilhadas)
- core/utilitarios/ (utilitários genéricos)
"""

# Módulos principais
from .monitoramento.motor import MotorMonitoramento, CalculadorIndices
from .imagens import GerenciadorImagens, ProcessadorImagens, ValidadorImagens, InfoImagem
from .comparacao import AnalisadorComparacao, AgrupadorTemporal, GerenciadorAlertas as AlertasComparacao
from .alertas import (
    TipoAlerta, SeveridadeAlerta, CanalNotificacao,
    AlertaConfigurado, AlertaDisparado,
    ConfiguradorAlertas, DisparadorAlertas, GerenciadorAlertas
)
from .processamento import (
    ConfigProcessamento, ResultadoProcessamento,
    NormalizadorImagens, AlinhadorImagens, RecortadorImagens, PadronizadorImagens,
    MotorProcessamento
)
from .exportacao import (
    ConfigExportadorPDF, ConfigExportadorCSV, ConfigExportadorExcel,
    ExportadorPDF, ExportadorCSV, ExportadorExcel, ExportadorGeoJSON,
    ExportadorShapefile, ExportadorGeoTIFF, MotorExportacao
)
from .agronomia import (
    TipoSolo, Cultura, FaseFenologica,
    ConfigAgronomia, IndicadorAgronomico, AnaliseAgronomica,
    AnalisadorAgronomico, HistoricoAgronomico, MonitoramentoAgronomico
)

# Modelos de dados
from .contratos import (
    TipoSensor, TipoIndice, TipoIntervalo, TipoComparacao,
    ImagemMonitoramento, SerieTemporalVigor, AnomaliaMonitoramento,
    ConfigComparacaoTemporal, ConfigAlerta, ResultadoComparacao,
    HistoricoMonitoramento, ConfigExportacao, AreaMonitoramento
)

__all__ = [
    # Módulos principais
    'MotorMonitoramento',
    'CalculadorIndices',
    'GerenciadorImagens',
    'ProcessadorImagens', 
    'ValidadorImagens',
    'InfoImagem',
    'AnalisadorComparacao',
    'AgrupadorTemporal',
    'AlertasComparacao',
    'TipoAlerta',
    'SeveridadeAlerta',
    'CanalNotificacao',
    'AlertaConfigurado',
    'AlertaDisparado',
    'ConfiguradorAlertas',
    'DisparadorAlertas',
    'GerenciadorAlertas',
    'ConfigProcessamento',
    'ResultadoProcessamento',
    'NormalizadorImagens',
    'AlinhadorImagens',
    'RecortadorImagens',
    'PadronizadorImagens',
    'MotorProcessamento',
    'ConfigExportadorPDF',
    'ConfigExportadorCSV',
    'ConfigExportadorExcel',
    'ExportadorPDF',
    'ExportadorCSV',
    'ExportadorExcel',
    'ExportadorGeoJSON',
    'ExportadorShapefile',
    'ExportadorGeoTIFF',
    'MotorExportacao',
    'TipoSolo',
    'Cultura',
    'FaseFenologica',
    'ConfigAgronomia',
    'IndicadorAgronomico',
    'AnaliseAgronomica',
    'AnalisadorAgronomico',
    'HistoricoAgronomico',
    'MonitoramentoAgronomico',
    
    # Modelos de dados
    'TipoSensor',
    'TipoIndice',
    'TipoIntervalo', 
    'TipoComparacao',
    'ImagemMonitoramento',
    'SerieTemporalVigor',
    'AnomaliaMonitoramento',
    'ConfigComparacaoTemporal',
    'ConfigAlerta',
    'ResultadoComparacao',
    'HistoricoMonitoramento',
    'ConfigExportacao',
    'AreaMonitoramento'
]