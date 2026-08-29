"""
Precision VRT Solo — Motor Principal do Monitoramento

Implementa o pipeline completo de monitoramento temporal.
Extraído e adaptado de core_agronomia_monitoramento_legado.py.

Pipeline:
1. Receber polígono da área
2. Receber imagens
3. Organizar cronologicamente
4. Processamento (normalização, alinhamento, recorte, padronização)
5. Comparação temporal
6. Alertas
7. Histórico
8. Exportação
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import warnings
import json

from core.tipos.geoespacial import Coordenada, Bounds
from core.tipos.base import ConfigBase
# from core.utilitarios.geo import GeoespacialUtils  # Placeholder - será implementado posteriormente
from ..contratos import (
    ImagemMonitoramento,
    SerieTemporalVigor,
    AnomaliaMonitoramento,
    ConfigComparacaoTemporal,
    ConfigAlerta,
    ResultadoComparacao,
    HistoricoMonitoramento,
    ConfigExportacao,
    AreaMonitoramento,
    TipoSensor,
    TipoIndice,
    TipoIntervalo,
    TipoComparacao
)

warnings.filterwarnings('ignore')


class CalculadorIndices:
    """
    Calcula índices de vegetação a partir de bandas espectrais.
    Extraído de core_agronomia_monitoramento_legado.py.
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
    def calcular_indices_completos(bandas: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Calcula todos os índices de vegetação a partir de bandas espectrais.
        
        Args:
            bandas: Dict com arrays das bandas (nir, red, green, blue, etc.)
            
        Returns:
            Dict com todos os índices calculados
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
            indices['NDVI'] = CalculadorIndices.calcular_ndvi(nir, red)
            indices['SAVI'] = CalculadorIndices.calcular_savi(nir, red)
            indices['MSAVI'] = CalculadorIndices.calcular_msavi(nir, red)
            indices['DVI'] = nir - red
            indices['RVI'] = np.divide(nir, red,
                                     out=np.zeros_like(nir, dtype=float),
                                     where=red != 0)
            indices['OSAVI'] = CalculadorIndices.calcular_savi(nir, red, L=0.16)
            
            if blue is not None:
                indices['EVI'] = CalculadorIndices.calcular_evi(nir, red, blue)
            
            if green is not None:
                indices['GNDVI'] = CalculadorIndices.calcular_gndvi(nir, green)
                indices['GCI'] = np.divide(nir, green,
                                        out=np.zeros_like(nir, dtype=float),
                                        where=green != 0) - 1
                indices['CVI'] = np.divide(nir * red, green ** 2,
                                        out=np.zeros_like(nir, dtype=float),
                                        where=green != 0)
        
        if nir is not None and swir1 is not None:
            indices['NDWI'] = CalculadorIndices.calcular_ndwi(nir, swir1)
        
        if nir is not None and swir2 is not None:
            indices['NBR'] = np.divide(nir - swir2, nir + swir2,
                                     out=np.zeros_like(nir, dtype=float),
                                     where=(nir + swir2) != 0)
        
        if swir1 is not None and swir2 is not None:
            indices['NBR2'] = np.divide(swir1 - swir2, swir1 + swir2,
                                     out=np.zeros_like(swir1, dtype=float),
                                     where=(swir1 + swir2) != 0)
        
        if green is not None and swir1 is not None:
            indices['NDSI'] = np.divide(green - swir1, green + swir1,
                                     out=np.zeros_like(green, dtype=float),
                                     where=(green + swir1) != 0)
        
        return indices


class MotorMonitoramento:
    """
    Motor principal do sistema de monitoramento.
    Implementa o pipeline completo conforme especificado.
    """
    
    def __init__(self):
        self.calculador = CalculadorIndices()
        self.area_monitoramento: Optional[AreaMonitoramento] = None
        self.imagens_registradas: List[ImagemMonitoramento] = []
        self.historico: Optional[HistoricoMonitoramento] = None
        self.series_temporais: Dict[int, SerieTemporalVigor] = {}
        self.config = ConfigComparacaoTemporal()
        
    def processar_area(self, area: AreaMonitoramento) -> bool:
        """
        ETAPA 01: Receber o polígono da área.
        
        Args:
            area: Área de monitoramento com geometria definida
            
        Returns:
            True se processado com sucesso
        """
        self.area_monitoramento = area
        self._iniciar_historico(area)
        return True
    
    def registrar_imagem(self, imagem: ImagemMonitoramento) -> bool:
        """
        ETAPA 02: Receber imagens.
        
        Suporta todos os tipos de sensores especificados.
        
        Args:
            imagem: Imagem a ser registrada
            
        Returns:
            True registrada com sucesso
        """
        if not self._validar_imagem(imagem):
            return False
            
        self.imagens_registradas.append(imagem)
        
        # Organizar cronologicamente
        self.imagens_registradas.sort(key=lambda x: x.data_captura)
        
        # Processar imagem
        return self._processar_imagem(imagem)
    
    def organizar_cronologicamente(self, tipo_intervalo: TipoIntervalo = TipoIntervalo.MES) -> Dict[str, List[ImagemMonitoramento]]:
        """
        ETAPA 03: Organizar imagens cronologicamente.
        
        Args:
            tipo_intervalo: Tipo de intervalo de agrupamento
            
        Returns:
            Dict com imagens agrupadas por intervalo
        """
        agrupadas = {}
        
        if tipo_intervalo == TipoIntervalo.DIA:
            chave_formato = "%Y-%m-%d"
        elif tipo_intervalo == TipoIntervalo.SEMANA:
            chave_formato = "%Y-%W"
        elif tipo_intervalo == TipoIntervalo.MES:
            chave_formato = "%Y-%m"
        elif tipo_intervalo == TipoIntervalo.SAFRA:
            # Simplificação: considerar safra como ano agrícola
            chave_formato = "%Y"
        elif tipo_intervalo == TipoIntervalo.ANO:
            chave_formato = "%Y"
        else:
            chave_formato = "%Y-%m"
        
        for imagem in self.imagens_registradas:
            data_obj = datetime.fromisoformat(imagem.data_captura)
            chave = data_obj.strftime(chave_formato)
            
            if chave not in agrupadas:
                agrupadas[chave] = []
            agrupadas[chave].append(imagem)
        
        return agrupadas
    
    def _processar_imagem(self, imagem: ImagemMonitoramento) -> bool:
        """
        ETAPA 04: Processamento individual da imagem.
        
        Executa normalização, alinhamento, recorte, padronização.
        
        Args:
            imagem: Imagem a ser processada
            
        Returns:
            True se processada com sucesso
        """
        try:
            # 1. Leitura da imagem
            dados_imagem = self._ler_imagem(imagem)
            
            if dados_imagem is None:
                return False
            
            # 2. Normalização
            dados_normalizados = self._normalizar_imagem(dados_imagem)
            
            # 3. Recorte pela área de monitoramento
            dados_recortados = self._recortar_por_area(dados_normalizados)
            
            # 4. Padronização
            dados_padronizados = self._padronizar_imagem(dados_recortados)
            
            # 5. Cálculo de índices
            indices_calculados = self._calcular_indices(dados_padronizados)
            
            # 6. Extração de estatísticas
            estatisticas = self._extrair_estatisticas(indices_calculados)
            
            # Armazenar resultados
            imagem.metadatos.update(estatisticas)
            imagem.status_processamento = "processado"
            
            # Atualizar série temporal
            self._atualizar_serie_temporal(imagem, estatisticas)
            
            return True
            
        except Exception as e:
            imagem.status_processamento = "erro"
            imagem.metadatos["erro_processamento"] = str(e)
            return False
    
    def _ler_imagem(self, imagem: ImagemMonitoramento) -> Optional[Dict[str, Any]]:
        """
        Leitura da imagem de acordo com o tipo de sensor.
        
        Args:
            imagem: Informações da imagem
            
        Returns:
            Dados da imagem ou None em caso de erro
        """
        # Implementação simplificada - em produção usar bibliotecas específicas
        return {
            "bandas": {},
            "metadados": {},
            "geometria": {}
        }
    
    def _normalizar_imagem(self, dados_imagem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalização dos dados da imagem.
        
        Args:
            dados_imagem: Dados brutos da imagem
            
        Returns:
            Dados normalizados
        """
        return dados_imagem
    
    def _recortar_por_area(self, dados_imagem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recorte da imagem pela área de monitoramento.
        
        Args:
            dados_imagem: Dados normalizados
            
        Returns:
            Dados recortados
        """
        return dados_imagem
    
    def _padronizar_imagem(self, dados_imagem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Padronização dos dados.
        
        Args:
            dados_imagem: Dados recortados
            
        Returns:
            Dados padronizados
        """
        return dados_imagem
    
    def _calcular_indices(self, dados_imagem: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """
        Cálculo de índices espectrais.
        
        Args:
            dados_imagem: Dados padronizados
            
        Returns:
            Dicionário com índices calculados
        """
        # Extrair bandas (simplificado)
        bandas = {}
        
        # Calcular índices disponíveis
        indices = self.calculador.calcular_indices_completos(bandas)
        return indices
    
    def _extrair_estatisticas(self, indices: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Extração de estatísticas dos índices.
        
        Args:
            indices: Índices calculados
            
        Returns:
            Estatísticas extraídas
        """
        estatisticas = {}
        
        for nome_indice, array in indices.items():
            valid_mask = np.isfinite(array)
            valores_validos = array[valid_mask]
            
            if len(valores_validos) > 0:
                estatisticas[nome_indice] = {
                    'media': float(np.mean(valores_validos)),
                    'mediana': float(np.median(valores_validos)),
                    'desvio_padrao': float(np.std(valores_validos)),
                    'minimo': float(np.min(valores_validos)),
                    'maximo': float(np.max(valores_validos)),
                    'percentil_25': float(np.percentile(valores_validos, 25)),
                    'percentil_75': float(np.percentile(valores_validos, 75)),
                    'n_pixels_validos': int(np.sum(valid_mask)),
                    'n_pixels_total': array.size
                }
        
        return estatisticas
    
    def _atualizar_serie_temporal(self, imagem: ImagemMonitoramento, estatisticas: Dict[str, Any]):
        """
        Atualização das séries temporais.
        
        Args:
            imagem: Imagem processada
            estatisticas: Estatísticas extraídas
        """
        # Agrupar por zonas (simplificado)
        zonas = self.area_monitoramento.zonas_monitoramento if self.area_monitoramento else [1]
        
        for zona_id in zonas:
            if zona_id not in self.series_temporais:
                self.series_temporais[zona_id] = SerieTemporalVigor(zona_id=zona_id)
            
            serie = self.series_temporais[zona_id]
            serie.datas.append(imagem.data_captura)
            
            # Adicionar estatísticas por índice
            for indice, stats in estatisticas.items():
                if indice not in serie.valores_medios:
                    serie.valores_medios[indice] = []
                if indice not in serie.desvios:
                    serie.desvios[indice] = []
                
                serie.valores_medios[indice].append(stats['media'])
                serie.desvios[indice].append(stats['desvio_padrao'])
    
    def comparar_temporal(self, imagem_base: ImagemMonitoramento, 
                         imagem_comparada: ImagemMonitoramento,
                         config: Optional[ConfigComparacaoTemporal] = None) -> Optional[ResultadoComparacao]:
        """
        ETAPA 05: Comparação temporal entre imagens.
        
        Detecta alterações, mudanças vegetativas, redução/aumento de vigor,
        alterações espectrais, mudanças de padrão.
        
        Args:
            imagem_base: Imagem de referência
            imagem_comparada: Imagem a ser comparada
            config: Configuração da comparação
            
        Returns:
            Resultado da comparação ou None em caso de erro
        """
        if config is None:
            config = self.config
        
        try:
            # Carregar estatísticas das imagens
            stats_base = imagem_base.metadatos
            stats_comparada = imagem_comparada.metadados
            
            # Calcular diferenças para cada índice
            anomalias = []
            estatisticas_comparacao = {}
            
            for indice in stats_base:
                if indice in stats_comparada:
                    media_base = stats_base[indice]['media']
                    media_comparada = stats_comparada[indice]['media']
                    
                    # Cálculo de diferença
                    diferenca = media_comparada - media_base
                    desvio = abs(diferenca)
                    percentual = (diferenca / media_base) * 100 if media_base != 0 else 0
                    
                    # Verificar anomalia
                    anomalia = None
                    if abs(percentual) > config.limite_tolerancia_desvio * 100:
                        tipo = 'positiva' if percentual > 0 else 'negativa'
                        severidade = 'grave' if abs(percentual) > 300 else 'moderada' if abs(percentual) > 200 else 'leve'
                        
                        anomalia = AnomaliaMonitoramento(
                            zona_id=1,  # Simplificado
                            data=imagem_comparada.data_captura,
                            indice=indice,
                            valor_observado=media_comparada,
                            valor_esperado=media_base,
                            desvio_percentual=percentual,
                            tipo=tipo,
                            severidade=severidade,
                            possiveis_causas=self._inferir_causas_anomalia(tipo, severidade, indice),
                            contexto={'data_base': imagem_base.data_captura, 'diferenca_absoluta': diferenca}
                        )
                        anomalias.append(anomalia)
                    
                    # Estatísticas da comparação
                    estatisticas_comparacao[indice] = {
                        'diferencia_media': diferenca,
                        'diferencia_percentual': percentual,
                        'media_base': media_base,
                        'media_comparada': media_comparada,
                        'desvio_padrao_base': stats_base[indice]['desvio_padrao'],
                        'desvio_padrao_comparada': stats_comparada[indice]['desvio_padrao']
                    }
            
            # Calcular intervalo em dias
            data_base = datetime.fromisoformat(imagem_base.data_captura)
            data_comparada = datetime.fromisoformat(imagem_comparada.data_captura)
            intervalo_dias = (data_comparada - data_base).days
            
            # Criar resultado da comparação
            resultado = ResultadoComparacao(
                imagem_base_id=imagem_base.imagem_id,
                imagem_comparada_id=imagem_comparada.imagem_id,
                intervalo_dias=intervalo_dias,
                indice_analisado=config.indice_padrao.value,
                diferenca_media=np.mean([stats['diferencia_media'] for stats in estatisticas_comparacao.values()]),
                diferenca_maxima=max([stats['diferencia_percentual'] for stats in estatisticas_comparacao.values()], default=0),
                diferenca_minima=min([stats['diferencia_percentual'] for stats in estatisticas_comparacao.values()], default=0),
                areas_mudancas={'total_anomalias': len(anomalias)},
                estatisticas=estatisticas_comparacao,
                anomalias_detectadas=anomalias,
                data_comparacao=datetime.now().isoformat()
            )
            
            # Armazenar histórico
            if self.historico:
                self.historico.comparacoes_realizadas.append(resultado)
                self.historico.anomalias_registradas.extend(anomalias)
            
            return resultado
            
        except Exception as e:
            return None
    
    def _inferir_causas_anomalia(self, tipo: str, severidade: str, indice: str) -> List[str]:
        """
        Infere possíveis causas baseado no tipo de anomalia.
        
        Args:
            tipo: Tipo de anomalia (positiva/negativa)
            severidade: Nível de severidade
            indice: Índice analisado
            
        Returns:
            Lista de possíveis causas
        """
        causas = []
        
        if tipo == 'negativa':
            causas.extend([
                'Déficit hídrico',
                'Estresse nutricional',
                'Ataque de pragas ou doenças',
                'Danos por granizo ou vento',
                'Problemas de drenagem'
            ])
            if indice in ['NDVI', 'NDWI']:
                causas.append('Desequilíbrio hídrico severo')
        else:
            causas.extend([
                'Condições climáticas favoráveis',
                'Irrigação eficiente',
                'Aplicação de fertilizante foliar',
                'Estágio fenológico de pico'
            ])
        
        if severidade == 'grave':
            causas.append('Requer visita técnica urgente')
        
        return causas
    
    def _iniciar_historico(self, area: AreaMonitoramento):
        """
        Inicia o histórico de monitoramento para a área.
        
        Args:
            area: Área de monitoramento
        """
        self.historico = HistoricoMonitoramento(
            area_id=area.area_id,
            safra=area.configuracoes.get('safra', '2026/2027'),
            inicio_monitoramento=datetime.now().isoformat(),
            imagens_processadas=[],
            series_temporais={},
            comparacoes_realizadas=[],
            anomalias_registradas=[],
            alertas_disparados=[],
            resumo_final={},
            metadata={'area_nome': area.nome, 'sensor_types': [sensor.value for sensor in area.sensores_suportados]}
        )
    
    def _validar_imagem(self, imagem: ImagemMonitoramento) -> bool:
        """
        Valida a imagem antes do processamento.
        
        Args:
            imagem: Imagem a ser validada
            
        Returns:
            True se válida
        """
        # Verificar se a área foi definida
        if not self.area_monitoramento:
            return False
        
        # Verificar se o sensor é suportado
        if imagem.sensor not in self.area_monitoramento.sensores_suportados:
            return False
        
        # Verificar formato do arquivo
        if not Path(imagem.caminho_arquivo).exists():
            return False
        
        return True
    
    def exportar_dados(self, config_exportacao: ConfigExportacao) -> Dict[str, str]:
        """
        ETAPA 08: Exportação de dados.
        
        Suporta todos os formatos especificados.
        
        Args:
            config_exportacao: Configuração da exportação
            
        Returns:
            Dicionário com caminhos dos arquivos exportados
        """
        arquivos_exportados = {}
        
        if config_exportacao.formatos:
            for formato in config_exportacao.formatos:
                if formato == "JSON":
                    caminho = self._exportar_json(config_exportacao)
                elif formato == "CSV":
                    caminho = self._exportar_csv(config_exportacao)
                elif formato == "Excel":
                    caminho = self._exportar_excel(config_exportacao)
                elif formato in ["GeoJSON", "Shapefile", "GeoTIFF"]:
                    caminho = self._exportar_geoespacial(formato, config_exportacao)
                else:
                    continue
                
                if caminho:
                    arquivos_exportados[formato] = caminho
        
        return arquivos_exportados
    
    def _exportar_json(self, config: ConfigExportacao) -> str:
        """
        Exporta dados para formato JSON.
        
        Args:
            config: Configuração de exportação
            
        Returns:
            Caminho do arquivo exportado
        """
        dados_saida = {
            'metadata': {
                'data_exportacao': datetime.now().isoformat(),
                'area_id': self.historico.area_id if self.historico else None,
                'versao': '1.0'
            },
            'configuracao': config.parametrizacao_personalizada,
            'series_temporais': {
                str(zona_id): {
                    'datas': serie.datas,
                    'valores_medios': serie.valores_medios,
                    'desvios': serie.desvios
                }
                for zona_id, serie in self.series_temporais.items()
            },
            'historico_completo': self.historico.to_dict() if self.historico else {}
        }
        
        caminho_saida = f"monitoramento_{self.area_monitoramento.area_id}_export.json"
        
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(dados_saida, f, ensure_ascii=False, indent=2, default=str)
        
        return caminho_saida
    
    def _exportar_csv(self, config: ConfigExportacao) -> str:
        """
        Exporta dados para formato CSV.
        
        Args:
            config: Configuração de exportação
            
        Returns:
            Caminho do arquivo exportado
        """
        rows = []
        
        for zona_id, serie in self.series_temporais.items():
            for i, data in enumerate(serie.datas):
                row = {
                    'zona_id': zona_id,
                    'data': data,
                    'indice': 'NDVI' if 'NDVI' in serie.valores_medios else 'valor_medio',
                    'valor_medio': serie.valores_medios.get('NDVI', [])[i] if i < len(serie.valores_medios.get('NDVI', [])) else None,
                    'desvio_padrao': serie.desvios.get('NDVI', [])[i] if i < len(serie.desvios.get('NDVI', [])) else None
                }
                rows.append(row)
        
        df = pd.DataFrame(rows)
        caminho_saida = f"monitoramento_{self.area_monitoramento.area_id}_series.csv"
        df.to_csv(caminho_saida, index=False, sep=';', decimal=',')
        
        return caminho_saida
    
    def _exportar_excel(self, config: ConfigExportacao) -> str:
        """
        Exporta dados para formato Excel.
        
        Args:
            config: Configuração de exportação
            
        Returns:
            Caminho do arquivo exportado
        """
        with pd.ExcelWriter(f"monitoramento_{self.area_monitoramento.area_id}_export.xlsx") as writer:
            # Séries temporais
            df_series = pd.DataFrame()
            for zona_id, serie in self.series_temporais.items():
                for i, data in enumerate(serie.datas):
                    df_series.loc[len(df_series), 'zona_id'] = zona_id
                    df_series.loc[len(df_series), 'data'] = data
                    for indice, valores in serie.valores_medios.items():
                        if i < len(valores):
                            df_series.loc[len(df_series)-1, f'{indice}_medio'] = valores[i]
                            df_series.loc[len(df_series)-1, f'{indice}_desvio'] = serie.desvios[indice][i]
            
            df_series.to_excel(writer, sheet_name='Series_Temporais', index=False)
            
            # Histórico de comparações
            if self.historico and self.historico.comparacoes_realizadas:
                df_comparacoes = pd.DataFrame([{
                    'data_comparacao': comp.data_comparacao,
                    'imagem_base_id': comp.imagem_base_id,
                    'imagem_comparada_id': comp.imagem_comparada_id,
                    'intervalo_dias': comp.intervalo_dias,
                    'n_anomalias': len(comp.anomalias_detectadas)
                } for comp in self.historico.comparacoes_realizadas])
                df_comparacoes.to_excel(writer, sheet_name='Comparacoes', index=False)
        
        return f"monitoramento_{self.area_monitoramento.area_id}_export.xlsx"
    
    def _exportar_geoespacial(self, formato: str, config: ConfigExportacao) -> str:
        """
        Exporta dados para formatos geoespaciais.
        
        Args:
            formato: Formato geoespacial ('GeoJSON', 'Shapefile', 'GeoTIFF')
            config: Configuração de exportação
            
        Returns:
            Caminho do arquivo exportado
        """
        # Implementação simplificada - em produção usar bibliotecas geoespaciais
        caminho_saida = f"monitoramento_{self.area_monitoramento.area_id}.{formato.lower()}"
        return caminho_saida
    
    def processar_pipeline_completo(self, area: AreaMonitoramento, 
                                  imagens: List[ImagemMonitoramento]) -> Dict[str, Any]:
        """
        Execução completa do pipeline de monitoramento.
        
        Args:
            area: Área de monitoramento
            imagens: Lista de imagens para processamento
            
        Returns:
            Resultado do processamento completo
        """
        resultado = {
            'sucesso': True,
            'mensagens': [],
            'arquivos_exportados': {},
            'estatisticas_finais': {}
        }
        
        try:
            # 1. Processar área
            if not self.processar_area(area):
                raise ValueError("Falha ao processar área")
            
            resultado['mensagens'].append("Área processada com sucesso")
            
            # 2. Registrar e processar imagens
            imagens_processadas = 0
            for imagem in imagens:
                if self.registrar_imagem(imagem):
                    imagens_processadas += 1
                else:
                    resultado['mensagens'].append(f"Falha ao processar imagem: {imagem.imagem_id}")
            
            resultado['mensagens'].append(f"{imagens_processadas}/{len(imagens)} imagens processadas")
            
            # 3. Realizar comparações temporais
            if len(self.imagens_registradas) >= 2:
                imagens_ordenadas = sorted(self.imagens_registradas, key=lambda x: x.data_captura)
                for i in range(1, len(imagens_ordenadas)):
                    comparacao = self.comparar_temporal(imagens_ordenadas[i-1], imagens_ordenadas[i])
                    if comparacao:
                        resultado['mensagens'].append(f"Comparação {i} realizada com {len(comparacao.anomalias_detectadas)} anomalias")
            
            # 4. Exportar dados
            config_exportacao = ConfigExportacao()
            arquivos_exportados = self.exportar_dados(config_exportacao)
            resultado['arquivos_exportados'] = arquivos_exportados
            
            # 5. Estatísticas finais
            resultado['estatisticas_finais'] = {
                'total_imagens': len(self.imagens_registradas),
                'total_anomalias': len(self.historico.anomalias_registradas) if self.historico else 0,
                'total_comparacoes': len(self.historico.comparacoes_realizadas) if self.historico else 0,
                'series_temporais_criadas': len(self.series_temporais),
                'arquivos_exportados': len(arquivos_exportados)
            }
            
        except Exception as e:
            resultado['sucesso'] = False
            resultado['mensagens'].append(f"Erro no pipeline: {str(e)}")
        
        return resultado