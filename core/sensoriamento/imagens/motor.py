"""
Precision VRT Solo — Motor de Gerenciamento de Imagens

Gerencia imagens de satélites e drones com suporte a múltiplos formatos
e tipos de sensores. Preparado para suportar drones RGB, multiespectral,
termal e hiperspectral.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from ..satelites.contratos import (
    ImagemSatelite, TipoSatelite, TipoSensor, TipoImagem, StatusProcessamento
)

logger = logging.getLogger(__name__)


class MotorGerenciamentoImagens:
    """Motor para gerenciamento de imagens de satélites e drones."""
    
    def __init__(self):
        logger.info("MotorGerenciamentoImagens inicializado")
        
        # Cache de imagens
        self._imagens_registradas: Dict[str, ImagemSatelite] = {}
        self._imagens_por_tipo: Dict[TipoImagem, List[ImagemSatelite]] = {
            TipoImagem.SATELITE: [],
            TipoImagem.DRONE: [],
            TipoImagem.COMBINADA: []
        }
        
        # Suporte a drones
        self._suporte_drones = {
            TipoSensor.RGB: True,
            TipoSensor.MULTIESPECTRAL: True,
            TipoSensor.HIPERSPECTRAL: True,
            TipoSensor.TERMAL: True,
            TipoSensor.RADAR: True
        }
        
        # Configurações de formatos
        self._formatos_suportados = {
            "geotiff": ["tif", "tiff"],
            "jpg": ["jpg", "jpeg"],
            "png": ["png"],
            "tiff": ["tiff"],
            "bin": ["bin"],
            "nc": ["nc"]
        }
        
        # Metadados típicos de imagens
        self._metadados_padrao = {
            "resolution": None,
            "bands": [],
            "crs": "EPSG:4326",
            "band_names": [],
            "data_type": "uint8",
            "nodata_value": 0,
            "bounds": None,
            "transform": None
        }
    
    # Métodos principais
    
    def adicionar_imagem_satelite(self, imagem_satelite: ImagemSatelite) -> bool:
        """Adicionar imagem de satélite ao gerenciador."""
        logger.info(f"Adicionando imagem satélite: {imagem_satelite.imagem_id}")
        
        try:
            # Validar imagem
            erros = self._validar_imagem_satelite(imagem_satelite)
            if erros:
                logger.error(f"Imagem inválida: {erros}")
                return False
            
            # Adicionar ao cache
            self._imagens_registradas[imagem_satelite.imagem_id] = imagem_satelite
            
            # Adicionar por tipo
            self._imagens_por_tipo[TipoImagem.SATELITE].append(imagem_satelite)
            
            # Criar diretório se não existir
            caminho_dir = Path(imagem_satelite.caminho_arquivo).parent
            caminho_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Imagem satélite {imagem_satelite.imagem_id} adicionada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar imagem satélite: {e}")
            return False
    
    def adicionar_imagem_drone(self, dados_imagem: Dict[str, Any]) -> bool:
        """Adicionar imagem de drone ao sistema."""
        logger.info(f"Adicionando imagem de drone: {dados_imagem.get('imagem_id', 'unknown')}")
        
        try:
            # Validar dados de drone
            erros = self._validar_imagem_drone(dados_imagem)
            if erros:
                logger.error(f"Imagem de drone inválida: {erros}")
                return False
            
            # Criar objeto de imagem
            imagem_drone = self._criar_objeto_drone(dados_imagem)
            
            # Adicionar ao gerenciador
            self._imagens_registradas[imagem_drone.imagem_id] = imagem_drone
            self._imagens_por_tipo[TipoImagem.DRONE].append(imagem_drone)
            
            # Criar estrutura de diretórios
            self._criar_estrutura_diretorios_drone(imagem_drone)
            
            logger.info(f"Imagem de drone {imagem_drone.imagem_id} adicionada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar imagem de drone: {e}")
            return False
    
    # Métodos de busca e consulta
    
    def buscar_imagens_por_area(self, area_id: str, tipo_imagem: Optional[TipoImagem] = None) -> List[ImagemSatelite]:
        """Buscar imagens por área e tipo opcional."""
        logger.info(f"Buscando imagens para área: {area_id}")
        
        imagens_encontradas = []
        
        for imagem_id, imagem in self._imagens_registradas.items():
            if area_id in imagem.areas_pertencentes:
                if tipo_imagem is None or imagem.tipo_imagem == tipo_imagem:
                    imagens_encontradas.append(imagem)
        
        logger.info(f"Encontradas {len(imagens_encontradas)} imagens para área {area_id}")
        return imagens_encontradas
    
    def buscar_imagens_por_satelite(self, tipo_satelite: TipoSatelite,
                                 tipo_sensor: Optional[TipoSensor] = None) -> List[ImagemSatelite]:
        """Buscar imagens por satélite e sensor opcional."""
        logger.info(f"Buscando imagens para satélite: {tipo_satelite.value}")
        
        imagens_encontradas = []
        
        for imagem in self._imagens_registradas.values():
            if imagem.satelite == tipo_satelite:
                if tipo_sensor is None or imagem.sensor == tipo_sensor:
                    imagens_encontradas.append(imagem)
        
        logger.info(f"Encontradas {len(imagens_encontradas)} imagens para satélite {tipo_satelite.value}")
        return imagens_encontradas
    
    def buscar_imagens_por_data(self, data_inicio: str, data_fim: str,
                             tipo_imagem: Optional[TipoImagem] = None) -> List[ImagemSatelite]:
        """Buscar imagens por período de tempo."""
        logger.info(f"Buscando imagens entre {data_inicio} e {data_fim}")
        
        imagens_encontradas = []
        inicio = datetime.fromisoformat(data_inicio)
        fim = datetime.fromisoformat(data_fim)
        
        for imagem in self._imagens_registradas.values():
            data_imagem = datetime.fromisoformat(imagem.data_captura)
            
            if inicio <= data_imagem <= fim:
                if tipo_imagem is None or imagem.tipo_imagem == tipo_imagem:
                    imagens_encontradas.append(imagem)
        
        logger.info(f"Encontradas {len(imagens_encontradas)} imagens no período")
        return imagens_encontradas
    
    def listar_todas_imagens(self, tipo_imagem: Optional[TipoImagem] = None) -> List[ImagemSatelite]:
        """Listar todas as imagens registradas."""
        if tipo_imagem:
            return self._imagens_por_tipo.get(tipo_imagem, [])
        else:
            return list(self._imagens_registradas.values())
    
    # Métodos de validação
    
    def _validar_imagem_satelite(self, imagem: ImagemSatelite) -> List[str]:
        """Validar imagem de satélite."""
        erros = []
        
        if not imagem.imagem_id:
            erros.append("ID da imagem não pode ser vazio")
        
        if not imagem.satelite:
            erros.append("Satélite não pode ser vazio")
        
        if not imagem.sensor:
            erros.append("Sensor não pode ser vazio")
        
        if not imagem.data_captura:
            erros.append("Data de captura não pode ser vazia")
        
        if not imagem.caminho_arquivo:
            erros.append("Caminho do arquivo não pode ser vazio")
        
        if imagem.resolucao_m <= 0:
            erros.append("Resolução deve ser maior que zero")
        
        return erros
    
    def _validar_imagem_drone(self, dados: Dict[str, Any]) -> List[str]:
        """Validar dados de imagem de drone."""
        erros = []
        
        if not dados.get("imagem_id"):
            erros.append("ID da imagem de drone não pode ser vazio")
        
        if not dados.get("tipo_sensor"):
            erros.append("Tipo de sensor não pode ser vazio")
        
        if not dados.get("data_captura"):
            erros.append("Data de captura não pode ser vazia")
        
        if not dados.get("caminho_arquivo"):
            erros.append("Caminho do arquivo não pode ser vazio")
        
        # Verificar se tipo de sensor é suportado
        try:
            tipo_sensor = TipoSensor(dados["tipo_sensor"])
            if not self.suporta_drone(tipo_sensor):
                erros.append(f"Tipo de drone não suportado: {tipo_sensor.value}")
        except ValueError:
            erros.append("Tipo de sensor inválido")
        
        return erros
    
    def _criar_objeto_drone(self, dados: Dict[str, Any]) -> ImagemSatelite:
        """Criar objeto ImagemSatelite a partir de dados de drone."""
        return ImagemSatelite(
            imagem_id=dados["imagem_id"],
            satelite=TipoSatelite.SENTINEL,  # Default para drone
            sensor=TipoSensor(dados["tipo_sensor"]),
            tipo_imagem=TipoImagem.DRONE,
            data_captura=dados["data_captura"],
            hora_captura=dados.get("hora_captura", "12:00:00"),
            cloud_cover_pct=dados.get("nuvem_pct", 0.0),
            resolucao_m=dados.get("resolucao_m", 0.1),  # Alta resolução típica de drones
            caminho_arquivo=dados["caminho_arquivo"],
            formatos_disponiveis=dados.get("formatos", ["jpg", "tiff"]),
            status_processamento=StatusProcessamento.PENDENTE,
            safra_id=dados.get("safra_id", "SAFRA_DRONE"),
            areas_pertencentes=dados.get("areas_pertencentes", [])
        )
    
    def _criar_estrutura_diretorios_drone(self, imagem: ImagemSatelite):
        """Criar estrutura de diretórios para imagens de drone."""
        base_dir = Path(imagem.caminho_arquivo).parent
        
        # Criar estrutura
        (base_dir / "drones").mkdir(parents=True, exist_ok=True)
        (base_dir / "drones" / imagem.sensor.value).mkdir(parents=True, exist_ok=True)
        (base_dir / "drones" / imagem.sensor.value / "processadas").mkdir(parents=True, exist_ok=True)
        
        # Criar arquivo de metadados
        arquivo_metadados = base_dir / "drones" / imagem.sensor.value / f"{imagem.imagem_id}_metadata.json"
        metadados = {
            "imagem_id": imagem.imagem_id,
            "sensor": imagem.sensor.value,
            "data_captura": imagem.data_captura,
            "hora_captura": imagem.hora_captura,
            "resolucao_m": imagem.resolucao_m,
            "areas_pertencentes": imagem.areas_pertencentes,
            "formatos_disponiveis": imagem.formatos_disponiveis
        }
        
        import json
        with arquivo_metadados.open('w') as f:
            json.dump(metadados, f, indent=2)
    
    # Métodos de suporte a drones
    
    def suporta_drone(self, tipo_sensor: TipoSensor) -> bool:
        """Verificar se suporta drone do tipo especificado."""
        return self._suporte_drones.get(tipo_sensor, False)
    
    def listar_tipos_drone_suportados(self) -> List[TipoSensor]:
        """Listar todos tipos de drones suportados."""
        return [sensor for sensor, suportado in self._suporte_drones.items() if suportado]
    
    def adicionar_tipo_drone(self, tipo_sensor: TipoSensor, configuracao: Dict[str, Any]) -> bool:
        """Adicionar novo tipo de drone ao sistema."""
        logger.info(f"Adicionando tipo de drone: {tipo_sensor.value}")
        
        try:
            self._suporte_drones[tipo_sensor] = configuracao.get("disponivel", True)
            logger.info(f"Tipo de drone {tipo_sensor.value} adicionado com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar tipo de drone: {e}")
            return False
    
    def remover_tipo_drone(self, tipo_sensor: TipoSensor) -> bool:
        """Remover tipo de drone do sistema."""
        logger.info(f"Removendo tipo de drone: {tipo_sensor.value}")
        
        try:
            if tipo_sensor in self._suporte_drones:
                del self._suporte_drones[tipo_sensor]
                logger.info(f"Tipo de drone {tipo_sensor.value} removido com sucesso")
                return True
            else:
                logger.warning(f"Tipo de drone não encontrado: {tipo_sensor.value}")
                return False
        except Exception as e:
            logger.error(f"Erro ao remover tipo de drone: {e}")
            return False
    
    # Métodos de formato
    
    def suporta_formato(self, formato: str) -> bool:
        """Verificar se suporta formato de imagem."""
        return formato.lower() in self._formatos_suportados
    
    def obter_formatos_suportados(self) -> List[str]:
        """Obter todos formatos suportados."""
        return list(self._formatos_suportados.keys())
    
    # Métodos de metadados
    
    def adicionar_metadados_imagem(self, imagem_id: str, metadados: Dict[str, Any]) -> bool:
        """Adicionar metadados específicos a uma imagem."""
        logger.info(f"Adicionando metadados para imagem: {imagem_id}")
        
        try:
            if imagem_id in self._imagens_registradas:
                imagem = self._imagens_registradas[imagem_id]
                imagem.metadados.update(metadados)
                
                # Salvar metadados em arquivo
                caminho_metadados = Path(imagem.caminho_arquivo).with_suffix(".json")
                import json
                with caminho_metadados.open('w') as f:
                    json.dump(imagem.metadados, f, indent=2)
                
                logger.info(f"Metadados adicionados para imagem {imagem_id}")
                return True
            else:
                logger.error(f"Imagem não encontrada: {imagem_id}")
                return False
        except Exception as e:
            logger.error(f"Erro ao adicionar metadados: {e}")
            return False
    
    def obter_metadados_imagem(self, imagem_id: str) -> Optional[Dict[str, Any]]:
        """Obter metadados de uma imagem."""
        if imagem_id in self._imagens_registradas:
            return self._imagens_registradas[imagem_id].metadados.copy()
        return None
    
    # Métodos de estado
    
    def contar_imagens(self, tipo_imagem: Optional[TipoImagem] = None) -> Dict[str, int]:
        """Contar imagens por tipo."""
        if tipo_imagem:
            return {tipo_imagem.value: len(self._imagens_por_tipo.get(tipo_imagem, []))}
        else:
            return {
                TipoImagem.SATELITE.value: len(self._imagens_por_tipo[TipoImagem.SATELITE]),
                TipoImagem.DRONE.value: len(self._imagens_por_tipo[TipoImagem.DRONE]),
                TipoImagem.COMBINADA.value: len(self._imagens_por_tipo[TipoImagem.COMBINADA])
            }
    
    def remover_imagem(self, imagem_id: str) -> bool:
        """Remover imagem do sistema."""
        logger.info(f"Removendo imagem: {imagem_id}")
        
        try:
            if imagem_id in self._imagens_registradas:
                imagem = self._imagens_registradas[imagem_id]
                
                # Remover de todos os caches
                self._imagens_registradas.pop(imagem_id)
                self._imagens_por_tipo[imagem.tipo_imagem].remove(imagem)
                
                # Remover arquivos
                if Path(imagem.caminho_arquivo).exists():
                    Path(imagem.caminho_arquivo).unlink()
                
                # Remover metadados
                metadados_path = Path(imagem.caminho_arquivo).with_suffix(".json")
                if metadados_path.exists():
                    metadados_path.unlink()
                
                logger.info(f"Imagem {imagem_id} removida com sucesso")
                return True
            else:
                logger.error(f"Imagem não encontrada: {imagem_id}")
                return False
        except Exception as e:
            logger.error(f"Erro ao remover imagem: {e}")
            return False
    
    def limpar_cache(self) -> bool:
        """Limpar cache de imagens."""
        logger.info("Limpando cache de imagens")
        
        try:
            self._imagens_registradas.clear()
            for tipo in self._imagens_por_tipo:
                self._imagens_por_tipo[tipo].clear()
            
            logger.info("Cache de imagens limpo com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return False