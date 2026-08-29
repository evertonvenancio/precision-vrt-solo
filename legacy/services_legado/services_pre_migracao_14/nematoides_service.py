"""
Precision VRT Solo — Serviço de Nematoides

Orquestrador do módulo de nematoides.
Responsável apenas por validar entradas e chamar o Core.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from core.nematoides.nematoides import MotorNematoides
from core.tipos.base import ConfigBase

logger = logging.getLogger(__name__)


class NematoidesService:
    """
    Serviço de orquestração para nematoides.
    Não contém lógica de negócio, apenas coordena chamadas ao Core.
    """
    
    def __init__(self):
        self.motor_nematoides = MotorNematoides()
    
    def processar_nematoides(self, 
                            amostras_nematoides_path: str,
                            limite_talhao_path: Optional[str] = None,
                            propriedade_id: Optional[int] = None,
                            talhao_id: Optional[int] = None,
                            configuracoes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processa análise de nematoides.
        
        Pipeline:
        1. Importação
        2. Imagem histórica (opcional)
        3. Interpolação (opcional)
        4. Zoneamento
        5. Mapa
        6. Exportação
        
        Args:
            amostras_nematoides_path: Caminho do arquivo com amostras de nematoides
            limite_talhao_path: Caminho do arquivo de limite do talhão (opcional)
            propriedade_id: ID da propriedade (opcional)
            talhao_id: ID do talhão (opcional)
            configuracoes: Configurações opcionais
            
        Returns:
            Dicionário com resultados da análise
        """
        try:
            # Validação básica de parâmetros
            if not amostras_nematoides_path or not Path(amostras_nematoides_path).exists():
                raise ValueError("Arquivo de amostras de nematoides inválido ou inexistente")
            
            # Instanciar configurações do Core
            config = ConfigBase()
            if configuracoes:
                config.update(configuracoes)
            
            # Processar amostras de nematoides
            resultado_processamento = self._processar_amostras_nematoides(amostras_nematoides_path)
            
            # Pipeline de processamento
            resultado_analise = self._processar_analise_nematoides(
                resultado_processamento, 
                limite_talhao_path,
                propriedade_id,
                talhao_id,
                config
            )
            
            # Exportar resultados
            arquivos_exportados = self._exportar_resultados(resultado_analise)
            
            return {
                'success': True,
                'resultado_processamento': resultado_processamento,
                'resultado_analise': resultado_analise,
                'arquivos_exportados': arquivos_exportados,
                'mensagem': 'Análise de nematoides processada com sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar nematoides: {e}")
            return {
                'success': False,
                'error': str(e),
                'mensagem': 'Falha ao processar análise de nematoides'
            }
    
    def _processar_amostras_nematoides(self, amostras_path: str) -> Dict[str, Any]:
        """
        Processa arquivo de amostras de nematoides.
        
        Args:
            amostras_path: Caminho do arquivo de amostras
            
        Returns:
            Dicionário com dados processados
        """
        from core.utilitarios import csv
        
        dados = csv.ler_csv(amostras_path)
        return {
            'dados_originais': dados,
            'total_amostras': len(dados),
            'arquivo_fonte': amostras_path
        }
    
    def _processar_analise_nematoides(self, 
                                     dados_processamento: Dict[str, Any],
                                     limite_talhao_path: Optional[str],
                                     propriedade_id: Optional[int],
                                     talhao_id: Optional[int],
                                     config: ConfigBase) -> Dict[str, Any]:
        """
        Processa análise de nematoides.
        
        Args:
            dados_processamento: Dados processados das amostras
            limite_talhao_path: Caminho do limite do talhão
            propriedade_id: ID da propriedade
            talhao_id: ID do talhão
            config: Configurações
            
        Returns:
            Resultado da análise
        """
        return self.motor_nematoides.processar_analise_nematoides(
            dados_processamento, 
            limite_talhao_path,
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
        
        # Exportar mapa de nematoides
        try:
            arquivo_mapa = self.motor_nematoides.exportar_mapa_nematoides(resultado_analise)
            arquivos['mapa_nematoides'] = arquivo_mapa
        except Exception as e:
            logger.warning(f"Não foi possível exportar mapa: {e}")
        
        # Exportar relatório
        try:
            arquivo_relatorio = self.motor_nematoides.exportar_relatorio(resultado_analise)
            arquivos['relatorio'] = arquivo_relatorio
        except Exception as e:
            logger.warning(f"Não foi possível exportar relatório: {e}")
        
        # Exportar dados em CSV
        try:
            arquivo_csv = self.motor_nematoides.exportar_dados_csv(resultado_analise)
            arquivos['dados_csv'] = arquivo_csv
        except Exception as e:
            logger.warning(f"Não foi possível exportar CSV: {e}")
        
        return arquivos
    
    def classificar_risco_nematoides(self, resultado_analise: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classifica o risco de infestação por nematoides.
        
        Args:
            resultado_analise: Resultado da análise
            
        Returns:
            Classificação de risco
        """
        return self.motor_nematoides.classificar_risco_nematoides(resultado_analise)
    
    def gerar_recomendacoes_controle(self, resultado_analise: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera recomendações de controle para nematoides.
        
        Args:
            resultado_analise: Resultado da análise
            
        Returns:
            Recomendações de controle
        """
        return self.motor_nematoides.gerar_recomendacoes_controle(resultado_analise)