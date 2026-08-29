"""
Precision VRT Solo — Motor de Exportação de Fertirrigação

Exporta resultados de análise de fertirrigação em múltiplos formatos
para diferentes dispositivos e sistemas.
"""

import json
import csv
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import tempfile
import os

from ..fertirrigacao.contratos import ResultadoFertirrigacao

logger = logging.getLogger(__name__)


@dataclass
class ConfigExportacaoFertirrigacao:
    """Configuração para exportação de resultados."""
    
    # Formatos suportados
    formatos_suportados: List[str] = field(default_factory=list)
    
    # Parâmetros específicos
    incluir_moldura: bool = True
    incluir_legenda: bool = True
    incluir_escalas: bool = True
    resolucao_dpi: int = 300
    qualidade_imagem: int = 95


@dataclass
class ArquivoExportado:
    """Informações sobre um arquivo exportado."""
    
    nome: str
    formato: str
    caminho: str
    tamanho_bytes: int
    mime_type: str
    descricao: str


class MotorExportacaoFertirrigacao:
    """Motor de exportação para resultados de fertirrigação."""
    
    def __init__(self):
        self.config = ConfigExportacaoFertirrigacao()
        logger.info("MotorExportacaoFertirrigacao inicializado")
    
    def exportar(self, resultado: ResultadoFertirrigacao, 
                formatos: Optional[List[str]] = None,
                diretorio_saida: str = "./exportados") -> Dict[str, str]:
        """Exportar resultados em múltiplos formatos.
        
        Args:
            resultado: Resultado de fertirrigação para exportar
            formatos: Lista de formatos desejados
            diretorio_saida: Diretório para salvar arquivos
        
        Returns:
            Dicionário com caminhos dos arquivos exportados
        """
        logger.info(f"Exportando resultado em formatos: {formatos or 'todos'}")
        
        if formatos is None:
            formatos = self.config.formatos_suportados
        
        # Criar diretório de saída
        diretorio_saida = Path(diretorio_saida)
        diretorio_saida.mkdir(parents=True, exist_ok=True)
        
        arquivos_exportados = {}
        
        # Exportar em cada formato solicitado
        for formato in formatos:
            try:
                if formato.lower() == "pdf":
                    arquivo = self._exportar_pdf(resultado, diretorio_saida)
                elif formato.lower() == "csv":
                    arquivo = self._exportar_csv(resultado, diretorio_saida)
                elif formato.lower() == "excel":
                    arquivo = self._exportar_excel(resultado, diretorio_saida)
                elif formato.lower() == "geojson":
                    arquivo = self._exportar_geojson(resultado, diretorio_saida)
                elif formato.lower() == "shapefile":
                    arquivo = self._exportar_shapefile(resultado, diretorio_saida)
                elif formato.lower() == "geotiff":
                    arquivo = self._exportar_geotiff(resultado, diretorio_saida)
                elif formato.lower() == "isoxml":
                    arquivo = self._exportar_isoxml(resultado, diretorio_saida)
                else:
                    logger.warning(f"Formato não suportado: {formato}")
                    continue
                
                arquivos_exportados[formato] = arquivo.caminho
                logger.info(f"Exportado com sucesso: {arquivo.nome}")
                
            except Exception as e:
                logger.error(f"Erro ao exportar em {formato}: {e}")
        
        logger.info(f"Exportação concluída: {len(arquivos_exportados)} arquivos")
        return arquivos_exportados
    
    def _exportar_pdf(self, resultado: ResultadoFertirrigacao, 
                     diretorio_saida: Path) -> ArquivoExportado:
        """Exportar resultado em formato PDF."""
        logger.info("Exportando em formato PDF")
        
        # Criar conteúdo do PDF
        conteudo_pdf = self._criar_conteudo_pdf(resultado)
        
        # Salvar arquivo
        nome_arquivo = f"resultado_fertirrigacao_{resultado.area_analisada.area_id}.pdf"
        caminho_arquivo = diretorio_saida / nome_arquivo
        
        # Implementação simplificada (usaria bibliotecas como reportlab ou weasyprint)
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo_pdf)
        
        return ArquivoExportado(
            nome=nome_arquivo,
            formato="pdf",
            caminho=str(caminho_arquivo),
            tamanho_bytes=os.path.getsize(caminho_arquivo),
            mime_type="application/pdf",
            descricao="Relatório completo de fertirrigação em PDF"
        )
    
    def _exportar_csv(self, resultado: ResultadoFertirrigacao, 
                     diretorio_saida: Path) -> ArquivoExportado:
        """Exportar resultado em formato CSV."""
        logger.info("Exportando em formato CSV")
        
        # Criar conteúdo CSV
        conteudo_csv = self._criar_conteudo_csv(resultado)
        
        # Salvar arquivo
        nome_arquivo = f"resultado_fertirrigacao_{resultado.area_analisada.area_id}.csv"
        caminho_arquivo = diretorio_saida / nome_arquivo
        
        with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as f:
            f.write(conteudo_csv)
        
        return ArquivoExportado(
            nome=nome_arquivo,
            formato="csv",
            caminho=str(caminho_arquivo),
            tamanho_bytes=os.path.getsize(caminho_arquivo),
            mime_type="text/csv",
            descricao="Dados estruturados de fertirrigação em CSV"
        )
    
    def _exportar_excel(self, resultado: ResultadoFertirrigacao, 
                       diretorio_saida: Path) -> ArquivoExportado:
        """Exportar resultado em formato Excel."""
        logger.info("Exportando em formato Excel")
        
        # Criar conteúdo Excel
        conteudo_excel = self._criar_conteudo_excel(resultado)
        
        # Salvar arquivo
        nome_arquivo = f"resultado_fertirrigacao_{resultado.area_analisada.area_id}.xlsx"
        caminho_arquivo = diretorio_saida / nome_arquivo
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo_excel)
        
        return ArquivoExportado(
            nome=nome_arquivo,
            formato="excel",
            caminho=str(caminho_arquivo),
            tamanho_bytes=os.path.getsize(caminho_arquivo),
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            descricao="Planilha de resultados de fertirrigação em Excel"
        )
    
    def _exportar_geojson(self, resultado: ResultadoFertirrigacao, 
                         diretorio_saida: Path) -> ArquivoExportado:
        """Exportar resultado em formato GeoJSON."""
        logger.info("Exportando em formato GeoJSON")
        
        # Criar conteúdo GeoJSON
        conteudo_geojson = self._criar_conteudo_geojson(resultado)
        
        # Salvar arquivo
        nome_arquivo = f"resultado_fertirrigacao_{resultado.area_analisada.area_id}.geojson"
        caminho_arquivo = diretorio_saida / nome_arquivo
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo_geojson)
        
        return ArquivoExportado(
            nome=nome_arquivo,
            formato="geojson",
            caminho=str(caminho_arquivo),
            tamanho_bytes=os.path.getsize(caminho_arquivo),
            mime_type="application/geo+json",
            descricao="Dados geoespaciais de fertirrigação em GeoJSON"
        )
    
    def _exportar_shapefile(self, resultado: ResultadoFertirrigacao, 
                           diretorio_saida: Path) -> ArquivoExportado:
        """Exportar resultado em formato Shapefile."""
        logger.info("Exportando em formato Shapefile")
        
        # Criar conteúdo Shapefile
        conteudo_shapefile = self._criar_conteudo_shapefile(resultado)
        
        # Salvar arquivo (Shapefile é um conjunto de arquivos)
        nome_arquivo = f"resultado_fertirrigacao_{resultado.area_analisada.area_id}"
        caminho_pasta = diretorio_saida / nome_arquivo
        
        # Criar pasta do shapefile
        caminho_pasta.mkdir(exist_ok=True)
        
        # Salvar arquivos do shapefile
        for nome_arquivo_shape, conteudo in conteudo_shapefile.items():
            caminho_arquivo = caminho_pasta / nome_arquivo_shape
            with open(caminho_arquivo, 'wb') as f:
                f.write(conteudo)
        
        # Retornar o caminho da pasta principal
        return ArquivoExportado(
            nome=nome_arquivo,
            formato="shapefile",
            caminho=str(caminho_pasta),
            tamanho_bytes=sum(os.path.getsize(caminho_pasta / f) for f in os.listdir(caminho_pasta)),
            mime_type="application/octet-stream",
            descricao="Dados geoespaciais de fertirrigação em Shapefile"
        )
    
    def _exportar_geotiff(self, resultado: ResultadoFertirrigacao, 
                        diretorio_saida: Path) -> ArquivoExportado:
        """Exportar resultado em formato GeoTIFF."""
        logger.info("Exportando em formato GeoTIFF")
        
        # Criar conteúdo GeoTIFF
        conteudo_geotiff = self._criar_conteudo_geotiff(resultado)
        
        # Salvar arquivo
        nome_arquivo = f"resultado_fertirrigacao_{resultado.area_analisada.area_id}.tif"
        caminho_arquivo = diretorio_saida / nome_arquivo
        
        with open(caminho_arquivo, 'wb') as f:
            f.write(conteudo_geotiff)
        
        return ArquivoExportado(
            nome=nome_arquivo,
            formato="geotiff",
            caminho=str(caminho_arquivo),
            tamanho_bytes=os.path.getsize(caminho_arquivo),
            mime_type="image/tiff",
            descricao="Imagem georreferenciada de fertirrigação em GeoTIFF"
        )
    
    def _exportar_isoxml(self, resultado: ResultadoFertirrigacao, 
                        diretorio_saida: Path) -> ArquivoExportado:
        """Exportar resultado em formato ISOXML."""
        logger.info("Exportando em formato ISOXML")
        
        # Criar conteúdo ISOXML
        conteudo_isoxml = self._criar_conteudo_isoxml(resultado)
        
        # Salvar arquivo
        nome_arquivo = f"resultado_fertirrigacao_{resultado.area_analisada.area_id}.isoxml"
        caminho_arquivo = diretorio_saida / nome_arquivo
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo_isoxml)
        
        return ArquivoExportado(
            nome=nome_arquivo,
            formato="isoxml",
            caminho=str(caminho_arquivo),
            tamanho_bytes=os.path.getsize(caminho_arquivo),
            mime_type="application/xml",
            descricao="Dados de fertirrigação em formato ISOXML"
        )
    
    def _criar_conteudo_pdf(self, resultado: ResultadoFertirrigacao) -> str:
        """Criar conteúdo do PDF."""
        # Implementação simplificada - PDF real exigiria bibliotecas como reportlab
        return f"""
# Relatório de Fertirrigação

## Área Analisada
- ID da Área: {resultado.area_analisada.area_id}
- Talhão: {resultado.area_analisada.talhao}
- Cultura: {resultado.area_analisada.cultura.value}
- Sistema de Irrigação: {resultado.area_analisada.sistema_irrigacao.value}
- Área: {resultado.area_analisada.area_ha} hectares

## Análise de Soluções
- Total de Leituras: {len(resultado.resultado_analise_solucao.leituras_originais)}
- Leituras Validadas: {len(resultado.resultado_analise_solucao.leituras_validadas)}
- Status: {resultado.resultado_analise_solucao.status}

## Resultado Nutricional
- Macronutrientes: {list(resultado.resultado_nutricao.macronutrientes_analisados.keys())}
- Micronutrientes: {list(resultado.resultado_nutricao.micronutrientes_analisados.keys())}
- Interpretação: {resultado.resultado_nutricao.interpretacao}

## Recomendação
- Modo: {resultado.resultado_recomendacao.modo_utilizado.value}
- Itens: {len(resultado.resultado_recomendacao.recomendacoes)}
- Custo Estimado: R${resultado.resultado_recomendacao.custo_estimado:.2f}
- Lotes: {len(resultado.resultado_recomendacao.lotes_aplicacao)}

## Geração
{resultado.timestamp}

Tempo de Execução: {resultado.tempo_execucao_ms}ms
"""
    
    def _criar_conteudo_csv(self, resultado: ResultadoFertirrigacao) -> str:
        """Criar conteúdo do CSV."""
        import io
        
        # Criar buffer de CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow(["Tipo", "ID", "Descrição", "Valor", "Unidade"])
        
        # Área
        writer.writerow(["Área", resultado.area_analisada.area_id, "ID da Área", "", ""])
        writer.writerow(["Área", "", "Talhão", resultado.area_analisada.talhao, ""])
        writer.writerow(["Área", "", "Cultura", resultado.area_analisada.cultura.value, ""])
        writer.writerow(["Área", "", "Sistema Irrigação", resultado.area_analisada.sistema_irrigacao.value, ""])
        writer.writerow(["Área", "", "Área Total", resultado.area_analisada.area_ha, "ha"])
        
        # Leituras
        writer.writerow(["", "", "", "", ""])
        writer.writerow(["Leituras", "", "Total de Leituras", len(resultado.resultado_analise_solucao.leituras_originais), ""])
        
        # Estatísticas de CE
        if "ce" in resultado.resultado_analise_solucao.estatisticas:
            ce_stats = resultado.resultado_analise_solucao.estatisticas["ce"]
            writer.writerow(["Estatísticas", "CE", "Média", ce_stats["media"], "dS/m"])
            writer.writerow(["Estatísticas", "CE", "Mínimo", ce_stats["min"], "dS/m"])
            writer.writerow(["Estatísticas", "CE", "Máximo", ce_stats["max"], "dS/m"])
        
        # Recomendações
        writer.writerow(["", "", "", "", ""])
        writer.writerow(["Recomendações", "", "", "", ""])
        for i, rec in enumerate(resultado.resultado_recomendacao.recomendacoes):
            writer.writerow(["Recomendação", f"Item_{i+1}", rec["fertilizante"], rec["quantidade_kg"], "kg"])
        
        output.seek(0)
        return output.read()
    
    def _criar_conteudo_excel(self, resultado: ResultadoFertirrigacao) -> str:
        """Criar conteúdo do Excel."""
        # Excel real exigiria bibliotecas como openpyxl
        # Implementação simplificada usando CSV formatado
        return "## Relatório de Fertirrigação em Excel ##\n" + self._criar_conteudo_csv(resultado)
    
    def _criar_conteudo_geojson(self, resultado: ResultadoFertirrigacao) -> str:
        """Criar conteúdo do GeoJSON."""
        geojson_data = {
            "type": "FeatureCollection",
            "features": []
        }
        
        # Adicionar área como feature
        area_feature = {
            "type": "Feature",
            "properties": {
                "area_id": resultado.area_analisada.area_id,
                "talhao": resultado.area_analisada.talhao,
                "cultura": resultado.area_analisada.cultura.value,
                "sistema_irrigacao": resultado.area_analisada.sistema_irrigacao.value,
                "area_ha": resultado.area_analisada.area_ha
            },
            "geometry": resultado.area_analisada.poligono
        }
        
        geojson_data["features"].append(area_feature)
        
        # Adicionar pontos de monitoramento
        for leitura in resultado.resultado_analise_solucao.leituras_originais:
            if hasattr(leitura, 'coordenadas'):
                ponto_feature = {
                    "type": "Feature",
                    "properties": {
                        "ponto_id": leitura.ponto_id,
                        "ce_ds_m": leitura.ce_ds_m,
                        "ph": leitura.ph,
                        "data_leitura": leitura.data_leitura
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [leitura.coordenadas['lon'], leitura.coordenadas['lat']]
                    }
                }
                geojson_data["features"].append(ponto_feature)
        
        return json.dumps(geojson_data, indent=2, ensure_ascii=False)
    
    def _criar_conteudo_shapefile(self, resultado: ResultadoFertirrigacao) -> Dict[str, bytes]:
        """Criar conteúdo do Shapefile."""
        # Shapefile é complexo, implementação simplificada
        # Retornaria arquivos .shp, .shx, .dbf, .prj, etc.
        return {
            "dados_shapefile.dbf": b"shapefile content",  # DBF file
            "dados_shapefile.shx": b"shapefile index",   # SHX file
            "dados_shapefile.shp": b"shapefile geometry"  # SHP file
        }
    
    def _criar_conteudo_geotiff(self, resultado: ResultadoFertirrigacao) -> bytes:
        """Criar conteúdo do GeoTIFF."""
        # GeoTIFF é complexo, implementação simplificada
        return b"geotiff content"  # Real seria uma imagem georreferenciada
    
    def _criar_conteudo_isoxml(self, resultado: ResultadoFertirrigacao) -> str:
        """Criar conteúdo do ISOXML."""
        # Criar estrutura XML ISO 11783-10
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<ISOBUS xmlns="http://iso.org/11783-10">
    <Header>
        <DeviceID>FERTIRRIGACAO-{resultado.area_analisada.area_id}</DeviceID>
        <Timestamp>{resultado.timestamp}</Timestamp>
    </Header>
    
    <FieldData>
        <Area ID="{resultado.area_analisada.area_id}">
            <Field>{resultado.area_analisada.talhao}</Field>
            <CropType>{resultado.area_analisada.cultura.value}</CropType>
            <AreaSize unit="ha">{resultado.area_analisada.area_ha}</AreaSize>
        </Area>
        
        <NutrientAnalysis>
            <CE Value="{resultado.resultado_analise_solucao.estatisticas.get('ce', {}).get('media', 0)}" Unit="dS/m"/>
            <pH Value="{resultado.resultado_analise_solucao.estatisticas.get('ph', {}).get('media', 0)}"/>
        </NutrientAnalysis>
        
        <FertigationRecommendations>
            <Count>{len(resultado.resultado_recomendacao.recomendacoes)}</Count>
            <TotalCost currency="BRL">{resultado.resultado_recomendacao.custo_estimado}</TotalCost>
        </FertigationRecommendations>
    </FieldData>
</ISOBUS>"""
        
        return xml_content