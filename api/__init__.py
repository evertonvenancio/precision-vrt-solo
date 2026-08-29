"""
Precision VRT Solo — Camada de API

Camada de API responsável apenas por gerenciar endpoints HTTP.
Toda lógica de negócio está em Services, Core fica isolado.
"""

from .app import app
from .dependencies import *

__all__ = ['app']