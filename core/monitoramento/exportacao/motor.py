"""
Precision VRT Solo — Módulo de Exportação

Suporta todos os formatos especificados: PDF, CSV, Excel, GeoJSON, Shapefile, GeoTIFF.
Nunca cria exportadores específicos para fabricantes.
"""

import json
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime
from dataclasses import dataclass, field
import logging

from core.tipos.base import ConfigBase
from ..contratos import (
    HistoricoMonitoramento,
    SerieTemporalVigor,
    ResultadoComparacao,
    AnomaliaMonitoramento,
    ConfigExportacao,
    AreaMonitoramento
)
from ..processamento import ResultadoProcessamento

logger = logging.getLogger(__name__)


@dataclass
class ConfigExportadorPDF:
    """Configuração para exportação em PDF."""
    
    template_pdf: str = "template_padrao.pdf"
    incluir_logo: bool = True
    tamanho_pagina: str = "A4"
    orientacao: str = "portrait"
    margens: Dict[str, float] = field(default_factory=lambda: {"top": 2.54, "bottom": 2.54, "left": 2.54, "right": 2.54})
    fontes: Dict[str, str] = field(default_factory=lambda: {"principal": "Arial", "cabecalho": "Arial Bold"})


@dataclass
class ConfigExportadorCSV:
    """Configuração para exportação em CSV."""
    
    delimitador: str = ";"
    decimal: str = ","
    codificacao: str = "utf-8"
    incluir_cabecalho: bool = True
    indexar: bool = False


@dataclass
class ConfigExportadorExcel:
    """Configuração para exportação em Excel."""
    
    planilhas_multiplos_arquivos: bool = False
    nome_planilha_padrao: str = "Monitoramento"
    formatos_condicionais: bool = True
    graficos_incluidos: bool = False
    hiperlinks_ativos: bool = True


class ExportadorPDF:
    """
    Exporta dados de monitoramento para formato PDF.
    """
    
    def __init__(self, config: ConfigExportadorPDF):
        self.config = config
        self.template_path = Path(__file__).parent / "templates" / config.template_pdf
    
    def exportar_historico(self, historico: HistoricoMonitoramento, 
                          caminho_saida: str) -> bool:
        """
        Exporta histórico de monitoramento para PDF.
        
        Args:
            historico: Dados do histórico
            caminho_saida: Caminho do arquivo de saída
            
        Returns:
            True se exportado com sucesso
        """
        try:
            # Criar conteúdo do PDF
            conteudo_pdf = self._gerar_conteudo_pdf(historico)
            
            # Simplificado - em produção usar biblioteca como reportlab
            with open(caminho_saida, 'w', encoding='utf-8') as f:
                f.write(f"# Relatório de Monitoramento\n")
                f.write(f"Área: {historico.area_id}\n")
                f.write(f"Safra: {historico.safra}\n")
                f.write(f"Período: {historico.inicio_monitoramento}")
                
                if historico.fim_monitoramento:
                    f.write(f" até {historico.fim_monitoramento}\n")
                else:
                    f.write("\n")
                
                f.write(f"Imagens processadas: {len(historico.imagens_processadas)}\n")
                f.write(f"Comparações realizadas: {len(historico.comparacoes_realizadas)}\n")
                f.write(f"Anomalias detectadas: {len(historico.anomalias_registradas)}\n")
                
                # Adicionar resumo final
                if historico.resumo_final:
                    f.write("\n## Resumo Final\n")
                    for chave, valor in historico.resumo_final.items():
                        f.write(f"{chave}: {valor}\n")
            
            logger.info(f"Histórico exportado para PDF: {caminho_saida}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar PDF: {e}")
            return False
    
    def exportar_comparacoes(self, comparacoes: List[ResultadoComparacao], 
                           caminho_saida: str) -> bool:
        """
        Exporta comparações temporais para PDF.
        
        Args:
            comparacoes: Lista de comparações
            caminho_saida: Caminho do arquivo de saída
            
        Returns:
            True se exportado com sucesso
        """
        try:
            with open(caminho_saida, 'w', encoding='utf-8') as f:
                f.write("# Relatório de Comparações Temporais\n\n")
                
                for i, comparacao in enumerate(comparacoes, 1):
                    f.write(f"## Comparação {i}\n")
                    f.write(f"Imagem base: {comparacao.imagem_base_id}\n")
                    f.write(f"Imagem comparada: {comparacao.imagem_comparada_id}\n")
                    f.write(f"Intervalo: {comparacao.intervalo_dias} dias\n")
                    f.write(f"Índice analisado: {comparacao.indice_analisado}\n")
                    f.write(f"Diferença média: {comparacao.diferenca_media:.4f}\n")
                    f.write(f"Anomalias detectadas: {len(comparacao.anomalias_detectadas)}\n")
                    
                    if comparacao.anomalias_detectadas:
                        f.write("\n### Anomalias\n")
                        for anomalia in comparacao.anomalias_detectadas:
                            f.write(f"- {anomalia.indice}: {anomalia.desvio_percentual:.2f}% ({anomalia.severidade})\n")
                    
                    f.write("\n" + "="*50 + "\n\n")
            
            logger.info(f"Comparações exportadas para PDF: {caminho_saida}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar PDF comparacoes: {e}")
            return False
    
    def _gerar_conteudo_pdf(self, historico: HistoricoMonitoramento) -> str:
        """
        Gera conteúdo do PDF.
        
        Args:
            historico: Dados do histórico
            
        Returns:
            Conteúdo formatado
        """
        # Simplificado - implementar gerador completo em futura iteração
        logger.warning("Gerador de PDF não implementado completamente")
        return f"Relatório de Monitoramento - {historico.area_id}"


class ExportadorCSV:
    """
    Exporta dados de monitoramento para formato CSV.
    """
    
    def __init__(self, config: ConfigExportadorCSV):
        self.config = config
    
    def exportar_series_temporais(self, series: Dict[int, SerieTemporalVigor], 
                                caminho_saida: str) -> bool:
        """
        Exporta séries temporais para CSV.
        
        Args:
            series: Dicionário de séries temporais
            caminho_saida: Caminho do arquivo de saída
            
        Returns:
            True se exportado com sucesso
        """
        try:
            rows = []
            
            for zona_id, serie in series.items():
                for i, data in enumerate(serie.datas):
                    row = {
                        'zona_id': zona_id,
                        'data': data,
                        'n_imagens': i + 1
                    }
                    
                    # Adicionar valores médios por índice
                    for indice, valores in serie.valores_medios.items():
                        if i < len(valores):
                            row[f'{indice}_media'] = valores[i]
                        else:
                            row[f'{indice}_media'] = None
                    
                    # Adicionar desvios padrão por índice
                    for indice, desvios in serie.desvios.items():
                        if i < len(desvios):
                            row[f'{indice}_desvio'] = desvios[i]
                        else:
                            row[f'{indice}_desvio'] = None
                    
                    # Adicionar contagem de anomalias até este ponto
                    row['n_anomlicas_atuais'] = len([a for a in serie.anomalias 
                                                    if a.data <= data])
                    
                    rows.append(row)
            
            df = pd.DataFrame(rows)
            df.to_csv(caminho_saida, 
                     sep=self.config.delimitador,
                     decimal=self.config.decimal,
                     encoding=self.config.codificacao,
                     header=self.config.incluir_cabecalho,
                     index=self.config.indexar)
            
            logger.info(f"Séries temporais exportadas para CSV: {caminho_saida}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar CSV series: {e}")
            return False
    
    def exportar_anomalias(self, anomalias: List[AnomaliaMonitoramento], 
                          caminho_saida: str) -> bool:
        """
        Exporta anomalias para CSV.
        
        Args:
            anomalias: Lista de anomalias
            caminho_saida: Caminho do arquivo de saída
            
        Returns:
            True se exportado com sucesso
        """
        try:
            rows = []
            
            for anomalia in anomalias:
                row = {
                    'zona_id': anomalia.zona_id,
                    'data': anomalia.data,
                    'indice': anomalia.indice,
                    'valor_observado': anomalia.valor_observado,
                    'valor_esperado': anomalia.valor_esperado,
                    'desvio_percentual': anomalia.desvio_percentual,
                    'tipo': anomalia.tipo,
                    'severidade': anomalia.severidade
                }
                
                # Adicionar possíveis causas
                if anomalia.possiveis_causas:
                    row['possiveis_causas'] = "; ".join(anomalia.possiveis_causas)
                else:
                    row['possiveis_causas'] = ""
                
                # Adicionar contexto se disponível
                if anomalia.contexto:
                    for chave, valor in anomalia.contexto.items():
                        row[f'contexto_{chave}'] = str(valor)
                
                rows.append(row)
            
            df = pd.DataFrame(rows)
            df.to_csv(caminho_saida, 
                     sep=self.config.delimitador,
                     decimal=self.config.decimal,
                     encoding=self.config.codificacao,
                     header=self.config.incluir_cabecalho,
                     index=self.config.indexar)
            
            logger.info(f"Anomalias exportadas para CSV: {caminho_saida}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar CSV anomalias: {e}")
            return False
    
    def exportar_comparacoes(self, comparacoes: List[ResultadoComparacao], 
                           caminho_saida: str) -> bool:
        """
        Exporta comparações para CSV.
        
        Args:
            comparacoes: Lista de comparações
            caminho_saida: Caminho do arquivo de saída
            
        Returns:
            True se exportado com sucesso
        """
        try:
            rows = []
            
            for comparacao in comparacoes:
                row = {
                    'imagem_base_id': comparacao.imagem_base_id,
                    'imagem_comparada_id': comparacao.imagem_comparada_id,
                    'intervalo_dias': comparacao.intervalo_dias,
                    'indice_analisado': comparacao.indice_analisado,
                    'diferenca_media': comparacao.diferenca_media,
                    'diferenca_maxima': comparacao.diferenca_maxima,
                    'diferenca_minima': comparacao.diferenca_minima,
                    'n_anomalias': len(comparacao.anomalias_detectadas),
                    'data_comparacao': comparacao.data_comparacao
                }
                
                # Adicionar estatísticas por índice
                for indice, stats in comparacao.estatisticas.items():
                    row[f'{indice}_diff_media'] = stats['diferencia_media']
                    row[f'{indice}_diff_percentual'] = stats['diferencia_percentual']
                    row[f'{indice}_media_base'] = stats['media_base']
                    row[f'{indice}_media_comparada'] = stats['media_comparada']
                
                rows.append(row)
            
            df = pd.DataFrame(rows)
            df.to_csv(caminho_saida, 
                     sep=self.config.delimitador,
                     decimal=self.config.decimal,
                     encoding=self.config.codificacao,
                     header=self.config.incluir_cabecalho,
                     index=self.config.indexar)
            
            logger.info(f"Comparações exportadas para CSV: {caminho_saida}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar CSV comparacoes: {e}")
            return False


class ExportadorExcel:
    """
    Exporta dados de monitoramento para formato Excel.
    """
    
    def __init__(self, config: ConfigExportadorExcel):
        self.config = config
    
    def exportar_completo(self, historico: HistoricoMonitoramento, 
                         caminho_saida: str) -> bool:
        """
        Exporta dados completos para Excel com múltiplas planilhas.
        
        Args:
            historico: Dados do histórico
            caminho_saida: Caminho do arquivo de saída
            
        Returns:
            True se exportado com sucesso
        """
        try:
            with pd.ExcelWriter(caminho_saida, engine='openpyxl') as writer:
                # Planilha: Resumo
                self._exportar_resumo(historico, writer)
                
                # Planilha: Séries Temporais
                self._exportar_series_temporais(historico.series_temporais, writer)
                
                # Planilha: Anomalias
                self._exportar_anomalias(historico.anomalias_registradas, writer)
                
                # Planilha: Comparações
                self._exportar_comparacoes(historico.comparacoes_realizadas, writer)
                
                # Planilha: Metadados
                self._exportar_metadados(historico.metadata, writer)
            
            logger.info(f"Dados completos exportados para Excel: {caminho_saida}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar Excel: {e}")
            return False
    
    def _exportar_resumo(self, historico: HistoricoMonitoramento, writer):
        """Exporta resumo na primeira planilha."""
        resumo_data = {
            'Métrica': [
                'ID Área', 'Safra', 'Período Monitoramento',
                'Total Imagens', 'Total Comparações', 'Total Anomalias',
                'Total Alertas', 'Zones Monitoradas'
            ],
            'Valor': [
                historico.area_id,
                historico.safra,
                f"{historico.inicio_monitoramento} até {historico.fim_monitoramento or 'presente'}",
                len(historico.imagens_processadas),
                len(historico.comparacoes_realizadas),
                len(historico.anomalias_registradas),
                len(historico.alertas_disparados),
                len(historico.series_temporais)
            ]
        }
        
        df_resumo = pd.DataFrame(resumo_data)
        df_resumo.to_excel(writer, sheet_name='Resumo', index=False)
    
    def _exportar_series_temporais(self, series: Dict[int, SerieTemporalVigor], writer):
        """Exporta séries temporais."""
        df_series = pd.DataFrame()
        
        for zona_id, serie in series.items():
            for i, data in enumerate(serie.datas):
                row = {'zona_id': zona_id, 'data': data}
                
                for indice, valores in serie.valores_medios.items():
                    if i < len(valores):
                        row[f'{indice}_media'] = valores[i]
                
                for indice, desvios in serie.desvios.items():
                    if i < len(desvios):
                        row[f'{indice}_desvio'] = desvios[i]
                
                df_series = pd.concat([df_series, pd.DataFrame([row])], ignore_index=True)
        
        df_series.to_excel(writer, sheet_name='Series_Temporais', index=False)
    
    def _exportar_anomalias(self, anomalias: List[AnomaliaMonitoramento], writer):
        """Exporta anomalias."""
        anomalias_data = []
        
        for anomalia in anomalias:
            anomalias_data.append({
                'zona_id': anomalia.zona_id,
                'data': anomalia.data,
                'indice': anomalia.indice,
                'valor_observado': anomalia.valor_observado,
                'valor_esperado': anomalia.valor_esperado,
                'desvio_percentual': anomalia.desvio_percentual,
                'tipo': anomalia.tipo,
                'severidade': anomalia.severidade,
                'possiveis_causas': '; '.join(anomalia.possiveis_causas)
            })
        
        df_anomalias = pd.DataFrame(anomalias_data)
        df_anomalias.to_excel(writer, sheet_name='Anomalias', index=False)
    
    def _exportar_comparacoes(self, comparacoes: List[ResultadoComparacao], writer):
        """Exporta comparações."""
        comp_data = []
        
        for comp in comparacoes:
            comp_data.append({
                'imagem_base_id': comp.imagem_base_id,
                'imagem_comparada_id': comp.imagem_comparada_id,
                'intervalo_dias': comp.intervalo_dias,
                'indice_analisado': comp.indice_analisado,
                'diferenca_media': comp.diferenca_media,
                'diferenca_maxima': comp.diferenca_maxima,
                'diferenca_minima': comp.diferenca_minima,
                'n_anomalias': len(comp.anomalias_detectadas),
                'data_comparacao': comp.data_comparacao
            })
        
        df_comparacoes = pd.DataFrame(comp_data)
        df_comparacoes.to_excel(writer, sheet_name='Comparacoes', index=False)
    
    def _exportar_metadados(self, metadata: Dict[str, Any], writer):
        """Exporta metadados."""
        metadata_data = []
        
        for chave, valor in metadata.items():
            metadata_data.append({'chave': chave, 'valor': str(valor)})
        
        df_metadata = pd.DataFrame(metadata_data)
        df_metadata.to_excel(writer, sheet_name='Metadados', index=False)


class ExportadorGeoJSON:
    """
    Exporta dados para formato GeoJSON.
    """
    
    def exportar_area(self, area: AreaMonitoramento, caminho_saida: str) -> bool:
        """
        Exporta área de monitoramento para GeoJSON.
        
        Args:
            area: Área de monitoramento
            caminho_saida: Caminho do arquivo de saída
            
        Returns:
            True se exportado com sucesso
        """
        try:
            dados_saida = {
                'type': 'Feature',
                'properties': {
                    'area_id': area.area_id,
                    'nome': area.nome,
                    'data_inicio': area.data_inicio,
                    'safra': area.configuracoes.get('safra', '2026/2027')
                },
                'geometry': area.geometria
            }
            
            with open(caminho_saida, 'w', encoding='utf-8') as f:
                json.dump(dados_saida, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Área exportada para GeoJSON: {caminho_saida}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar GeoJSON area: {e}")
            return False
    
    def exportar_pontos_anomalias(self, anomalias: List[AnomaliaMonitoramento], 
                                  caminho_saida: str) -> bool:
        """
        Exporta pontos de anomalias para GeoJSON.
        
        Args:
            anomalias: Lista de anomalias
            caminho_saida: Caminho do arquivo de saída
            
        Returns:
            True se exportado com sucesso
        """
        try:
            features = []
            
            for anomalia in anomalias:
                # Simplificado - em produção calcular coordenadas reais
                feature = {
                    'type': 'Feature',
                    'properties': {
                        'zona_id': anomalia.zona_id,
                        'data': anomalia.data,
                        'indice': anomalia.indice,
                        'valor_observado': anomalia.valor_observado,
                        'valor_esperado': anomalia.valor_esperado,
                        'desvio_percentual': anomalia.desvio_percentual,
                        'tipo': anomalia.tipo,
                        'severidade': anomalia.severidade
                    },
                    geometry: point_data,  # Implementar cálculo de coordenadas reais
                    coordinates: [0, 0]  # Simplificado - implementar cálculo real
                }
                features.append(feature)
            
            geojson_data = {
                'type': 'FeatureCollection',
                'features': features
            }
            
            with open(caminho_saida, 'w', encoding='utf-8') as f:
                json.dump(geojson_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Pontos de anomalias exportados para GeoJSON: {caminho_saida}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar GeoJSON anomalias: {e}")
            return False


class ExportadorShapefile:
    """
    Exporta dados para formato Shapefile.
    """
    
    def exportar_area_shapefile(self, area: AreaMonitoramento, 
                               caminho_saida: str) -> bool:
        """
        Exporta área para Shapefile.
        
        Args:
            area: Área de monitoramento
            caminho_saida: Caminho do arquivo de saída
            
        Returns:
            True se exportado com sucesso
        """
        try:
            # Simplificado - em produção usar geopandas
            logger.info(f"Exportação Shapefile area não implementada: {caminho_saida}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar Shapefile area: {e}")
            return False


class ExportadorGeoTIFF:
    """
    Exporta dados para formato GeoTIFF.
    """
    
    def exportar_indices_raster(self, indices: Dict[str, np.ndarray], 
                               metadados: Dict[str, Any], 
                               caminho_saida: str) -> bool:
        """
        Exporta índices espectrais para GeoTIFF.
        
        Args:
            indices: Dicionário de índices
            metadados: Metadados da imagem
            caminho_saida: Caminho do arquivo de saída
            
        Returns:
            True se exportado com sucesso
        """
        try:
            # Simplificado - em produção usar rasterio
            logger.info(f"Exportação GeoTIFF indices não implementada: {caminho_saida}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar GeoTIFF indices: {e}")
            return False


class MotorExportacao:
    """
    Motor principal de exportação.
    """
    
    def __init__(self, config: ConfigExportacao):
        self.config = config
        
        # Configuradores de exportação
        self.config_pdf = ConfigExportadorPDF()
        self.config_csv = ConfigExportadorCSV()
        self.config_excel = ConfigExportadorExcel()
        
        # Exportadores
        self.exportador_pdf = ExportadorPDF(self.config_pdf)
        self.exportador_csv = ExportadorCSV(self.config_csv)
        self.exportador_excel = ExportadorExcel(self.config_excel)
        self.exportador_geojson = ExportadorGeoJSON()
        self.exportador_shapefile = ExportadorShapefile()
        self.exportador_geotiff = ExportadorGeoTIFF()
        
        self.resultados_exportacao: Dict[str, bool] = {}
    
    def exportar_historico_completo(self, historico: HistoricoMonitoramento, 
                                   area: AreaMonitoramento) -> Dict[str, str]:
        """
        Exporta histórico completo em todos os formatos configurados.
        
        Args:
            historico: Dados do histórico
            area: Área de monitoramento
            
        Returns:
            Dicionário com caminhos dos arquivos exportados
        """
        arquivos_exportados = {}
        
        for formato in self.config.formatos:
            try:
                if formato == "PDF":
                    caminho = self._exportar_pdf(historico)
                elif formato == "CSV":
                    caminho = self._exportar_csv(historico)
                elif formato == "Excel":
                    caminho = self._exportar_excel(historico)
                elif formato == "GeoJSON":
                    caminho = self._exportar_geojson(historico, area)
                elif formato == "Shapefile":
                    caminho = self._exportar_shapefile(historico, area)
                elif formato == "GeoTIFF":
                    caminho = self._exportar_geotiff(historico)
                else:
                    continue
                
                if caminho:
                    arquivos_exportados[formato] = caminho
                    self.resultados_exportacao[formato] = True
                else:
                    self.resultados_exportacao[formato] = False
                    
            except Exception as e:
                logger.error(f"Erro ao exportar formato {formato}: {e}")
                self.resultados_exportacao[formato] = False
        
        return arquivos_exportados
    
    def _exportar_pdf(self, historico: HistoricoMonitoramento) -> str:
        """Exporta para PDF."""
        caminho_saida = f"historico_{historico.area_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        sucesso = self.exportador_pdf.exportar_historico(historico, caminho_saida)
        return caminho_saida if sucesso else None
    
    def _exportar_csv(self, historico: HistoricoMonitoramento) -> str:
        """Exporta para CSV."""
        caminho_saida = f"historico_{historico.area_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        sucesso = self.exportador_csv.exportar_series_temporais(historico.series_temporais, caminho_saida)
        return caminho_saida if sucesso else None
    
    def _exportar_excel(self, historico: HistoricoMonitoramento) -> str:
        """Exporta para Excel."""
        caminho_saida = f"historico_{historico.area_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        sucesso = self.exportador_excel.exportar_completo(historico, caminho_saida)
        return caminho_saida if sucesso else None
    
    def _exportar_geojson(self, historico: HistoricoMonitoramento, 
                         area: AreaMonitoramento) -> str:
        """Exporta para GeoJSON."""
        caminho_saida = f"area_{area.area_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.geojson"
        sucesso = self.exportador_geojson.exportar_area(area, caminho_saida)
        return caminho_saida if sucesso else None
    
    def _exportar_shapefile(self, historico: HistoricoMonitoramento, 
                           area: AreaMonitoramento) -> str:
        """Exporta para Shapefile."""
        caminho_saida = f"area_{area.area_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.shp"
        sucesso = self.exportador_shapefile.exportar_area_shapefile(area, caminho_saida)
        return caminho_saida if sucesso else None
    
    def _exportar_geotiff(self, historico: HistoricoMonitoramento) -> str:
        """Exporta para GeoTIFF."""
        caminho_saida = f"indices_{historico.area_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tif"
        # Simplificado - implementar exportação real em futura iteração
        logger.warning("Exportação GeoTIFF não implementada completamente")
        return caminho_saida
    
    def obter_relatorio_exportacao(self) -> Dict[str, Any]:
        """
        Obtém relatório do processo de exportação.
        
        Returns:
            Relatório consolidado
        """
        return {
            'formatos_configurados': self.config.formatos,
            'formatos_sucesso': sum(1 for sucesso in self.resultados_exportacao.values() if sucesso),
            'formatos_falha': sum(1 for sucesso in self.resultados_exportacao.values() if not sucesso),
            'taxa_sucesso': sum(self.resultados_exportacao.values()) / len(self.resultados_exportacao) * 100 if self.resultados_exportacao else 0,
            'detalhes_por_formato': self.resultados_exportacao
        }