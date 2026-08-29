"""
Precision VRT Solo — Serviço de Sensoriamento

Orquestrador do módulo de sensoriamento.
Responsável apenas por validar entradas e chamar o Core.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from core.sensoriamento.processamento.motor import MotorProcessamentoSensoriamento
from core.tipos.base import ConfigBase

logger = logging.getLogger(__name__)


class SensoriamentoService:
    """
    Serviço de orquestração para sensoriamento.
    Não contém lógica de negócio, apenas coordena chamadas ao Core.
    """
    
    def __init__(self):
        self.motor_sensoriamento = MotorProcessamentoSensoriamento()
    
    def processar_sensoriamento(self, 
                               area_geojson_path: str,
                               fonte_dados: str,
                               parametros_sensoriamento: Optional[Dict[str, Any]] = None,
                               configuracoes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processa sensoriamento da área.
        
        Pipeline:
        1. Área
        2. Satélite
        3. Download
        4. Índices
        5. Mapas
        6. Resultado
        
        Args:
            area_geojson_path: Caminho do arquivo GeoJSON com a área a ser sensoriada
            fonte_dados: Fonte dos dados (satélite, drone, etc.)
            parametros_sensoriamento: Parâmetros específicos do sensoriamento
            configuracoes: Configurações opcionais
            
        Returns:
            Dicionário com resultados do sensoriamento
        """
        try:
            # Validação básica de parâmetros
            if not area_geojson_path or not Path(area_geojson_path).exists():
                raise ValueError("Arquivo GeoJSON da área inválido ou inexistente")
            
            if not fonte_dados:
                raise ValueError("Fonte de dados não especificada")
            
            # Instanciar configurações do Core
            config = ConfigBase()
            if configuracoes:
                config.update(configuracoes)
            
            # Processar área
            resultado_area = self._processar_area(area_geojson_path)
            
            # Pipeline de processamento
            resultado_sensoriamento = self._processar_sensoriamento(
                resultado_area,
                fonte_dados,
                parametros_sensoriamento,
                config
            )
            
            # Exportar resultados
            arquivos_exportados = self._exportar_resultados(resultado_sensoriamento)
            
            return {
                'success': True,
                'resultado_area': resultado_area,
                'resultado_sensoriamento': resultado_sensoriamento,
                'arquivos_exportados': arquivos_exportados,
                'mensagem': 'Sensoriamento processado com sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar sensoriamento: {e}")
            return {
                'success': False,
                'error': str(e),
                'mensagem': 'Falha ao processar sensoriamento'
            }
    
    def _processar_area(self, area_geojson_path: str) -> Dict[str, Any]:
        """
        Processa arquivo GeoJSON da área.
        
        Args:
            area_geojson_path: Caminho do arquivo GeoJSON
            
        Returns:
            Dicionário com dados processados da área
        """
        import json
        
        with open(area_geojson_path, 'r', encoding='utf-8') as f:
            area_data = json.load(f)
        
        return {
            'dados_originais': area_data,
            'arquivo_fonte': area_geojson_path
        }
    
    def _processar_sensoriamento(self, 
                                area_dados: Dict[str, Any],
                                fonte_dados: str,
                                parametros_sensoriamento: Optional[Dict[str, Any]],
                                config: ConfigBase) -> Dict[str, Any]:
        """
        Processa sensoriamento completo.
        
        Args:
            area_dados: Dados processados da área
            fonte_dados: Fonte dos dados
            parametros_sensoriamento: Parâmetros específicos
            config: Configurações
            
        Returns:
            Resultado do sensoriamento
        """
        return self.motor_sensoriamento.processar_sensoriamento(
            area_dados,
            fonte_dados,
            parametros_sensoriamento,
            config
        )
    
    def _exportar_resultados(self, resultado_sensoriamento: Dict[str, Any]) -> Dict[str, str]:
        """
        Exporta resultados em múltiplos formatos.
        
        Args:
            resultado_sensoriamento: Resultado do sensoriamento
            
        Returns:
            Dicionário com caminhos dos arquivos exportados
        """
        arquivos = {}
        
        # Exportar mapa de sensoriamento
        try:
            arquivo_mapa = self.motor_sensoriamento.exportar_mapa_sensoriamento(resultado_sensoriamento)
            arquivos['mapa_sensoriamento'] = arquivo_mapa
        except Exception as e:
            logger.warning(f"Não foi possível exportar mapa: {e}")
        
        # Exportar índices vegetais
        try:
            arquivo_indices = self.motor_sensoriamento.exportar_indices(resultado_sensoriamento)
            arquivos['indices_vegetais'] = arquivo_indices
        except Exception as e:
            logger.warning(f"Não foi possível exportar índices: {e}")
        
        # Exportar dados em CSV
        try:
            arquivo_csv = self.motor_sensoriamento.exportar_dados_csv(resultado_sensoriamento)
            arquivos['dados_csv'] = arquivo_csv
        except Exception as e:
            logger.warning(f"Não foi possível exportar CSV: {e}")
        
        return arquivos
    
    def calcular_indices_vegetais(self, resultado_sensoriamento: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula índices vegetais com base nos dados de sensoriamento.
        
        Args:
            resultado_sensoriamento: Resultado do sensoriamento
            
        Returns:
            Índices vegetais calculados
        """
        return self.motor_sensoriamento.calcular_indices_vegetais(resultado_sensoriamento)
    
    def gerar_mapas_temporais(self, resultado_sensoriamento: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera mapas temporais com base nas séries temporais.
        
        Args:
            resultado_sensoriamento: Resultado do sensoriamento
            
        Returns:
            Mapas temporais
        """
        return self.motor_sensoriamento.gerar_mapas_temporais(resultado_sensoriamento)
    
    def analisar_serie_temporal(self, resultado_sensoriamento: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa série temporal dos dados de sensoriamento.
        
        Args:
            resultado_sensoriamento: Resultado do sensoriamento
            
        Returns:
            Análise da série temporal
        """
        return self.motor_sensoriamento.analisar_serie_temporal(resultado_sensoriamento)