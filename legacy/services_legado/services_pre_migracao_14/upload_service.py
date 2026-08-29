"""
Precision VRT Solo - Serviço de Upload Completo
==============================================

Serviço responsável por processar qualquer tipo de arquivo de entrada e saída:
• CSV
• XLSX  
• SHP (Shapefile)
• GeoJSON
• TIFF (GeoTIFF)
• ZIP (contendo qualquer dos formatos acima)
• ISOXML

Este serviço utiliza a nova arquitetura com CamadaTematica e Motor composto.
"""

import logging
import shutil
import tempfile
import uuid
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd
import geopandas as gpd
import numpy as np
from fastapi import UploadFile, HTTPException, status
from shapely.geometry import Point, Polygon, MultiPolygon
from datetime import datetime

# Import de classes temporariamente comentado para desbloquear inicialização
from core.tipos.camada_tematica import (
    CamadaTematica,
    TipoCamada,
    TipoIndice,
    FabricaCamadasTematicas
)
from core.prescricao_vrt.motor_composto import MotorPrescricaoComposto
from core.prescricao_vrt.configuracao import ConfigPrescricao
from services.geo_parser_service import parse_upload
from utils.geojson import gdf_para_geojson_dict

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

logger = logging.getLogger(__name__)

# Tipos de arquivo suportados
TIPOS_ARQUIVOS_SUPORTADOS = {
    'csv': ['text/csv', 'application/csv'],
    'xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
    'xls': ['application/vnd.ms-excel'],
    'shp': ['application/octet-stream'],  # Shapefile
    'geojson': ['application/json', 'application/geo+json'],
    'tif': ['image/tiff', 'image/geotiff'],
    'tiff': ['image/tiff', 'image/geotiff'],
    'zip': ['application/zip', 'application/x-zip-compressed'],
    'isoxml': ['application/xml', 'text/xml']
}

# Extensões de arquivo
EXTENCOES_ARQUIVOS = {
    'csv': '.csv',
    'xlsx': '.xlsx',
    'xls': '.xls',
    'shp': '.shp',
    'geojson': '.geojson',
    'tif': '.tif',
    'tiff': '.tiff',
    'zip': '.zip',
    'isoxml': '.xml'
}

# ============================================================================
# DETECTOR DE TIPO DE ARQUIVO
# ============================================================================

class DetectorTipoArquivo:
    """Detecta o tipo de arquivo com base no conteúdo e extensão."""
    
    @staticmethod
    def detectar(file: UploadFile) -> str:
        """Detecta o tipo de arquivo."""
        # Verificar extensão do arquivo
        filename = file.filename or ""
        extensao = filename.lower().split('.')[-1] if '.' in filename else ""
        
        # Verificar conteúdo do arquivo
        content_type = file.content_type or ""
        
        # Lógica de detecção
        if extensao == 'zip':
            return 'zip'
        elif extensao in ['csv', 'txt']:
            return 'csv'
        elif extensao in ['xlsx', 'xls']:
            return 'xlsx'
        elif extensao == 'geojson':
            return 'geojson'
        elif extensao in ['tif', 'tiff']:
            return 'tiff'
        elif extensao == 'shp':
            return 'shp'
        elif extensao == 'xml':
            return 'isoxml'
        else:
            # Tentar detectar pelo content-type
            if 'csv' in content_type:
                return 'csv'
            elif 'excel' in content_type or 'spreadsheet' in content_type:
                return 'xlsx'
            elif 'json' in content_type:
                return 'geojson'
            elif 'tiff' in content_type or 'image' in content_type:
                return 'tiff'
            elif 'zip' in content_type:
                return 'zip'
            else:
                return 'desconhecido'
    
    @staticmethod
    def eh_suportado(tipo: str) -> bool:
        """Verifica se o tipo de arquivo é suportado."""
        return tipo in TIPOS_ARQUIVOS_SUPORTADOS

# ============================================================================
# EXTRAÇÃO DE ARQUIVOS ZIP
# ============================================================================

class ExtratorZip:
    """Extrai arquivos ZIP e identifica o conteúdo."""
    
    @staticmethod
    def extrair(zip_file: UploadFile) -> List[Tuple[str, bytes]]:
        """Extrai arquivos de um arquivo ZIP."""
        arquivos_extraidos = []
        
        try:
            # Criar diretório temporário
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Salvar arquivo ZIP
                zip_path = temp_path / "temp.zip"
                with open(zip_path, 'wb') as f:
                    f.write(zip_file.file.read())
                
                # Extrair ZIP
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Identificar arquivos extraídos
                for file_path in temp_path.rglob('*'):
                    if file_path.is_file():
                        # Tentar identificar tipo de arquivo
                        tipo = DetectorTipoArquivo.detectar_from_path(str(file_path))
                        if DetectorTipoArquivo.eh_suportado(tipo):
                            with open(file_path, 'rb') as f:
                                arquivos_extraidos.append((tipo, f.read()))
        
        except Exception as e:
            logger.error(f"[EXTRATOR_ZIP] Erro ao extrair ZIP: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao extrair arquivo ZIP: {str(e)}"
            )
        
        return arquivos_extraidos
    
    @staticmethod
    def detectar_from_path(file_path: str) -> str:
        """Detecta tipo de arquivo a partir do caminho."""
        extensao = Path(file_path).lower().suffix
        if extensao == '.zip':
            return 'zip'
        elif extensao in ['.csv', '.txt']:
            return 'csv'
        elif extensao in ['.xlsx', '.xls']:
            return 'xlsx'
        elif extensao == '.geojson':
            return 'geojson'
        elif extensao in ['.tif', '.tiff']:
            return 'tiff'
        elif extensao == '.shp':
            return 'shp'
        elif extensao == '.xml':
            return 'isoxml'
        else:
            return 'desconhecido'

# ============================================================================
# PROCESSADOR DE ARQUIVOS
# ============================================================================

class ProcessadorArquivos:
    """Processa diferentes tipos de arquivos e converte para CamadaTematica."""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"[PROCESSADOR] Diretório temporário criado: {self.temp_dir}")
    
    def __del__(self):
        """Limpa diretório temporário."""
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            logger.info(f"[PROCESSADOR] Diretório temporário limpo: {self.temp_dir}")
        except Exception:
            pass
    
    def processar_arquivo(self, file: UploadFile, tipo: str) -> List:  # CamadaTematicaInterface temporariamente comentado
        """Processa um arquivo e retorna lista de CamadasTematica."""
        try:
            logger.info(f"[PROCESSADOR] Processando arquivo: {file.filename} (tipo: {tipo})")
            
            # Salvar arquivo temporariamente
            temp_path = Path(self.temp_dir) / f"{uuid.uuid4()}_{file.filename}"
            with open(temp_path, 'wb') as f:
                f.write(file.file.read())
            
            # Processar de acordo com o tipo
            if tipo == 'csv':
                return self._processar_csv(temp_path)
            elif tipo in ['xlsx', 'xls']:
                return self._processar_excel(temp_path)
            elif tipo == 'geojson':
                return self._processar_geojson(temp_path)
            elif tipo in ['tif', 'tiff']:
                return self._processar_geotiff(temp_path)
            elif tipo == 'shp':
                return self._processar_shapefile(temp_path)
            elif tipo == 'zip':
                return self._processar_zip(temp_path)
            elif tipo == 'isoxml':
                return self._processar_isoxml(temp_path)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tipo de arquivo não suportado: {tipo}"
                )
        
        except Exception as e:
            logger.error(f"[PROCESSADOR] Erro ao processar arquivo: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao processar arquivo: {str(e)}"
            )
    
    def _processar_csv(self, file_path: Path) -> List:  # CamadaTematicaInterface temporariamente comentado
        """Processa arquivo CSV."""
        try:
            # Ler CSV
            df = pd.read_csv(file_path)
            
            # Verificar se tem colunas geográficas
            if 'latitude' in df.columns and 'longitude' in df.columns:
                # Criar geometria a partir de coordenadas
                geometrias = []
                for _, row in df.iterrows():
                    ponto = Point(row['longitude'], row['latitude'])
                    geometrias.append(ponto)
                
                gdf = gpd.GeoDataFrame(df, geometry=geometrias, crs='EPSG:4326')
                
                # Identificar coluna de valor
                coluna_valor = self._identificar_coluna_valor(df.columns)
                if coluna_valor:
                    gdf['valor'] = gdf[coluna_valor]
                
                # Criar CamadaTematica
                camada = FabricaCamadasTematicas.criar_mapa_laboratorio(
                    id=f"csv_{uuid.uuid4()}",
                    nome=f"CSV - {file_path.stem}",
                    geometria=gdf,
                    parametro_analise=coluna_valor or "analise"
                )
                
                return [camada]
            
            else:
                # CSV sem informações geográficas - tratar como dados de análise
                gdf = gpd.GeoDataFrame(df, geometry=[Point(0, 0)] * len(df), crs='EPSG:4326')
                
                camada = FabricaCamadasTematicas.criar_mapa_laboratorio(
                    id=f"csv_{uuid.uuid4()}",
                    nome=f"CSV - {file_path.stem}",
                    geometria=gdf,
                    parametro_analise="dados"
                )
                
                return [camada]
        
        except Exception as e:
            logger.error(f"[PROCESSADOR_CSV] Erro: {e}")
            raise
    
    def _processar_excel(self, file_path: Path) -> List:  # CamadaTematicaInterface temporariamente comentado
        """Processa arquivo Excel."""
        try:
            # Ler Excel
            df = pd.read_excel(file_path)
            
            # Lógica similar ao CSV
            if 'latitude' in df.columns and 'longitude' in df.columns:
                geometrias = []
                for _, row in df.iterrows():
                    ponto = Point(row['longitude'], row['latitude'])
                    geometrias.append(ponto)
                
                gdf = gpd.GeoDataFrame(df, geometry=geometrias, crs='EPSG:4326')
                
                coluna_valor = self._identificar_coluna_valor(df.columns)
                if coluna_valor:
                    gdf['valor'] = gdf[coluna_valor]
                
                camada = FabricaCamadasTematicas.criar_mapa_laboratorio(
                    id=f"excel_{uuid.uuid4()}",
                    nome=f"Excel - {file_path.stem}",
                    geometria=gdf,
                    parametro_analise=coluna_valor or "analise"
                )
                
                return [camada]
            else:
                gdf = gpd.GeoDataFrame(df, geometry=[Point(0, 0)] * len(df), crs='EPSG:4326')
                
                camada = FabricaCamadasTematicas.criar_mapa_laboratorio(
                    id=f"excel_{uuid.uuid4()}",
                    nome=f"Excel - {file_path.stem}",
                    geometria=gdf,
                    parametro_analise="dados"
                )
                
                return [camada]
        
        except Exception as e:
            logger.error(f"[PROCESSADOR_EXCEL] Erro: {e}")
            raise
    
    def _processar_geojson(self, file_path: Path) -> List:  # CamadaTematicaInterface temporariamente comentado
        """Processa arquivo GeoJSON."""
        try:
            # Ler GeoJSON
            gdf = gpd.read_file(file_path)
            
            # Identificar tipo de camada
            tipo_camada = self._identificar_tipo_geojson(gdf)
            
            # Criar CamadaTematica apropriada
            if tipo_camada == 'indice_espectral':
                return [FabricaCamadasTematicas.criar_indice_espectral(
                    id=f"geojson_{uuid.uuid4()}",
                    nome=f"GeoJSON - {file_path.stem}",
                    geometria=gdf,
                    tipo_indice=TipoIndice.NDVI.value  # Usar .value para enum
                )]
            elif tipo_camada == 'produtividade':
                return [FabricaCamadasTematicas.criar_mapa_produtividade(
                    id=f"geojson_{uuid.uuid4()}",
                    nome=f"GeoJSON - {file_path.stem}",
                    geometria=gdf
                )]
            elif tipo_camada == 'compactacao':
                return [FabricaCamadasTematicas.criar_mapa_compactacao(
                    id=f"geojson_{uuid.uuid4()}",
                    nome=f"GeoJSON - {file_path.stem}",
                    geometria=gdf
                )]
            elif tipo_camada == 'umidade':
                return [FabricaCamadasTematicas.criar_mapa_umidade(
                    id=f"geojson_{uuid.uuid4()}",
                    nome=f"GeoJSON - {file_path.stem}",
                    geometria=gdf
                )]
            else:
                # Tratar como laboratorial
                return [FabricaCamadasTematicas.criar_mapa_laboratorio(
                    id=f"geojson_{uuid.uuid4()}",
                    nome=f"GeoJSON - {file_path.stem}",
                    geometria=gdf
                )]
        
        except Exception as e:
            logger.error(f"[PROCESSADOR_GEOJSON] Erro: {e}")
            raise
    
    def _processar_geotiff(self, file_path: Path) -> List[CamadaTematica]:
        """Processa arquivo GeoTIFF."""
        try:
            # TODO: Implementar processamento real de GeoTIFF
            # Por enquanto, criar uma camada de exemplo
            from shapely.geometry import box
            
            # Criar geometria de exemplo
            bbox = box(-180, -90, 180, 90)  # Mundo inteiro
            gdf = gpd.GeoDataFrame([{'valor': 0.5}], geometry=[bbox], crs='EPSG:4326')
            
            return [FabricaCamadasTematicas.criar_indice_espectral(
                id=f"geotiff_{uuid.uuid4()}",
                nome=f"GeoTIFF - {file_path.stem}",
                geometria=gdf,
                tipo_indice=TipoIndice.NDVI.value
            )]
        
        except Exception as e:
            logger.error(f"[PROCESSADOR_GEO TIFF] Erro: {e}")
            raise
    
    def _processar_shapefile(self, file_path: Path) -> List:  # CamadaTematicaInterface temporariamente comentado
        """Processa arquivo Shapefile."""
        try:
            # Ler Shapefile
            gdf = gpd.read_file(file_path)
            
            # Identificar tipo de camada
            tipo_camada = self._identificar_tipo_shapefile(gdf)
            
            # Criar CamadaTematica apropriada
            if tipo_camada == 'indice_espectral':
                return [FabricaCamadasTematicas.criar_indice_espectral(
                    id=f"shp_{uuid.uuid4()}",
                    nome=f"Shapefile - {file_path.stem}",
                    geometria=gdf,
                    tipo_indice=TipoIndice.NDVI.value
                )]
            elif tipo_camada == 'produtividade':
                return [FabricaCamadasTematicas.criar_mapa_produtividade(
                    id=f"shp_{uuid.uuid4()}",
                    nome=f"Shapefile - {file_path.stem}",
                    geometria=gdf
                )]
            else:
                return [FabricaCamadasTematicas.criar_mapa_laboratorio(
                    id=f"shp_{uuid.uuid4()}",
                    nome=f"Shapefile - {file_path.stem}",
                    geometria=gdf
                )]
        
        except Exception as e:
            logger.error(f"[PROCESSADOR_SHAPEFILE] Erro: {e}")
            raise
    
    def _processar_zip(self, file_path: Path) -> List:  # CamadaTematicaInterface temporariamente comentado
        """Processa arquivo ZIP."""
        try:
            arquivos_extraidos = []
            
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            # Processar cada arquivo extraído
            for extracted_file in Path(self.temp_dir).rglob('*'):
                if extracted_file.is_file():
                    tipo = ExtratorZip.detectar_from_path(str(extracted_file))
                    if DetectorTipoArquivo.eh_suportado(tipo):
                        # Criar UploadFile temporário
                        with open(extracted_file, 'rb') as f:
                            temp_upload = UploadFile(
                                filename=extracted_file.name,
                                file=f
                            )
                            camadas = self.processar_arquivo(temp_upload, tipo)
                            arquivos_extraidos.extend(camadas)
            
            return arquivos_extraidos
        
        except Exception as e:
            logger.error(f"[PROCESSADOR_ZIP] Erro: {e}")
            raise
    
    def _processar_isoxml(self, file_path: Path) -> List:  # CamadaTematicaInterface temporariamente comentado
        """Processa arquivo ISOXML."""
        try:
            # TODO: Implementar processamento real de ISOXML
            # Por enquanto, criar uma camada de exemplo
            from shapely.geometry import box
            
            bbox = box(-180, -90, 180, 90)
            gdf = gpd.GeoDataFrame([{'valor': 0.5}], geometry=[bbox], crs='EPSG:4326')
            
            return [FabricaCamadasTematicas.criar_mapa_laboratorio(
                id=f"isoxml_{uuid.uuid4()}",
                nome=f"ISOXML - {file_path.stem}",
                geometria=gdf,
                parametro_analise="isoxml"
            )]
        
        except Exception as e:
            logger.error(f"[PROCESSADOR_ISOXML] Erro: {e}")
            raise
    
    def _identificar_coluna_valor(self, colunas: List[str]) -> Optional[str]:
        """Identifica coluna de valor em um DataFrame."""
        colunas_valor = ['valor', 'value', 'result', 'resultado', 'ndvi', 'ndre', 'savi']
        
        for coluna in colunas:
            coluna_lower = coluna.lower()
            for valor in colunas_valor:
                if valor in coluna_lower:
                    return coluna
        
        return None
    
    def _identificar_tipo_geojson(self, gdf: gpd.GeoDataFrame) -> str:
        """Identifica tipo de camada GeoJSON."""
        # Verificar colunas para identificar tipo
        colunas = [col.lower() for col in gdf.columns]
        
        if any('ndvi' in col for col in colunas):
            return 'indice_espectral'
        elif any('produtividade' in col or 'prod' in col for col in colunas):
            return 'produtividade'
        elif any('compactacao' in col or 'comp' in col for col in colunas):
            return 'compactacao'
        elif any('umidade' in col or 'umid' in col for col in colunas):
            return 'umidade'
        else:
            return 'laboratorio'
    
    def _identificar_tipo_shapefile(self, gdf: gpd.GeoDataFrame) -> str:
        """Identifica tipo de camada Shapefile."""
        # Lógica similar ao GeoJSON
        colunas = [col.lower() for col in gdf.columns]
        
        if any('ndvi' in col for col in colunas):
            return 'indice_espectral'
        elif any('produtividade' in col or 'prod' in col for col in colunas):
            return 'produtividade'
        else:
            return 'laboratorio'

# ============================================================================
# SERVIÇO PRINCIPAL
# ============================================================================

class UploadService:
    """Serviço principal de upload e processamento de arquivos."""
    
    def __init__(self):
        self.processador = ProcessadorArquivos()
        self.motor = MotorPrescricaoComposto(ConfigPrescricao())
        logger.info("[UPLOAD_SERVICE] Serviço inicializado")
    
    async def upload_arquivo(self, file: UploadFile) -> Dict[str, Any]:
        """Processa upload de arquivo e retorna resultado."""
        try:
            logger.info(f"[UPLOAD_SERVICE] Recebendo arquivo: {file.filename}")
            
            # Detectar tipo de arquivo
            tipo = DetectorTipoArquivo.detectar(file)
            logger.info(f"[UPLOAD_SERVICE] Tipo detectado: {tipo}")
            
            if not DetectorTipoArquivo.eh_suportado(tipo):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tipo de arquivo não suportado: {tipo}"
                )
            
            # Processar arquivo
            camadas = self.processador.processar_arquivo(file, tipo)
            logger.info(f"[UPLOAD_SERVICE] Processado {len(camadas)} camadas")
            
            # Retornar resultado
            return {
                'status': 'sucesso',
                'tipo_arquivo': tipo,
                'arquivo_original': file.filename,
                'camadas_processadas': len(camadas),
                'camadas': [
                    {
                        'id': camada.id,
                        'nome': camada.nome,
                        'tipo': camada.tipo_camada.value,
                        'crs': camada.crs,
                        'geometrias': len(camada.geometria),
                        'metadados': camada.metadados
                    }
                    for camada in camadas
                ],
                'timestamp': datetime.now().isoformat()
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[UPLOAD_SERVICE] Erro inesperado: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao processar arquivo: {str(e)}"
            )
    
    async def processar_prescricao(self, 
                                 camadas: List,  # CamadaTematicaInterface temporariamente comentado
                                 zonas: gpd.GeoDataFrame,
                                 cultura: str,
                                 safra: str,
                                 metodologias: List[str]) -> Dict[str, Any]:
        """Processa prescrição usando o motor composto."""
        try:
            logger.info(f"[UPLOAD_SERVICE] Processando prescrição para {cultura} - {safra}")
            
            # Usar motor composto
            resultado = self.motor.prescrever_todas_zonas(
                camadas=camadas,
                zonas=zonas,
                cultura=cultura,
                safra=safra,
                metodologias_disponiveis=metodologias,
                formato_exportacao='caderno_tecnico'
            )
            
            # Exportar resultado
            arquivo_saida = ExportadorService.exportar_prescricao(resultado, 'caderno_tecnico')
            
            return {
                'status': 'sucesso',
                'cultura': cultura,
                'safra': safra,
                'metodologias': metodologias,
                'arquivo_saida': arquivo_saida,
                'resultado_prescricao': resultado,
                'timestamp': resultado.get('timestamp')
            }
        
        except Exception as e:
            logger.error(f"[UPLOAD_SERVICE] Erro na prescrição: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao processar prescrição: {str(e)}"
            )

# ============================================================================
# EXPORTAÇÃO
# ============================================================================

class ExportadorService:
    """Serviço de exportação de resultados em múltiplos formatos."""
    
    @staticmethod
    def exportar_prescricao(prescricao: Dict[str, Any], formato: str) -> str:
        """Exporta prescrição em formato específico."""
        try:
            logger.info(f"[EXPORTADOR] Exportando prescrição em formato: {formato}")
            
            # TODO: Implementar exportação real
            if formato == 'caderno_tecnico':
                return "caderno_tecnico.pdf"
            elif formato == 'cartao_cabine':
                return "cartao_cabine.csv"
            elif formato == 'maquina':
                return "prescricao_maquina.shp"
            else:
                raise ValueError(f"Formato não suportado: {formato}")
        
        except Exception as e:
            logger.error(f"[EXPORTADOR] Erro na exportação: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao exportar: {str(e)}"
            )

# ============================================================================
# FUNÇÕES PÚBLICAS
# ============================================================================

# Instância global do serviço
upload_service = UploadService()

async def upload_arquivo(file: UploadFile) -> Dict[str, Any]:
    """Função pública para upload de arquivo."""
    return await upload_service.upload_arquivo(file)

async def processar_prescricao(camadas: List,  # CamadaTematicaInterface temporariamente comentado
                              zonas: gpd.GeoDataFrame,
                              cultura: str,
                              safra: str,
                              metodologias: List[str]) -> Dict[str, Any]:
    """Função pública para processar prescrição."""
    return await upload_service.processar_prescricao(camadas, zonas, cultura, safra, metodologias)

def exportar_prescricao(prescricao: Dict[str, Any], formato: str) -> str:
    """Função pública para exportar prescrição."""
    return ExportadorService.exportar_prescricao(prescricao, formato)