"""
Precision VRT Solo — Módulo de Validação Global

Responsável pela validação estrutural, unidades, metodologia e normalização.
Não contém lógica de negócio.
"""

from .leitura import *
from .estrutura import *
from .unidades import *
from .metodologia import *
from .normalizacao import *
from .validadores import *

__all__ = [
    # Leitura
    'LeitorPDF', 'LeitorCSV', 'LeitorXLS', 'LeitorXLSX', 'LeitorGeoJSON',
    'LeitorShapefile', 'LeitorGeoTIFF', 'LeitorISOML', 'LeitorKML', 'LeitorKMZ',
    
    # Estrutura
    'ValidadorEstrutural', 'ArquivoVazio', 'ArquivoCorrompido', 'CampoObrigatorio',
    'ColunaObrigatoria', 'DuplicidadeCampos', 'TiposIncompativeis', 'CoordenadasInvalidas',
    
    # Unidades
    'ValidadorUnidades', 'IdentificadorUnidades', 'NormalizadorUnidades', 'UnidadeCanonica',
    'cmolc_dm3', 'mmolc_dm3', 'mg_dm3', 'ppm', 'porcentagem', 'g_dm3', 'kg_ha', 't_ha',
    
    # Metodologia
    'ValidadorMetodologia', 'GerenciadorMetodologias', 'MetodologiaPadrao', 'MetodologiaExcepcional',
    
    # Normalização
    'NormalizadorDados', 'ConversorUnidades', 'ValidadorNormalizacao',
    
    # Validadores
    'ValidadorCampos', 'ValidadorArquivos', 'ValidadorCoordenadas', 'ValidadorMetadados'
]