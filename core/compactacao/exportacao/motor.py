"""
Precision VRT Solo — Motor de Exportação da Compactação

Exporta resultados de análise de compactação em múltiplos formatos
para diferentes dispositivos e sistemas.
"""

import json
import csv
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime
import tempfile
import os

from ...tipos.base import ConfigBase, ResultadoBase
from ..compactacao.contratos import (
    PerfilCompactacao, 
    ResultadoZoneamentoCompactacao,
    ClassificacaoSolo
)
from ..interpolacao.motor import ResultadoInterpolacaoCompactacao
from ..zoneamento.motor import ZonaCompactacao


@dataclass
class ConfigExportacaoCompactacao(ConfigBase):
    """Configuração para exportação de compactação."""
    
    # Formatos de exportação suportados
    formatos_suportados: List[str] = field(default_factory=list)
    
    # Configurações específicas por formato
    pdf_config: Dict[str, Any] = field(default_factory=dict)
    excel_config: Dict[str, Any] = field(default_factory=dict)
    shapefile_config: Dict[str, Any] = field(default_factory=dict)
    
    # Metadados da exportação
    incluir_metadados: bool = True
    incluir_graficos: bool = True
    incluir_mapas: bool = True
    
    def __post_init__(self):
        """Valida configuração."""
        for formato in self.formatos_suportados:
            if formato not in ["PDF", "CSV", "Excel", "GeoJSON", "Shapefile", "GeoTIFF", "ISOXML"]:
                raise ValueError(f"Formato não suportado: {formato}")


@dataclass
class ResultadoExportacaoCompactacao:
    """Resultado da exportação de compactação."""
    
    # Campos obrigatórios primeiro
    arquivos_exportados: Dict[str, str]  # formato -> caminho_arquivo
    metadados_exportacao: Dict[str, Any]
    tamanho_total_bytes: int
    formatos_suportados: List[str]
    
    # Campos opcionais
    timestamp: datetime = field(default_factory=datetime.now)
    tempo_execucao_ms: float = 0.0
    config: Optional[ConfigBase] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte resultado para dicionário serializável."""
        return {
            "arquivos_exportados": self.arquivos_exportados,
            "metadados_exportacao": self.metadados_exportacao,
            "tamanho_total_bytes": self.tamanho_total_bytes,
            "formatos_suportados": self.formatos_suportados,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "tempo_execucao_ms": self.tempo_execucao_ms
        }


class MotorExportacaoCompactacao:
    """
    Motor de exportação específico para compactação do solo.
    
    Exporta resultados em múltiplos formatos padrão, sem criar
    exportações específicas para fabricantes.
    """
    
    def __init__(self, config: ConfigExportacaoCompactacao):
        self.config = config
        self.temp_dir = tempfile.mkdtemp(prefix="exportacao_compactacao_")
    
    def exportar(self, 
                perfis: List[PerfilCompactacao],
                resultado_zoneamento: Optional[ResultadoZoneamentoCompactacao] = None,
                resultado_interpolacao: Optional[ResultadoInterpolacaoCompactacao] = None,
                formatos: Optional[List[str]] = None) -> ResultadoExportacaoCompactacao:
        """
        Exporta dados de compactação nos formatos especificados.
        
        Args:
            perfis: Lista de perfis de compactação
            resultado_zoneamento: Resultado do zoneamento (opcional)
            resultado_interpolacao: Resultado da interpolação (opcional)
            formatos: Formatos para exportar. None = todos os suportados
            
        Returns:
            Resultado com informações dos arquivos exportados
        """
        if formatos is None:
            formatos = self.config.formatos_suportados
        
        arquivos_exportados = {}
        metadados_exportacao = {
            "total_perfis": len(perfis),
            "total_pontos": sum(len(p.ponto_id) for p in perfis),
            "data_exportacao": datetime.now().isoformat(),
            "formatos_solicitados": formatos
        }
        
        # Adicionar metadados do zoneamento, se existir
        if resultado_zoneamento:
            metadados_exportacao.update({
                "total_zonas": len(resultado_zoneamento.zonas),
                "classificacao_predominante": resultado_zoneamento.classificacao_predominante,
                "percentual_impedimento": resultado_zoneamento.percentual_impedimento,
                "percentual_restricao": resultado_zoneamento.percentual_restricao,
                "percentual_apto": resultado_zoneamento.percentual_apto
            })
        
        tamanho_total = 0
        
        for formato in formatos:
            try:
                if formato == "PDF":
                    arquivo_pdf = self._exportar_pdf(perfis, resultado_zoneamento)
                    arquivos_exportados["PDF"] = arquivo_pdf
                    tamanho_total += os.path.getsize(arquivo_pdf)
                
                elif formato == "CSV":
                    arquivo_csv = self._exportar_csv(perfis)
                    arquivos_exportados["CSV"] = arquivo_csv
                    tamanho_total += os.path.getsize(arquivo_csv)
                
                elif formato == "Excel":
                    arquivo_excel = self._exportar_excel(perfis, resultado_zoneamento)
                    arquivos_exportados["Excel"] = arquivo_excel
                    tamanho_total += os.path.getsize(arquivo_excel)
                
                elif formato == "GeoJSON":
                    arquivo_geojson = self._exportar_geojson(perfis, resultado_zoneamento)
                    arquivos_exportados["GeoJSON"] = arquivo_geojson
                    tamanho_total += os.path.getsize(arquivo_geojson)
                
                elif formato == "Shapefile":
                    arquivo_shapefile = self._exportar_shapefile(perfis, resultado_zoneamento)
                    arquivos_exportados["Shapefile"] = arquivo_shapefile
                    tamanho_total += os.path.getsize(arquivo_shapefile)
                
                elif formato == "GeoTIFF":
                    arquivo_geotiff = self._exportar_geotiff(resultado_interpolacao)
                    arquivos_exportados["GeoTIFF"] = arquivo_geotiff
                    tamanho_total += os.path.getsize(arquivo_geotiff)
                
                elif formato == "ISOXML":
                    arquivo_isoxml = self._exportar_isoxml(perfis, resultado_zoneamento)
                    arquivos_exportados["ISOXML"] = arquivo_isoxml
                    tamanho_total += os.path.getsize(arquivo_isoxml)
                
            except Exception as e:
                print(f"Erro ao exportar em formato {formato}: {e}")
                continue
        
        return ResultadoExportacaoCompactacao(
            timestamp=datetime.now(),
            tempo_execucao_ms=0.0,  # Será calculado externamente
            config=self.config,
            arquivos_exportados=arquivos_exportados,
            metadados_exportacao=metadados_exportacao,
            tamanho_total_bytes=tamanho_total,
            formatos_suportados=formatos
        )
    
    def _exportar_pdf(self, perfis: List[PerfilCompactacao], 
                     resultado_zoneamento: Optional[ResultadoZoneamentoCompactacao]) -> str:
        """Exporta dados em formato PDF."""
        # Simplificado - implementação real usaria reportlab ou similar
        pdf_path = os.path.join(self.temp_dir, "relatorio_compactacao.pdf")
        
        # Criar conteúdo básico do PDF
        conteudo_pdf = {
            "titulo": "Relatório de Análise de Compactação do Solo",
            "data": datetime.now().strftime("%d/%m/%Y"),
            "perfis": len(perfis),
            "resumo": self._gerar_resumo_textual(perfis, resultado_zoneamento),
            "detalhes": [
                {
                    "ponto_id": p.ponto_id,
                    "classificacao": p.classificacao_geral,
                    "necessita_escarificacao": p.necessita_escarificacao,
                    "camadas": len(p.camadas)
                }
                for p in perfis[:10]  # Limitar para não exceder tamanho
            ]
        }
        
        # Salvar conteúdo (simulado)
        with open(pdf_path, "w", encoding="utf-8") as f:
            f.write(f"# {conteudo_pdf['titulo']}\n")
            f.write(f"Data: {conteudo_pdf['data']}\n")
            f.write(f"Total de Perfis: {conteudo_pdf['perfis']}\n\n")
            f.write("## Resumo\n")
            f.write(conteudo_pdf['resumo'] + "\n\n")
            f.write("## Detalhes\n")
            for detalhe in conteudo_pdf['detalhes']:
                f.write(f"- Ponto {detalhe['ponto_id']}: {detalhe['classificacao']}, "
                       f"Escarificação: {detalhe['necessita_escarificacao']}, "
                       f"Camadas: {detalhe['camadas']}\n")
        
        return pdf_path
    
    def _exportar_csv(self, perfis: List[PerfilCompactacao]) -> str:
        """Exporta dados em formato CSV."""
        csv_path = os.path.join(self.temp_dir, "dados_compactacao.csv")
        
        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            
            # Cabeçalho
            writer.writerow([
                "ponto_id", "latitude", "longitude", "classificacao_geral",
                "necessita_escarificacao", "profundidade_maxima_restricao",
                "numero_camadas"
            ])
            
            # Dados
            for perfil in perfis:
                writer.writerow([
                    perfil.ponto_id,
                    perfil.coordenada.latitude,
                    perfil.coordenada.longitude,
                    perfil.classificacao_geral,
                    perfil.necessita_escarificacao,
                    perfil.profundidade_maxima_restricao,
                    len(perfil.camadas)
                ])
        
        return csv_path
    
    def _exportar_excel(self, perfis: List[PerfilCompactacao], 
                       resultado_zoneamento: Optional[ResultadoZoneamentoCompactacao]) -> str:
        """Exporta dados em formato Excel."""
        excel_path = os.path.join(self.temp_dir, "dados_compactacao.xlsx")
        
        try:
            import pandas as pd
            
            # Criar DataFrame com perfis
            perfis_data = []
            for perfil in perfis:
                perfis_data.append({
                    "ponto_id": perfil.ponto_id,
                    "latitude": perfil.coordenada.latitude,
                    "longitude": perfil.coordenada.longitude,
                    "classificacao_geral": perfil.classificacao_geral,
                    "necessita_escarificacao": perfil.necessita_escarificacao,
                    "profundidade_maxima_restricao": perfil.profundidade_maxima_restricao,
                    "numero_camadas": len(perfil.camadas)
                })
            
            df_perfis = pd.DataFrame(perfis_data)
            
            # Criar Excel writer
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df_perfis.to_excel(writer, sheet_name='Perfis', index=False)
                
                # Adicionar sheet de resumo se houver zoneamento
                if resultado_zoneamento:
                    resumo_data = {
                        "Métrica": [
                            "Total de Zonas",
                            "Classificação Predominante",
                            "Percentual Impedimento",
                            "Percentual Restrição", 
                            "Percentual Apto",
                            "Recomendação Geral"
                        ],
                        "Valor": [
                            len(resultado_zoneamento.zonas),
                            resultado_zoneamento.classificacao_predominante,
                            f"{resultado_zoneamento.percentual_impedimento}%",
                            f"{resultado_zoneamento.percentual_restricao}%",
                            f"{resultado_zoneamento.percentual_apto}%",
                            resultado_zoneamento.recomendacao_geral
                        ]
                    }
                    df_resumo = pd.DataFrame(resumo_data)
                    df_resumo.to_excel(writer, sheet_name='Resumo', index=False)
        
        except ImportError:
            # Se pandas não estiver disponível, criar CSV como alternativa
            csv_path = os.path.join(self.temp_dir, "dados_compactacao.csv")
            self._exportar_csv(perfis)
            os.rename(csv_path, excel_path)
        
        return excel_path
    
    def _exportar_geojson(self, perfis: List[PerfilCompactacao], 
                         resultado_zoneamento: Optional[ResultadoZoneamentoCompactacao]) -> str:
        """Exporta dados em formato GeoJSON."""
        geojson_path = os.path.join(self.temp_dir, "dados_compactacao.geojson")
        
        # Criar estrutura GeoJSON
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        
        # Adicionar perfis como features
        for perfil in perfis:
            feature = {
                "type": "Feature",
                "properties": {
                    "ponto_id": perfil.ponto_id,
                    "classificacao_geral": perfil.classificacao_geral,
                    "necessita_escarificacao": perfil.necessita_escarificacao,
                    "profundidade_maxima_restricao": perfil.profundidade_maxima_restricao,
                    "numero_camadas": len(perfil.camadas)
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [perfil.coordenada.longitude, perfil.coordenada.latitude]
                }
            }
            geojson["features"].append(feature)
        
        # Adicionar zonas do zoneamento, se existir
        if resultado_zoneamento:
            for zona in resultado_zoneamento.zonas:
                # Criar polygon para a zona
                polygon_coords = zona.pontos[:10]  # Limitar para simplificar
                polygon_coords.append(polygon_coords[0])  # Fechar polygon
                
                feature_zona = {
                    "type": "Feature",
                    "properties": {
                        "zona_id": zona.id,
                        "classificacao_predominante": zona.classificacao_predominante,
                        "resistencia_media": zona.resistencia_media,
                        "area_ha": zona.area_ha,
                        "centroid_lon": zona.centroid_lon,
                        "centroid_lat": zona.centroid_lat
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [polygon_coords]
                    }
                }
                geojson["features"].append(feature_zona)
        
        # Salvar GeoJSON
        with open(geojson_path, "w", encoding="utf-8") as f:
            json.dump(geojson, f, indent=2, ensure_ascii=False)
        
        return geojson_path
    
    def _exportar_shapefile(self, perfis: List[PerfilCompactacao], 
                          resultado_zoneamento: Optional[ResultadoZoneamentoCompactacao]) -> str:
        """Exporta dados em formato Shapefile."""
        shapefile_path = os.path.join(self.temp_dir, "dados_compactacao.shp")
        
        try:
            import geopandas as gpd
            from shapely.geometry import Point, Polygon
            
            # Criar GeoDataFrame
            geometries = []
            properties = []
            
            # Adicionar perfis
            for perfil in perfis:
                point = Point(perfil.coordenada.longitude, perfil.coordenada.latitude)
                geometries.append(point)
                properties.append({
                    "ponto_id": perfil.ponto_id,
                    "classificacao_geral": perfil.classificacao_geral,
                    "necessita_escarificacao": perfil.necessita_escarificacao,
                    "profundidade_maxima_restricao": perfil.profundidade_maxima_restricao
                })
            
            # Adicionar zonas, se existir
            if resultado_zoneamento:
                for zona in resultado_zoneamento.zonas:
                    coords = zona.pontos[:10]  # Limitar
                    if len(coords) >= 3:
                        polygon = Polygon(coords)
                        geometries.append(polygon)
                        properties.append({
                            "zona_id": zona.id,
                            "classificacao_predominante": zona.classificacao_predominante,
                            "resistencia_media": zona.resistencia_media,
                            "area_ha": zona.area_ha
                        })
            
            # Criar GeoDataFrame e salvar
            gdf = gpd.GeoDataFrame(properties, geometry=geometries)
            gdf.to_file(shapefile_path)
            
        except ImportError:
            # Se geopandas não estiver disponível, criar GeoJSON como alternativa
            geojson_path = os.path.join(self.temp_dir, "dados_compactacao.geojson")
            self._exportar_geojson(perfis, resultado_zoneamento)
            os.rename(geojson_path, shapefile_path)
        
        return shapefile_path
    
    def _exportar_geotiff(self, resultado_interpolacao: Optional[ResultadoInterpolacaoCompactacao]) -> str:
        """Exporta dados em formato GeoTIFF."""
        geotiff_path = os.path.join(self.temp_dir, "interpolacao_compactacao.tif")
        
        if resultado_interpolacao is None:
            raise ValueError("Nenhum resultado de interpolação disponível para exportar como GeoTIFF")
        
        try:
            import rasterio
            from rasterio.transform import from_bounds
            
            # Obter informações da grade
            grade = resultado_interpolacao.grade_regular
            bounds = grade["bounds"]
            shape = grade["shape"]
            resolucao = grade["resolucao"]
            
            # Criar transformada
            transform = from_bounds(
                bounds.min_lon, bounds.min_lat, 
                bounds.max_lon, bounds.max_lat,
                shape[1], shape[0]  # colunas, linhas
            )
            
            # Criar e salvar GeoTIFF
            with rasterio.open(
                geotiff_path,
                'w',
                driver='GTiff',
                height=shape[0],
                width=shape[1],
                count=1,
                dtype=rasterio.float32,
                crs='EPSG:4326',
                transform=transform
            ) as dst:
                dst.write(resultado_interpolacao.valores_interpolados.astype(rasterio.float32), 1)
                
                # Adicionar metadados
                dst.update_tags(
                    description='Interpolação de Compactação do Solo',
                    units='MPa'
                )
        
        except ImportError:
            # Se rasterio não estiver disponível, criar arquivo simplificado
            with open(geotiff_path, "w") as f:
                f.write("# GeoTIFF simulado para interpolação de compactação\n")
                f.write(f"# Formato: {resultado_interpolacao.config.metodo}\n")
                f.write(f"# Resolução: {resultado_interpolacao.config.resolucao_grade}m\n")
                f.write(f"# Shape: {resultado_interpolacao.valores_interpolados.shape}\n")
                f.write(f"# Valores: min={np.min(resultado_interpolacao.valores_interpolados):.2f}, "
                       f"max={np.max(resultado_interpolacao.valores_interpolados):.2f}\n")
        
        return geotiff_path
    
    def _exportar_isoxml(self, perfis: List[PerfilCompactacao], 
                        resultado_zoneamento: Optional[ResultadoZoneamentoCompactacao]) -> str:
        """Exporta dados em formato ISOXML."""
        isoxml_path = os.path.join(self.temp_dir, "dados_compactacao.isoxml")
        
        # Criar estrutura XML simplificada compatível com ISOXML
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ISO11783_TaskData xmlns="http://www.isobus.org/schemas">
    <Header>
        <SoftwareName>Precision VRT Solo</SoftwareName>
        <Version>1.0</Version>
        <Timestamp>{timestamp}</Timestamp>
        <TotalPoints>{total_points}</TotalPoints>
    </Header>
    <Points>""".format(
            timestamp=datetime.now().isoformat(),
            total_points=len(perfis)
        )
        
        # Adicionar pontos
        for perfil in perfis:
            xml_content += f"""
        <Point>
            <ID>{perfil.ponto_id}</ID>
            <Position>
                <Longitude>{perfil.coordenada.longitude}</Longitude>
                <Latitude>{perfil.coordenada.latitude}</Latitude>
            </Position>
            <Classification>{perfil.classificacao_geral}</Classification>
            <ScarificationRequired>{perfil.necessita_escarificacao}</ScarificationRequired>
            <MaxRestrictionDepth>{perfil.profundidade_maxima_restricao or 0}</MaxRestrictionDepth>
            <LayerCount>{len(perfil.camadas)}</LayerCount>
        </Point>"""
        
        # Fechar estrutura XML
        xml_content += """
    </Points>
    <Recommendation>{recommendation}</Recommendation>
</ISO11783_TaskData>""".format(recommendation=resultado_zoneamento.recomendacao_geral if resultado_zoneamento else "Monitoramento recomendado")
        
        # Salvar XML
        with open(isoxml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        
        return isoxml_path
    
    def _gerar_resumo_textual(self, perfis: List[PerfilCompactacao], 
                            resultado_zoneamento: Optional[ResultadoZoneamentoCompactacao]) -> str:
        """Gera resumo textual para exportação."""
        total_perfis = len(perfis)
        perfis_escarificacao = sum(1 for p in perfis if p.necessita_escarificacao)
        
        resumo = f"Análise de {total_perfis} pontos de amostragem. "
        resumo += f"Perfis com necessidade de escarificação: {perfis_escarificacao}. "
        
        if resultado_zoneamento:
            resumo += f"Zoneamento identificou {len(resultado_zoneamento.zonas)} zonas. "
            resumo += f"Classificação predominante: {resultado_zoneamento.classificacao_predominante}. "
            resumo += f"Recomendação: {resultado_zoneamento.recomendacao_geral}"
        
        return resumo
    
    def limpar_temporarios(self):
        """Limpa arquivos temporários."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)