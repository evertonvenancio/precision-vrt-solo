"""
Precision VRT Solo — Camada Models

Camada responsável pelo armazenamento e representação dos dados persistidos.
Models representam apenas entidades persistidas, sem lógica de negócio.
"""

from .base import BaseModel
from .cliente import Cliente
from .empresa import Empresa
from .propriedade import Propriedade
from .talhao import Talhao
from .projeto import Projeto
from .amostra_solo import AmostraSolo
from .analise_solo import AnaliseSolo
from .compactacao import Compactacao
from .nematoides import Nematoides
from .fertirrigacao import Fertirrigacao
from .sensoriamento import Sensoriamento
from .monitoramento import Monitoramento
from .prescricao_vrt import PrescricaoVrt
from .exportacao import Exportacao
from .arquivos import Arquivos
from .equipamentos import Equipamentos
from .culturas import Culturas
from .metodologia import Metodologias
from .fertilizantes import Fertilizantes
from .usuario import Usuario
from .permissoes import Permissoes
from .configuracoes import Configuracoes

__all__ = [
    'BaseModel',
    'Cliente',
    'Empresa',
    'Propriedade',
    'Talhao',
    'Projeto',
    'AmostraSolo',
    'AnaliseSolo',
    'Compactacao',
    'Nematoides',
    'Fertirrigacao',
    'Sensoriamento',
    'Monitoramento',
    'PrescricaoVrt',
    'Exportacao',
    'Arquivos',
    'Equipamentos',
    'Culturas',
    'Metodologias',
    'Fertilizantes',
    'Usuario',
    'Permissoes',
    'Configuracoes'
]