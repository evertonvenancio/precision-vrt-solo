"""
Precision VRT Solo — Motor de Seleção de Satélites

Implementa a seleção automática e manual de satélites para sensoriamento remoto.
Suporta toda a infraestrutura de satélites disponível no projeto.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from ..satelites.contratos import (
    ConfigAreaSensoriamento, ConfigSatelite, ImagemSatelite, 
    TipoSatelite, TipoSensor, StatusProcessamento
)

logger = logging.getLogger(__name__)


class MotorSelecaoSatelites:
    """Motor para seleção de satélites conforme disponibilidade e requisitos."""
    
    def __init__(self):
        logger.info("MotorSelecaoSatelites inicializado")
        
        # Infraestrutura de satélites suportados
        self.satelites_disponiveis = self._criar_infraestrutura_satelites()
        
        # Cache de imagens disponíveis
        self._imagens_cache: Dict[str, List[ImagemSatelite]] = {}
        
        # Configurações por satélite
        self.configuracoes_satelites = {
            TipoSatelite.SENTINEL: {
                "sensor": TipoSensor.MULTIESPECTRAL,
                "resolucao_m": 10.0,
                "cobertura_max_graus": 180.0,
                "frequencia_dias": 5,
                "max_safras": 10
            },
            TipoSatelite.LANDSAT: {
                "sensor": TipoSensor.MULTIESPECTRAL,
                "resolucao_m": 30.0,
                "cobertura_max_graus": 180.0,
                "frequencia_dias": 16,
                "max_safras": 5
            },
            TipoSatelite.PLANET: {
                "sensor": TipoSensor.MULTIESPECTRAL,
                "resolucao_m": 3.0,
                "cobertura_max_graus": 180.0,
                "frequencia_dias": 1,
                "max_safras": 15
            },
            TipoSatelite.CBERS: {
                "sensor": TipoSensor.MULTIESPECTRAL,
                "resolucao_m": 20.0,
                "cobertura_max_graus": 180.0,
                "frequencia_dias": 26,
                "max_safras": 8
            },
            TipoSatelite.SENTINEL_2: {
                "sensor": TipoSensor.MULTIESPECTRAL,
                "resolucao_m": 10.0,
                "cobertura_max_graus": 180.0,
                "frequencia_dias": 5,
                "max_safras": 10
            },
            TipoSatelite.SENTINEL_1: {
                "sensor": TipoSensor.RADAR,
                "resolucao_m": 10.0,
                "cobertura_max_graus": 180.0,
                "frequencia_dias": 12,
                "max_safras": 10
            },
            TipoSatelite.MODIS: {
                "sensor": TipoSensor.MULTIESPECTRAL,
                "resolucao_m": 250.0,
                "cobertura_max_graus": 180.0,
                "frequencia_dias": 1,
                "max_safras": 20
            }
        }
    
    def _criar_infraestrutura_satelites(self) -> Dict[str, Dict[str, Any]]:
        """Criar infraestrutura completa de satélites suportados."""
        return {
            TipoSatelite.SENTINEL.value: {
                "nome": "Sentinel-1",
                "agencia": "ESA",
                "descricao": "Satélite de radar para observação contínua",
                "disponivel": True,
                "instrumentos": ["C-SAR", "SLC", "GRD"]
            },
            TipoSatelite.LANDSAT.value: {
                "nome": "Landsat",
                "agencia": "USGS",
                "descricao": "Série de satélites para observação terrestre de longo prazo",
                "disponivel": True,
                "instrumentos": ["OLI", "ETM+", "TM", "MSS"]
            },
            TipoSatelite.PLANET.value: {
                "nome": "PlanetScope",
                "agencia": "Planet",
                "descricao": "Constelação de pequenos satélites para imagens de alta frequência",
                "disponivel": True,
                "instrumentos": ["PlanetScope", "SkySat"]
            },
            TipoSatelite.CBERS.value: {
                "nome": "CBERS",
                "agencia": "INPE",
                "descricao": "Satélite sino-brasileiro de recursos terrestres",
                "disponivel": True,
                "instrumentos": ["WFI", "CCD", "IRMSS"]
            },
            TipoSatelite.SENTINEL_2.value: {
                "nome": "Sentinel-2",
                "agencia": "ESA",
                "descricao": "Satélite para serviços de monitoramento terrestre",
                "disponivel": True,
                "instrumentos": ["MSI", "SLSTR"]
            },
            TipoSatelite.SENTINEL_1.value: {
                "nome": "Sentinel-1",
                "agencia": "ESA",
                "descricao": "Satélite de radar C-band para todas as condições meteorológicas",
                "disponivel": True,
                "instrumentos": ["C-SAR"]
            },
            TipoSatelite.MODIS.value: {
                "nome": "MODIS",
                "agencia": "NASA",
                "descricao": "Instrumento de imagens moderada resolução para sensoriamento terrestre",
                "disponivel": True,
                "instrumentos": ["Terra MODIS", "Aqua MODIS"]
            }
        }
    
    def selecionar_satelite(self, config_area: ConfigAreaSensoriamento,
                          config_satelite: ConfigSatelite,
                          modo: str = "automatico",
                          preferencias: Optional[Dict[str, Any]] = None) -> List[ImagemSatelite]:
        """
        Selecionar satélite(s) conforme configuração da área e preferências.
        
        Args:
            config_area: Configuração da área
            config_satelite: Configuração do satélite
            modo: 'automatico' ou 'manual'
            preferencias: Preferências adicionais para seleção
        
        Returns:
            Lista de imagens selecionadas
        """
        logger.info(f"Selecionando satélite em modo {modo}")
        
        if modo == "manual":
            return self._selecao_manual(config_satelite)
        elif modo == "automatico":
            return self._selecao_automatica(config_area, config_satelite, preferencias)
        else:
            raise ValueError(f"Modo de seleção inválido: {modo}")
    
    def _selecao_automatica(self, config_area: ConfigAreaSensoriamento,
                           config_satelite: ConfigSatelite,
                           preferencias: Optional[Dict[str, Any]] = None) -> List[ImagemSatelite]:
        """Seleção automática baseada em critérios técnicos."""
        logger.info("Realizando seleção automática de satélites")
        
        imagens_selecionadas = []
        
        # Verificar quais satélites são adequados para a área
        satelites_adequados = self._filtrar_satelites_por_area(config_area)
        
        # Ordenar por prioridade (resolução + frequência + cobertura)
        satelites_priorizados = self._priorizar_satelites(satelites_adequados, config_area)
        
        # Selecionar imagens para cada satélite priorizado
        for satelite_info in satelites_priorizados:
            imagens = self._buscar_imagens_satelite(
                satelite_info["tipo"], config_area, config_satelite
            )
            imagens_selecionadas.extend(imagens)
            
            # Limitar número de satélites conforme preferência
            if preferencias and preferencias.get("max_satelites", 3) <= len(imagens_selecionadas):
                break
        
        logger.info(f"Seleção automática concluída: {len(imagens_selecionadas)} imagens")
        return imagens_selecionadas
    
    def _selecao_manual(self, config_satelite: ConfigSatelite) -> List[ImagemSatelite]:
        """Seleção manual específica do usuário."""
        logger.info("Realizando seleção manual de satélites")
        
        tipo_satelite = config_satelite.satelite
        imagens = []
        
        # Buscar apenas para o satélite especificado
        config_area = ConfigAreaSensoriamento()  # Área genérica para busca
        imagens_satelite = self._buscar_imagens_satelite(tipo_satelite, config_area, config_satelite)
        imagens.extend(imagens_satelite)
        
        logger.info(f"Seleção manual concluída: {len(imagens)} imagens de {tipo_satelite.value}")
        return imagens
    
    def _filtrar_satelites_por_area(self, config_area: ConfigAreaSensoriamento) -> List[Dict[str, Any]]:
        """Filtrar satélites adequados para a área geográfica."""
        satelites_adequados = []
        
        for tipo_satelite, info in self.satelites_disponiveis.items():
            if not info["disponivel"]:
                continue
            
            # Verificar cobertura geográfica
            cobertura_adequada = self._verificar_cobertura_geografica(
                config_area, tipo_satelite
            )
            
            if cobertura_adequada:
                satelites_adequados.append({
                    "tipo": tipo_satelite,
                    "info": info,
                    "config": self.configuracoes_satelites[tipo_satelite]
                })
        
        logger.info(f"Satélites adequados para área: {len(satelites_adequados)}")
        return satelites_adequados
    
    def _priorizar_satelites(self, satelites_adequados: List[Dict[str, Any]],
                           config_area: ConfigAreaSensoriamento) -> List[Dict[str, Any]]:
        """Priorizar satélites por resolução, frequência e cobertura."""
        satelites_com_score = []
        
        for satelite_info in satelites_adequados:
            tipo_satelite = satelite_info["tipo"]
            config_satelite = self.configuracoes_satelites[tipo_satelite]
            
            # Calcular score baseado em múltiplos critérios
            score = self._calcular_score_satelite(config_area, config_satelite)
            
            satelite_info["score"] = score
            satelites_com_score.append(satelite_info)
        
        # Ordenar por score (maior primeiro)
        satelites_priorizados = sorted(satelites_com_score, key=lambda x: x["score"], reverse=True)
        
        logger.info("Satélites priorizados por score")
        return satelites_priorizados
    
    def _verificar_cobertura_geografica(self, config_area: ConfigAreaSensoriamento,
                                      tipo_satelite: TipoSatelite) -> bool:
        """Verificar se o satélite cobre a área geográfica."""
        # Lógica simplificada - na implementação real, verificar limites orbitais
        # Por enquanto, assume-se que todos satélites globais cobrem qualquer área
        
        # Verificar se a área está dentro dos limites máximos
        poligono = config_area.poligono
        if "bounds" in poligono:
            bounds = poligono["bounds"]
            # Verificar se a área não é muito extensa para o satélite
            diff_lat = abs(bounds["max_lat"] - bounds["min_lat"])
            diff_lon = abs(bounds["max_lon"] - bounds["min_lon"])
            
            config = self.configuracoes_satelites[tipo_satelite]
            max_graus = config["cobertura_max_graus"]
            
            if diff_lat > max_graus or diff_lon > max_graus:
                logger.warning(f"Área muito extensa para {tipo_satelite.value}")
                return False
        
        return True
    
    def _calcular_score_satelite(self, config_area: ConfigAreaSensoriamento,
                               config_satelite: Dict[str, Any]) -> float:
        """Calcular score de adequação do satélite."""
        score = 0.0
        
        # 1. Resolução (quanto menor, melhor)
        resolucao = config_satelite["resolucao_m"]
        score += (1.0 / max(resolucao, 0.1)) * 0.3  # Peso 30%
        
        # 2. Frequência (quanto menor, melhor)
        frequencia = config_satelite["frequencia_dias"]
        score += (1.0 / max(frequencia, 1.0)) * 0.3  # Peso 30%
        
        # 3. Disponibilidade
        if config_satelite.get("disponivel", False):
            score += 1.0 * 0.2  # Peso 20%
        
        # 4. Cobertura
        cobertura = config_satelite.get("cobertura_max_graus", 180.0)
        score += (cobertura / 180.0) * 0.2  # Peso 20%
        
        return min(score, 10.0)  # Limitar score máximo
    
    def _buscar_imagens_satelite(self, tipo_satelite: TipoSatelite,
                               config_area: ConfigAreaSensoriamento,
                               config_satelite: ConfigSatelite) -> List[ImagemSatelite]:
        """Buscar imagens específicas de um satélite."""
        logger.info(f"Buscando imagens para satélite: {tipo_satelite.value}")
        
        imagens_encontradas = []
        
        # Gerar imagens simuladas para demonstrar funcionalidade
        # Na implementação real, consultaria APIs de satélites
        
        # Obter configuração padrão para o satélite
        config_default = self.configuracoes_satelites.get(tipo_satelite)
        
        if config_default:
            # Criar imagem base
            imagem_base = ImagemSatelite(
                imagem_id=f"{tipo_satelite.value}_001",
                satelite=tipo_satelite,
                sensor=config_default["sensor"],
                tipo_imagem=TipoImagem.SATELITE,
                data_captura=self._gerar_data_aleatoria(config_area),
                hora_captura="12:00:00",
                cloud_cover_pct=0.0,
                resolucao_m=config_default["resolucao_m"],
                caminho_arquivo=f"imagens/{tipo_satelite.value}_001.tif",
                formatos_disponiveis=["geotiff", "jpg"],
                status_processamento=StatusProcessamento.PENDENTE,
                safra_id="SAFRA_2026",
                areas_pertencentes=[config_area.area_id]
            )
            imagens_encontradas.append(imagem_base)
        
        # Adicionar múltiplas imagens se necessário
        num_imagens = 2  # Para demonstração
        for i in range(1, num_imagens):
            imagem = ImagemSatelite(
                imagem_id=f"{tipo_satelite.value}_{i+1:03d}",
                satelite=tipo_satelite,
                sensor=config_default["sensor"],
                tipo_imagem=TipoImagem.SATELITE,
                data_captura=self._gerar_data_aleatoria(config_area),
                hora_captura=f"14:{30*i:02d}:00",
                cloud_cover_pct=5.0 + (i * 2),
                resolucao_m=config_default["resolucao_m"],
                caminho_arquivo=f"imagens/{tipo_satelite.value}_{i+1:03d}.tif",
                formatos_disponiveis=["geotiff", "jpg"],
                status_processamento=StatusProcessamento.PENDENTE,
                safra_id="SAFRA_2026",
                areas_pertencentes=[config_area.area_id]
            )
            imagens_encontradas.append(imagem)
        
        logger.info(f"Encontradas {len(imagens_encontradas)} imagens para {tipo_satelite.value}")
        return imagens_encontradas
    
    def _gerar_data_aleatoria(self, config_area: ConfigAreaSensoriamento) -> str:
        """Gerar data aleatória dentro do período definido."""
        import random
        
        if config_area.data_inicio and config_area.data_fim:
            inicio = datetime.fromisoformat(config_area.data_inicio)
            fim = datetime.fromisoformat(config_area.data_fim)
            
            # Gerar data aleatória no período
            delta = fim - inicio
            dias_aleatorios = random.randint(0, delta.days)
            data_aleatoria = inicio + timedelta(days=dias_aleatorios)
            
            return data_aleatoria.strftime("%Y-%m-%d")
        else:
            # Data atual se período não definido
            return datetime.now().strftime("%Y-%m-%d")
    
    # Métodos públicos para consulta
    
    def obter_satelites_disponiveis(self) -> Dict[str, Dict[str, Any]]:
        """Obter todos satélites disponíveis."""
        return {sat: info for sat, info in self.satelites_disponiveis.items() if info["disponivel"]}
    
    def obter_sensores_satelite(self, tipo_satelite: TipoSatelite) -> List[TipoSensor]:
        """Obter sensores disponíveis para um satélite."""
        config = self.configuracoes_satelites.get(tipo_satelite, {})
        return [config.get("sensor", TipoSensor.MULTIESPECTRAL)]
    
    def verifica_disponibilidade(self, tipo_satelite: TipoSatelite,
                               config_area: ConfigAreaSensoriamento) -> bool:
        """Verificar se satélite está disponível para área específica."""
        if tipo_satelite not in self.satelites_disponivevis:
            return False
        
        return self._verificar_cobertura_geografica(config_area, tipo_satelite)
    
    def suporta_satelite(self, tipo_satelite: TipoSatelite) -> bool:
        """Verificar se sistema suporta o satélite."""
        return tipo_satelite in self.satelites_disponiveis
    
    # Métodos para expansão futura
    
    def adicionar_satelite(self, tipo_satelite: TipoSatelite, configuracao: Dict[str, Any]) -> bool:
        """Adicionar novo satélite ao sistema."""
        logger.info(f"Adicionando satélite: {tipo_satelite.value}")
        
        try:
            self.satelites_disponiveis[tipo_satelite.value] = configuracao
            self.configuracoes_satelites[tipo_satelite] = configuracao
            logger.info(f"Satélite {tipo_satelite.value} adicionado com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar satélite: {e}")
            return False
    
    def remover_satelite(self, tipo_satelite: TipoSatelite) -> bool:
        """Remover satélite do sistema."""
        logger.info(f"Removendo satélite: {tipo_satelite.value}")
        
        try:
            if tipo_satelite.value in self.satelites_disponiveis:
                del self.satelites_disponiveis[tipo_satelite.value]
            if tipo_satelite in self.configuracoes_satelites:
                del self.configuracoes_satelites[tipo_satelite]
            
            logger.info(f"Satélite {tipo_satelite.value} removido com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover satélite: {e}")
            return False
    
    # Método de validação
    
    def validar_config_satelite(self, config_satelite: ConfigSatelite) -> List[str]:
        """Validar configuração de satélite."""
        erros = []
        
        if not self.suporta_satelite(config_satelite.satelite):
            erros.append(f"Satélite não suportado: {config_satelite.satelite.value}")
        
        if config_satelite.resolucao_m <= 0:
            erros.append("Resolução deve ser maior que zero")
        
        if config_satelite.frequencia_dias <= 0:
            erros.append("Frequência deve ser maior que zero")
        
        return erros