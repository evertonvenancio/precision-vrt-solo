"""
Precision VRT Solo — Interpolação Espacial de Atributos de Solo

Interpola atributos químicos e físicos do solo sobre uma grade regular
usando RBF (Radial Basis Function) com normalização de coordenadas.
"""

import logging
import warnings
from typing import Dict, List, Optional, Tuple, Any, Union

import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.interpolate import RBFInterpolator, griddata
from scipy.spatial import cKDTree

# Imports dos submódulos extraídos
from .algoritmos import interpolar_rbf, interpolar_idw
from .grade import gerar_malha, normalizar_coordenadas
from .estatistica import calcular_estatisticas
from .configuracao import (
    MetodoInterpolacao,
    RESOLUCAO_PADRAO_M,
    FUNCAO_RBF_PADRAO,
    SUAVIZACAO_PADRAO,
    RANDOM_STATE_PADRAO,
    COLUNAS_COORDENADAS,
    COLUNAS_EXCLUIR,
)
from .contratos import EstatisticaInterpolacao, ConfigInterpolacao
from .validacao import validar_dados_entrada, detectar_coluna_coordenada, selecionar_atributos_numericos

logger = logging.getLogger(__name__)


class Interpolador:
    """Interpolador de atributos de solo usando métodos espaciais avançados."""

    def __init__(
        self,
        resolucao_m: int = RESOLUCAO_PADRAO_M,
        funcao: str = FUNCAO_RBF_PADRAO,
        suavizacao: float = SUAVIZACAO_PADRAO,
        config: Optional[ConfigInterpolacao] = None,
    ):
        """Inicializa o Interpolador.

        Args:
            resolucao_m: Resolução da grade em metros.
            funcao: Função RBF a ser utilizada.
            suavizacao: Parâmetro de suavização do RBF.
            config: Configuração avançada opcional.
        """
        self.config = config or ConfigInterpolacao(
            resolucao_m=resolucao_m,
            funcao_rbf=funcao,
            suavizacao=suavizacao,
        )
        self.resolucao_m = self.config.resolucao_m
        self.funcao = self.config.funcao_rbf
        self.suavizacao = self.config.suavizacao

        self.resultados: Optional[Dict[str, Any]] = None
        self.atributos_interpolados: Optional[List[str]] = None
        self.estatisticas: Optional[Dict[str, EstatisticaInterpolacao]] = None
        self.grid_x: Optional[np.ndarray] = None
        self.grid_y: Optional[np.ndarray] = None
        self.coordenadas: Optional[Dict[str, float]] = None
        self.x_original: Optional[np.ndarray] = None
        self.y_original: Optional[np.ndarray] = None

    def interpolar_talhao(
        self,
        gdf: Union[gpd.GeoDataFrame, pd.DataFrame],
        x_col: Optional[str] = None,
        y_col: Optional[str] = None,
        atributos: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Interpola todos os atributos numéricos do GeoDataFrame ou DataFrame.

        Args:
            gdf: GeoDataFrame ou DataFrame com dados de solo.
            x_col: Nome da coluna de longitude/X. Se None, detecta automaticamente.
            y_col: Nome da coluna de latitude/Y. Se None, detecta automaticamente.
            atributos: Lista de atributos a interpolar. Se None, detecta automaticamente.
            **kwargs: Parâmetros adicionais para sobrescrever configuração.

        Returns:
            Dict com grid_x, grid_y, coordenadas, atributos interpolados e estatísticas.
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        validar_dados_entrada(gdf)

        x, y, df = self._extrair_coordenadas(gdf, x_col, y_col)

        atributos_interp = selecionar_atributos_numericos(df, COLUNAS_EXCLUIR)

        if not atributos_interp:
            raise ValueError("Nenhum atributo numérico encontrado para interpolação")

        grid_x, grid_y = gerar_malha(x, y, self.resolucao_m)

        resultados = {"atributos": {}}
        estatisticas: Dict[str, EstatisticaInterpolacao] = {}

        for attr in atributos_interp:
            try:
                pred, est = self._interpolar_atributo(x, y, df, attr, grid_x, grid_y)
                resultados["atributos"][attr] = {
                    "predicao": pred,
                    **est.to_dict(),
                }
                estatisticas[attr] = est
            except Exception as e:
                logger.error("Erro na interpolação de '%s': %s", attr, e)
                continue

        resultados["grid_x"] = grid_x
        resultados["grid_y"] = grid_y
        resultados["coordenadas"] = {
            "xmin": float(x.min()),
            "xmax": float(x.max()),
            "ymin": float(y.min()),
            "ymax": float(y.max()),
        }
        resultados["estatisticas"] = {k: v.to_dict() for k, v in estatisticas.items()}
        resultados["atributos_interpolados"] = list(resultados["atributos"].keys())
        resultados["configuracao"] = self.config.to_dict()

        self.resultados = resultados
        self.atributos_interpolados = resultados["atributos_interpolados"]
        self.estatisticas = estatisticas
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.coordenadas = resultados["coordenadas"]

        return resultados

    def _extrair_coordenadas(
        self,
        gdf: Union[gpd.GeoDataFrame, pd.DataFrame],
        x_col: Optional[str] = None,
        y_col: Optional[str] = None,
    ) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
        """Extrai coordenadas X/Y do GeoDataFrame ou DataFrame."""
        if isinstance(gdf, gpd.GeoDataFrame):
            x = np.array([geom.x for geom in gdf.geometry], dtype=float)
            y = np.array([geom.y for geom in gdf.geometry], dtype=float)
            df = pd.DataFrame(gdf.drop(columns="geometry"))
        else:
            # DataFrame com colunas x/y
            if x_col is None:
                x_col = detectar_coluna_coordenada(gdf, "x")
            if y_col is None:
                y_col = detectar_coluna_coordenada(gdf, "y")

            if x_col not in gdf.columns:
                raise ValueError(f"Coluna X '{x_col}' não encontrada")
            if y_col not in gdf.columns:
                raise ValueError(f"Coluna Y '{y_col}' não encontrada")

            x = np.asarray(gdf[x_col].values, dtype=float)
            y = np.asarray(gdf[y_col].values, dtype=float)
            df = gdf.copy()

        self.x_original = x.copy()
        self.y_original = y.copy()

        logger.info("Coordenadas extraídas: %d pontos.", len(x))

        return x, y, df

    def _tratar_outliers(self, valores: np.ndarray) -> np.ndarray:
        """Trata outliers usando o método do desvio padrão."""
        if not self.config.tratar_outliers:
            return valores

        media = np.nanmean(valores)
        desvio = np.nanstd(valores)

        if desvio == 0:
            return valores

        limite_inferior = media - self.config.limite_outlier_std * desvio
        limite_superior = media + self.config.limite_outlier_std * desvio

        valores_tratados = valores.copy()
        mascara_outliers = (valores < limite_inferior) | (valores > limite_superior)

        if mascara_outliers.any():
            n_outliers = mascara_outliers.sum()
            valores_tratados[mascara_outliers] = np.nan
            logger.info("%d outliers tratados (limites: %.2f - %.2f).",
                        n_outliers, limite_inferior, limite_superior)

        return valores_tratados

    def _preencher_nulos(self, valores: np.ndarray) -> np.ndarray:
        """Preenche valores nulos com a mediana."""
        if not self.config.preencher_nulos:
            return valores

        valores = valores.copy()
        mask_nan = np.isnan(valores)

        if mask_nan.any():
            mediana = np.nanmedian(valores)
            if np.isnan(mediana):
                mediana = 0.0
            valores[mask_nan] = mediana
            logger.info("%d valores nulos preenchidos com mediana (%.2f).",
                        mask_nan.sum(), mediana)

        return valores

    def _interpolar_atributo(
        self,
        x: np.ndarray,
        y: np.ndarray,
        df: pd.DataFrame,
        attr: str,
        grid_x: np.ndarray,
        grid_y: np.ndarray,
    ) -> Tuple[np.ndarray, EstatisticaInterpolacao]:
        """Interpola um único atributo."""
        z = np.asarray(df[attr].values, dtype=float)

        # Tratar outliers
        z = self._tratar_outliers(z)

        # Filtrar NaN
        mask_validos = ~np.isnan(z)
        if mask_validos.sum() < 4:
            logger.warning("Atributo '%s' possui menos de 4 pontos válidos. Pulando.", attr)
            raise ValueError(f"Pontos válidos insuficientes para '{attr}'")

        x_valid = x[mask_validos]
        y_valid = y[mask_validos]
        z_valid = z[mask_validos]

        # Preencher nulos se necessário (não deve haver nulos após filtro, mas garante)
        z_valid = self._preencher_nulos(z_valid)

        # Normalizar coordenadas para estabilidade numérica
        if self.config.normalizar_coords:
            xy_norm, grid_norm = normalizar_coordenadas(x_valid, y_valid, grid_x, grid_y)
        else:
            xy_norm = np.column_stack([x_valid, y_valid])
            grid_norm = np.column_stack([grid_x.ravel(), grid_y.ravel()])

        # Executar interpolação
        metodo = self.config.metodo.lower()

        if metodo == "rbf":
            pred = interpolar_rbf(xy_norm, z_valid, grid_norm, grid_x.shape, self.funcao, self.suavizacao)
        elif metodo == "idw":
            pred = interpolar_idw(xy_norm, z_valid, grid_norm, grid_x.shape)
        elif metodo == "nearest":
            pred = self._interpolar_nearest(xy_norm, z_valid, grid_norm, grid_x.shape)
        elif metodo == "linear":
            pred = self._interpolar_griddata(xy_norm, z_valid, grid_norm, grid_x.shape, "linear")
        elif metodo == "cubic":
            pred = self._interpolar_griddata(xy_norm, z_valid, grid_norm, grid_x.shape, "cubic")
        else:
            logger.warning("Método '%s' desconhecido. Usando RBF.", metodo)
            pred = interpolar_rbf(xy_norm, z_valid, grid_norm, grid_x.shape, self.funcao, self.suavizacao)

        # Calcular estatísticas
        est = self._calcular_estatisticas(z_valid, pred)

        logger.info("Interpolação de '%s' concluída. Média: %.2f, Min: %.2f, Max: %.2f",
                    attr, est.media, est.minimo, est.maximo)

        return pred, est

    def _interpolar_nearest(
        self,
        xy: np.ndarray,
        z: np.ndarray,
        grid: np.ndarray,
        shape: Tuple[int, int],
    ) -> np.ndarray:
        """Interpolação usando vizinho mais próximo."""
        tree = cKDTree(xy)
        _, indices = tree.query(grid, k=1)
        return z[indices].reshape(shape)

    def _interpolar_griddata(
        self,
        xy: np.ndarray,
        z: np.ndarray,
        grid: np.ndarray,
        shape: Tuple[int, int],
        metodo: str,
    ) -> np.ndarray:
        """Interpolação usando scipy.griddata."""
        pred = griddata(xy, z, grid, method=metodo, fill_value=np.nanmedian(z))
        return pred.reshape(shape)

    def _calcular_estatisticas(
        self,
        z_valid: np.ndarray,
        pred: np.ndarray,
    ) -> EstatisticaInterpolacao:
        """Calcula estatísticas do atributo interpolado."""
        est_dict = calcular_estatisticas(z_valid, pred)
        
        return EstatisticaInterpolacao(
            minimo=est_dict["minimo"],
            maximo=est_dict["maximo"],
            media=est_dict["media"],
            mediana=est_dict["mediana"],
            desvio=est_dict["desvio"],
            variancia=est_dict["variancia"],
            q1=est_dict["q1"],
            q3=est_dict["q3"],
            iqr=est_dict["iqr"],
            coef_variacao=est_dict["coef_variacao"],
            n_pontos_validos=est_dict["n_pontos_validos"],
            n_pontos_interpolados=est_dict["n_pontos_interpolados"],
            pct_cobertura=est_dict["pct_cobertura"],
        )

    def obter_resultados(self) -> Optional[Dict[str, Any]]:
        """Retorna os resultados da última interpolação."""
        return self.resultados

    def obter_atributos_interpolados(self) -> Optional[List[str]]:
        """Retorna a lista de atributos interpolados."""
        return self.atributos_interpolados

    def obter_estatisticas(self) -> Optional[Dict[str, EstatisticaInterpolacao]]:
        """Retorna as estatísticas dos atributos interpolados."""
        return self.estatisticas

    def obter_grid(self) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """Retorna a malha de interpolação."""
        if self.grid_x is None or self.grid_y is None:
            return None
        return self.grid_x, self.grid_y

    def obter_coordenadas(self) -> Optional[Dict[str, float]]:
        """Retorna as coordenadas dos limites do talhão."""
        return self.coordenadas

    def atualizar_configuracao(self, **kwargs: Any) -> None:
        """Atualiza a configuração do interpolador."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        if "resolucao_m" in kwargs:
            self.resolucao_m = kwargs["resolucao_m"]
        if "funcao" in kwargs:
            self.funcao = kwargs["funcao"]
        if "suavizacao" in kwargs:
            self.suavizacao = kwargs["suavizacao"]

    def exportar_raster(self, atributo: str) -> Optional[np.ndarray]:
        """Exporta o raster interpolado de um atributo específico."""
        if self.resultados is None or "atributos" not in self.resultados:
            return None
        if atributo not in self.resultados["atributos"]:
            return None
        return self.resultados["atributos"][atributo]["predicao"].copy()


# Alias para compatibilidade
InterpoladorSolo = Interpolador