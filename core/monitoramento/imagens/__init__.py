"""
Precision VRT Solo — Submódulo de Imagens

Implementa funcionalidades específicas para gerenciamento de imagens
de diferentes sensores (satélite, drone, RGB, multiespectral, etc.).
"""

from .motor import GerenciadorImagens, ProcessadorImagens, ValidadorImagens, InfoImagem

__all__ = [
    'GerenciadorImagens',
    'ProcessadorImagens', 
    'ValidadorImagens',
    'InfoImagem'
]