"""
Precision VRT Solo — Módulo de Agronomia para Monitoramento

Implementa funcionalidades de agronomia específicas para monitoramento.
Baseado em código extraído de core_agronomia_monitoramento_legado.py.

Este módulo NÃO realiza recomendações, apenas estrutura para futuras
implementações de diagnóstico agronômico.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime, date
from dataclasses import dataclass, field
from enum import Enum
import logging

from core.tipos.base import ConfigBase
from ..contratos import (
    AreaMonitoramento,
    SerieTemporalVigor,
    AnomaliaMonitoramento,
    TipoIndice,
    TipoSensor
)

logger = logging.getLogger(__name__)


class TipoSolo(Enum):
    """Tipos de solo."""
    ARGILoso = "argilos"
    FRANco_ARGILoso = "franco_argilos"
    FRANco = "franco"
    FRANco_ARENOSo = "franco_arenos"
    ARENoso = "arenos"


class Cultura(Enum):
    """Culturas suportadas."""
    SOJA = "soja"
    MILHO = "milho"
    ALGODAO = "algodao"
    CAFE = "cafe"
    CANA_DE_ACUCAR = "cana_acucar"
    CITRINOS = "citricos"
    TRIGO = "trigo"


class FaseFenologica(Enum):
    """Fases fenológicas."""
    SEMEADURA = "semeadura"
    EMERGENCIA = "emergencia"
    DESENVOLVIMENTO_VEGETATIVO = "desenv_vegetativo"
    FLORACAO = "floracao"
    FRUTIFICACAO = "frutificacao"
    MATURACAO = "maturacao"
    COLHEITA = "colheita"
    Pós_COLHEITA = "pos_colheita"


@dataclass
class ConfigAgronomia:
    """Configuração para análise agronômica."""
    
    cultura: Cultura
    fase_fenologica: FaseFenologica
    tipo_solo: TipoSolo
    data_plantio: str
    data_estimada_colheita: str
    variedade: str = "padrao"
    densidade_plantio: float = 12.0  # plantas/m²
    potencial_produtivo: float = 60.0  # bag/ha para soja
    
    # Parâmetros de referência
    referencia_ndvi: float = 0.7
    referencia_ndwi: float = -0.1
    referencia_ndre: float = 0.6
    
    # Limites de alerta
    limite_vigor_baixo: float = 0.3
    limite_vigor_alto: float = 0.8
    limite_desvio_toleravel: float = 20.0


@dataclass
class IndicadorAgronomico:
    """Indicador agronômico calculado."""
    
    nome: str
    valor_atual: float
    valor_referencia: float
    desvio_percentual: float
    classificacao: str
    observacoes: List[str] = field(default_factory=list)
    contexto: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnaliseAgronomica:
    """Análise agronômica da área."""
    
    area_id: str
    cultura: Cultura
    fase_fenologica: FaseFenologica
    data_analise: str
    indicadores: List[IndicadorAgronomico] = field(default_factory=list)
    alertas: List[str] = field(default_factory=list)
    recomendacoes_preliminares: List[str] = field(default_factory=list)
    observacoes_gerais: str = ""
    
    def adicionar_alerta(self, alerta: str):
        """Adiciona alerta à análise."""
        if alerta not in self.alertas:
            self.alertas.append(alerta)
    
    def adicionar_recomendacao_preliminar(self, recomendacao: str):
        """Adiciona recomendação preliminar."""
        if recomendacao not in self.recomendacoes_preliminares:
            self.recomendacoes_preliminares.append(recomendacao)


class AnalisadorAgronomico:
    """
    Realiza análises agronômicas baseadas em dados de monitoramento.
    Este módulo NÃO emite diagnóstico, apenas identifica tendências.
    """
    
    def __init__(self, config: ConfigAgronomia):
        self.config = config
        self.parametros_cultura = self._carregar_parametros_cultura()
    
    def _carregar_parametros_cultura(self) -> Dict[Cultura, Dict]:
        """Carrega parâmetros de referência por cultura."""
        return {
            Cultura.SOJA: {
                'fases': {
                    FaseFenologica.SEMEADURA: {'ndvi_min': 0.1, 'ndvi_max': 0.3, 'dias': 10},
                    FaseFenologica.EMERGENCIA: {'ndvi_min': 0.2, 'ndvi_max': 0.4, 'dias': 15},
                    FaseFenologica.DESENVOLVIMENTO_VEGETATIVO: {'ndvi_min': 0.4, 'ndvi_max': 0.7, 'dias': 40},
                    FaseFenologica.FLORACAO: {'ndvi_min': 0.6, 'ndvi_max': 0.8, 'dias': 20},
                    FaseFenologica.FRUTIFICACAO: {'ndvi_min': 0.5, 'ndvi_max': 0.7, 'dias': 30},
                    FaseFenologica.MATURACAO: {'ndvi_min': 0.2, 'ndvi_max': 0.5, 'dias': 20},
                    FaseFenologica.COLHEITA: {'ndvi_min': 0.0, 'ndvi_max': 0.2, 'dias': 5}
                },
                'indices_referencia': {
                    'NDVI': {'otimo': 0.6, 'minimo': 0.3, 'maximo': 0.8},
                    'NDWI': {'optimo': -0.1, 'minimo': -0.3, 'maximo': 0.1},
                    'NDRE': {'optimo': 0.6, 'minimo': 0.3, 'maximo': 0.8}
                }
            },
            Cultura.MILHO: {
                'fases': {
                    FaseFenologica.SEMEADURA: {'ndvi_min': 0.1, 'ndvi_max': 0.3, 'dias': 7},
                    FaseFenologica.EMERGENCIA: {'ndvi_min': 0.2, 'ndvi_max': 0.4, 'dias': 10},
                    FaseFenologica.DESENVOLVIMENTO_VEGETATIVO: {'ndvi_min': 0.4, 'ndvi_max': 0.7, 'dias': 50},
                    FaseFenologica.FLORACAO: {'ndvi_min': 0.6, 'ndvi_max': 0.8, 'dias': 25},
                    FaseFenologica.FRUTIFICACAO: {'ndvi_min': 0.5, 'ndvi_max': 0.7, 'dias': 40},
                    FaseFenologica.MATURACAO: {'ndvi_min': 0.3, 'ndvi_max': 0.6, 'dias': 20},
                    FaseFenologica.COLHEITA: {'ndvi_min': 0.0, 'ndvi_max': 0.2, 'dias': 5}
                },
                'indices_referencia': {
                    'NDVI': {'otimo': 0.65, 'minimo': 0.35, 'maximo': 0.85},
                    'NDWI': {'optimo': -0.1, 'minimo': -0.3, 'maximo': 0.1},
                    'NDRE': {'optimo': 0.65, 'minimo': 0.35, 'maximo': 0.85}
                }
            }
        }
    
    def calcular_indicadores(self, area: AreaMonitoramento, 
                           series_temporais: Dict[int, SerieTemporalVigor],
                           anomalias: List[AnomaliaMonitoramento]) -> AnaliseAgronomica:
        """
        Calcula indicadores agronômicos baseados em dados de monitoramento.
        
        Args:
            area: Área de monitoramento
            series_temporais: Séries temporais disponíveis
            anomalias: Anomalias detectadas
            
        Returns:
            Análise agronômica
        """
        analise = AnaliseAgronomica(
            area_id=area.area_id,
            cultura=self.config.cultura,
            fase_fenologica=self.config.fase_fenologica,
            data_analise=datetime.now().isoformat()
        )
        
        # Calcular indicadores para cada zona
        for zona_id, serie in series_temporais.items():
            indicadores_zona = self._calcular_indicadores_zona(
                zona_id, serie, area
            )
            analise.indicadores.extend(indicadores_zona)
        
        # Identificar alertas baseados em anomalias
        self._identificar_alertas(analise, anomalias)
        
        # Gerar observações gerais
        self._gerar_observacoes_gerais(analise)
        
        return analise
    
    def _calcular_indicadores_zona(self, zona_id: int, 
                                  serie: SerieTemporalVigor,
                                  area: AreaMonitoramento) -> List[IndicadorAgronomico]:
        """
        Calcula indicadores para uma zona específica.
        
        Args:
            zona_id: ID da zona
            serie: Série temporal da zona
            area: Área de monitoramento
            
        Returns:
            Lista de indicadores calculados
        """
        indicadores = []
        
        # Obter parâmetros da cultura
        if self.config.cultura in self.parametros_cultura:
            params_cultura = self.parametros_cultura[self.config.cultura]
            
            # Verificar se a fase fenológica está nos parâmetros
            if self.config.fase_fenologica in params_cultura['fases']:
                fase_params = params_cultura['fases'][self.config.fase_fenologica]
                
                # Calcular indicadores para cada índice disponível
                for indice_str in serie.valores_medios:
                    if indice_str in params_cultura['indices_referencia']:
                        referencia = params_cultura['indices_referencia'][indice_str]
                        
                        # Obter valor atual (último valor da série)
                        valores = serie.valores_medios[indice_str]
                        if valores:
                            valor_atual = valores[-1]
                            
                            # Calcular desvio percentual em relação ao ótimo
                            desvio = ((valor_atual - referencia['optimo']) / referencia['optimo']) * 100
                            
                            # Classificar o estado
                            if valor_atual < referencia['minimo']:
                                classificacao = "abaixo_do_minimo"
                            elif valor_atual > referencia['maximo']:
                                classificacao = "acima_do_maximo"
                            elif abs(desvio) < 10:
                                classificacao = "ótimo"
                            elif abs(desvio) < 20:
                                classificacao = "bom"
                            else:
                                classificacao = "fora_da_faixa"
                            
                            indicador = IndicadorAgronomico(
                                nome=f"Indicador {indice_str} - Zona {zona_id}",
                                valor_atual=valor_atual,
                                valor_referencia=referencia['optimo'],
                                desvio_percentual=desvio,
                                classificacao=classificacao,
                                contexto={
                                    'zona_id': zona_id,
                                    'fase_fenologica': self.config.fase_fenologica.value,
                                    'cultura': self.config.cultura.value,
                                    'valores_historicos': valores[-5:] if len(valores) > 5 else valores,
                                    'parametros_referencia': referencia
                                }
                            )
                            indicadores.append(indicador)
        
        return indicadores
    
    def _identificar_alertas(self, analise: AnaliseAgronomica, 
                            anomalias: List[AnomaliaMonitoramento]):
        """
        Identifica alertas baseados em anomalias detectadas.
        
        Args:
            analise: Análise a ser atualizada
            anomalias: Anomalias detectadas
        """
        for anomalia in anomalias:
            # Alerta por redução acentuada de vigor
            if (anomalia.tipo == 'negativa' and 
                anomalia.severidade in ['moderada', 'grave'] and
                anomalia.indice in ['NDVI', 'NDRE']):
                
                alerta = (f"Redução significativa de {anomalia.indice} "
                         f"({abs(anomalia.desvio_percentual):.1f}%) "
                         f"em zona {anomalia.zona_id}")
                analise.adicionar_alerta(alerta)
                
                # Adicionar recomendação preliminar
                recomendacao = f"Investigar causa da redução de vigor na zona {anomalia.zona_id}"
                analise.adicionar_recomendacao_preliminar(recomendacao)
            
            # Alerta por aumento anormal de vigor
            elif (anomalia.tipo == 'positiva' and 
                  anomalia.severidade == 'grave' and
                  anomalia.indice in ['NDVI', 'NDRE']):
                
                alerta = (f"Aumento anormal de {anomalia.indice} "
                         f"({anomalia.desvio_percentual:.1f}%) "
                         f"em zona {anomalia.zona_id}")
                analise.adicionar_alerta(alerta)
                
                recomendacao = f"Verificar se o aumento de vigor é esperado para a fase fenológica"
                analise.adicionar_recomendacao_preliminar(recomendacao)
            
            # Alerta por estresse hídrico
            elif anomalia.indice == 'NDWI' and anomalia.tipo == 'negativa':
                
                alerta = (f"Estresse hídrico detectado (NDWI: {anomalia.valor_observado:.3f}) "
                         f"em zona {anomalia.zona_id}")
                analise.adicionar_alerta(alerta)
                
                recomendacao = f"Avaliar necessidade de irrigação na zona {anomalia.zona_id}"
                analise.adicionar_recomendacao_preliminar(recomendacao)
    
    def _gerar_observacoes_gerais(self, analise: AnaliseAgronomica):
        """
        Gera observações gerais sobre a análise.
        
        Args:
            analise: Análise a ser atualizada
        """
        # Contagem de alertas
        n_alertas = len(analise.alertas)
        n_indicadores = len(analise.indicadores)
        
        if n_alertas == 0:
            analise.observacoes_gerais = (f"Análise normal com {n_indicadores} indicadores "
                                        f"sem alertas críticos. Monitoramento estável.")
        elif n_alertas < 3:
            analise.observacoes_gerais = (f"Análise com {n_alertas} alertas baixos/moderados "
                                        f"e {n_indicadores} indicadores. Requer atenção.")
        else:
            analise.observacoes_gerais = (f"Análise com {n_alertas} alertas. "
                                        f"Recomenda avaliação técnica detalhada.")


class HistoricoAgronomico:
    """
    Gerencia histórico de análises agronômicas.
    """
    
    def __init__(self):
        self.analises_realizadas: List[AnaliseAgronomica] = []
        self.parametros_referencia: Dict[str, Dict] = {}
    
    def adicionar_analise(self, analise: AnaliseAgronomica):
        """
        Adiciona nova análise ao histórico.
        
        Args:
            analise: Análise agronômica realizada
        """
        self.analises_realizadas.append(analise)
        
        # Atualizar parâmetros de referência
        if analise.area_id not in self.parametros_referencia:
            self.parametros_referencia[analise.area_id] = {}
        
        for indicador in analise.indicadores:
            chave = f"{indicador.nome}"
            if chave not in self.parametros_referencia[analise.area_id]:
                self.parametros_referencia[analise.area_id][chave] = []
            
            self.parametros_referencia[analise.area_id][chave].append({
                'data': analise.data_analise,
                'valor': indicador.valor_atual,
                'classificacao': indicador.classificacao
            })
    
    def obter_evolucao_temporal(self, area_id: str, indicador_nome: str) -> Dict[str, Any]:
        """
        Obtém evolução temporal de um indicador.
        
        Args:
            area_id: ID da área
            indicador_nome: Nome do indicador
            
        Returns:
            Dados da evolução temporal
        """
        if area_id not in self.parametros_referencia:
            return {'dados': [], 'tendencia': 'nao_disponivel'}
        
        chave = indicador_nome
        if chave not in self.parametros_referencia[area_id]:
            return {'dados': [], 'tendencia': 'nao_disponivel'}
        
        dados = self.parametros_referencia[area_id][chave]
        
        # Calcular tendência
        if len(dados) >= 3:
            valores = [d['valor'] for d in dados]
            tendencia = self._calcular_tendencia(valores)
        else:
            tendencia = 'dados_insuficientes'
        
        return {
            'dados': dados,
            'tendencia': tendencia,
            'n_medicoes': len(dados)
        }
    
    def _calcular_tendencia(self, valores: List[float]) -> str:
        """
        Calcula tendência baseada nos valores.
        
        Args:
            valores: Lista de valores
            
        Returns:
            Tendência detectada
        """
        if len(valores) < 3:
            return 'dados_insuficientes'
        
        # Calcular inclinação (simples regressão linear)
        x = np.arange(len(valores))
        y = np.array(valores)
        inclinacao = np.polyfit(x, y, 1)[0]
        
        if abs(inclinacao) < 0.01:
            return 'estavel'
        elif inclinacao > 0:
            return 'crescente'
        else:
            return 'decrescente'
    
    def gerar_resumo_historico(self, area_id: str) -> Dict[str, Any]:
        """
        Gera resumo do histórico de análises.
        
        Args:
            area_id: ID da área
            
        Returns:
            Resumo do histórico
        """
        analises_area = [a for a in self.analises_realizadas if a.area_id == area_id]
        
        if not analises_area:
            return {'mensagem': 'Nenhuma análise realizada para esta área'}
        
        # Contagens
        n_total = len(analises_area)
        n_com_alertas = len([a for a in analises_area if a.alertas])
        n_com_recomendacoes = len([a for a in analises_area if a.recomendacoes_preliminares])
        
        # Alertas mais comuns
        todos_alertas = []
        for analise in analises_area:
            todos_alertas.extend(analise.alertas)
        
        alertas_frequentes = {}
        for alerta in todos_alertas:
            alertas_frequentes[alerta] = alertas_frequentes.get(alerta, 0) + 1
        
        return {
            'area_id': area_id,
            'total_analises': n_total,
            'analises_com_alertas': n_com_alertas,
            'analises_com_recomendacoes': n_com_recomendacoes,
            'alertas_mais_comuns': sorted(alertas_frequentes.items(), key=lambda x: x[1], reverse=True)[:5],
            'periodo_analise': {
                'inicio': min(a.data_analise for a in analises_area),
                'fim': max(a.data_analise for a in analises_area)
            }
        }


class MonitoramentoAgronomico:
    """
    Sistema integrado de monitoramento agronômico.
    """
    
    def __init__(self):
        self.analisador = None
        self.historico = HistoricoAgronomico()
    
    def configurar_analise(self, config: ConfigAgronomia):
        """
        Configura análise agronômica.
        
        Args:
            config: Configuração da análise
        """
        self.analisador = AnalisadorAgronomico(config)
    
    def realizar_analise_integrada(self, area: AreaMonitoramento,
                                 series_temporais: Dict[int, SerieTemporalVigor],
                                 anomalias: List[AnomaliaMonitoramento]) -> AnaliseAgronomica:
        """
        Realiza análise integrada da área.
        
        Args:
            area: Área de monitoramento
            series_temporais: Séries temporais disponíveis
            anomalias: Anomalias detectadas
            
        Returns:
            Análise agronômica completa
        """
        if not self.analisador:
            raise ValueError("Analisador não configurado. Use configurar_analise() primeiro.")
        
        # Realizar análise
        analise = self.analisador.calcular_indicadores(area, series_temporais, anomalias)
        
        # Adicionar ao histórico
        self.historico.adicionar_analise(analise)
        
        return analise
    
    def obter_historico_completo(self, area_id: str) -> List[AnaliseAgronomica]:
        """
        Obtém histórico completo de análises para uma área.
        
        Args:
            area_id: ID da área
            
        Returns:
            Lista de análises realizadas
        """
        return [a for a in self.historico.analises_realizadas if a.area_id == area_id]
    
    def gerar_relatorio_diagnostico_preliminar(self, area_id: str) -> Dict[str, Any]:
        """
        Gera relatório preliminar de diagnóstico (sem conclusões definitivas).
        
        Args:
            area_id: ID da área
            
        Returns:
            Relatório preliminar
        """
        analises = self.obter_historico_completo(area_id)
        
        if not analises:
            return {'status': 'sem_dados', 'mensagem': 'Nenhuma análise realizada'}
        
        # Obter resumo do histórico
        resumo_historico = self.historico.gerar_resumo_historico(area_id)
        
        # Analisar tendências recentes
        tendencias = {}
        for analise in analises[-3:]:  # Últimas 3 análises
            for indicador in analise.indicadores:
                chave = f"{indicador.nome}"
                evolucao = self.historico.obter_evolucao_temporal(area_id, chave)
                if evolucao['tendencia'] != 'nao_disponivel':
                    if chave not in tendencias:
                        tendencias[chave] = []
                    tendencias[chave].append(evolucao['tendencia'])
        
        # Consolidar tendências
        tendencias_consolidadas = {}
        for chave, tendencias_lista in tendencias.items():
            if len(tendencias_lista) >= 2:
                # Tendência mais frequente nos últimos 3 períodos
                tendencia_mais_frequente = max(set(tendencias_lista), key=tendencias_lista.count)
                tendencias_consolidadas[chave] = {
                    'tendencia_atual': tendencias_lista[-1],
                    'tendencia_historica': tendencia_mais_frequente,
                    'consistencia': len([t for t in tendencias_lista if t == tendencias_lista[-1]]) / len(tendencias_lista)
                }
        
        return {
            'status': 'analisado',
            'area_id': area_id,
            'resumo_historico': resumo_historico,
            'tendencias_consolidadas': tendencias_consolidadas,
            'alertas_recentes': analises[-1].alertas if analises else [],
            'observacoes': analises[-1].observacoes_gerais if analises else '',
            'data_analise': analises[-1].data_analise if analises else None
        }