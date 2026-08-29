"""
Precision VRT Solo — Relatórios de Exportação

Exporta todas as funções e classes de geração de relatórios.
"""

from .laudo import gerar_relatorio_texto, exportar_txt
from .cabine import gerar_cartao_cabine

__all__ = [
    "gerar_relatorio_texto",
    "exportar_txt",
    "gerar_cartao_cabine",
]