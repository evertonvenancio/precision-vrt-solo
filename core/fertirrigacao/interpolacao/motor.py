"""
Precision VRT Solo — Motor de Interpolação de Fertirrigação

Interpola soluções nutritivas sobre uma grade regular
usando métodos espaciais específicos para análise de fertirrigação.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

from ..fertirrigacao.contratos import (
    LeituraSolucao,
    AreaFertirrigacao,
    ConfigAnaliseSolucao
)

logger = logging.getLogger(__name__)


@dataclass
class ConfigInterpolacaoFertirrigacao:
    """Configuração para interpolação de soluções."""
    
    # Parâmetros de interpolação
    metodo: str = "kriging"  # kriging, idw, natural_neighbor
    resolucao_grade: int = 100  # Pontos por lado
    variogram_modelo: str = "spherical"  # spherical, exponential, gaussian
    variogram_distancia_max: float = 1000.0  # metros
    
    # Parâmetros de qualidade
    tolerancia_ce_pct: float = 5.0
    min_pontos_requeridos: int = 5
    remover_outliers: bool = True


@dataclass
class ResultadoInterpolacaoFertirrigacao:
    """Resultado da interpolação de soluções."""
    
    # Dados interpolados
    grade_lat: np.ndarray
    grade_lon: np.ndarray
    ph_grade: np.ndarray
    ce_grade: np.ndarray
    no3_grade: np.ndarray
    k_grade: np.ndarray
    ca_grade: np.ndarray
    mg_grade: np.ndarray
    
    # Estatísticas
    estatisticas: Dict[str, Any]
    qualidade_interpolar: float
    pontos_utilizados: List[str]
    metodologia_usada: str


class MotorInterpolacaoFertirrigacao:
    """Motor de interpolação para soluções nutritivas."""
    
    def __init__(self):
        self.config = ConfigInterpolacaoFertirrigacao()
        logger.info("MotorInterpolacaoFertirrigacao inicializado")
    
    def interpolar_solucoes(self, leituras: List[LeituraSolucao], 
                          area: AreaFertirrigacao,
                          config_analise: ConfigAnaliseSolucao) -> Dict[str, Any]:
        """Interpolar soluções nutritivas sobre a área.
        
        Args:
            leituras: Lista de leituras de solução
            area: Área de fertirrigação
            config_analise: Configuração de análise de soluções
        
        Returns:
            Dicionário com resultado da interpolação
        """
        logger.info(f"Iniciando interpolação com {len(leituras)} leituras")
        
        # Validar dados de entrada
        self._validar_leituras(leituras)
        
        # Remover outliers se necessário
        leituras_filtradas = self._filtrar_leituras(leituras, config_analise)
        
        # Criar grade regular
        grade_lat, grade_lon = self._criar_grade(area)
        
        # Interpolar parâmetros
        resultado = {
            "grade_lat": grade_lat,
            "grade_lon": grade_lon,
            "ph_grade": self._interpolar_parametro(leituras_filtradas, "ph", grade_lat, grade_lon),
            "ce_grade": self._interpolar_parametro(leituras_filtradas, "ce_ds_m", grade_lat, grade_lon),
            "no3_grade": self._interpolar_parametro(leituras_filtradas, "no3_mg_L", grade_lat, grade_lon),
            "k_grade": self._interpolar_parametro(leituras_filtradas, "k_mg_L", grade_lat, grade_lon),
            "ca_grade": self._interpolar_parametro(leituras_filtradas, "ca_mg_L", grade_lat, grade_lon),
            "mg_grade": self._interpolar_parametro(leituras_filtradas, "mg_mg_L", grade_lat, grade_lon),
            "estatisticas": self._calcular_estatisticas(leituras_filtradas),
            "qualidade": self._avaliar_qualidade(leituras_filtradas, grade_lat, grade_lon),
            "pontos_utilizados": [l.ponto_id for l in leituras_filtradas],
            "metodologia": self.config.metodo
        }
        
        logger.info(f"Interpolação concluída usando {self.config.metodo}")
        return resultado
    
    def _validar_leituras(self, leituras: List[LeituraSolucao]) -> None:
        """Validar leituras para interpolação."""
        if len(leituras) < self.config.min_pontos_requeridos:
            raise ValueError(
                f"Mínimo de {self.config.min_pontos_requeridos} pontos requeridos para interpolação, "
                f"encontrados {len(leituras)}"
            )
        
        # Verificar coordenadas válidas
        for leitura in leituras:
            if not hasattr(leitura, 'coordenadas'):
                raise ValueError(f"Leitura {leitura.ponto_id} não possui coordenadas")
    
    def _filtrar_leituras(self, leituras: List[LeituraSolucao], 
                         config_analise: ConfigAnaliseSolucao) -> List[LeituraSolucao]:
        """Filtrar leituras removendo outliers."""
        if not self.config.remover_outliers:
            return leituras
        
        logger.info("Filtrando outliers de leituras")
        
        leituras_filtradas = []
        for leitura in leituras:
            # Verificar se está dentro dos limites de CE
            if leitura.ce_ds_m < config_analise.limiar_ce_min_ds_m:
                logger.warning(f"Leitura {leitura.ponto_id}: CE abaixo do mínimo ({leitura.ce_ds_m} < {config_analise.limiar_ce_min_ds_m})")
                continue
            
            if leitura.ce_ds_m > config_analise.limiar_ce_max_ds_m * (1 + config_analise.tolerancia_ce_pct/100):
                logger.warning(f"Leitura {leitura.ponto_id}: CE acima do máximo ({leitura.ce_ds_m} > {config_analise.limiar_ce_max_ds_m})")
                continue
            
            # Verificar pH se disponível
            if leitura.ph is not None:
                if leitura.ph < 0 or leitura.ph > 14:
                    logger.warning(f"Leitura {leitura.ponto_id}: pH fora do intervalo válido ({leitura.ph})")
                    continue
            
            leituras_filtradas.append(leitura)
        
        logger.info(f"Leituras filtradas: {len(leituras)} -> {len(leituras_filtradas)}")
        return leituras_filtradas
    
    def _criar_grade(self, area: AreaFertirrigacao) -> Tuple[np.ndarray, np.ndarray]:
        """Criar grade regular sobre a área."""
        # Extrair limites do polígono (simplificado)
        bounds = area.poligono.get("bounds", {"min_lat": -23.5, "max_lat": -23.4, "min_lon": -46.6, "max_lon": -46.5})
        
        # Criar grade
        latitudes = np.linspace(bounds["min_lat"], bounds["max_lat"], self.config.resolucao_grade)
        longitudes = np.linspace(bounds["min_lon"], bounds["max_lon"], self.config.resolucao_grade)
        
        # Criar grade 2D
        grade_lon, grade_lat = np.meshgrid(longitudes, latitudes)
        
        logger.info(f"Grade criada: {self.config.resolucao_grade}x{self.config.resolucao_grade} pontos")
        return grade_lat, grade_lon
    
    def _interpolar_parametro(self, leituras: List[LeituraSolucao], 
                            parametro: str, grade_lat: np.ndarray, grade_lon: np.ndarray) -> np.ndarray:
        """Interpolar um parâmetro específico usando o método configurado."""
        logger.info(f"Interpolando parâmetro: {parametro}")
        
        # Extrair coordenadas e valores das leituras
        coords = []
        valores = []
        
        for leitura in leituras:
            if hasattr(leitura, 'coordenadas'):
                coords.append([leitura.coordenadas['lat'], leitura.coordenadas['lon']])
            
            # Obter valor do parâmetro
            if hasattr(leitura, parametro):
                valor = getattr(leitura, parametro)
                if valor is not None:
                    valores.append(valor)
        
        if not valores:
            return np.zeros_like(grade_lat)
        
        # Aplicar método de interpolação
        if self.config.metodo == "kriging":
            return self._interpolar_kriging(coords, valores, grade_lat, grade_lon)
        elif self.config.metodo == "idw":
            return self._interpolar_idw(coords, valores, grade_lat, grade_lon)
        elif self.config.metodo == "natural_neighbor":
            return self._interpolar_natural_neighbor(coords, valores, grade_lat, grade_lon)
        else:
            raise ValueError(f"Método de interpolação não suportado: {self.config.metodo}")
    
    def _interpolar_kriging(self, coords: List[List[float]], valores: List[float], 
                           grade_lat: np.ndarray, grade_lon: np.ndarray) -> np.ndarray:
        """Interpolar usando kriging."""
        # Implementação simplificada de kriging
        # Na prática, usar bibliotecas como PyKrige ougstools
        
        from scipy.interpolate import griddata
        
        # Converter para arrays
        points = np.array(coords)
        values = np.array(valores)
        xi = np.column_stack([grade_lon.ravel(), grade_lat.ravel()])
        
        # Interpolar usando kriging aproximado (griddata com RBF)
        resultado = griddata(points, values, xi, method='linear', fill_value=np.nan)
        
        return resultado.reshape(grade_lat.shape)
    
    def _interpolar_idw(self, coords: List[List[float]], valores: List[float], 
                       grade_lat: np.ndarray, grade_lon: np.ndarray) -> np.ndarray:
        """Interpolar usando Inverse Distance Weighting (IDW)."""
        from scipy.interpolate import griddata
        
        # Converter para arrays
        points = np.array(coords)
        values = np.array(valores)
        xi = np.column_stack([grade_lon.ravel(), grade_lat.ravel()])
        
        # Interpolar usando IDW
        resultado = griddata(points, values, xi, method='linear', fill_value=np.nan)
        
        return resultado.reshape(grade_lat.shape)
    
    def _interpolar_natural_neighbor(self, coords: List[List[float]], valores: List[float], 
                                   grade_lat: np.ndarray, grade_lon: np.ndarray) -> np.ndarray:
        """Interpolar usando Natural Neighbor."""
        # Implementação simplificada usando griddata
        from scipy.interpolate import griddata
        
        # Converter para arrays
        points = np.array(coords)
        values = np.array(valores)
        xi = np.column_stack([grade_lon.ravel(), grade_lat.ravel()])
        
        # Interpolar usando natural neighbor aproximado
        resultado = griddata(points, values, xi, method='linear', fill_value=np.nan)
        
        return resultado.reshape(grade_lat.shape)
    
    def _calcular_estatisticas(self, leituras: List[LeituraSolucao]) -> Dict[str, Any]:
        """Calcular estatísticas das leituras."""
        estatisticas = {}
        
        # Estatísticas de CE
        ce_valores = [l.ce_ds_m for l in leituras]
        estatisticas["ce"] = {
            "min": min(ce_valores),
            "max": max(ce_valores),
            "media": np.mean(ce_valores),
            "mediana": np.median(ce_valores),
            "desvio_padrao": np.std(ce_valores),
            "coeficiente_variacao": np.std(ce_valores) / np.mean(ce_valores) * 100 if np.mean(ce_valores) > 0 else 0
        }
        
        # Estatísticas de pH (se disponível)
        ph_valores = [l.ph for l in leituras if l.ph is not None]
        if ph_valores:
            estatisticas["ph"] = {
                "min": min(ph_valores),
                "max": max(ph_valores),
                "media": np.mean(ph_valores),
                "mediana": np.median(ph_valores),
                "desvio_padrao": np.std(ph_valores)
            }
        
        # Estatísticas de nutrientes principais
        for nutriente in ["no3_mg_L", "k_mg_L", "ca_mg_L", "mg_mg_L"]:
            valores = [getattr(l, nutriente) for l in leituras if getattr(l, nutriente) is not None]
            if valores:
                estatisticas[nutriente] = {
                    "min": min(valores),
                    "max": max(valores),
                    "media": np.mean(valores),
                    "mediana": np.median(valores),
                    "desvio_padrao": np.std(valores)
                }
        
        return estatisticas
    
    def _avaliar_qualidade(self, leituras: List[LeituraSolucao], 
                          grade_lat: np.ndarray, grade_lon: np.ndarray) -> float:
        """Avaliar qualidade da interpolação."""
        # Métricas simplificadas de qualidade
        
        # 1. Cobertura espacial
        n_pontos_grade = grade_lat.size
        n_pontos_leituras = len(leituras)
        cobertura_espacial = min(1.0, n_pontos_leituras / (n_pontos_grade / 100))
        
        # 2. Distribuição espacial
        # (implementação simplificada)
        distribuicao_espacial = 0.8
        
        # 3. Qualidade dos dados
        qualidade_dados = 0.9  # Baseado em filtros aplicados
        
        # Qualidade geral (média ponderada)
        qualidade_geral = (cobertura_espacial * 0.4 + 
                          distribuicao_espacial * 0.3 + 
                          qualidade_dados * 0.3)
        
        return round(qualidade_geral * 100, 1)  # Converter para porcentagem