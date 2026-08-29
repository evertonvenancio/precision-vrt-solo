
"""
Precision VRT Solo — Modelo de Extrator de Solucao

Implementa modelos de dados para gestão de pontos de monitoramento,
leituras, diagnostico nutricional e curvas nutritivas.
"""

from typing import Annotated, Optional
from datetime import datetime
from enum import Enum

class TipoPonto(Enum):
    """Tipos de pontos de monitoramento."""
    solo = "solo"
    foliar = "foliar"
    agua = "agua"
    ar = "ar"
    fertilizante = "fertilizante"
    equipamento = "equipamento"

class StatusLeitura(Enum):
    """Status das leituras."""
    ativo = "ativo"
    inativo = "inativo"
    pendente = "pendente"
    validado = "validado"
    invalido = "invalido"

class TipoParametro(Enum):
    """Tipos de parâmetros monitorados."""
    ph = "ph"
    nitrogenio = "nitrogenio"
    fosforo = "fosforo"
    potassio = "potassio"
    calcio = "calcio"
    magnesio = "magnesio"
    enxofre = "enxofre"
    ferro = "ferro"
    zinco = "zinco"
    manganes = "manganes"
    cobre = "cobre"
    boro = "boro"
    molibdenio = "molibdenio"
    sodio = "sodio"
    cloro = "cloro"
    umidade = "umidade"
    temperatura = "temperatura"
    condutividade = "condutividade"
    oxigenio = "oxigenio"
    turbidez = "turbidez"

class PontoExtrator:
    """
    Representa um ponto de monitoramento.
    """
    
    def __init__(self,
                 id: str,
                 nome: str,
                 descricao: str,
                 tipo: TipoPonto,
                 latitude: float,
                 longitude: float,
                 altitude: Optional[float] = None,
                 dados_adicionais: Optional[dict] = None):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.tipo = tipo
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.dados_adicionais = dados_adicionais or {}
        self.criado_em = datetime.now()
        self.atualizado_em = datetime.now()
        
    def to_dict(self) -> dict:
        """
        Converte para dicionário.
        """
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'tipo': self.tipo.value,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'dados_adicionais': self.dados_adicionais,
            'criado_em': self.criado_em.isoformat(),
            'atualizado_em': self.atualizado_em.isoformat()
        }

class LeituraExtrator:
    """
    Representa uma leitura do ponto de monitoramento.
    """
    
    def __init__(self,
                 id: str,
                 ponto_id: str,
                 parametro: TipoParametro,
                 valor: float,
               unidade: str,
               status: StatusLeitura = StatusLeitura.ativo,
               timestamp: Optional[datetime] = None,
               dados_adicionais: Optional[dict] = None):
        self.id = id
        self.ponto_id = ponto_id
        self.parametro = parametro
        self.valor = valor
        self.unidade = unidade
        self.status = status
        self.timestamp = timestamp or datetime.now()
        self.dados_adicionais = dados_adicionais or {}
        self.criado_em = datetime.now()
        
    def to_dict(self) -> dict:
        """
        Converte para dicionário.
        """
        return {
            'id': self.id,
            'ponto_id': self.ponto_id,
            'parametro': self.parametro.value,
            'valor': self.valor,
            'unidade': self.unidade,
            'status': self.status.value,
            'timestamp': self.timestamp.isoformat(),
            'dados_adicionais': self.dados_adicionais,
            'criado_em': self.criado_em.isoformat()
        }

class CurvaNutritiva:
    """
    Representa uma curva nutritiva para diagnóstico.
    """
    
    def __init__(self,
                 id: str,
                 cultura: str,
                 fase_cultivo: str,
                 nutrientes: dict,
                 faixa_ideal: dict,
                 faixa_critica: dict,
                 dados_adicionais: Optional[dict] = None):
        self.id = id
        self.cultura = cultura
        self.fase_cultivo = fase_cultivo
        self.nutrientes = nutrientes
        self.faixa_ideal = faixa_ideal
        self.faixa_critica = faixa_critica
        self.dados_adicionais = dados_adicionais or {}
        self.criado_em = datetime.now()
        self.atualizado_em = datetime.now()
        
    def to_dict(self) -> dict:
        """
        Converte para dicionário.
        """
        return {
            'id': self.id,
            'cultura': self.cultura,
            'fase_cultivo': self.fase_cultivo,
            'nutrientes': self.nutrientes,
            'faixa_ideal': self.faixa_ideal,
            'faixa_critica': self.faixa_critica,
            'dados_adicionais': self.dados_adicionais,
            'criado_em': self.criado_em.isoformat(),
            'atualizado_em': self.atualizado_em.isoformat()
        }
