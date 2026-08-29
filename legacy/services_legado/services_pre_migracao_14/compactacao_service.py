"""
Precision VRT Solo — Serviço de Compactação

Orquestrador do módulo de compactação.
Responsável apenas por validar entradas e chamar o Core.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from core.compactacao.compactacao import MotorCompactacao
from core.tipos.base import ConfigBase

logger = logging.getLogger(__name__)


class CompactacaoService:
    """
    Serviço de orquestração para compactação.
    Não contém lógica de negócio, apenas coordena chamadas ao Core.
    """
    
    def __init__(self):
        self.motor_compactacao = MotorCompactacao()
    
    def processar_compactacao(self, 
                              arquivo_csv_path: str,
                              propriedade_id: Optional[int] = None,
                              talhao_id: Optional[int] = None,
                              configuracoes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processa análise de compactação.
        
        Pipeline:
        1. Importação
        2. Imagem histórica (opcional)
        3. Interpolação (opcional)
        4. Zoneamento
        5. Mapa
        6. Exportação
        
        Args:
            arquivo_csv_path: Caminho do arquivo CSV com dados de compactação
            propriedade_id: ID da propriedade (opcional)
            talhao_id: ID do talhão (opcional)
            configuracoes: Configurações opcionais
            
        Returns:
            Dicionário com resultados da análise
        """
        try:
            # Validação básica de parâmetros
            if not arquivo_csv_path or not Path(arquivo_csv_path).exists():
                raise ValueError("Arquivo CSV de compactação inválido ou inexistente")
            
            # Instanciar configurações do Core
            config = ConfigBase()
            if configuracoes:
                config.update(configuracoes)
            
            # Processar arquivo CSV
            resultado_processamento = self._processar_arquivo_csv(arquivo_csv_path)
            
            # Pipeline de processamento
            resultado_analise = self._processar_analise_compactacao(
                resultado_processamento, propriedade_id, talhao_id, config
            )
            
            # Exportar resultados
            arquivos_exportados = self._exportar_resultados(resultado_analise)
            
            return {
                'success': True,
                'resultado_processamento': resultado_processamento,
                'resultado_analise': resultado_analise,
                'arquivos_exportados': arquivos_exportados,
                'mensagem': 'Análise de compactação processada com sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar compactação: {e}")
            return {
                'success': False,
                'error': str(e),
                'mensagem': 'Falha ao processar análise de compactação'
            }
    
    def _processar_arquivo_csv(self, arquivo_csv_path: str) -> Dict[str, Any]:
        """
        Processa arquivo CSV de compactação.
        
        Args:
            arquivo_csv_path: Caminho do arquivo CSV
            
        Returns:
            Dicionário com dados processados
        """
        from core.utilitarios import csv
        
        dados = csv.ler_csv(arquivo_csv_path)
        return {
            'dados_originais': dados,
            'total_pontos': len(dados),
            'arquivo_fonte': arquivo_csv_path
        }
    
    def _processar_analise_compactacao(self, 
                                      dados_processamento: Dict[str, Any],
                                      propriedade_id: Optional[int],
                                      talhao_id: Optional[int],
                                      config: ConfigBase) -> Dict[str, Any]:
        """
        Processa análise de compactação.
        
        Args:
            dados_processamento: Dados processados do arquivo CSV
            propriedade_id: ID da propriedade
            talhao_id: ID do talhão
            config: Configurações
            
        Returns:
            Resultado da análise
        """
        return self.motor_compactacao.processar_analise_compactacao(
            dados_processamento, propriedade_id, talhao_id, config
        )
    
    def _exportar_resultados(self, resultado_analise: Dict[str, Any]) -> Dict[str, str]:
        """
        Exporta resultados em múltiplos formatos.
        
        Args:
            resultado_analise: Resultado da análise
            
        Returns:
            Dicionário com caminhos dos arquivos exportados
        """
        arquivos = {}
        
        # Exportar mapa de compactação
        try:
            arquivo_mapa = self.motor_compactacao.exportar_mapa_compactacao(resultado_analise)
            arquivos['mapa_compactacao'] = arquivo_mapa
        except Exception as e:
            logger.warning(f"Não foi possível exportar mapa: {e}")
        
        # Exportar relatório
        try:
            arquivo_relatorio = self.motor_compactacao.exportar_relatorio(resultado_analise)
            arquivos['relatorio'] = arquivo_relatorio
        except Exception as e:
            logger.warning(f"Não foi possível exportar relatório: {e}")
        
        # Exportar dados em CSV
        try:
            arquivo_csv = self.motor_compactacao.exportar_dados_csv(resultado_analise)
            arquivos['dados_csv'] = arquivo_csv
        except Exception as e:
            logger.warning(f"Não foi possível exportar CSV: {e}")
        
        return arquivos
    
    def gerar_resumo_estatistico(self, resultado_analise: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera resumo estatístico da análise de compactação.
        
        Args:
            resultado_analise: Resultado da análise
            
        Returns:
            Resumo estatístico
        """
        return self.motor_compactacao.gerar_resumo_estatistico(resultado_analise)
    
    def gerar_flags_escarificacao(self, resultado_analise: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera flags de escarificação para pontos problemáticos.
        
        Args:
            resultado_analise: Resultado da análise
            
        Returns:
            Flags de escarificação
        """
        return self.motor_compactacao.gerar_flags_escarificacao(resultado_analise)