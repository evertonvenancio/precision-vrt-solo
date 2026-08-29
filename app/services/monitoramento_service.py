"""
Precision VRT Solo — Serviço de Monitoramento

Orquestrador do módulo de monitoramento.
Responsável apenas por validar entradas e chamar o Core.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from core.monitoramento.monitoramento import MotorMonitoramento
from core.tipos.base import ConfigBase

logger = logging.getLogger(__name__)


class MonitoramentoService:
    """
    Serviço de orquestração para monitoramento.
    Não contém lógica de negócio, apenas coordena chamadas ao Core.
    """
    
    def __init__(self):
        self.motor_monitoramento = MotorMonitoramento()
    
    def processar_monitoramento(self, 
                               area_geojson_path: str,
                               imagem_atual_path: str,
                                imagens_historico_path: Optional[str] = None,
                                configuracoes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processa monitoramento temporal da área.
        
        Pipeline:
        1. Área
        2. Imagem
        3. Comparação
        4. Histórico
        5. Alertas
        6. Resultado
        
        Args:
            area_geojson_path: Caminho do arquivo GeoJSON com a área a ser monitorada
            imagem_atual_path: Caminho da imagem atual
            imagens_historico_path: Caminho das imagens históricas (opcional)
            configuracoes: Configurações opcionais
            
        Returns:
            Dicionário com resultados do monitoramento
        """
        try:
            # Validação básica de parâmetros
            if not area_geojson_path or not Path(area_geojson_path).exists():
                raise ValueError("Arquivo GeoJSON da área inválido ou inexistente")
            
            if not imagem_atual_path or not Path(imagem_atual_path).exists():
                raise ValueError("Arquivo da imagem atual inválido ou inexistente")
            
            # Instanciar configurações do Core
            config = ConfigBase()
            if configuracoes:
                config.update(configuracoes)
            
            # Processar área
            resultado_area = self._processar_area(area_geojson_path)
            
            # Processar imagem atual
            resultado_imagem = self._processar_imagem_atual(imagem_atual_path)
            
            # Processar imagens históricas (se fornecido)
            resultado_historico = None
            if imagens_historico_path and Path(imagens_historico_path).exists():
                resultado_historico = self._processar_imagens_historico(imagens_historico_path)
            
            # Pipeline de processamento
            resultado_monitoramento = self._processar_monitoramento(
                resultado_area,
                resultado_imagem,
                resultado_historico,
                config
            )
            
            # Gerar alertas
            resultado_alertas = self._gerar_alertas(resultado_monitoramento, config)
            
            # Exportar resultados
            arquivos_exportados = self._exportar_resultados(resultado_monitoramento, resultado_alertas)
            
            return {
                'success': True,
                'resultado_area': resultado_area,
                'resultado_imagem': resultado_imagem,
                'resultado_historico': resultado_historico,
                'resultado_monitoramento': resultado_monitoramento,
                'resultado_alertas': resultado_alertas,
                'arquivos_exportados': arquivos_exportados,
                'mensagem': 'Monitoramento processado com sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar monitoramento: {e}")
            return {
                'success': False,
                'error': str(e),
                'mensagem': 'Falha ao processar monitoramento'
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
    
    def _processar_imagem_atual(self, imagem_path: str) -> Dict[str, Any]:
        """
        Processa imagem atual de monitoramento.
        
        Args:
            imagem_path: Caminho da imagem
            
        Returns:
            Dicionário com dados processados da imagem
        """
        return self.motor_monitoramento.processar_imagem(imagem_path)
    
    def _processar_imagens_historico(self, imagens_path: str) -> Dict[str, Any]:
        """
        Processa imagens históricas.
        
        Args:
            imagens_path: Caminho das imagens
            
        Returns:
            Dicionário com dados processados das imagens históricas
        """
        return self.motor_monitoramento.processar_imagens_historico(imagens_path)
    
    def _processar_monitoramento(self, 
                               area_dados: Dict[str, Any],
                               imagem_dados: Dict[str, Any],
                               historico_dados: Optional[Dict[str, Any]],
                               config: ConfigBase) -> Dict[str, Any]:
        """
        Processa monitoramento completo.
        
        Args:
            area_dados: Dados processados da área
            imagem_dados: Dados processados da imagem atual
            historico_dados: Dados processados do histórico
            config: Configurações
            
        Returns:
            Resultado do monitoramento
        """
        return self.motor_monitoramento.processar_monitoramento(
            area_dados,
            imagem_dados,
            historico_dados,
            config
        )
    
    def _gerar_alertas(self, resultado_monitoramento: Dict[str, Any], config: ConfigBase) -> Dict[str, Any]:
        """
        Gera alertas com base nos resultados do monitoramento.
        
        Args:
            resultado_monitoramento: Resultado do monitoramento
            config: Configurações
            
        Returns:
            Alertas gerados
        """
        return self.motor_monitoramento.gerar_alertas(resultado_monitoramento, config)
    
    def _exportar_resultados(self, 
                            resultado_monitoramento: Dict[str, Any],
                            resultado_alertas: Dict[str, Any]) -> Dict[str, str]:
        """
        Exporta resultados em múltiplos formatos.
        
        Args:
            resultado_monitoramento: Resultado do monitoramento
            resultado_alertas: Resultado dos alertas
            
        Returns:
            Dicionário com caminhos dos arquivos exportados
        """
        arquivos = {}
        
        # Exportar mapa de monitoramento
        try:
            arquivo_mapa = self.motor_monitoramento.exportar_mapa_monitoramento(resultado_monitoramento)
            arquivos['mapa_monitoramento'] = arquivo_mapa
        except Exception as e:
            logger.warning(f"Não foi possível exportar mapa: {e}")
        
        # Exportar relatório de monitoramento
        try:
            arquivo_relatorio = self.motor_monitoramento.exportar_relatorio(resultado_monitoramento)
            arquivos['relatorio_monitoramento'] = arquivo_relatorio
        except Exception as e:
            logger.warning(f"Não foi possível exportar relatório: {e}")
        
        # Exportar alertas
        try:
            arquivo_alertas = self.motor_monitoramento.exportar_alertas(resultado_alertas)
            arquivos['alertas'] = arquivo_alertas
        except Exception as e:
            logger.warning(f"Não foi possível exportar alertas: {e}")
        
        # Exportar dados em CSV
        try:
            arquivo_csv = self.motor_monitoramento.exportar_dados_csv(resultado_monitoramento)
            arquivos['dados_csv'] = arquivo_csv
        except Exception as e:
            logger.warning(f"Não foi possível exportar CSV: {e}")
        
        return arquivos
    
    def analisar_mudanças_temporais(self, resultado_monitoramento: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa mudanças temporais com base nos resultados do monitoramento.
        
        Args:
            resultado_monitoramento: Resultado do monitoramento
            
        Returns:
            Análise de mudanças temporais
        """
        return self.motor_monitoramento.analisar_mudanças_temporais(resultado_monitoramento)
    
    def gerar_historico_monitoramento(self, resultado_monitoramento: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera histórico de monitoramento.
        
        Args:
            resultado_monitoramento: Resultado do monitoramento
            
        Returns:
            Histórico de monitoramento
        """
        return self.motor_monitoramento.gerar_historico_monitoramento(resultado_monitoramento)