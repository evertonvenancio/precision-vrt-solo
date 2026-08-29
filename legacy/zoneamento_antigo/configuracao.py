"""
Precision VRT Solo — Configurações do Módulo de Zoneamento

Constantes e defaults do módulo.
"""

from .contratos import AlgoritmoEnum, ConfigZoneamento

# Limites de configuração
MIN_ZONAS = 2
MAX_ZONAS = 20

# Configuração padrão sensata
DEFAULT_CONFIG = ConfigZoneamento(
    n_zonas=4,
    algoritmo=AlgoritmoEnum.KMEANS,
    random_state=42,
    colunas_features=None,
    normalizar=True,
    remover_outliers=False,
    pesos_features=None,
    diferenca_minima_dose=None
)

# Registro de algoritmos disponíveis
ALGORITMO_REGISTRY = {
    AlgoritmoEnum.KMEANS: "core.zoneamento.algoritmos.KMeansAlgoritmo",
    AlgoritmoEnum.FUZZY: "core.zoneamento.algoritmos.FuzzyCMeansAlgoritmo",
    AlgoritmoEnum.GAUSSIAN: "core.zoneamento.algoritmos.GaussianMixtureAlgoritmo",
    AlgoritmoEnum.DBSCAN: "core.zoneamento.algoritmos.DBSCANAlgoritmo",
    AlgoritmoEnum.AGLOMERATIVO: "core.zoneamento.algoritmos.AglomerativoAlgoritmo",
    AlgoritmoEnum.SPECTRAL: "core.zoneamento.algoritmos.SpectralClusteringAlgoritmo",
}