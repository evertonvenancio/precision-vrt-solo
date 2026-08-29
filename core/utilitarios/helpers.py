"""
Proxy de compatibilidade — funções movidas para módulos especializados.
MANTIDO para não quebrar imports existentes em services/ (será removido na Fase 6).
"""
from .geo import _parse_upload, _calcular_area_ha, _gdf_para_geojson
from .arquivos import _salvar_upload
from .normalizacao import _padronizar_id

__all__ = [
    "_parse_upload",
    "_salvar_upload",
    "_padronizar_id",
    "_calcular_area_ha",
    "_gdf_para_geojson",
]