"""
Precision VRT Solo — Módulo de Interpolação

Interpola atributos químicos e físicos do solo sobre uma grade regular
usando métodos espaciais avançados.
"""

# Tentar importar cada módulo individualmente para evitar erros
try:
    from .configuracao import (
        MetodoInterpolacao,
        RESOLUCAO_PADRAO_M,
        FUNCAO_RBF_PADRAO,
        SUAVIZACAO_PADRAO,
        RANDOM_STATE_PADRAO,
        COLUNAS_COORDENADAS,
        COLUNAS_EXCLUIR,
    )
except ImportError as e:
    print(f"⚠️ Erro ao importar configuracao: {e}")
    # Criar objetos vazios para evitar erro de import
    MetodoInterpolacao = None
    RESOLUCAO_PADRAO_M = 10
    FUNCAO_RBF_PADRAO = "thin_plate_spline"
    SUAVIZACAO_PADRAO = 0.0
    RANDOM_STATE_PADRAO = 42
    COLUNAS_COORDENADAS = set()
    COLUNAS_EXCLUIR = set()

try:
    from .contratos import EstatisticaInterpolacao, ConfigInterpolacao, ResultadoInterpolacao
except ImportError as e:
    print(f"⚠️ Erro ao importar contratos: {e}")
    # Criar classes vazias
    from dataclasses import dataclass
    @dataclass
    class EstatisticaInterpolacao:
        pass
    @dataclass
    class ConfigInterpolacao:
        pass
    @dataclass
    class ResultadoInterpolacao:
        pass

try:
    from .motor import Interpolador
    # Criar alias para compatibilidade
    InterpoladorSolo = Interpolador
except ImportError as e:
    print(f"⚠️ Erro ao importar motor: {e}")
    # Criar classe vazia
    class Interpolador:
        pass
    InterpoladorSolo = Interpolador

try:
    from .validacao import validar_dados_entrada, detectar_coluna_coordenada, selecionar_atributos_numericos
except ImportError as e:
    print(f"⚠️ Erro ao importar validacao: {e}")
    # Criar funções vazias
    def validar_dados_entrada(gdf):
        pass
    def detectar_coluna_coordenada(df, eixo):
        pass
    def selecionar_atributos_numericos(df, colunas_excluir):
        pass

__all__ = [
    "Interpolador",
    "InterpoladorSolo",
    "MetodoInterpolacao",
    "EstatisticaInterpolacao",
    "ConfigInterpolacao",
    "ResultadoInterpolacao",
    "RESOLUCAO_PADRAO_M",
    "FUNCAO_RBF_PADRAO",
    "SUAVIZACAO_PADRAO",
    "RANDOM_STATE_PADRAO",
    "COLUNAS_COORDENADAS",
    "COLUNAS_EXCLUIR",
    "validar_dados_entrada",
    "detectar_coluna_coordenada",
    "selecionar_atributos_numericos",
]