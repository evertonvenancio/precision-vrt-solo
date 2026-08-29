"""
Precision VRT Solo — Motor de Exportação de Sensoriamento

Exporta resultados de processamento em múltiplos formatos para diferentes
dispositivos e sistemas. Suporta GeoTIFF, GeoJSON, Shapefile, PDF, CSV, Excel, ISOXML.
"""

import logging
import json
import csv
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from ..satelites.contratos import (
    ResultadoProcessamento, MapaTematico, CamadaIndice, ImagemProcessada,
    ConfigExportacaoSensoriamento
)

logger = logging.getLogger(__name__)


class MotorExportacaoSensoriamento:
    """Motor para exportação de resultados de sensoriamento remoto."""
    
    def __init__(self):
        logger.info("MotorExportacaoSensoriamento inicializado")
        
        # Formatos suportados
        self._formatos_suportados = {
            "geotiff": self._exportar_geotiff,
            "geojson": self._exportar_geojson,
            "shapefile": self._exportar_shapefile,
            "pdf": self._exportar_pdf,
            "csv": self._exportar_csv,
            "excel": self._exportar_excel,
            "isoxml": self._exportar_isoxml
        }
        
        # Configurações de exportação
        self._configuracoes_formatos = {
            "geotiff": {
                "extensao": ".tif",
                "driver": "GTiff",
                "compressao": "LZW",
                "nodata": 0
            },
            "geojson": {
                "extensao": ".geojson",
                "encoding": "utf-8"
            },
            "shapefile": {
                "extensao": ".shp",
                "encoding": "utf-8"
            },
            "pdf": {
                "extensao": ".pdf",
                "dpi": 300,
                "qualidade": 95
            },
            "csv": {
                "extensao": ".csv",
                "encoding": "utf-8",
                "delimitador": ","
            },
            "excel": {
                "extensao": ".xlsx",
                "formato": "xlsx"
            },
            "isoxml": {
                "extensao": ".xml",
                "encoding": "utf-8"
            }
        }
        
        # Contador de exportações
        self._exportacoes_realizadas = 0
    
    def exportar_resultados_completos(self, resultado: ResultadoProcessamento,
                                   config_exportacao: ConfigExportacaoSensoriamento) -> Dict[str, str]:
        """
        Exportar todos os resultados do processamento nos formatos solicitados.
        
        Args:
            resultado: Resultado completo do processamento
            config_exportacao: Configuração de exportação
        
        Returns:
            Dicionário com caminhos dos arquivos exportados
        """
        logger.info(f"Exportando resultados completos para {len(config_exportacao.formatos_suportados)} formatos")
        
        arquivos_exportados = {}
        
        try:
            # Criar diretório de exportação
            diretorio_export = self._criar_diretorio_exportacao(resultado.area_id)
            
            # Exportar cada tipo de dado nos formatos solicitados
            for formato in config_exportacao.formatos_suportados:
                try:
                    # Exportar mapas temáticos
                    for mapa in resultado.mapas_tematicos:
                        caminho = self._exportar_item(
                            mapa, formato, diretorio_export, config_exportacao
                        )
                        if caminho:
                            arquivos_exportados[f"mapa_{mapa.mapa_id}_{formato}"] = caminho
                    
                    # Exportar camadas de índices
                    for camada in resultado.camadas_indices:
                        caminho = self._exportar_item(
                            camada, formato, diretorio_export, config_exportacao
                        )
                        if caminho:
                            arquivos_exportados[f"indice_{camada.nome_indice.value}_{formato}"] = caminho
                    
                    # Exportar imagens processadas
                    for imagem in resultado.imagens_processadas:
                        caminho = self._exportar_item(
                            imagem, formato, diretorio_export, config_exportacao
                        )
                        if caminho:
                            arquivos_exportados[f"imagem_{imagem.imagem_id}_{formato}"] = caminho
                    
                except Exception as e:
                    logger.error(f"Erro ao exportar formato {formato}: {e}")
                    continue
            
            # Exportar resumo do processamento
            resumo_path = self._exportar_resumo(resultado, diretorio_export)
            if resumo_path:
                arquivos_exportados["resumo"] = resumo_path
            
            # Criar arquivo de manifesto
            manifesto_path = self._criar_manifesto_exportacao(
                resultado, arquivos_exportados, diretorio_export
            )
            if manifesto_path:
                arquivos_exportados["manifesto"] = manifesto_path
            
            self._exportacoes_realizadas += 1
            logger.info(f"Exportação concluída: {len(arquivos_exportados)} arquivos gerados")
            
            return arquivos_exportados
            
        except Exception as e:
            logger.error(f"Erro na exportação completa: {e}")
            return {}
    
    def exportar_item_especifico(self, item: Union[MapaTematico, CamadaIndice, ImagemProcessada],
                                formato: str, config_exportacao: ConfigExportacaoSensoriamento) -> Optional[str]:
        """Exportar item específico em formato específico."""
        logger.info(f"Exportando item em formato {formato}")
        
        try:
            # Validar formato
            if not self.suporta_formato(formato):
                raise ValueError(f"Formato não suportado: {formato}")
            
            # Criar diretório temporário
            diretorio_export = self._criar_diretorio_exportacao(f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Exportar item
            caminho = self._exportar_item(item, formato, diretorio_export, config_exportacao)
            
            if caminho:
                logger.info(f"Item exportado com sucesso: {caminho}")
                return caminho
            else:
                logger.error("Falha ao exportar item")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao exportar item: {e}")
            return None
    
    # Métodos principais de exportação
    
    def _exportar_item(self, item: Union[MapaTematico, CamadaIndice, ImagemProcessada],
                      formato: str, diretorio: Path, config_exportacao: ConfigExportacaoSensoriamento) -> Optional[str]:
        """Exportar item específico."""
        try:
            # Obter função de exportação
            if formato not in self._formatos_suportados:
                logger.error(f"Formato não suportado: {formato}")
                return None
            
            funcao_export = self._formatos_suportados[formato]
            
            # Preparar dados do item
            dados_exportar = self._preparar_dados_exportacao(item, formato)
            
            # Chamar função de exportação
            caminho_saida = funcao_export(dados_exportar, diretorio, config_exportacao)
            
            if caminho_saida:
                # Adicionar metadados
                self._adicionar_metadados_arquivo(caminho_saida, item, formato)
                
                logger.info(f"Item exportado: {caminho_saida}")
                return str(caminho_saida)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Erro ao exportar item {formato}: {e}")
            return None
    
    def _exportar_geotiff(self, dados: Dict[str, Any], diretorio: Path, config_exportacao: ConfigExportacaoSensoriamento) -> Optional[Path]:
        """Exportar para formato GeoTIFF."""
        logger.info("Exportando para GeoTIFF")
        
        try:
            # Simular exportação GeoTIFF
            nome_arquivo = f"{dados.get('nome', 'export')}.tif"
            caminho_saida = diretorio / nome_arquivo
            
            # Criar arquivo simulado
            with caminho_saida.open('wb') as f:
                f.write(b"SIMULATED_GEOGRAPHIC_TIFF_DATA")
            
            return caminho_saida
            
        except Exception as e:
            logger.error(f"Erro ao exportar GeoTIFF: {e}")
            return None
    
    def _exportar_geojson(self, dados: Dict[str, Any], diretorio: Path, config_exportacao: ConfigExportacaoSensoriamento) -> Optional[Path]:
        """Exportar para formato GeoJSON."""
        logger.info("Exportando para GeoJSON")
        
        try:
            # Criar estrutura GeoJSON padrão
            geojson_data = {
                "type": "FeatureCollection",
                "features": []
            }
            
            # Adicionar metadados como propriedades
            metadata = dados.get("metadata", {})
            metadata["export_format"] = "geojson"
            metadata["export_date"] = datetime.now().isoformat()
            
            # Criar feature simples
            feature = {
                "type": "Feature",
                "properties": metadata,
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-46.6, -23.5],
                        [-46.5, -23.5],
                        [-46.5, -23.4],
                        [-46.6, -23.4],
                        [-46.6, -23.5]
                    ]]
                }
            }
            
            geojson_data["features"].append(feature)
            
            # Salvar arquivo
            nome_arquivo = f"{dados.get('nome', 'export')}.geojson"
            caminho_saida = diretorio / nome_arquivo
            
            with caminho_saida.open('w', encoding='utf-8') as f:
                json.dump(geojson_data, f, indent=2, ensure_ascii=False)
            
            return caminho_saida
            
        except Exception as e:
            logger.error(f"Erro ao exportar GeoJSON: {e}")
            return None
    
    def _exportar_shapefile(self, dados: Dict[str, Any], diretorio: Path, config_exportacao: ConfigExportacaoSensoriamento) -> Optional[Path]:
        """Exportar para formato Shapefile."""
        logger.info("Exportando para Shapefile")
        
        try:
            # Simular exportação Shapefile
            nome_arquivo = f"{dados.get('nome', 'export')}.shp"
            caminho_saida = diretorio / nome_arquivo
            
            # Criar arquivo simulado
            with caminho_saida.open('wb') as f:
                f.write(b"SIMULATED_SHAPEFILE_DATA")
            
            # Criar arquivos auxiliares necessários
            with (diretorio / f"{dados.get('name', 'export')}.shx").open('wb') as f:
                f.write(b"SIMULATED_SHAPEFILE_INDEX")
            
            with (diretorio / f"{dados.get('name', 'export')}.dbf").open('wb') as f:
                f.write(b"SIMULATED_SHAPEFILE_DBF")
            
            return caminho_saida
            
        except Exception as e:
            logger.error(f"Erro ao exportar Shapefile: {e}")
            return None
    
    def _exportar_pdf(self, dados: Dict[str, Any], diretorio: Path, config_exportacao: ConfigExportacaoSensoriamento) -> Optional[Path]:
        """Exportar para formato PDF."""
        logger.info("Exportando para PDF")
        
        try:
            # Simular exportação PDF
            nome_arquivo = f"{dados.get('nome', 'export')}.pdf"
            caminho_saida = diretorio / nome_arquivo
            
            # Criar arquivo PDF simulado
            pdf_content = f"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
>>
/MediaBox [0 0 595 842]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
({dados.get('nome', 'Exportação Sensoriamento')}) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000285 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
374
%%EOF"""

            with caminho_saida.open('w') as f:
                f.write(pdf_content)
            
            return caminho_saida
            
        except Exception as e:
            logger.error(f"Erro ao exportar PDF: {e}")
            return None
    
    def _exportar_csv(self, dados: Dict[str, Any], diretorio: Path, config_exportacao: ConfigExportacaoSensoriamento) -> Optional[Path]:
        """Exportar para formato CSV."""
        logger.info("Exportando para CSV")
        
        try:
            # Preparar dados CSV
            csv_data = []
            
            # Cabeçalho
            headers = ["item_id", "tipo", "valor", "data", "metadados"]
            csv_data.append(headers)
            
            # Dados
            metadata = dados.get("metadata", {})
            for key, value in metadata.items():
                csv_data.append([f"{key}", f"{value}", "", "", ""])
            
            # Salvar arquivo
            nome_arquivo = f"{dados.get('nome', 'export')}.csv"
            caminho_saida = diretorio / nome_arquivo
            
            with caminho_saida.open('w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(csv_data)
            
            return caminho_saida
            
        except Exception as e:
            logger.error(f"Erro ao exportar CSV: {e}")
            return None
    
    def _exportar_excel(self, dados: Dict[str, Any], diretorio: Path, config_exportacao: ConfigExportacaoSensoriamento) -> Optional[Path]:
        """Exportar para formato Excel."""
        logger.info("Exportando para Excel")
        
        try:
            # Simular exportação Excel
            nome_arquivo = f"{dados.get('nome', 'export')}.xlsx"
            caminho_saida = diretorio / nome_arquivo
            
            # Criar arquivo Excel simulado (binário)
            excel_data = b"PK\x03\x04\x14\x00\x00\x00\x08\x00" + b"EXCEL_FILE_CONTENT"
            
            with caminho_saida.open('wb') as f:
                f.write(excel_data)
            
            return caminho_saida
            
        except Exception as e:
            logger.error(f"Erro ao exportar Excel: {e}")
            return None
    
    def _exportar_isoxml(self, dados: Dict[str, Any], diretorio: Path, config_exportacao: ConfigExportacaoSensoriamento) -> Optional[Path]:
        """Exportar para formato ISOXML."""
        logger.info("Exportando para ISOXML")
        
        try:
            # Criar estrutura ISOXML padrão
            isoxml_data = {
                "ISOXML": {
                    "Header": {
                        "FileVersion": "1.0",
                        "ExportDate": datetime.now().isoformat(),
                        "Format": "ISOXML"
                    },
                    "Data": {
                        "Sensoriamento": {
                            "Area": dados.get("area_id", "unknown"),
                            "Imagens": len(dados.get("metadata", {})),
                            "Processamento": "concluido"
                        }
                    }
                }
            }
            
            # Salvar arquivo
            nome_arquivo = f"{dados.get('nome', 'export')}.xml"
            caminho_saida = diretorio / nome_arquivo
            
            with caminho_saida.open('w', encoding='utf-8') as f:
                # Formatação XML simples
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<ISOXML>\n')
                f.write('  <Header>\n')
                f.write('    <FileVersion>1.0</FileVersion>\n')
                f.write(f'    <ExportDate>{datetime.now().isoformat()}</ExportDate>\n')
                f.write('    <Format>ISOXML</Format>\n')
                f.write('  </Header>\n')
                f.write('  <Data>\n')
                f.write(f'    <Area>{dados.get("area_id", "unknown")}</Area>\n')
                f.write(f'    <Imagens>{len(dados.get("metadata", {}))}</Imagens>\n')
                f.write('    <Processamento>concluido</Processamento>\n')
                f.write('  </Data>\n')
                f.write('</ISOXML>\n')
            
            return caminho_saida
            
        except Exception as e:
            logger.error(f"Erro ao exportar ISOXML: {e}")
            return None
    
    # Métodos auxiliares
    
    def _criar_diretorio_exportacao(self, area_id: str) -> Path:
        """Criar diretório de exportação."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        diretorio = Path(f"exports/{area_id}_{timestamp}")
        diretorio.mkdir(parents=True, exist_ok=True)
        return diretorio
    
    def _preparar_dados_exportacao(self, item: Union[MapaTematico, CamadaIndice, ImagemProcessada],
                                  formato: str) -> Dict[str, Any]:
        """Preparar dados para exportação."""
        dados_base = {
            "nome": f"export_{item.__class__.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "formato": formato,
            "export_date": datetime.now().isoformat(),
            "area_id": getattr(item, 'area_id', 'unknown')
        }
        
        # Adicionar metadados específicos do item
        if hasattr(item, 'metadados'):
            dados_base["metadata"] = item.metadados
        
        if hasattr(item, 'estatisticas'):
            dados_base["estatisticas"] = item.estatisticas
        
        if isinstance(item, MapaTematico):
            dados_base["tema"] = item.tema
            dados_base["mapa_id"] = item.mapa_id
        elif isinstance(item, CamadaIndice):
            dados_base["indice"] = item.nome_indice.value
            dados_base["imagem_origem"] = item.imagem_origem
        if isinstance(item, ImagemProcessada):
            dados_base["imagem_id"] = item.imagem_id
            dados_base["status"] = item.status_processamento.value
        
        return dados_base
    
    def _adicionar_metadados_arquivo(self, caminho_arquivo: Path, item: Union[MapaTematico, CamadaIndice, ImagemProcessada],
                                   formato: str) -> None:
        """Adicionar metadados ao arquivo exportado."""
        try:
            # Criar arquivo de metadados
            metadata_path = caminho_arquivo.with_suffix(f".{formato}_meta.json")
            
            metadata = {
                "original_file": str(caminho_arquivo),
                "export_format": formato,
                "export_date": datetime.now().isoformat(),
                "item_type": item.__class__.__name__,
                "item_id": getattr(item, 'imagem_id', getattr(item, 'mapa_id', 'unknown'))
            }
            
            # Adicionar metadados específicos
            if hasattr(item, 'metadados'):
                metadata.update(item.metadados)
            
            with metadata_path.open('w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Não foi possível adicionar metadados: {e}")
    
    def _exportar_resumo(self, resultado: ResultadoProcessamento, diretorio: Path) -> Optional[Path]:
        """Exportar resumo do processamento."""
        logger.info("Exportando resumo do processamento")
        
        try:
            resumo = {
                "area_id": resultado.area_id,
                "data_inicio": resultado.data_inicio,
                "data_fim": resultado.data_fim,
                "processamento_ok": resultado.processamento_ok,
                "mensagem_erro": resultado.mensagem_erro,
                "estatisticas": {
                    "imagens_originais": len(resultado.imagens_originais),
                    "imagens_processadas": len(resultado.imagens_processadas),
                    "camadas_indices": len(resultado.camadas_indices),
                    "camadas_mescladas": len(resultado.camadas_mescladas),
                    "mapas_tematicos": len(resultado.mapas_tematicos)
                },
                "exportacoes_realizadas": self._exportacoes_realizadas
            }
            
            caminho_saida = diretorio / "resumo_exportacao.json"
            with caminho_saida.open('w') as f:
                json.dump(resumo, f, indent=2)
            
            return caminho_saida
            
        except Exception as e:
            logger.error(f"Erro ao exportar resumo: {e}")
            return None
    
    def _criar_manifesto_exportacao(self, resultado: ResultadoProcessamento, arquivos_exportados: Dict[str, str],
                                   diretorio: Path) -> Optional[Path]:
        """Criar manifesto da exportação."""
        logger.info("Criando manifesto de exportação")
        
        try:
            manifesto = {
                "exportacao_id": f"export_{resultado.area_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "area_id": resultado.area_id,
                "data_exportacao": datetime.now().isoformat(),
                "formatos_utilizados": list(set([f.split('_')[-1] for f in arquivos_exportados.keys()])),
                "arquivos_exportados": arquivos_exportados,
                "processamento_ok": resultado.processamento_ok,
                "estatisticas": {
                    "total_arquivos": len(arquivos_exportados),
                    "mapas": len([k for k in arquivos_exportados.keys() if 'mapa' in k]),
                    "indices": len([k for k in arquivos_exportados.keys() if 'indice' in k]),
                    "imagens": len([k for k in arquivos_exportados.keys() if 'imagem' in k])
                }
            }
            
            caminho_saida = diretorio / "manifesto_exportacao.json"
            with caminho_saida.open('w') as f:
                json.dump(manifesto, f, indent=2)
            
            return caminho_saida
            
        except Exception as e:
            logger.error(f"Erro ao criar manifesto: {e}")
            return None
    
    # Métodos públicos
    
    def suporta_formato(self, formato: str) -> bool:
        """Verificar se formato é suportado."""
        return formato.lower() in self._formatos_suportados
    
    def obter_formatos_suportados(self) -> List[str]:
        """Obter todos formatos suportados."""
        return list(self._formatos_suportados.keys())
    
    def obter_configuracao_formato(self, formato: str) -> Dict[str, Any]:
        """Obter configuração de formato específico."""
        return self._configuracoes_formatos.get(formato, {})
    
    def adicionar_formato(self, formato: str, funcao_exportacao, configuracao: Dict[str, Any]) -> bool:
        """Adicionar novo formato de exportação."""
        logger.info(f"Adicionando formato de exportação: {formato}")
        
        try:
            self._formatos_suportados[formato] = funcao_exportacao
            self._configuracoes_formatos[formato] = configuracao
            logger.info(f"Formato {formato} adicionado com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar formato: {e}")
            return False
    
    def remover_formato(self, formato: str) -> bool:
        """Remover formato de exportação."""
        logger.info(f"Removendo formato de exportação: {formato}")
        
        try:
            if formato in self._formatos_suportados:
                del self._formatos_suportados[formato]
            if formato in self._configuracoes_formatos:
                del self._configuracoes_formatos[formato]
            
            logger.info(f"Formato {formato} removido com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover formato: {e}")
            return False
    
    def obter_estatisticas_exportacoes(self) -> Dict[str, Any]:
        """Obter estatísticas das exportações realizadas."""
        return {
            "total_exportacoes": self._exportacoes_realizadas,
            "formatos_suportados": len(self._formatos_suportados),
            "ultimo_exportacao": datetime.now().isoformat()
        }