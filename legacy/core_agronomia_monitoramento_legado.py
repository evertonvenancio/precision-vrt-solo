"""
Modulo de Monitoramento de Vigor e Analise de Safra
Processamento de indices de vegetacao e correlacao com fertilidade do solo.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import warnings
import sqlite3\n
warnings.filterwarnings('ignore')

# Tentar importar rasterio/gdal
try:
    import rasterio
    from rasterio.mask import mask
    from rasterio.plot import show
    RASTERIO_DISPONIVEL = True
except ImportError:
    RASTERIO_DISPONIVEL = False
    logging.info("[AVISO] rasterio nao disponivel. Funcionalidades de leitura GeoTIFF limitadas.")

try:
    from osgeo import gdal, osr, ogr
    GDAL_DISPONIVEL = True
except ImportError:
    GDAL_DISPONIVEL = False


class IndiceVegetacao(Enum):
    """Indices de vegetacao suportados."""
    NDVI = "NDVI"
    EVI = "EVI"
    SAVI = "SAVI"
    NDWI = "NDWI"
    GNDVI = "GNDVI"
    MSAVI = "MSAVI"
    NDRE = "NDRE"
    GCI = "GCI"
    RECI = "RECI"
    MTCI = "MTCI"
    OSAVI = "OSAVI"
    TVI = "TVI"
    CVI = "CVI"
    DVI = "DVI"
    RVI = "RVI"
    IPVI = "IPVI"
    NBR = "NBR"
    NBR2 = "NBR2"
    NDSI = "NDSI"
    BAI = "BAI"


@dataclass
class SerieTemporalVigor:
    """Serie temporal de vigor para uma zona de manejo."""
    zona_id: int
    datas: List[str] = field(default_factory=list)
    valores_medios: Dict[str, List[float]] = field(default_factory=dict)
    desvios: Dict[str, List[float]] = field(default_factory=dict)
    anomalias: List[Dict] = field(default_factory=list)


@dataclass
class AnomaliaVigor:
    """Representa uma anomalia detectada no vigor."""
    zona_id: int
    data: str
    indice: str
    valor_observado: float
    valor_esperado: float
    desvio_percentual: float
    tipo: str  # 'positiva' ou 'negativa'
    severidade: str  # 'leve', 'moderada', 'grave'
    possiveis_causas: List[str] = field(default_factory=list)


class CalculadorIndices:
    """
    Calcula indices de vegetacao a partir de bandas espectrais.
    Suporta Sentinel-2, Landsat e outras fontes.
    """
    
    @staticmethod
    def calcular_ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
        """Normalized Difference Vegetation Index."""
        ndvi = np.divide(nir - red, nir + red, 
                        out=np.zeros_like(nir, dtype=float), 
                        where=(nir + red) != 0)
        return np.clip(ndvi, -1, 1)
    
    @staticmethod
    def calcular_evi(nir: np.ndarray, red: np.ndarray, blue: np.ndarray,
                     L: float = 1.0, C1: float = 6.0, C2: float = 7.5, 
                     G: float = 2.5) -> np.ndarray:
        """Enhanced Vegetation Index."""
        denominador = nir + C1 * red - C2 * blue + L
        evi = np.divide(G * (nir - red), denominador,
                       out=np.zeros_like(nir, dtype=float),
                       where=denominador != 0)
        return np.clip(evi, -1, 1)
    
    @staticmethod
    def calcular_savi(nir: np.ndarray, red: np.ndarray, L: float = 0.5) -> np.ndarray:
        """Soil Adjusted Vegetation Index."""
        denominador = nir + red + L
        savi = np.divide((1 + L) * (nir - red), denominador,
                        out=np.zeros_like(nir, dtype=float),
                        where=denominador != 0)
        return np.clip(savi, -1, 1)
    
    @staticmethod
    def calcular_ndwi(nir: np.ndarray, swir1: np.ndarray) -> np.ndarray:
        """Normalized Difference Water Index."""
        ndwi = np.divide(nir - swir1, nir + swir1,
                        out=np.zeros_like(nir, dtype=float),
                        where=(nir + swir1) != 0)
        return np.clip(ndwi, -1, 1)
    
    @staticmethod
    def calcular_gndvi(nir: np.ndarray, green: np.ndarray) -> np.ndarray:
        """Green Normalized Difference Vegetation Index."""
        gndvi = np.divide(nir - green, nir + green,
                         out=np.zeros_like(nir, dtype=float),
                         where=(nir + green) != 0)
        return np.clip(gndvi, -1, 1)
    
    @staticmethod
    def calcular_msavi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
        """Modified Soil Adjusted Vegetation Index."""
        d = (2 * nir + 1) ** 2 - 8 * (nir - red)
        d = np.maximum(d, 0)  # Evitar raiz negativa
        msavi = (2 * nir + 1 - np.sqrt(d)) / 2
        return np.clip(msavi, -1, 1)
    
    @staticmethod
    def calcular_ndre(nir: np.ndarray, red_edge: np.ndarray) -> np.ndarray:
        """Normalized Difference Red Edge."""
        ndre = np.divide(nir - red_edge, nir + red_edge,
                        out=np.zeros_like(nir, dtype=float),
                        where=(nir + red_edge) != 0)
        return np.clip(ndre, -1, 1)
    
    @staticmethod
    def calcular_gci(nir: np.ndarray, green: np.ndarray) -> np.ndarray:
        """Green Chlorophyll Index."""
        gci = np.divide(nir, green,
                       out=np.zeros_like(nir, dtype=float),
                       where=green != 0)
        return gci - 1
    
    @staticmethod
    def calcular_reci(nir: np.ndarray, red_edge: np.ndarray) -> np.ndarray:
        """Red Edge Chlorophyll Index."""
        reci = np.divide(nir, red_edge,
                        out=np.zeros_like(nir, dtype=float),
                        where=red_edge != 0)
        return reci - 1
    
    @staticmethod
    def calcular_mtci(nir: np.ndarray, red_edge: np.ndarray, red: np.ndarray) -> np.ndarray:
        """MERIS Terrestrial Chlorophyll Index."""
        denominador = red_edge + red
        mtci = np.divide(nir - red_edge, denominador,
                        out=np.zeros_like(nir, dtype=float),
                        where=denominador != 0)
        return mtci
    
    @staticmethod
    def calcular_osavi(nir: np.ndarray, red: np.ndarray, Y: float = 0.16) -> np.ndarray:
        """Optimized Soil Adjusted Vegetation Index."""
        denominador = nir + red + Y
        osavi = np.divide(nir - red, denominador,
                         out=np.zeros_like(nir, dtype=float),
                         where=denominador != 0)
        return np.clip(osavi, -1, 1)
    
    @staticmethod
    def calcular_tvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
        """Triangular Vegetation Index."""
        tvi = 0.5 * (120 * (nir - green) - 200 * (red - green))
        return tvi
    
    @staticmethod
    def calcular_cvi(nir: np.ndarray, red: np.ndarray, green: np.ndarray) -> np.ndarray:
        """Chlorophyll Vegetation Index."""
        cvi = np.divide(nir * red, green ** 2,
                       out=np.zeros_like(nir, dtype=float),
                       where=green != 0)
        return cvi
    
    @staticmethod
    def calcular_dvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
        """Difference Vegetation Index."""
        return nir - red
    
    @staticmethod
    def calcular_rvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
        """Ratio Vegetation Index."""
        rvi = np.divide(nir, red,
                       out=np.zeros_like(nir, dtype=float),
                       where=red != 0)
        return rvi
    
    @staticmethod
    def calcular_ipvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
        """Infrared Percentage Vegetation Index."""
        denominador = nir + red
        ipvi = np.divide(nir, denominador,
                        out=np.zeros_like(nir, dtype=float),
                        where=denominador != 0)
        return ipvi
    
    @staticmethod
    def calcular_nbr(nir: np.ndarray, swir2: np.ndarray) -> np.ndarray:
        """Normalized Burn Ratio."""
        nbr = np.divide(nir - swir2, nir + swir2,
                       out=np.zeros_like(nir, dtype=float),
                       where=(nir + swir2) != 0)
        return np.clip(nbr, -1, 1)
    
    @staticmethod
    def calcular_nbr2(swir1: np.ndarray, swir2: np.ndarray) -> np.ndarray:
        """Normalized Burn Ratio 2."""
        nbr2 = np.divide(swir1 - swir2, swir1 + swir2,
                        out=np.zeros_like(swir1, dtype=float),
                        where=(swir1 + swir2) != 0)
        return np.clip(nbr2, -1, 1)
    
    @staticmethod
    def calcular_ndsi(green: np.ndarray, swir1: np.ndarray) -> np.ndarray:
        """Normalized Difference Snow Index."""
        ndsi = np.divide(green - swir1, green + swir1,
                        out=np.zeros_like(green, dtype=float),
                        where=(green + swir1) != 0)
        return np.clip(ndsi, -1, 1)
    
    @staticmethod
    def calcular_bai(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
        """Burned Area Index."""
        denominador = (0.1 - nir) ** 2 + (0.06 - red) ** 2
        bai = np.divide(1.0, denominador,
                       out=np.zeros_like(nir, dtype=float),
                       where=denominador != 0)
        return bai


class LeitorGeoTIFF:
    """
    Leitor de imagens GeoTIFF de indices de vegetacao.
    Compativel com rasterio e gdal.
    """
    
    def __init__(self, caminho: Union[str, Path]):
        self.caminho = Path(caminho)
        self.dataset = None
        self.perfil = None
        self._abrir()
    
    def _abrir(self):
        """Abre o arquivo GeoTIFF."""
        if RASTERIO_DISPONIVEL:
            self.dataset = rasterio.open(str(self.caminho))
            self.perfil = self.dataset.profile
        elif GDAL_DISPONIVEL:
            self.dataset = gdal.Open(str(self.caminho))
        else:
            raise ImportError("Nenhuma biblioteca de leitura GeoTIFF disponivel. "
                          "Instale rasterio: pip install rasterio")
    
    def ler_banda(self, banda: int = 1) -> np.ndarray:
        """Le uma banda especifica."""
        if RASTERIO_DISPONIVEL:
            return self.dataset.read(banda)
        elif GDAL_DISPONIVEL:
            return self.dataset.GetRasterBand(banda).ReadAsArray()
    
    def ler_todas_bandas(self) -> np.ndarray:
        """Le todas as bandas como array 3D."""
        if RASTERIO_DISPONIVEL:
            return self.dataset.read()
        return None
    
    def get_transform(self) -> Tuple:
        """Retorna transformacao afim."""
        if RASTERIO_DISPONIVEL:
            return self.dataset.transform
        elif GDAL_DISPONIVEL:
            return self.dataset.GetGeoTransform()
    
    def get_crs(self):
        """Retorna sistema de coordenadas."""
        if RASTERIO_DISPONIVEL:
            return self.dataset.crs
        return None
    
    def get_shape(self) -> Tuple[int, int]:
        """Retorna dimensoes (altura, largura)."""
        if RASTERIO_DISPONIVEL:
            return (self.dataset.height, self.dataset.width)
        elif GDAL_DISPONIVEL:
            return (self.dataset.RasterYSize, self.dataset.RasterXSize)
    
    def recortar_por_geometria(self, geometria: Dict) -> np.ndarray:
        """Recorta imagem por geometria (GeoJSON)."""
        if RASTERIO_DISPONIVEL:
            recorte, transform = mask(self.dataset, [geometria], crop=True)
            return recorte
        return None
    
    def fechar(self):
        """Fecha o dataset."""
        if RASTERIO_DISPONIVEL and self.dataset:
            self.dataset.close()
        elif GDAL_DISPONIVEL and self.dataset:
            self.dataset = None


class AnalisadorVigor:
    """
    Analisa vigor vegetacional e cruza com dados de fertilidade.
    """
    
    # Limites para classificacao de vigor (NDVI)
    LIMITE_VIGOR_BAIXO = 0.2
    LIMITE_VIGOR_MEDIO = 0.4
    LIMITE_VIGOR_ALTO = 0.6
    
    def __init__(self):
        self.calculador = CalculadorIndices()
        self.series_temporais: Dict[int, SerieTemporalVigor] = {}
        self.anomalias: List[AnomaliaVigor] = []
    
    def processar_geotiff(self, caminho: Union[str, Path],
                          indice: str = "NDVI",
                          data: Optional[str] = None) -> Dict:
        """
        Processa um arquivo GeoTIFF e extrai estatisticas de vigor.
        
        Args:
            caminho: Caminho do arquivo GeoTIFF
            indice: Nome do indice contido no arquivo
            data: Data da imagem (ISO format)
            
        Returns:
            Dict com estatisticas e array do indice
        """
        leitor = LeitorGeoTIFF(caminho)
        
        try:
            array = leitor.ler_banda(1)
            transform = leitor.get_transform()
            crs = leitor.get_crs()
            shape = leitor.get_shape()
            
            # Mascara de valores validos
            valid_mask = (array > -1) & (array < 1) & np.isfinite(array)
            valores_validos = array[valid_mask]
            
            estatisticas = {
                'indice': indice,
                'data': data or datetime.now().isoformat(),
                'shape': shape,
                'crs': str(crs) if crs else None,
                'estatisticas': {
                    'media': float(np.mean(valores_validos)),
                    'mediana': float(np.median(valores_validos)),
                    'desvio': float(np.std(valores_validos)),
                    'min': float(np.min(valores_validos)),
                    'max': float(np.max(valores_validos)),
                    'percentil_25': float(np.percentile(valores_validos, 25)),
                    'percentil_75': float(np.percentile(valores_validos, 75)),
                    'n_pixels_validos': int(np.sum(valid_mask)),
                    'n_pixels_total': array.size
                },
                'array': array,
                'valid_mask': valid_mask,
                'transform': transform
            }
            
            return estatisticas
            
        finally:
            leitor.fechar()
    
    def classificar_vigor(self, valor_ndvi: float) -> str:
        """Classifica nivel de vigor baseado em NDVI."""
        if valor_ndvi < self.LIMITE_VIGOR_BAIXO:
            return "muito_baixo"
        elif valor_ndvi < self.LIMITE_VIGOR_MEDIO:
            return "baixo"
        elif valor_ndvi < self.LIMITE_VIGOR_ALTO:
            return "medio"
        else:
            return "alto"
    
    def calcular_indices_completos(self, bandas: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Calcula todos os indices de vegetacao a partir de bandas espectrais.
        
        Args:
            bandas: Dict com arrays das bandas (nir, red, green, blue, etc.)
            
        Returns:
            Dict com todos os indices calculados
        """
        indices = {}
        
        nir = bandas.get('nir')
        red = bandas.get('red')
        green = bandas.get('green')
        blue = bandas.get('blue')
        red_edge = bandas.get('red_edge')
        swir1 = bandas.get('swir1')
        swir2 = bandas.get('swir2')
        
        if nir is not None and red is not None:
            indices['NDVI'] = self.calculador.calcular_ndvi(nir, red)
            indices['SAVI'] = self.calculador.calcular_savi(nir, red)
            indices['MSAVI'] = self.calculador.calcular_msavi(nir, red)
            indices['DVI'] = self.calculador.calcular_dvi(nir, red)
            indices['RVI'] = self.calculador.calcular_rvi(nir, red)
            indices['IPVI'] = self.calculador.calcular_ipvi(nir, red)
            indices['OSAVI'] = self.calculador.calcular_osavi(nir, red)
            
            if blue is not None:
                indices['EVI'] = self.calculador.calcular_evi(nir, red, blue)
            
            if green is not None:
                indices['GNDVI'] = self.calculador.calcular_gndvi(nir, green)
                indices['GCI'] = self.calculador.calcular_gci(nir, green)
                indices['CVI'] = self.calculador.calcular_cvi(nir, red, green)
                indices['TVI'] = self.calculador.calcular_tvi(nir, red)
            
            if red_edge is not None:
                indices['NDRE'] = self.calculador.calcular_ndre(nir, red_edge)
                indices['RECI'] = self.calculador.calcular_reci(nir, red_edge)
                indices['MTCI'] = self.calculador.calcular_mtci(nir, red_edge, red)
        
        if nir is not None and swir1 is not None:
            indices['NDWI'] = self.calculador.calcular_ndwi(nir, swir1)
        
        if nir is not None and swir2 is not None:
            indices['NBR'] = self.calculador.calcular_nbr(nir, swir2)
        
        if swir1 is not None and swir2 is not None:
            indices['NBR2'] = self.calculador.calcular_nbr2(swir1, swir2)
        
        if green is not None and swir1 is not None:
            indices['NDSI'] = self.calculador.calcular_ndsi(green, swir1)
        
        if nir is not None and red is not None:
            indices['BAI'] = self.calculador.calcular_bai(nir, red)
        
        return indices
    
    def cruzar_vigor_fertilidade(self, 
                                  raster_vigor: np.ndarray,
                                  raster_zonas: np.ndarray,
                                  perfis_zonas: Dict,
                                  atributo_fertilidade: str = 'p_mg_dm3') -> Dict:
        """
        Cruza dados de vigor (NDVI) com fertilidade por zona.
        
        Args:
            raster_vigor: Array 2D com valores de vigor
            raster_zonas: Array 2D com IDs das zonas de manejo
            perfis_zonas: Dict com perfis de fertilidade por zona
            atributo_fertilidade: Atributo de fertilidade para correlacao
            
        Returns:
            Dict com analise de correlacao por zona
        """
        resultados = {}
        
        zonas_unicas = np.unique(raster_zonas[raster_zonas >= 0])
        
        for zona_id in zonas_unicas:
            mascara_zona = raster_zonas == zona_id
            vigor_zona = raster_vigor[mascara_zona]
            vigor_zona = vigor_zona[np.isfinite(vigor_zona)]
            
            if len(vigor_zona) == 0:
                continue
            
            # Estatisticas de vigor na zona
            stats_vigor = {
                'media': float(np.mean(vigor_zona)),
                'mediana': float(np.median(vigor_zona)),
                'desvio': float(np.std(vigor_zona)),
                'min': float(np.min(vigor_zona)),
                'max': float(np.max(vigor_zona))
            }
            
            # Fertilidade da zona
            fertilidade = perfis_zonas.get(int(zona_id), {}).get(atributo_fertilidade, {})
            valor_fertilidade = fertilidade.get('media', 0) if isinstance(fertilidade, dict) else fertilidade
            
            # Classificacao de vigor
            classificacao = self.classificar_vigor(stats_vigor['media'])
            
            # Deteccao de anomalia: vigor baixo com fertilidade alta
            anomalia = None
            if classificacao in ['baixo', 'muito_baixo'] and valor_fertilidade > 20:
                anomalia = {
                    'tipo': 'vigor_baixo_fertilidade_alta',
                    'severidade': 'moderada',
                    'mensagem': 'Vigor abaixo do esperado para nivel de fertilidade.',
                    'possiveis_causas': [
                        'Problemas hidricos (deficit ou excesso)',
                        'Ataque de pragas/doencas',
                        'Compactacao do solo',
                        'Problemas de germinacao/estabelecimento',
                        'Variedade inadequada ao ambiente'
                    ]
                }
            elif classificacao == 'alto' and valor_fertilidade < 10:
                anomalia = {
                    'tipo': 'vigor_alto_fertilidade_baixa',
                    'severidade': 'leve',
                    'mensagem': 'Vigor alto apesar de fertilidade baixa.',
                    'possiveis_causas': [
                        'Eficiencia alta de uso de nutrientes',
                        'Residuos de cultura anterior',
                        'Fixacao biologica de nitrogenio',
                        'Erro de amostragem na fertilidade'
                    ]
                }
            
            resultados[int(zona_id)] = {
                'vigor': stats_vigor,
                'fertilidade': {
                    'atributo': atributo_fertilidade,
                    'valor': valor_fertilidade
                },
                'classificacao_vigor': classificacao,
                'anomalia': anomalia,
                'n_pixels': int(np.sum(mascara_zona))
            }
        
        return resultados
    
    def detectar_anomalias_temporais(self,
                                      serie_vigor: List[float],
                                      datas: List[str],
                                      zona_id: int,
                                      indice: str = "NDVI") -> List[AnomaliaVigor]:
        """
        Detecta anomalias em serie temporal de vigor.
        
        Args:
            serie_vigor: Lista de valores de vigor
            datas: Lista de datas correspondentes
            zona_id: ID da zona
            indice: Nome do indice
            
        Returns:
            Lista de anomalias detectadas
        """
        if len(serie_vigor) < 3:
            return []
        
        anomalias = []
        serie = np.array(serie_vigor)
        media = np.mean(serie)
        desvio = np.std(serie)
        
        if desvio == 0:
            return []
        
        for i, (valor, data) in enumerate(zip(serie_vigor, datas)):
            z_score = (valor - media) / desvio
            
            if abs(z_score) > 2.0:  # Mais de 2 desvios padrao
                desvio_pct = ((valor - media) / media) * 100 if media != 0 else 0
                
                if z_score < 0:
                    tipo = 'negativa'
                    severidade = 'grave' if z_score < -3 else 'moderada' if z_score < -2.5 else 'leve'
                else:
                    tipo = 'positiva'
                    severidade = 'grave' if z_score > 3 else 'moderada' if z_score > 2.5 else 'leve'
                
                anomalia = AnomaliaVigor(
                    zona_id=zona_id,
                    data=data,
                    indice=indice,
                    valor_observado=round(valor, 4),
                    valor_esperado=round(media, 4),
                    desvio_percentual=round(desvio_pct, 2),
                    tipo=tipo,
                    severidade=severidade,
                    possiveis_causas=self._inferir_causas_anomalia(tipo, severidade, indice)
                )
                anomalias.append(anomalia)
                self.anomalias.append(anomalia)
        
        return anomalias
    
    def _inferir_causas_anomalia(self, tipo: str, severidade: str, 
                                  indice: str) -> List[str]:
        """Infere possiveis causas baseado no tipo de anomalia."""
        causas = []
        
        if tipo == 'negativa':
            causas.extend([
                'Deficit hidrico',
                'Stresse nutricional',
                'Ataque de pragas ou doencas',
                'Danos por granizo ou vento',
                'Problemas de drenagem'
            ])
            if indice in ['NDWI', 'NDVI']:
                causas.append('Desequilibrio hidrico severo')
        else:
            causas.extend([
                'Condicoes climaticas favoraveis',
                'Irrigacao eficiente',
                'Aplicacao de fertilizante foliar',
                'Estadio fenologico de pico'
            ])
        
        if severidade == 'grave':
            causas.append('Requer visita tecnica urgente')
        
        return causas
    
    def preparar_dados_dashboard(self,
                                  resultados_zonas: Dict,
                                  series_temporais: Dict[int, SerieTemporalVigor],
                                  anomalias: List[AnomaliaVigor]) -> Dict:
        """
        Prepara dados estruturados para exportacao ao dashboard BI (Fase 6).
        
        Returns:
            Dict com dados formatados para consumo do dashboard
        """
        dados_dashboard = {
            'metadata': {
                'data_geracao': datetime.now().isoformat(),
                'versao': '1.0',
                'n_zonas': len(resultados_zonas),
                'n_series_temporais': len(series_temporais),
                'n_anomalias': len(anomalias)
            },
            'resumo_zonas': [],
            'series_temporais': [],
            'anomalias': [],
            'correlacoes': []
        }
        
        # Resumo por zona
        for zona_id, dados in resultados_zonas.items():
            resumo = {
                'zona_id': zona_id,
                'vigor_medio': dados['vigor']['media'],
                'fertilidade': dados['fertilidade']['valor'],
                'classificacao_vigor': dados['classificacao_vigor'],
                'tem_anomalia': dados['anomalia'] is not None,
                'n_pixels': dados['n_pixels']
            }
            dados_dashboard['resumo_zonas'].append(resumo)
        
        # Series temporais
        for zona_id, serie in series_temporais.items():
            serie_dict = {
                'zona_id': zona_id,
                'datas': serie.datas,
                'indices': serie.valores_medios,
                'desvios': serie.desvios,
                'n_anomalias': len(serie.anomalias)
            }
            dados_dashboard['series_temporais'].append(serie_dict)
        
        # Anomalias
        for anomalia in anomalias:
            anomalia_dict = {
                'zona_id': anomalia.zona_id,
                'data': anomalia.data,
                'indice': anomalia.indice,
                'valor_observado': anomalia.valor_observado,
                'valor_esperado': anomalia.valor_esperado,
                'desvio_percentual': anomalia.desvio_percentual,
                'tipo': anomalia.tipo,
                'severidade': anomalia.severidade,
                'possiveis_causas': anomalia.possiveis_causas
            }
            dados_dashboard['anomalias'].append(anomalia_dict)
        
        # Correlacoes vigor x fertilidade
        if resultados_zonas:
            vigores = [d['vigor']['media'] for d in resultados_zonas.values()]
            fertilidades = [d['fertilidade']['valor'] for d in resultados_zonas.values()]
            
            if len(vigores) > 2:
                correlacao = np.corrcoef(vigores, fertilidades)[0, 1]
                dados_dashboard['correlacoes'].append({
                    'tipo': 'vigor_x_fertilidade',
                    'coeficiente': round(float(correlacao), 4),
                    'interpretacao': (
                        'Forte correlacao positiva' if correlacao > 0.7
                        else 'Correlacao moderada' if correlacao > 0.4
                        else 'Correlacao fraca' if correlacao > 0.2
                        else 'Sem correlacao significativa'
                    )
                })
        
        return dados_dashboard
    
    def exportar_para_json(self, dados_dashboard: Dict, 
                           caminho_saida: Union[str, Path]) -> str:
        """
        Exporta dados do dashboard para JSON.
        
        Returns:
            Caminho do arquivo gerado
        """
        import json
        
        caminho = Path(caminho_saida)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(dados_dashboard, f, ensure_ascii=False, indent=2)
        
        return str(caminho)
    
    def exportar_series_csv(self,
                            series_temporais: Dict[int, SerieTemporalVigor],
                            caminho_saida: Union[str, Path]) -> str:
        """
        Exporta series temporais para CSV.
        
        Returns:
            Caminho do arquivo gerado
        """
        caminho = Path(caminho_saida)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        
        rows = []
        for zona_id, serie in series_temporais.items():
            for i, data in enumerate(serie.datas):
                row = {'zona_id': zona_id, 'data': data}
                for indice, valores in serie.valores_medios.items():
                    row[f'{indice}_medio'] = valores[i] if i < len(valores) else None
                for indice, desvios in serie.desvios.items():
                    row[f'{indice}_desvio'] = desvios[i] if i < len(desvios) else None
                rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(caminho, index=False, sep=';', decimal=',')
        
        return str(caminho)


# ============================================================
# FUNCOES DE CONVENIENCIA
# ============================================================

def processar_imagem_vigor(caminho_geotiff: Union[str, Path],
                            indice: str = "NDVI") -> Dict:
    """
    Processa uma imagem GeoTIFF e retorna estatisticas de vigor.
    """
    analisador = AnalisadorVigor()
    return analisador.processar_geotiff(caminho_geotiff, indice)


def calcular_todos_indices(bandas: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """
    Calcula todos os indices de vegetacao a partir de bandas espectrais.
    """
    calculador = CalculadorIndices()
    return calculador.calcular_indices_completos(bandas)


def detectar_anomalias_zona(serie_vigor: List[float],
                             datas: List[str],
                             zona_id: int) -> List[AnomaliaVigor]:
    """
    Detecta anomalias em serie temporal de uma zona.
    """
    analisador = AnalisadorVigor()
    return analisador.detectar_anomalias_temporais(serie_vigor, datas, zona_id)


def exportar_dados_bi(resultados_zonas: Dict,
                      series_temporais: Dict[int, SerieTemporalVigor],
                      anomalias: List[AnomaliaVigor],
                      caminho_json: Union[str, Path],
                      caminho_csv: Optional[Union[str, Path]] = None) -> Tuple[str, Optional[str]]:
    """
    Exporta dados completos para dashboard BI.
    
    Returns:
        Tuple: (caminho_json, caminho_csv)
    """
    analisador = AnalisadorVigor()
    dados = analisador.preparar_dados_dashboard(resultados_zonas, series_temporais, anomalias)
    
    caminho_j = analisador.exportar_para_json(dados, caminho_json)
    
    caminho_c = None
    if caminho_csv:
        caminho_c = analisador.exportar_series_csv(series_temporais, caminho_csv)
    
    return caminho_j, caminho_c

# ============================================================
# CLASSE: SerieTemporalMonitoramento
# Baseado em Mulla (2013) - Precision Agriculture
# Calculo de anomalias e medias moveis para series temporais NDVI
# ============================================================

@dataclass
class ResultadoMediaMovel:
    """Resultado do calculo de media movel."""
    data: str
    valor_original: float
    valor_suavizado: float
    residuo: float
    desvio_padrao_janela: float
    limite_superior: float
    limite_inferior: float
    eh_anomalia: bool


class SerieTemporalMonitoramento:
    """
    Monitoramento de series temporais de indices de vegetacao.
    Implementa deteccao de anomalias via media movel e desvio padrao
    conforme metodologia de Mulla (2013) para agricultura de precisao.

    Referencia:
        Mulla, D.J. (2013). Twenty five years of remote sensing in precision
        agriculture: Key advances and remaining knowledge gaps.
        Biosystems Engineering, 114(4), 358-371.
    """

    def __init__(self, janela_media_movel: int = 3, fator_desvio: float = 2.0):
        """
        Args:
            janela_media_movel: Tamanho da janela para media movel (padrao: 3)
            fator_desvio: Multiplicador do desvio padrao para limite de anomalia (padrao: 2.0)
        """
        self.janela = janela_media_movel
        self.fator_desvio = fator_desvio
        self.resultados: List[ResultadoMediaMovel] = []

    def calcular_media_movel_central(self, valores: List[float]) -> List[Optional[float]]:
        """
        Calcula media movel central (centered moving average).
        Valores nas bordas retornam None.

        Args:
            valores: Lista de valores da serie temporal

        Returns:
            Lista com medias moveis (None nas bordas)
        """
        n = len(valores)
        if n < self.janela:
            return [None] * n

        metade = self.janela // 2
        medias = [None] * n

        for i in range(metade, n - metade):
            janela = valores[i - metade:i + metade + 1]
            medias[i] = float(np.mean(janela))

        return medias

    def calcular_desvio_padrao_movel(self, valores: List[float]) -> List[Optional[float]]:
        """
        Calcula desvio padrao movel para cada janela.

        Args:
            valores: Lista de valores da serie temporal

        Returns:
            Lista com desvios padroes moveis (None nas bordas)
        """
        n = len(valores)
        if n < self.janela:
            return [None] * n

        metade = self.janela // 2
        desvios = [None] * n

        for i in range(metade, n - metade):
            janela = valores[i - metade:i + metade + 1]
            desvios[i] = float(np.std(janela, ddof=1))

        return desvios

    def detectar_anomalias_medias_moveis(
        self,
        datas: List[str],
        valores: List[float],
        nome_indice: str = "NDVI"
    ) -> Dict:
        """
        Detecta anomalias usando media movel e bandas de confianca.
        Metodologia baseada em Mulla (2013) para deteccao de desvios
        em series temporais de vegetacao.

        Args:
            datas: Lista de datas (ISO format)
            valores: Lista de valores do indice
            nome_indice: Nome do indice analisado

        Returns:
            Dict com resultados da analise
        """
        if len(datas) != len(valores):
            raise ValueError("Listas de datas e valores devem ter o mesmo tamanho")

        if len(valores) < self.janela:
            return {
                "erro": "Serie temporal muito curta para a janela especificada",
                "n_pontos": len(valores),
                "janela": self.janela
            }

        medias = self.calcular_media_movel_central(valores)
        desvios = self.calcular_desvio_padrao_movel(valores)

        self.resultados = []
        anomalias_detectadas = []

        for i, (data, valor) in enumerate(zip(datas, valores)):
            if medias[i] is None or desvios[i] is None:
                continue

            residuo = valor - medias[i]
            limite_sup = medias[i] + (self.fator_desvio * desvios[i])
            limite_inf = medias[i] - (self.fator_desvio * desvios[i])
            eh_anomalia = valor > limite_sup or valor < limite_inf

            resultado = ResultadoMediaMovel(
                data=data,
                valor_original=round(valor, 4),
                valor_suavizado=round(medias[i], 4),
                residuo=round(residuo, 4),
                desvio_padrao_janela=round(desvios[i], 4),
                limite_superior=round(limite_sup, 4),
                limite_inferior=round(limite_inf, 4),
                eh_anomalia=eh_anomalia
            )
            self.resultados.append(resultado)

            if eh_anomalia:
                severidade = "grave" if abs(residuo) > 3 * desvios[i] else "moderada"
                anomalias_detectadas.append({
                    "data": data,
                    "valor_observado": round(valor, 4),
                    "valor_esperado": round(medias[i], 4),
                    "residuo": round(residuo, 4),
                    "severidade": severidade,
                    "tipo": "positiva" if residuo > 0 else "negativa",
                    "nome_indice": nome_indice
                })

        # Estatisticas resumidas
        residuos = [r.residuo for r in self.resultados]
        valores_suavizados = [r.valor_suavizado for r in self.resultados]

        return {
            "nome_indice": nome_indice,
            "janela_media_movel": self.janela,
            "fator_desvio": self.fator_desvio,
            "n_pontos_analisados": len(self.resultados),
            "n_anomalias": len(anomalias_detectadas),
            "anomalias": anomalias_detectadas,
            "estatisticas": {
                "media_residuos": round(float(np.mean(residuos)), 4) if residuos else 0,
                "desvio_residuos": round(float(np.std(residuos, ddof=1)), 4) if residuos else 0,
                "min_valor_suavizado": round(min(valores_suavizados), 4) if valores_suavizados else 0,
                "max_valor_suavizado": round(max(valores_suavizados), 4) if valores_suavizados else 0
            },
            "resultados_detalhados": [
                {
                    "data": r.data,
                    "valor_original": r.valor_original,
                    "valor_suavizado": r.valor_suavizado,
                    "residuo": r.residuo,
                    "limite_superior": r.limite_superior,
                    "limite_inferior": r.limite_inferior,
                    "eh_anomalia": r.eh_anomalia
                }
                for r in self.resultados
            ]
        }

    def calcular_tendencia_linear(self, valores: List[float]) -> Dict:
        """
        Calcula tendencia linear da serie temporal via regressao simples.

        Args:
            valores: Lista de valores

        Returns:
            Dict com coeficiente angular, intercepto e R2
        """
        if len(valores) < 2:
            return {"erro": "Minimo 2 pontos necessarios"}

        x = np.arange(len(valores))
        y = np.array(valores)

        # Regressao linear: y = ax + b
        n = len(x)
        a = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - (np.sum(x))**2)
        b = (np.sum(y) - a * np.sum(x)) / n

        # R2
        y_pred = a * x + b
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        return {
            "coeficiente_angular": round(float(a), 6),
            "intercepto": round(float(b), 4),
            "r_quadrado": round(float(r_squared), 4),
            "tendencia": "crescente" if a > 0.001 else "decrescente" if a < -0.001 else "estavel",
            "n_pontos": n
        }

    def salvar_no_banco(
        self,
        conn: sqlite3.Connection,
        talhao_id: int,
        safra: str,
        resultados: Dict
    ) -> bool:
        """
        Persiste resultados da analise temporal no banco de dados.
        Preparado para integracao com db_schema.py.

        Args:
            conn: Conexao SQLite ativa
            talhao_id: ID do talhao monitorado
            safra: Identificacao da safra (ex: "2025/2026")
            resultados: Dict retornado por detectar_anomalias_medias_moveis

        Returns:
            True se sucesso, False caso contrario
        """
        try:
            cursor = conn.cursor()

            # Criar tabela se nao existir (compativel com db_schema.py)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monitoramento_temporal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    talhao_id INTEGER,
                    safra TEXT,
                    nome_indice TEXT,
                    janela_media_movel INTEGER,
                    fator_desvio REAL,
                    n_pontos INTEGER,
                    n_anomalias INTEGER,
                    estatisticas_json TEXT,
                    data_analise TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(talhao_id) REFERENCES talhoes(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monitoramento_anomalias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    monitoramento_id INTEGER,
                    data TEXT,
                    valor_observado REAL,
                    valor_esperado REAL,
                    residuo REAL,
                    severidade TEXT,
                    tipo TEXT,
                    nome_indice TEXT,
                    FOREIGN KEY(monitoramento_id) REFERENCES monitoramento_temporal(id)
                )
            """)

            # Inserir resultado principal
            estatisticas_json = json.dumps(resultados.get("estatisticas", {}))
            cursor.execute("""
                INSERT INTO monitoramento_temporal 
                (talhao_id, safra, nome_indice, janela_media_movel, fator_desvio, 
                 n_pontos, n_anomalias, estatisticas_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                talhao_id, safra, resultados.get("nome_indice", "NDVI"),
                resultados.get("janela_media_movel", 3),
                resultados.get("fator_desvio", 2.0),
                resultados.get("n_pontos_analisados", 0),
                resultados.get("n_anomalias", 0),
                estatisticas_json
            ))

            monitoramento_id = cursor.lastrowid

            # Inserir anomalias
            for anomalia in resultados.get("anomalias", []):
                cursor.execute("""
                    INSERT INTO monitoramento_anomalias
                    (monitoramento_id, data, valor_observado, valor_esperado, 
                     residuo, severidade, tipo, nome_indice)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    monitoramento_id, anomalia.get("data"),
                    anomalia.get("valor_observado"),
                    anomalia.get("valor_esperado"),
                    anomalia.get("residuo"),
                    anomalia.get("severidade"),
                    anomalia.get("tipo"),
                    anomalia.get("nome_indice", "NDVI")
                ))

            conn.commit()
            return True

        except Exception as e:
            logging.info(f"[ERRO] Falha ao salvar monitoramento: {e}")
            return False


# ============================================================
# FUNCOES DE CONVENIENCIA
# ============================================================

def analisar_serie_temporal(
    datas: List[str],
    valores: List[float],
    janela: int = 3,
    fator_desvio: float = 2.0,
    nome_indice: str = "NDVI"
) -> Dict:
    """
    Funcao de conveniencia para analise rapida de serie temporal.

    Args:
        datas: Lista de datas ISO
        valores: Lista de valores do indice
        janela: Tamanho da janela de media movel
        fator_desvio: Fator para limite de anomalia
        nome_indice: Nome do indice

    Returns:
        Dict com resultados completos da analise
    """
    monitor = SerieTemporalMonitoramento(janela_media_movel=janela, fator_desvio=fator_desvio)
    return monitor.detectar_anomalias_medias_moveis(datas, valores, nome_indice)


def comparar_safras(
    safra_atual: Dict[str, List[float]],
    safra_historica: Dict[str, List[float]],
    nome_indice: str = "NDVI"
) -> Dict:
    """
    Compara serie temporal da safra atual contra media historica.
    Util para identificar se a safra atual esta acima/abaixo do esperado.

    Args:
        safra_atual: Dict com 'datas' e 'valores'
        safra_historica: Dict com 'datas' e 'valores' (media historica)
        nome_indice: Nome do indice

    Returns:
        Dict com comparacao e desvios
    """
    datas_atual = safra_atual.get("datas", [])
    valores_atual = safra_atual.get("valores", [])
    valores_hist = safra_historica.get("valores", [])

    if len(valores_atual) != len(valores_hist):
        return {"erro": "Series temporais de tamanhos diferentes"}

    desvios = []
    for i, (va, vh) in enumerate(zip(valores_atual, valores_hist)):
        desvio = va - vh
        desvios.append({
            "data": datas_atual[i] if i < len(datas_atual) else "",
            "valor_atual": round(va, 4),
            "valor_historico": round(vh, 4),
            "desvio": round(desvio, 4),
            "desvio_percentual": round((desvio / vh * 100), 2) if vh != 0 else 0
        })

    return {
        "nome_indice": nome_indice,
        "n_pontos": len(desvios),
        "desvio_medio": round(float(np.mean([d["desvio"] for d in desvios])), 4),
        "desvio_maximo": round(max([abs(d["desvio"]) for d in desvios]), 4),
        "comparacao": desvios
    }

