"""
Precision VRT Solo — Motor de Zoneamento

Classe orquestradora que valida, normaliza, executa algoritmos, caracteriza e calcula métricas.
Integração completa da ETAPA Z2 com normalização, caracterização e métricas de qualidade.
"""

import logging
import time
from typing import List

import geopandas as gpd
import numpy as np

from .configuracao import ALGORITMO_REGISTRY, ConfigZoneamento, DEFAULT_CONFIG
from .contratos import ResultadoZoneamento, PerfilZona
from .exceptions import ConfiguracaoError
from .validacao import validar_geodataframe, validar_configuracao, extrair_features
from .utils import Normalizador, CalculadorMetricas

# Funções de caracterização (compatibilidade com código anterior)
def caracterizar_zonas(gdf: gpd.GeoDataFrame, colunas_features: List[str]) -> dict:
    """
    Caracteriza as zonas do GeoDataFrame.
    Retorna dicionário com estatísticas por zona.
    """
    if 'zona' not in gdf.columns:
        raise ConfiguracaoError("GeoDataFrame deve conter coluna 'zona'")
    
    # Identificar colunas numéricas
    colunas_numericas = []
    for coluna in colunas_features:
        if coluna in gdf.columns:
            try:
                # Testar se é numérico
                pd.to_numeric(gdf[coluna].dropna())
                colunas_numericas.append(coluna)
            except:
                # Não é numérico, pular
                continue
    
    perfis = {}
    zonas_unicas = gdf['zona'].unique()
    
    for zona_id in zonas_unicas:
        gdf_zona = gdf[gdf['zona'] == zona_id]
        perfil = {}
        
        for coluna in colunas_numericas:
            valores = gdf_zona[coluna].dropna()
            if len(valores) > 0:
                perfil[coluna] = {
                    'media': float(valores.mean()),
                    'desvio': float(valores.std()),
                    'min': float(valores.min()),
                    'max': float(valores.max()),
                    'count': len(valores)
                }
        
        perfis[zona_id] = perfil
    
    return perfis

logger = logging.getLogger(__name__)

__all__ = [
    'Zoneador',
]


class Zoneador:
    """
    Classe principal para orquestração do processo de zoneamento.
    
    É responsável por:
    1. Validar entrada
    2. Extrair features e normalizar (NOVO Z2)
    3. Selecionar algoritmo apropriado
    4. Executar zoneamento
    5. Caracterizar zonas (NOVO Z2)
    6. Calcular métricas de qualidade (NOVO Z2)
    7. Retornar resultado completo
    """
    
    def __init__(self, config: ConfigZoneamento = None):
        """
        Inicializa o zoneador.
        
        Args:
            config: Configuração de zoneamento. Se None, usa DEFAULT_CONFIG.
        """
        self.config = config or DEFAULT_CONFIG
        self._historico: List[ResultadoZoneamento] = []
        
        # Inicializar componentes de Z2
        self.normalizador = Normalizador("minmax")  # Default para compatibilidade
        self.calculador_metricas = CalculadorMetricas()
        
        logger.info(f"Zoneador inicializado com config: {self.config}")
    
    def executar(self, gdf: gpd.GeoDataFrame) -> ResultadoZoneamento:
        """
        Executa o processo completo de zoneamento.
        Fluxo integrado da ETAPA Z2: validação → normalização → algoritmo → caracterização → métricas.
        
        Args:
            gdf: GeoDataFrame com dados para zoneamento
            
        Returns:
            Resultado do zoneamento completo
            
        Raises:
            ValidacaoError: Se os dados ou configuração forem inválidos
            ConfiguracaoError: Se o algoritmo não estiver no registro
        """
        import time
        start_time = time.time()
        
        # 1. Validar entrada
        logger.debug("Validando entrada...")
        validar_geodataframe(gdf)
        validar_configuracao(self.config, gdf)
        
        # 2. Extrair features
        logger.debug("Extraindo features...")
        X = self._extrair_features(gdf, self.config)
        
        # 3. Normalizar (NOVO Z2)
        X_normalizado = X
        if self.config.normalizar:
            logger.debug("Aplicando normalização...")
            X_normalizado = self.normalizador.normalizar(X)
            
            # Aplicar pesos se fornecidos
            if self.config.pesos_features and self.config.colunas_features:
                logger.debug("Aplicando pesos às features...")
                X_normalizado = self._aplicar_pesos(X_normalizado, self.config.pesos_features, self.config.colunas_features)
        
        # 4. Resolver algoritmo via registry
        logger.debug("Resolvendo algoritmo...")
        try:
            # Importar dinamicamente a classe do algoritmo
            module_path, class_name = ALGORITMO_REGISTRY[self.config.algoritmo].rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            classe_algoritmo = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ConfiguracaoError(
                f"Algoritmo '{self.config.algoritmo.value}' não encontrado no registro"
            ) from e
        
        # 5. Criar e executar algoritmo (passar X normalizado)
        logger.debug("Executando algoritmo...")
        algoritmo = classe_algoritmo(self.config)
        resultado = algoritmo.executar(gdf, self.config, X_normalizado=X_normalizado)
        
        # 6. Caracterizar zonas (NOVO Z2)
        logger.debug("Caracterizando zonas...")
        colunas = self.config.colunas_features or [c for c in gdf.columns if c not in ['geometry', 'zona']]
        perfis = caracterizar_zonas(resultado.gdf, colunas)
        resultado.perfis = perfis
        
        # 7. Calcular métricas (NOVO Z2)
        logger.debug("Calculando métricas de qualidade...")
        try:
            # Converter labels para índices começando em 0
            labels = resultado.gdf['zona'].values - 1
            
            # Agrupar dados por cluster
            clusters = {}
            unique_labels = np.unique(labels)
            
            for label in unique_labels:
                cluster_data = X_normalizado[labels == label]
                clusters[int(label)] = cluster_data
            
            # Calcular métricas
            inercia = self.calculador_metricas.calcular_inercia_intra(clusters)
            silhueta = self.calculador_metricas.calcular_silhueta_media(X_normalizado, clusters)
            calinski = self.calculador_metricas.calcular_indice_calinski_harabasz(X_normalizado, clusters)
            
            resultado.metricas = {
                'inercia_intra': inercia,
                'silhueta_media': silhueta,
                'calinski_harabasz': calinski
            }
        except Exception as e:
            logger.warning(f"Não foi possível calcular métricas: {e}")
            resultado.metricas = {
                'inercia_intra': None,
                'silhueta_media': None,
                'calinski_harabasz': None
            }
        
        # 8. Registrar no histórico
        resultado.tempo_execucao_ms = (time.time() - start_time) * 1000
        self._historico.append(resultado)
        
        logger.info(
            f"Zoneamento concluído: {resultado.n_zonas_efetivas} zonas, "
            f"tempo={resultado.tempo_execucao_ms:.2f}ms, "
            f"métricas={len(resultado.metricas)} calculadas"
        )
        
        return resultado
    
    def _extrair_features(self, gdf: gpd.GeoDataFrame, config: ConfigZoneamento) -> np.ndarray:
        """
        Extrai features do GeoDataFrame para algoritmos de clustering.
        Método privado para reutilização.
        
        Args:
            gdf: GeoDataFrame com dados
            config: Configuração de zoneamento
            
        Returns:
            Array numpy 2D com features extraídas
        """
        from .validacao import extrair_features
        return extrair_features(gdf, config)
    
    def _aplicar_pesos(self, X: np.ndarray, pesos: dict, colunas: list) -> np.ndarray:
        """
        Aplica pesos às features normalizadas.
        Método privado para reutilização.
        
        Args:
            X: Array numpy 2D normalizado
            pesos: Dicionário com pesos por feature
            colunas: Lista de nomes das colunas
            
        Returns:
            Array numpy 2D com pesos aplicados
        """
        from .utils.matriz import aplicar_pesos_features
        return aplicar_pesos_features(X, pesos, colunas)
    
    @property
    def historico(self) -> List[ResultadoZoneamento]:
        """
        Retorna cópia do histórico de execuções.
        
        Returns:
            Lista de resultados de zoneamento
        """
        return self._historico.copy()