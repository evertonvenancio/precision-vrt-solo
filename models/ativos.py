
"""
Precision VRT Solo — Modelo de Ativos Patrimoniais

Implementa modelos de dados para gestão de ativos e patrimônio.
Baseado nas definições de governança existentes.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

class CategoriaAtivo(Enum):
    """Categorias de ativos patrimoniais."""
    EQUIPAMENTOS = "equipamentos"
    VEHICULOS = "veiculos"
    COMPUTACAO = "computacao"
    COMUNICACAO = "comunicacao"
    SENSORES = "sensores"
    SOFTWARE = "software"
    MOVEIS = "moveis"
    IMOVEIS = "imoveis"
    FERRAMENTAS = "ferramentas"
    OUTROS = "outros"

# Mapeamento de categorias existentes em governança
CATEGORIAS_ATIVO = [
    "equipamentos",
    "veiculos", 
    "computacao",
    "comunicacao",
    "sensores",
    "software",
    "moveis",
    "imoveis",
    "ferramentas",
    "outros"
]

class TipoAtivo(Enum):
    """Tipos de ativos."""
    MAQUINA = "maquina"
    VEICULO = "veiculo"
    EQUIPAMENTO = "equipamento"
    COMPUTADOR = "computador"
    NOTEBOOK = "notebook"
    TABLET = "tablet"
    CELULAR = "celular"
    DRONE = "drone"
    SENSOR = "sensor"
    LICENCA = "licenca"
    FERRAMENTA = "ferramenta"
    MOVEL = "movel"
    IMOBILIARIO = "imobiliario"

class AtivoPatrimonial:
    """
    Representa um ativo patrimonial.
    Baseado em ItemPatrimonial da governança.
    """
    
    def __init__(self,
                 id_ativo: str,
                 tipo: TipoAtivo,
                 categoria: CategoriaAtivo,
                 descricao: str,
                 valor: float,
                 data_aquisicao: datetime,
                 fornecedor: Optional[str] = None,
                 vida_util: Optional[int] = None,
                 depreciacao_anual: Optional[float] = None,
                 localizacao: Optional[str] = None,
                 responsavel: Optional[str] = None,
                 situacao: str = "ativo",
                 dados_adicionais: Optional[Dict[str, Any]] = None):
        self.id_ativo = id_ativo
        self.tipo = tipo
        self.categoria = categoria
        self.descricao = descricao
        self.valor = valor
        self.data_aquisicao = data_aquisicao
        self.fornecedor = fornecedor
        self.vida_util = vida_util
        self.depreciacao_anual = depreciacao_anual
        self.localizacao = localizacao
        self.responsavel = responsavel
        self.situacao = situacao
        self.dados_adicionais = dados_adicionais or {}
        self.historico: List[Dict[str, Any]] = []
        self.criado_em = datetime.now()
        self.atualizado_em = datetime.now()
        
    def adicionar_historico(self, evento: str, usuario_id: str, dados: Optional[Dict[str, Any]] = None):
        """
        Adiciona evento ao histórico do ativo.
        """
        historico_item = {
            'evento': evento,
            'timestamp': datetime.now(),
            'usuario_id': usuario_id,
            'dados': dados or {}
        }
        
        self.historico.append(historico_item)
        self.atualizado_em = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte para dicionário.
        """
        return {
            'id_ativo': self.id_ativo,
            'tipo': self.tipo.value,
            'categoria': self.categoria.value,
            'descricao': self.descricao,
            'valor': self.valor,
            'data_aquisicao': self.data_aquisicao.isoformat(),
            'fornecedor': self.fornecedor,
            'vida_util': self.vida_util,
            'depreciacao_anual': self.depreciacao_anual,
            'localizacao': self.localizacao,
            'responsavel': self.responsavel,
            'situacao': self.situacao,
            'dados_adicionais': self.dados_adicionais,
            'historico': self.historico,
            'criado_em': self.criado_em.isoformat(),
            'atualizado_em': self.atualizado_em.isoformat()
        }
