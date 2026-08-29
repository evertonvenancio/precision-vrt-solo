"""
Precision VRT Solo — Motor de Exportação de Nematoides

Exporta resultados de análise de nematoides em múltiplos formatos
para diferentes dispositivos e sistemas.
"""

import json
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import tempfile
import logging
import pandas as pd

from ...tipos.base import ConfigBase, ResultadoBase
from ..nematoides.contratos import (
    ResultadoNematoides,
    ResultadoInterpolacaoNematoides,
    ResultadoZoneamentoNematoides,
    ZonaRiscoNematoides,
    PontoAmostraNematoides,
    NivelRiscoNematoides
)


@dataclass
class ConfigExportacaoNematoides(ConfigBase):
    """Configuração para exportação de resultados de nematoides."""
    formatos: List[str] = field(default_factory=list)
    incluir_amostras_individuais: bool = True
    incluir_estatisticas: bool = True
    incluir_recomendacoes: bool = True
    incluir_mapas: bool = True
    diretorio_saida: str = "./exportados_nematoides"


class MotorExportacaoNematoides:
    """
    Motor de exportação específico para nematoides.
    
    Exporta resultados em múltiplos formatos padrão, sem criar
    exportações específicas para fabricantes.
    """
    
    def __init__(self, config: ConfigExportacaoNematoides):
        self.config = config
        self.temp_dir = tempfile.mkdtemp(prefix="exportacao_nematoides_")
        self.logger = logging.getLogger(__name__)
    
    def exportar(self, resultado: ResultadoNematoides) -> Dict[str, str]:
        """
        Exporta resultados em todos os formatos configurados.
        
        Args:
            resultado: Resultado completo da análise de nematoides
            
        Returns:
            Dicionário com formatos e caminhos dos arquivos exportados
        """
        arquivos_exportados = {}
        
        for formato in self.config.formatos:
            try:
                caminho_arquivo = self._exportar_formato(resultado, formato)
                if caminho_arquivo:
                    arquivos_exportados[formato] = caminho_arquivo
                    self.logger.info(f"Exportado {formato}: {caminho_arquivo}")
            except Exception as e:
                self.logger.error(f"Erro ao exportar {formato}: {e}")
        
        # Limpar diretório temporário
        self._limpar_temporario()
        
        return arquivos_exportados
    
    def _exportar_formato(self, resultado: ResultadoNematoides, formato: str) -> Optional[str]:
        """Exporta em um formato específico."""
        if formato.lower() == "pdf":
            return self._exportar_pdf(resultado)
        elif formato.lower() == "csv":
            return self._exportar_csv(resultado)
        elif formato.lower() in ["excel", "xlsx"]:
            return self._exportar_excel(resultado)
        elif formato.lower() == "geojson":
            return self._exportar_geojson(resultado)
        elif formato.lower() == "shapefile":
            return self._exportar_shapefile(resultado)
        elif formato.lower() == "geotiff":
            return self._exportar_geotiff(resultado)
        elif formato.lower() == "isoxml":
            return self._exportar_isoxml(resultado)
        else:
            self.logger.warning(f"Formato não suportado: {formato}")
            return None
    
    def _exportar_pdf(self, resultado: ResultadoNematoides) -> str:
        """Exporta resultados em formato PDF."""
        # Estrutura básica do PDF
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_pdf = f"{self.temp_dir}/resultado_nematoides_{timestamp}.pdf"
        
        # Criar conteúdo do PDF
        conteudo_pdf = self._gerar_conteudo_pdf(resultado)
        
        # Em um ambiente real, usaríamos bibliotecas como reportlab ou weasyprint
        # Por enquanto, criar um arquivo de texto como placeholder
        with open(caminho_pdf.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
            f.write(conteudo_pdf)
        
        # Placeholder - em produção gerar PDF real
        return caminho_pdf.replace('.pdf', '.txt')
    
    def _gerar_conteudo_pdf(self, resultado: ResultadoNematoides) -> str:
        """Gera conteúdo para exportação PDF."""
        conteudo = f"""
RELATÓRIO DE ANÁLISE DE NEMATOIDES
===================================

Data da Análise: {resultado.timestamp}
Cultura: Milho (padrão)
Área Total Analisada: {resultado.area_total_analisada:.2f} hectares
Risco Global: {resultado.risco_global.value}

RESUMO ESTATÍSTICO
------------------
Total de Amostras: {len(resultado.resultado_interpolacao.pontos_originais)}
Número de Zonas: {len(resultado.resultado_zoneamento.zonas_risco)}
Custo Estimado Tratamento: R$ {resultado.custo_estimado_tratamento:.2f}

ZONAS DE RISCO
--------------
"""
        
        for zona in resultado.resultado_zoneamento.zonas_risco:
            conteudo += f"""
Zona {zona.zona_id}:
  - Risco: {zona.risco_classificacao.value}
  - População Média: {zona.populacao_media:.2f} nematoides/100g
  - População Máxima: {zona.populacao_maxima:.2f} nematoides/100g
  - Área: {zona.area_hectares:.2f} hectares
  - Prioridade: {zona.prioridade_acao}
  - Recomendação: {zona.recomendacao_manejo}

"""
        
        conteudo += """
RECOMENDAÇÕES GERAIS
-------------------
"""
        
        for rec in resultado.recomendacoes_gerais:
            conteudo += f"- {rec}\n"
        
        return conteudo
    
    def _exportar_csv(self, resultado: ResultadoNematoides) -> str:
        """Exporta resultados em formato CSV."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_csv = f"{self.temp_dir}/resultado_nematoides_{timestamp}.csv"
        
        dados_exportar = []
        
        # Exportar dados das zonas
        for zona in resultado.resultado_zoneamento.zonas_risco:
            dados_exportar.append({
                "tipo": "zona_risco",
                "zona_id": zona.zona_id,
                "risco_classificacao": zona.risco_classificacao.value,
                "populacao_media": zona.populacao_media,
                "populacao_maxima": zona.populacao_maxima,
                "area_hectares": zona.area_hectares,
                "prioridade_acao": zona.prioridade_acao,
                "recomendacao_manejo": zona.recomendacao_manejo,
                "generos_detectados": ",".join([g.value for g in zona.generos_detectados])
            })
        
        # Exportar amostras individuais
        if self.config.incluir_amostras_individuais:
            for amostra in resultado.resultado_interpolacao.pontos_originais:
                dados_exportar.append({
                    "tipo": "amostra_individual",
                    "ponto_id": amostra.ponto_id,
                    "latitude": amostra.coordenada.y,
                    "longitude": amostra.coordenada.x,
                    "profundidade_cm": amostra.profundidade_cm,
                    "populacao_nematoides_100g_solo": amostra.populacao_nematoides_100g_solo,
                    "especie_predominante": amostra.especie_predominante.value,
                    "observacoes": amostra.observacoes,
                    "risco_classificacao": self._classificar_risco_amostra(amostra.populacao_nematoides_100g_solo)
                })
        
        # Exportar estatísticas gerais
        if self.config.incluir_estatisticas:
            dados_exportar.append({
                "tipo": "estatisticas_gerais",
                "risco_global": resultado.risco_global.value,
                "area_total_analisada": resultado.area_total_analisada,
                "custo_estimado_tratamento": resultado.custo_estimado_tratamento,
                "n_amostras": len(resultado.resultado_interpolacao.pontos_originais),
                "n_zonas": len(resultado.resultado_zoneamento.zonas_risco)
            })
        
        # Criar DataFrame e exportar
        df = pd.DataFrame(dados_exportar)
        df.to_csv(caminho_csv, index=False, sep=';', decimal=',')
        
        return caminho_csv
    
    def _exportar_excel(self, resultado: ResultadoNematoides) -> str:
        """Exporta resultados em formato Excel."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_excel = f"{self.temp_dir}/resultado_nematoides_{timestamp}.xlsx"
        
        # Criar writer do Excel
        with pd.ExcelWriter(caminho_excel, engine='openpyxl') as writer:
            # Planilha de resumo
            dados_resumo = [{
                'Métrica': 'Risco Global',
                'Valor': resultado.risco_global.value
            }, {
                'Métrica': 'Área Total Analisada (ha)',
                'Valor': resultado.area_total_analisada
            }, {
                'Métrica': 'Custo Estimado Tratamento (R$)',
                'Valor': resultado.custo_estimado_tratamento
            }, {
                'Métrica': 'Total de Amostras',
                'Valor': len(resultado.resultado_interpolacao.pontos_originais)
            }, {
                'Métrica': 'Número de Zonas',
                'Valor': len(resultado.resultado_zoneamento.zonas_risco)
            }]
            
            df_resumo = pd.DataFrame(dados_resumo)
            df_resumo.to_excel(writer, sheet_name='Resumo', index=False)
            
            # Planilha de zonas de risco
            dados_zonas = []
            for zona in resultado.resultado_zoneamento.zonas_risco:
                dados_zonas.append({
                    'Zona ID': zona.zona_id,
                    'Risco': zona.risco_classificacao.value,
                    'População Média': zona.populacao_media,
                    'População Máxima': zona.populacao_maxima,
                    'Área (ha)': zona.area_hectares,
                    'Prioridade': zona.prioridade_acao,
                    'Recomendação': zona.recomendacao_manejo,
                    'Espécies Detectadas': ', '.join([g.value for g in zona.generos_detectados])
                })
            
            df_zonas = pd.DataFrame(dados_zonas)
            df_zonas.to_excel(writer, sheet_name='Zonas de Risco', index=False)
            
            # Planilha de amostras
            if self.config.incluir_amostras_individuais:
                dados_amostras = []
                for amostra in resultado.resultado_interpolacao.pontos_originais:
                    dados_amostras.append({
                        'Ponto ID': amostra.ponto_id,
                        'Latitude': amostra.coordenada.y,
                        'Longitude': amostra.coordenada.x,
                        'Profundidade (cm)': amostra.profundidade_cm,
                        'População (nem/100g)': amostra.populacao_nematoides_100g_solo,
                        'Espécie Predominante': amostra.especie_predominante.value,
                        'Observações': amostra.observacoes
                    })
                
                df_amostras = pd.DataFrame(dados_amostras)
                df_amostras.to_excel(writer, sheet_name='Amostras Individuais', index=False)
            
            # Planilha de recomendações
            if self.config.incluir_recomendacoes:
                dados_recomendacoes = [{'Recomendação': rec} for rec in resultado.recomendacoes_gerais]
                df_recomendacoes = pd.DataFrame(dados_recomendacoes)
                df_recomendacoes.to_excel(writer, sheet_name='Recomendações', index=False)
        
        return caminho_excel
    
    def _exportar_geojson(self, resultado: ResultadoNematoides) -> str:
        """Exporta resultados em formato GeoJSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_geojson = f"{self.temp_dir}/resultado_nematoides_{timestamp}.geojson"
        
        geojson_data = {
            "type": "FeatureCollection",
            "features": []
        }
        
        # Exportar zonas de risco como features
        for zona in resultado.resultado_zoneamento.zonas_risco:
            # Criar geometria simplificada (ponto no centroide)
            feature = {
                "type": "Feature",
                "properties": {
                    "zona_id": zona.zona_id,
                    "risco_classificacao": zona.risco_classificacao.value,
                    "populacao_media": zona.populacao_media,
                    "populacao_maxima": zona.populacao_maxima,
                    "area_hectares": zona.area_hectares,
                    "prioridade_acao": zona.prioridade_acao,
                    "recomendacao_manejo": zona.recomendacao_manejo,
                    "generos_detectados": [g.value for g in zona.generos_detectados]
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [0, 0]  # Placeholder - em produção usar coordenadas reais
                }
            }
            
            geojson_data["features"].append(feature)
        
        # Exportar amostras individuais
        if self.config.incluir_amostras_individuais:
            for amostra in resultado.resultado_interpolacao.pontos_originais:
                feature = {
                    "type": "Feature",
                    "properties": {
                        "ponto_id": amostra.ponto_id,
                        "profundidade_cm": amostra.profundidade_cm,
                        "populacao_nematoides_100g_solo": amostra.populacao_nematoides_100g_solo,
                        "especie_predominante": amostra.especie_predominante.value,
                        "observacoes": amostra.observacoes,
                        "risco_classificacao": self._classificar_risco_amostra(amostra.populacao_nematoides_100g_solo)
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [amostra.coordenada.x, amostra.coordenada.y]
                    }
                }
                
                geojson_data["features"].append(feature)
        
        # Salvar GeoJSON
        with open(caminho_geojson, 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f, indent=2, ensure_ascii=False)
        
        return caminho_geojson
    
    def _exportar_shapefile(self, resultado: ResultadoNematoides) -> str:
        """Exporta resultados em formato Shapefile."""
        # Shapefile requer bibliotecas como geopandas ou fiona
        # Por enquanto, criar placeholder GeoJSON
        return self._exportar_geojson(resultado)
    
    def _exportar_geotiff(self, resultado: ResultadoNematoides) -> str:
        """Exporta resultados em formato GeoTIFF."""
        # GeoTIFF requer bibliotecas como rasterio ou gdal
        # Por enquanto, criar placeholder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_geotiff = f"{self.temp_dir}/resultado_nematoides_{timestamp}.tiff"
        
        # Criar arquivo de texto como placeholder
        with open(caminho_geotiff, 'w') as f:
            f.write("GeoTIFF placeholder para análise de nematoides")
        
        return caminho_geotiff
    
    def _exportar_isoxml(self, resultado: ResultadoNematoides) -> str:
        """Exporta resultados em formato ISOXML."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_isoxml = f"{self.temp_dir}/resultado_nematoides_{timestamp}.isoxml"
        
        # Criar estrutura XML básica
        root = ET.Element("isoXML")
        root.set("version", "1.0")
        
        # Adicionar informações básicas
        info = ET.SubElement(root, "Informacoes")
        ET.SubElement(info, "DataAnalise").text = resultado.timestamp.isoformat()
        ET.SubElement(info, "Cultura").text = "milho"
        ET.SubElement(info, "AreaTotal").text = str(resultado.area_total_analisada)
        
        # Adicionar zonas
        zonas = ET.SubElement(root, "ZonasRisco")
        for zona in resultado.resultado_zoneamento.zonas_risco:
            zona_elem = ET.SubElement(zonas, "Zona")
            zona_elem.set("id", str(zona.zona_id))
            ET.SubElement(zona_elem, "Risco").text = zona.risco_classificacao.value
            ET.SubElement(zona_elem, "PopulacaoMedia").text = str(zona.populacao_media)
            ET.SubElement(zona_elem, "PopulacaoMaxima").text = str(zona.populacao_maxima)
            ET.SubElement(zona_elem, "Area").text = str(zona.area_hectares)
            ET.SubElement(zona_elem, "Recomendacao").text = zona.recomendacao_manejo
        
        # Salvar XML
        tree = ET.ElementTree(root)
        tree.write(caminho_isoxml, encoding='utf-8', xml_declaration=True)
        
        return caminho_isoxml
    
    def _classificar_risco_amostra(self, populacao: float) -> str:
        """Classifica risco de uma amostra individual."""
        from ..nematoides.motor import MotorNematoides
        motor = MotorNematoides()
        return motor.classificar_risco(populacao).value
    
    def _limpar_temporario(self):
        """Limpa diretório temporário."""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            self.logger.warning(f"Não foi possível limpar diretório temporário: {e}")