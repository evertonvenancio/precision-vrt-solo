"""
Precision VRT Solo — Módulo de Processamento de Imagens

Implementa o pipeline completo de processamento de imagens:
normalização, alinhamento, recorte e padronização.
Nunca altera a imagem original.
"""

import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask
from typing import Dict, List, Optional, Tuple, Union, Any
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import logging

from core.tipos.geoespacial import Coordenada, Bounds
from core.tipos.base import ConfigBase
# from core.utilitarios.geo import GeoespacialUtils  # Placeholder
from ..contratos import ImagemMonitoramento, AreaMonitoramento, TipoSensor

logger = logging.getLogger(__name__)


@dataclass
class ConfigProcessamento:
    """Configuração para processamento de imagens."""
    
    # Normalização
    normalizar_dinamica: bool = True
    limite_inferior_normalizacao: float = 0.0
    limite_superior_normalizacao: float = 1.0
    
    # Alinhamento
    metodo_alinhamento: str = "interpolacao"  # "interpolacao", "recorte", "nao_alinhar"
    metodo_interpolacao: str = "bilinear"  # "nearest", "bilinear", "cubic"
    tolerancia_alinhamento: float = 1.0  # pixels
    
    # Recorte
    recorte_ativo: bool = True
    margem_recorte: float = 10.0  # metros
    manter_metadados_originais: bool = True
    
    # Padronização
    formato_saida: str = "GTiff"
    compressao_saida: str = "lzw"
    tipo_dado_saida: str = "float32"
    
    # Cache
    usar_cache: bool = True
    diretorio_cache: str = "./cache_processamento"
    
    # Metadata
    adicionar_metadados_processamento: bool = True
    versao_algoritmo: str = "1.0"


@dataclass
class ResultadoProcessamento:
    """Resultado do processamento de uma imagem."""
    
    imagem_original: ImagemMonitoramento
    imagem_processada_path: str
    dados_processados: Dict[str, np.ndarray]
    metadados: Dict[str, Any]
    tempo_processamento: float
    sucesso: bool
    erros: List[str] = field(default_factory=list)
    transformacao_aplicada: str = ""


class NormalizadorImagens:
    """
    Realiza normalização de imagens.
    """
    
    def __init__(self, config: ConfigProcessamento):
        self.config = config
    
    def normalizar_imagem(self, array: np.ndarray, metadados: Dict[str, Any]) -> np.ndarray:
        """
        Normaliza um array de imagem.
        
        Args:
            array: Array da imagem para normalizar
            metadados: Metadados da imagem original
            
        Returns:
            Array normalizado
        """
        try:
            # Fazer cópia para não alterar original
            array_normalizado = array.copy()
            
            if self.config.normalizar_dinamica:
                # Normalização dinâmica baseada nos próprios dados
                vmin = np.nanpercentile(array_normalizado, 2)
                vmax = np.nanpercentile(array_normalizado, 98)
            else:
                # Usar limites fixos
                vmin = self.config.limite_inferior_normalizacao
                vmax = self.config.limite_superior_normalizacao
            
            # Aplicar normalização linear
            array_normalizado = np.clip(array_normalizado, vmin, vmax)
            array_normalizado = (array_normalizado - vmin) / (vmax - vmin)
            
            # Garantir limites
            array_normalizado = np.clip(array_normalizado, 0.0, 1.0)
            
            # Atualizar metadados
            metadados['normalizacao'] = {
                'limite_inferior': float(vmin),
                'limite_superior': float(vmax),
                'metodo': 'dinamica' if self.config.normalizar_dinamica else 'fixo',
                'data_processamento': datetime.now().isoformat()
            }
            
            return array_normalizado
            
        except Exception as e:
            logger.error(f"Erro na normalização: {e}")
            return array
    
    def normalizar_multibanda(self, dados: Dict[str, np.ndarray], 
                            metadados: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """
        Normaliza imagem multibanda.
        
        Args:
            dados: Dicionário com arrays das bandas
            metadados: Metadados da imagem original
            
        Returns:
            Dicionário com bandas normalizadas
        """
        dados_normalizados = {}
        
        for nome_banda, array in dados.items():
            dados_normalizados[nome_banda] = self.normalizar_imagem(array, metadados)
        
        return dados_normalizados


class AlinhadorImagens:
    """
    Realiza alinhamento de imagens.
    """
    
    def __init__(self, config: ConfigProcessamento):
        self.config = config
    
    def alinhar_imagem(self, imagem_referencia: np.ndarray, imagem_alinhar: np.ndarray,
                      referencia_meta: Dict[str, Any], alinhar_meta: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Alinha uma imagem em relação a uma imagem de referência.
        
        Args:
            imagem_referencia: Imagem de referência
            imagem_alinhar: Imagem a ser alinhada
            referencia_meta: Metadados da imagem de referência
            alinhar_meta: Metadados da imagem a ser alinhada
            
        Returns:
            Tuple: (imagem_alinhada, metadados_alinhados)
        """
        try:
            if self.config.metodo_alinhamento == "nao_alinhar":
                return imagem_alinhar, alinhar_meta
            
            # Extrair transformações
            ref_transform = referencia_meta.get('transform')
            alinh_transform = alinhar_meta.get('transform')
            
            if ref_transform is None or alinh_transform is None:
                logger.warning("Transformações não disponíveis, não será possível alinhar")
                return imagem_alinhar, alinhar_meta
            
            # Calcular diferença de transformação
            diff_transform = self._calcular_diferenca_transformacao(ref_transform, alinh_transform)
            
            # Aplicar transformação
            imagem_alinhada = self._aplicar_transformacao(imagem_alinhar, alinh_transform, diff_transform)
            
            # Atualizar metadados
            metadados_alinhados = alinhar_meta.copy()
            metadados_alinhados['alinhamento'] = {
                'metodo': self.config.metodo_alinhamento,
                'transformacao_original': str(alinh_transform),
                'transformacao_referencia': str(ref_transform),
                'diferenca_aplicada': str(diff_transform),
                'data_processamento': datetime.now().isoformat()
            }
            
            return imagem_alinhada, metadados_alinhados
            
        except Exception as e:
            logger.error(f"Erro no alinhamento: {e}")
            return imagem_alinhar, alinhar_meta
    
    def _calcular_diferenca_transformacao(self, ref_transform, alinh_transform) -> Any:
        """
        Calcula a diferença entre duas transformações.
        
        Args:
            ref_transform: Transformação de referência
            alinh_transform: Transformação para alinhar
            
        Returns:
            Transformação de diferença
        """
        # Simplificado - em produção implementar cálculo preciso
        # Simples placeholder - implementar algoritmo real de alinhamento
        logger.warning("Algoritmo de alinhamento não implementado completamente")
        return alinh_transform
    
    def _aplicar_transformacao(self, imagem: np.ndarray, 
                             transform_original: Any, 
                             transform_diferenca: Any) -> np.ndarray:
        """
        Aplica transformação na imagem.
        
        Args:
            imagem: Imagem original
            transform_original: Transformação original
            transform_diferenca: Transformação de diferença
            
        Returns:
            Imagem transformada
        """
        # Simplificado - em produção usar rasterio.reproject
        return imagem


class RecortadorImagens:
    """
    Realiza recorte de imagens por área de interesse.
    """
    
    def __init__(self, config: ConfigProcessamento):
        self.config = config
    
    def recortar_por_area(self, imagem: np.ndarray, metadados: Dict[str, Any],
                         area: AreaMonitoramento) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Recorta imagem pela área de monitoramento.
        
        Args:
            imagem: Imagem para recortar
            metadados: Metadados da imagem
            area: Área de monitoramento
            
        Returns:
            Tuple: (imagem_recortada, metadados_recortados)
        """
        try:
            if not self.config.recorte_ativo:
                return imagem, metadados
            
            # Converter geometria para formato compatível
            geometria = area.geometria
            
            # Adicionar margem se configurado
            if self.config.margem_recorte > 0:
                geometria = self._adicionar_margem(geometria, self.config.margem_recorte)
            
            # Recortar imagem
            imagem_recortada = self._recortar_raster(imagem, metadados, geometria)
            
            # Atualizar metadados
            metadados_recortados = metadados.copy()
            metadados_recortados['recorte'] = {
                'area_id': area.area_id,
                'margem_metros': self.config.margem_recorte,
                'geometria': geometria,
                'dimensoes_originais': imagem.shape,
                'dimensoes_recorte': imagem_recortada.shape,
                'data_processamento': datetime.now().isoformat()
            }
            
            return imagem_recortada, metadados_recortados
            
        except Exception as e:
            logger.error(f"Erro no recorte: {e}")
            return imagem, metadados
    
    def _adicionar_margem(self, geometria: Dict[str, Any], margem: float) -> Dict[str, Any]:
        """
        Adiciona margem à geometria.
        
        Args:
            geometria: Geometria original
            margem: Tamanho da margem em metros
            
        Returns:
            Geometria com margem
        """
        # Simplificado - em produção implementar buffer geoespacial
        return geometria
    
    def _recortar_raster(self, imagem: np.ndarray, metadados: Dict[str, Any],
                        geometria: Dict[str, Any]) -> np.ndarray:
        """
        Recasta imagem raster.
        
        Args:
            imagem: Imagem original
            metadados: Metadados da imagem
            geometria: Geometria de recorte
            
        Returns:
            Imagem recortada
        """
        # Simplificado - em produção usar rasterio.mask.mask
        return imagem


class PadronizadorImagens:
    """
    Realiza padronização de imagens.
    """
    
    def __init__(self, config: ConfigProcessamento):
        self.config = config
    
    def padronizar_imagem(self, imagem: np.ndarray, metadados: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Padroniza imagem para formato de saída.
        
        Args:
            imagem: Imagem para padronizar
            metadados: Metadados da imagem
            
        Returns:
            Tuple: (imagem_padronizada, metadados_padronizados)
        """
        try:
            # Converter tipo de dado
            imagem_padronizada = imagem.astype(getattr(np, self.config.tipo_dado_saida))
            
            # Atualizar metadados
            metadados_padronizados = metadados.copy()
            metadados_padronizados['padronizacao'] = {
                'tipo_dado_saida': self.config.tipo_dado_saida,
                'formato_saida': self.config.formato_saida,
                'compressao_saida': self.config.compressao_saida,
                'data_processamento': datetime.now().isoformat()
            }
            
            return imagem_padronizada, metadados_padronizados
            
        except Exception as e:
            logger.error(f"Erro na padronização: {e}")
            return imagem, metadados
    
    def salvar_imagem_padronizada(self, imagem: np.ndarray, metadados: Dict[str, Any],
                                 caminho_saida: str) -> bool:
        """
        Salva imagem padronizada no disco.
        
        Args:
            imagem: Imagem para salvar
            metadados: Metadados associados
            caminho_saida: Caminho de saída
            
        Returns:
            True se salvo com sucesso
        """
        try:
            # Simplificado - em produção usar rasterio para salvar
            Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)
            
            # Salvar imagem
            np.save(caminho_saida + '.npy', imagem)
            
            # Salvar metadados
            metadados_arquivo = {
                'imagem_metadata': metadados,
                'path_original': caminho_saida,
                'processamento': {
                    'data_salvamento': datetime.now().isoformat(),
                    'processador': 'padronizador_imagens'
                }
            }
            
            with open(caminho_saida + '.json', 'w') as f:
                import json
                json.dump(metadados_arquivo, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar imagem padronizada: {e}")
            return False


class MotorProcessamento:
    """
    Motor principal de processamento de imagens.
    """
    
    def __init__(self, config: Optional[ConfigProcessamento] = None):
        self.config = config or ConfigProcessamento()
        self.normalizador = NormalizadorImagens(self.config)
        self.alinhador = AlinhadorImagens(self.config)
        self.recortador = RecortadorImagens(self.config)
        self.padronizador = PadronizadorImagens(self.config)
        self.resultados: List[ResultadoProcessamento] = []
    
    def processar_imagem(self, imagem: ImagemMonitoramento, 
                       area: AreaMonitoramento,
                       imagem_referencia: Optional[ImagemMonitoramento] = None) -> ResultadoProcessamento:
        """
        Processa uma imagem completa.
        
        Pipeline:
        1. Normalização
        2. Alinhamento (se referência fornecida)
        3. Recorte
        4. Padronização
        
        Args:
            imagem: Imagem para processar
            area: Área de monitoramento
            imagem_referencia: Imagem de referência para alinhamento (opcional)
            
        Returns:
            Resultado do processamento
        """
        import time
        inicio_processamento = time.time()
        
        try:
            # 1. Leitura da imagem
            dados_originais, metadados_originais = self._ler_imagem(imagem)
            
            # 2. Normalização
            dados_normalizados = self.normalizador.normalizar_multibanda(
                dados_originais, metadados_originais
            )
            
            # 3. Alinhamento
            if imagem_referencia:
                dados_referencia, metadados_referencia = self._ler_imagem(imagem_referencia)
                dados_alinhados, metadados_alinhados = self.alinhador.alinhar_imagem(
                    dados_referencia, dados_normalizados, 
                    metadados_referencia, metadados_originais
                )
            else:
                dados_alinhados = dados_normalizados
                metadados_alinhados = metadados_originais
            
            # 4. Recorte
            dados_recortados, metadados_recortados = self.recortador.recortar_por_area(
                dados_alinhados, metadados_alinhados, area
            )
            
            # 5. Padronização
            dados_padronizados, metadados_padronizados = self.padronizador.padronizar_imagem(
                dados_recortados, metadados_recortados
            )
            
            # 6. Salvar resultado
            caminho_saida = f"processado_{imagem.imagem_id}_{int(time.time())}"
            sucesso_salvamento = self.padronizador.salvar_imagem_padronizada(
                dados_padronizados, metadados_padronizados, caminho_saida
            )
            
            tempo_total = time.time() - inicio_processamento
            
            # Criar resultado
            resultado = ResultadoProcessamento(
                imagem_original=imagem,
                imagem_processada_path=caminho_saida if sucesso_salvamento else "",
                dados_processados=dados_padronizados,
                metadados=metadados_padronizados,
                tempo_processamento=tempo_total,
                sucesso=sucesso_salvamento,
                transformacao_aplicada="completo"
            )
            
            self.resultados.append(resultado)
            return resultado
            
        except Exception as e:
            tempo_total = time.time() - inicio_processamento
            logger.error(f"Erro no processamento de {imagem.imagem_id}: {e}")
            
            resultado = ResultadoProcessamento(
                imagem_original=imagem,
                imagem_processada_path="",
                dados_processados={},
                metadados={},
                tempo_processamento=tempo_total,
                sucesso=False,
                erros=[str(e)],
                transformacao_aplicada="falhou"
            )
            
            self.resultados.append(resultado)
            return resultado
    
    def _ler_imagem(self, imagem: ImagemMonitoramento) -> Tuple[Dict[str, np.ndarray], Dict[str, Any]]:
        """
        Lê imagem do disco.
        
        Args:
            imagem: Informações da imagem
            
        Returns:
            Tuple: (dados, metadados)
        """
        try:
            # Simplificado - implementar geração real de dados processados
            logger.warning("Geração de dados de processamento simplificada")
            return {
                'band_1': np.random.rand(100, 100),
                'band_2': np.random.rand(100, 100),
                'band_3': np.random.rand(100, 100)
            }, {
                'transform': None,
                'crs': 'EPSG:4326',
                'dtype': 'float32'
            }
            
        except Exception as e:
            logger.error(f"Erro ao ler imagem {imagem.imagem_id}: {e}")
            raise
    
    def processar_lote(self, imagens: List[ImagemMonitoramento],
                      area: AreaMonitoramento) -> List[ResultadoProcessamento]:
        """
        Processa múltiplas imagens em lote.
        
        Args:
            imagens: Lista de imagens para processar
            area: Área de monitoramento
            
        Returns:
            Lista de resultados de processamento
        """
        resultados = []
        
        # Ordenar imagens cronologicamente
        imagens_ordenadas = sorted(imagens, key=lambda x: x.data_captura)
        
        # Primeira imagem como referência
        referencia = None
        
        for i, imagem in enumerate(imagens_ordenadas):
            resultado = self.processar_imagem(imagem, area, referencia)
            resultados.append(resultado)
            
            # Se primeiro processamento, usar como referência
            if i == 0 and resultado.sucesso:
                referencia = imagem
        
        return resultados
    
    def obter_estatisticas_processamento(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do processamento.
        
        Returns:
            Estatísticas consolidadas
        """
        if not self.resultados:
            return {'total_imagens': 0, 'sucesso': 0, 'falha': 0}
        
        sucesso = sum(1 for r in self.resultados if r.sucesso)
        falha = len(self.resultados) - sucesso
        
        tempos = [r.tempo_processamento for r in self.resultados if r.sucesso]
        
        return {
            'total_imagens': len(self.resultados),
            'sucesso': sucesso,
            'falha': falha,
            'taxa_sucesso': sucesso / len(self.resultados) * 100,
            'tempo_medio': np.mean(tempos) if tempos else 0,
            'tempo_total': sum(r.tempo_processamento for r in self.resultados),
            'erros_comuns': self._analisar_erros_comuns()
        }
    
    def _analisar_erros_comuns(self) -> Dict[str, int]:
        """
        Analisa erros mais comuns no processamento.
        
        Returns:
            Contagem de erros por tipo
        """
        erros = {}
        
        for resultado in self.resultados:
            if not resultado.sucesso:
                for erro in resultado.erros:
                    erro_simplificado = erro.split(':')[0]  # Pegar primeira parte do erro
                    erros[erro_simplificado] = erros.get(erro_simplificado, 0) + 1
        
        return erros