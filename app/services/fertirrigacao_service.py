"""
Precision VRT Solo — Serviço de Fertirrigação

Orquestrador do módulo de fertirrigação.
Responsável apenas por validar entradas e chamar o Core.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from core.fertirrigacao.fertirrigacao import MotorFertirrigacao
from core.tipos.base import ConfigBase

logger = logging.getLogger(__name__)


class FertirrigacaoService:
    """
    Serviço de orquestração para fertirrigação.
    Não contém lógica de negócio, apenas coordena chamadas ao Core.
    """
    
    def __init__(self):
        self.motor_fertirrigacao = MotorFertirrigacao()
    
    def processar_fertirrigacao(self, 
                                arquivo_irrigacao_path: str,
                                arquivo_fertilizante_path: Optional[str] = None,
                                limite_talhao_path: Optional[str] = None,
                                cultura: Optional[str] = None,
                                propriedade_id: Optional[int] = None,
                                talhao_id: Optional[int] = None,
                                configuracoes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processa análise de fertirrigação.
        
        Pipeline:
        1. Importação
        2. Georreferenciamento (opcional)
        3. Interpolação (opcional)
        4. Mapa (opcional)
        5. Recomendação
        6. Exportação
        
        Args:
            arquivo_irrigacao_path: Caminho do arquivo com dados de irrigação
            arquivo_fertilizante_path: Caminho do arquivo com dados de fertilizante (opcional)
            limite_talhao_path: Caminho do arquivo de limite do talhão (opcional)
            cultura: Cultura (opcional)
            propriedade_id: ID da propriedade (opcional)
            talhao_id: ID do talhão (opcional)
            configuracoes: Configurações opcionais
            
        Returns:
            Dicionário com resultados da análise
        """
        try:
            # Validação básica de parâmetros
            if not arquivo_irrigacao_path or not Path(arquivo_irrigacao_path).exists():
                raise ValueError("Arquivo de irrigação inválido ou inexistente")
            
            # Instanciar configurações do Core
            config = ConfigBase()
            if configuracoes:
                config.update(configuracoes)
            
            # Processar dados de irrigação
            resultado_irrigacao = self._processar_dados_irrigacao(arquivo_irrigacao_path)
            
            # Processar dados de fertilizante (se fornecido)
            resultado_fertilizante = None
            if arquivo_fertilizante_path and Path(arquivo_fertilizante_path).exists():
                resultado_fertilizante = self._processar_dados_fertilizante(arquivo_fertilizante_path)
            
            # Pipeline de processamento
            resultado_analise = self._processar_analise_fertirrigacao(
                resultado_irrigacao,
                resultado_fertilizante,
                limite_talhao_path,
                cultura,
                propriedade_id,
                talhao_id,
                config
            )
            
            # Exportar resultados
            arquivos_exportados = self._exportar_resultados(resultado_analise)
            
            return {
                'success': True,
                'resultado_irrigacao': resultado_irrigacao,
                'resultado_fertilizante': resultado_fertilizante,
                'resultado_analise': resultado_analise,
                'arquivos_exportados': arquivos_exportados,
                'mensagem': 'Análise de fertirrigação processada com sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar fertirrigação: {e}")
            return {
                'success': False,
                'error': str(e),
                'mensagem': 'Falha ao processar análise de fertirrigação'
            }
    
    def _processar_dados_irrigacao(self, irrigacao_path: str) -> Dict[str, Any]:
        """
        Processa arquivo de dados de irrigação.
        
        Args:
            irrigacao_path: Caminho do arquivo de irrigação
            
        Returns:
            Dicionário com dados processados
        """
        from core.utilitarios import csv
        
        dados = csv.ler_csv(irrigacao_path)
        return {
            'dados_originais': dados,
            'total_registros': len(dados),
            'arquivo_fonte': irrigacao_path
        }
    
    def _processar_dados_fertilizante(self, fertilizante_path: str) -> Dict[str, Any]:
        """
        Processa arquivo de dados de fertilizante.
        
        Args:
            fertilizante_path: Caminho do arquivo de fertilizante
            
        Returns:
            Dicionário com dados processados
        """
        from core.utilitarios import csv
        
        dados = csv.ler_csv(fertilizante_path)
        return {
            'dados_originais': dados,
            'total_registros': len(dados),
            'arquivo_fonte': fertilizante_path
        }
    
    def _processar_analise_fertirrigacao(self, 
                                       dados_irrigacao: Dict[str, Any],
                                       dados_fertilizante: Optional[Dict[str, Any]],
                                       limite_talhao_path: Optional[str],
                                       cultura: Optional[str],
                                       propriedade_id: Optional[int],
                                       talhao_id: Optional[int],
                                       config: ConfigBase) -> Dict[str, Any]:
        """
        Processa análise de fertirrigação.
        
        Args:
            dados_irrigacao: Dados processados de irrigação
            dados_fertilizante: Dados processados de fertilizante
            limite_talhao_path: Caminho do limite do talhão
            cultura: Cultura
            propriedade_id: ID da propriedade
            talhao_id: ID do talhão
            config: Configurações
            
        Returns:
            Resultado da análise
        """
        return self.motor_fertirrigacao.processar_analise_fertirrigacao(
            dados_irrigacao,
            dados_fertilizante,
            limite_talhao_path,
            cultura,
            propriedade_id,
            talhao_id,
            config
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
        
        # Exportar mapa de fertirrigação
        try:
            arquivo_mapa = self.motor_fertirrigacao.exportar_mapa_fertirrigacao(resultado_analise)
            arquivos['mapa_fertirrigacao'] = arquivo_mapa
        except Exception as e:
            logger.warning(f"Não foi possível exportar mapa: {e}")
        
        # Exportar relatório
        try:
            arquivo_relatorio = self.motor_fertirrigacao.exportar_relatorio(resultado_analise)
            arquivos['relatorio'] = arquivo_relatorio
        except Exception as e:
            logger.warning(f"Não foi possível exportar relatório: {e}")
        
        # Exportar dados em CSV
        try:
            arquivo_csv = self.motor_fertirrigacao.exportar_dados_csv(resultado_analise)
            arquivos['dados_csv'] = arquivo_csv
        except Exception as e:
            logger.warning(f"Não foi possível exportar CSV: {e}")
        
        return arquivos
    
    def gerar_recomendacoes_agronomicas(self, resultado_analise: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera recomendações agronômicas para fertirrigação.
        
        Args:
            resultado_analise: Resultado da análise
            
        Returns:
            Recomendações agronômicas
        """
        return self.motor_fertirrigacao.gerar_recomendacoes_agronomicas(resultado_analise)
    
    def otimizar_programa_irrigacao(self, resultado_analise: Dict[str, Any]) -> Dict[str, Any]:
        """
        Otimiza programa de irrigação com base nos resultados.
        
        Args:
            resultado_analise: Resultado da análise
            
        Returns:
            Programa otimizado
        """
        return self.motor_fertirrigacao.otimizar_programa_irrigacao(resultado_analise)