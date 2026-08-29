"""
Precision VRT Solo — Serviço de Prescrição VRT

Orquestrador do módulo de prescrição VRT.
Responsável apenas por validar entradas e chamar o Core.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from core.prescricao_vrt.prescricao import MotorPrescricao
from core.prescricao_vrt.interpolacao import InterpoladorSolo
from core.prescricao_vrt.zoneamento import Zoneador
from core.tipos.base import ConfigBase
from config.culturas import listar_culturas
from config.formulas import get_formula, listar_formulas

logger = logging.getLogger(__name__)


class PrescricaoVrtService:
    """
    Serviço de orquestração para prescrição VRT.
    Não contém lógica de negócio, apenas coordena chamadas ao Core.
    """
    
    def __init__(self):
        self.motor_prescricao = MotorPrescricao()
        self.interpolador = InterpoladorSolo()
        self.zoneador = Zoneador()
    
    def processar_prescricao(self, 
                             limite_talhao_path: str,
                             amostras_solo_path: str,
                             cultura: str,
                             formula: str,
                             configuracoes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processa prescrição VRT completa.
        
        Pipeline:
        1. Importação
        2. Validação 
        3. Interpolação
        4. Zoneamento
        5. Prescrição
        6. Exportação
        
        Args:
            limite_talhao_path: Caminho do arquivo de limite do talhão
            amostras_solo_path: Caminho do arquivo de amostras de solo
            cultura: Cultura a ser prescrita
            formula: Fórmula de fertilizante
            configuracoes: Configurações opcionais
            
        Returns:
            Dicionário com resultados do processamento
        """
        try:
            # Validação básica de parâmetros
            if not limite_talhao_path or not Path(limite_talhao_path).exists():
                raise ValueError("Arquivo de limite do talhão inválido ou inexistente")
            
            if not amostras_solo_path or not Path(amostras_solo_path).exists():
                raise ValueError("Arquivo de amostras de solo inválido ou inexistente")
            
            if not cultura:
                raise ValueError("Cultura não especificada")
            
            if not formula:
                raise ValueError("Fórmula não especificada")
            
            # Instanciar configurações do Core
            config = ConfigBase()
            if configuracoes:
                config.update(configuracoes)
            
            # Pipeline de processamento
            resultado_interpolacao = self._processar_interpolacao(
                limite_talhao_path, amostras_solo_path, config
            )
            
            resultado_zoneamento = self._processar_zoneamento(
                resultado_interpolacao, config
            )
            
            resultado_prescricao = self._processar_prescricao(
                resultado_zoneamento, cultura, formula, config
            )
            
            # Exportar resultados
            arquivos_exportados = self._exportar_resultados(resultado_prescricao)
            
            return {
                'success': True,
                'resultado_interpolacao': resultado_interpolacao,
                'resultado_zoneamento': resultado_zoneamento,
                'resultado_prescricao': resultado_prescricao,
                'arquivos_exportados': arquivos_exportados,
                'mensagem': 'Prescrição VRT processada com sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar prescrição VRT: {e}")
            return {
                'success': False,
                'error': str(e),
                'mensagem': 'Falha ao processar prescrição VRT'
            }
    
    def _processar_interpolacao(self, 
                               limite_talhao_path: str,
                               amostras_solo_path: str,
                               config: ConfigBase) -> Dict[str, Any]:
        """
        Processa interpolação de solo.
        
        Args:
            limite_talhao_path: Caminho do limite do talhão
            amostras_solo_path: Caminho das amostras de solo
            config: Configurações
            
        Returns:
            Resultado da interpolação
        """
        return self.interpolador.processar_interpolacao(
            limite_talhao_path, amostras_solo_path, config
        )
    
    def _processar_zoneamento(self, 
                             resultado_interpolacao: Dict[str, Any],
                             config: ConfigBase) -> Dict[str, Any]:
        """
        Processa zoneamento da área.
        
        Args:
            resultado_interpolacao: Resultado da interpolação
            config: Configurações
            
        Returns:
            Resultado do zoneamento
        """
        return self.zoneador.processar_zoneamento(
            resultado_interpolacao, config
        )
    
    def _processar_prescricao(self, 
                             resultado_zoneamento: Dict[str, Any],
                             cultura: str,
                             formula: str,
                             config: ConfigBase) -> Dict[str, Any]:
        """
        Processa prescrição final.
        
        Args:
            resultado_zoneamento: Resultado do zoneamento
            cultura: Cultura
            formula: Fórmula
            config: Configurações
            
        Returns:
            Resultado da prescrição
        """
        return self.motor_prescricao.processar_prescricao(
            resultado_zoneamento, cultura, formula, config
        )
    
    def _exportar_resultados(self, resultado_prescricao: Dict[str, Any]) -> Dict[str, str]:
        """
        Exporta resultados em múltiplos formatos.
        
        Args:
            resultado_prescricao: Resultado da prescrição
            
        Returns:
            Dicionário com caminhos dos arquivos exportados
        """
        arquivos = {}
        
        # Exportar mapa de prescrição
        try:
            arquivo_mapa = self.motor_prescricao.exportar_mapa_prescricao(resultado_prescricao)
            arquivos['mapa_prescricao'] = arquivo_mapa
        except Exception as e:
            logger.warning(f"Não foi possível exportar mapa: {e}")
        
        # Exportar relatório
        try:
            arquivo_relatorio = self.motor_prescricao.exportar_relatorio(resultado_prescricao)
            arquivos['relatorio'] = arquivo_relatorio
        except Exception as e:
            logger.warning(f"Não foi possível exportar relatório: {e}")
        
        return arquivos
    
    def obter_culturas_disponiveis(self) -> list:
        """
        Retorna lista de culturas disponíveis.
        
        Returns:
            Lista de culturas
        """
        return listar_culturas()
    
    def obter_formulas_disponiveis(self, cultura: str) -> list:
        """
        Retorna lista de fórmulas disponíveis para uma cultura.
        
        Args:
            cultura: Nome da cultura
            
        Returns:
            Lista de fórmulas
        """
        return listar_formulas(cultura)
    
    def obter_configuracoes_padrao(self, cultura: str, formula: str) -> Dict[str, Any]:
        """
        Retorna configurações padrão para cultura e fórmula.
        
        Args:
            cultura: Nome da cultura
            formula: Nome da fórmula
            
        Returns:
            Configurações padrão
        """
        config = get_formula(formula)
        if config and cultura:
            config['cultura'] = cultura
        return config or {}