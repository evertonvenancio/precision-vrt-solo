"""
Precision VRT Solo — Módulo de Gerenciamento de Imagens

Implementa funcionalidades específicas para gerenciamento de imagens
de diferentes sensores (satélite, drone, RGB, multiespectral, etc.).
"""

import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime
from dataclasses import dataclass, field
import json

from core.tipos.geoespacial import Bounds
from ..contratos import ImagemMonitoramento, TipoSensor, TipoIndice


@dataclass
class InfoImagem:
    """Informações básicas de uma imagem."""
    
    nome_arquivo: str
    caminho_completo: str
    tamanho_bytes: int
    formato: str
    dimensao: Tuple[int, int]
    numero_bandas: int
    sistema_coordenadas: str = "EPSG:4326"
    cloud_cover: Optional[float] = None
    data_processamento: Optional[str] = None


class GerenciadorImagens:
    """
    Gerencia imagens de diferentes sensores para monitoramento.
    """
    
    def __init__(self):
        self.imagens_registradas: List[ImagemMonitoramento] = []
        self.cache_metadados: Dict[str, Dict] = {}
        
    def registrar_imagem(self, imagem: ImagemMonitoramento) -> bool:
        """
        Registra uma nova imagem no sistema.
        
        Args:
            imagem: Dados da imagem a ser registrada
            
        Returns:
            True se registrada com sucesso
        """
        if not self._validar_imagem(imagem):
            return False
            
        # Verificar se já existe
        if any(imo.imagem_id == imagem.imagem_id for imo in self.imagens_registradas):
            return False
            
        self.imagens_registradas.append(imagem)
        return True
    
    def obter_imagem(self, imagem_id: str) -> Optional[ImagemMonitoramento]:
        """
        Obtém uma imagem pelo ID.
        
        Args:
            imagem_id: ID da imagem
            
        Returns:
            Imagem ou None se não encontrada
        """
        for imagem in self.imagens_registradas:
            if imagem.imagem_id == imagem_id:
                return imagem
        return None
    
    def filtrar_por_sensor(self, tipo_sensor: TipoSensor) -> List[ImagemMonitoramento]:
        """
        Filtra imagens por tipo de sensor.
        
        Args:
            tipo_sensor: Tipo de sensor
            
        Returns:
            Lista de imagens do sensor especificado
        """
        return [img for img in self.imagens_registradas if img.sensor == tipo_sensor]
    
    def filtrar_por_periodo(self, data_inicio: str, data_fim: str) -> List[ImagemMonitoramento]:
        """
        Filtra imagens por período de captura.
        
        Args:
            data_inicio: Data inicial (formato ISO)
            data_fim: Data final (formato ISO)
            
        Returns:
            Lista de imagens no período especificado
        """
        imagens_filtradas = []
        
        for imagem in self.imagens_registradas:
            if data_inicio <= imagem.data_captura <= data_fim:
                imagens_filtradas.append(imagem)
                
        return imagens_filtradas
    
    def listar_imagens_disponiveis(self) -> List[str]:
        """
        Lista todos os IDs de imagens disponíveis.
        
        Returns:
            Lista de IDs
        """
        return [img.imagem_id for img in self.imagens_registradas]
    
    def _validar_imagem(self, imagem: ImagemMonitoramento) -> bool:
        """
        Valida os dados de uma imagem.
        
        Args:
            imagem: Imagem a ser validada
            
        Returns:
            True se válida
        """
        # Verificar campos obrigatórios
        if not imagem.imagem_id or not imagem.caminho_arquivo:
            return False
            
        # Verificar se o arquivo existe
        if not Path(imagem.caminho_arquivo).exists():
            return False
            
        # Verificar sensor válido
        if not isinstance(imagem.sensor, TipoSensor):
            return False
            
        return True


class ProcessadorImagens:
    """
    Processa imagens de acordo com o tipo de sensor.
    """
    
    def __init__(self):
        self.gerenciador = GerenciadorImagens()
        
    def processar_imagem_satelite(self, imagem: ImagemMonitoramento) -> Dict[str, Any]:
        """
        Processa imagem de satélite.
        
        Args:
            imagem: Imagem de satélite
            
        Returns:
            Dados processados
        """
        return {
            'sensor': 'satelite',
            'processamento': 'normalizado',
            'bandas_disponiveis': ['blue', 'green', 'red', 'nir', 'swir1'],
            'resolucao': 10.0,
            'cloud_cover': imagem.cloud_cover_pct
        }
    
    def processar_imagem_drone(self, imagem: ImagemMonitoramento) -> Dict[str, Any]:
        """
        Processa imagem de drone.
        
        Args:
            imagem: Imagem de drone
            
        Returns:
            Dados processados
        """
        return {
            'sensor': 'drone',
            'processamento': 'georreferenciado',
            'bandas_disponiveis': ['red', 'green', 'blue', 'nir', 'red_edge'],
            'resolucao': 0.1,
            'altitude_voo': 120.0
        }
    
    def processar_imagem_rgb(self, imagem: ImagemMonitoramento) -> Dict[str, Any]:
        """
        Processa imagem RGB.
        
        Args:
            imagem: Imagem RGB
            
        Returns:
            Dados processados
        """
        return {
            'sensor': 'rgb',
            'processamento': 'basic',
            'bandas_disponiveis': ['red', 'green', 'blue'],
            'resolucao': 1.0
        }
    
    def processar_imagem_multiespectral(self, imagem: ImagemMonitoramento) -> Dict[str, Any]:
        """
        Processa imagem multiespectral.
        
        Args:
            imagem: Imagem multiespectral
            
        Returns:
            Dados processados
        """
        return {
            'sensor': 'multiespectral',
            'processamento': 'calibrado',
            'bandas_disponiveis': ['blue', 'green', 'red', 'red_edge', 'nir'],
            'resolucao': 5.0,
            'calibracao': 'radiometrica'
        }
    
    def processar_imagem_thermal(self, imagem: ImagemMonitoramento) -> Dict[str, Any]:
        """
        Processa imagem térmica.
        
        Args:
            imagem: Imagem térmica
            
        Returns:
            Dados processados
        """
        return {
            'sensor': 'thermal',
            'processamento': 'temperatura',
            'bandas_disponiveis': ['thermal'],
            'resolucao': 0.5,
            'temperatura_min': 15.0,
            'temperatura_max': 35.0
        }
    
    def processar_imagem_hyperspectral(self, imagem: ImagemMonitoramento) -> Dict[str, Any]:
        """
        Processa imagem hiperspectral.
        
        Args:
            imagem: Imagem hiperspectral
            
        Returns:
            Dados processados
        """
        return {
            'sensor': 'hyperspectral',
            'processamento': 'espectral',
            'bandas_disponiveis': [f'band_{i}' for i in range(200)],
            'resolucao': 1.0,
            'n_bandas': 200
        }


class ValidadorImagens:
    """
    Valida imagens antes do processamento.
    """
    
    @staticmethod
    def validar_formato_arquivo(caminho_arquivo: str) -> Tuple[bool, str]:
        """
        Valida o formato do arquivo de imagem.
        
        Args:
            caminho_arquivo: Caminho do arquivo
            
        Returns:
            Tuple (valido, mensagem)
        """
        path = Path(caminho_arquivo)
        
        if not path.exists():
            return False, f"Arquivo não encontrado: {caminho_arquivo}"
            
        formatos_suportados = {'.tif', '.tiff', '.jpg', '.jpeg', '.png', '.jp2', '.hdf'}
        
        if path.suffix.lower() not in formatos_suportados:
            return False, f"Formato não suportado: {path.suffix}"
            
        return True, "Formato válido"
    
    @staticmethod
    def validar_metadados_imagem(imagem: ImagemMonitoramento) -> Tuple[bool, List[str]]:
        """
        Valida os metadados da imagem.
        
        Args:
            imagem: Imagem a ser validada
            
        Returns:
            Tuple (valido, lista_erros)
        """
        erros = []
        
        if not imagem.imagem_id:
            erros.append("ID da imagem não informado")
            
        if not imagem.data_captura:
            erros.append("Data de captura não informada")
            
        if not imagem.caminho_arquivo:
            erros.append("Caminho do arquivo não informado")
            
        if not isinstance(imagem.sensor, TipoSensor):
            erros.append("Tipo de sensor inválido")
            
        if imagem.cloud_cover_pct < 0 or imagem.cloud_cover_pct > 100:
            erros.append("Percentual de cobertura de nuvens inválido")
            
        return len(erros) == 0, erros