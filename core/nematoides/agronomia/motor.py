"""
Precision VRT Solo — Módulo de Agronomia de Nematoides

Implementa regras e cálculos agronômicos específicos para análise de nematoides.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta

from ...tipos.base import ConfigBase, ResultadoBase
from ...tipos.geoespacial import Bounds, Coordenada
from ..nematoides.contratos import (
    NivelRiscoNematoides,
    EspecieNematoides,
    PontoAmostraNematoides,
    ZonaRiscoNematoides,
    ResultadoNematoides
)


class Cultura(str, Enum):
    """Culturas suportadas no sistema."""
    SOJA = "soja"
    MILHO = "milho"
    CAFE = "cafe"
    CANA = "cana"
    CITROS = "citros"
    FEIJAO = "feijao"
    ALGODAO = "algodao"
    TRIGO = "trigo"
    ARROZ = "arroz"
    SORGO = "sorgo"
    TOMATE = "tomate"
    BATATA = "batata"


class TipoSolo(str, Enum):
    """Tipos de solo para recomendações específicas."""
    ARGILOSO = "argiloso"
    ARENOSO = "arenoso"
    MISTO = "misto"
    ORGANICO = "organico"
    NEOSSOLO = "neossolo"


class MetodoControle(str, Enum):
    """Métodos de controle de nematoides."""
    QUIMICO = "quimico"
    BIOLOGICO = "biologico"
    CULTURAL = "cultural"
    INTEGRADO = "integrado"


@dataclass
class ConfigAgronomiaNematoides(ConfigBase):
    """Configuração para recomendações agronômicas de nematoides."""
    cultura: Cultura = Cultura.MILHO
    tipo_solo: TipoSolo = TipoSolo.MISTO
    historia_nematoides: List[str] = field(default_factory=list)
    tolerancia_adesao: float = 0.8  # tolerância a adesão de tratamentos
    custo_maximo_hectare: float = 500.0
    preferencia_metodo_controle: MetodoControle = MetodoControle.INTEGRADO


@dataclass
class RecomendacaoAgronomica:
    """Recomendação agronômica específica."""
    # Campos obrigatórios primeiro
    tipo: str  # "tratamento", "prevencao", "monitoramento"
    descricao: str
    cultura_alvo: Cultura
    urgencia: str  # "imediata", "semanal", "mensal", "anual"
    
    # Campos opcionais
    especie_alvo: Optional[EspecieNematoides] = None
    custo_estimado_hectare: float = 0.0
    eficacia_esperada: float = 0.0  # 0-1
    produtos_recomendados: List[str] = field(default_factory=list)
    metodos_implementacao: List[str] = field(default_factory=list)
    monitoramento_recomendado: str = ""


@dataclass
class PlanoControle:
    """Plano de controle integrado para nematoides."""
    cultura: Cultura
    tipo_solo: TipoSolo
    risco_global: NivelRiscoNematoides
    custo_total_estimado: float
    tratamentos_recomendados: List[RecomendacaoAgronomica]
    monitoramentos_programados: List[Dict[str, Any]]
    prazos_execucao: Dict[str, datetime]
    impacto_esperado: Dict[str, float]


class MotorAgronomiaNematoides:
    """
    Motor de agronomia específico para nematoides.
    
    Implementa recomendações baseadas em metodologias científicas
    de manejo integrado de nematoides em agricultura de precisão.
    """
    
    # Limites ajustados por cultura
    LIMITES_POPULACAO = {
        Cultura.SOJA: {"baixo": 80.0, "moderado": 400.0, "alto": 800.0},
        Cultura.MILHO: {"baixo": 100.0, "moderado": 500.0, "alto": 1000.0},
        Cultura.CAFE: {"baixo": 60.0, "moderado": 300.0, "alto": 600.0},
        Cultura.CANA: {"baixo": 120.0, "moderado": 600.0, "alto": 1200.0},
        Cultura.CITROS: {"baixo": 50.0, "moderado": 250.0, "alto": 500.0},
        Cultura.FEIJAO: {"baixo": 70.0, "moderado": 350.0, "alto": 700.0},
        Cultura.ALGODAO: {"baixo": 70.0, "moderado": 350.0, "alto": 700.0},
        Cultura.TRIGO: {"baixo": 110.0, "moderado": 550.0, "alto": 1100.0},
        Cultura.ARROZ: {"baixo": 100.0, "moderado": 500.0, "alto": 1000.0},
        Cultura.SORGO: {"baixo": 100.0, "moderado": 500.0, "alto": 1000.0},
        Cultura.TOMATE: {"baixo": 40.0, "moderado": 200.0, "alto": 400.0},
        Cultura.BATATA: {"baixo": 60.0, "moderado": 300.0, "alto": 600.0}
    }
    
    # Protocolos de controle por espécie
    PROTOCOLOS_CONTROLE = {
        EspecieNematoides.MELOIDOGYNE: {
            "quimico": ["Fenamiphos", "Carbofuran", "Oxamyl"],
            "biologico": ["Paecilomyces lilacinus", "Arthrobotrys spp."],
            "cultural": ["Rotação com gramíneas", "Resistência varietal"],
            "integrado": ["Fenamiphos + adubação verde"]
        },
        EspecieNematoides.PRATYLENCHUS: {
            "quimico": ["Oxamyl", "Carbosulfan"],
            "biologico": ["Purpureocillium lilacinum"],
            "cultural": ["Rotação com Brassicaceae", "Solarização"],
            "integrado": ["Oxamyl + cobertura morta"]
        },
        EspecieNematoides.HETERODERA: {
            "quimico": ["Dazomet", "Methyl bromide"],
            "biologico": ["Verticillium chlamydosporium"],
            "cultural": ["Rotação com não-hospedeiros", "Resistência varietal"],
            "integrado": ["Dazomet + solarização"]
        },
        EspecieNematoides.GALLUS: {
            "quimico": ["Abamectin", "Spirotetramat"],
            "biologico": ["Beauveria bassiana"],
            "cultural": ["Higiene de equipamentos", "Quarentena"],
            "integrado": ["Abamectin + higiene"]
        }
    }
    
    # Produtos registrados (exemplos)
    PRODUTOS_REGISTRADOS = {
        "Fenamiphos": {"dose_ml_ha": 2000, "intervalo_seguranca": 30, "culturas": ["soja", "milho", "cafe"]},
        "Carbofuran": {"dose_ml_ha": 1500, "intervalo_seguranca": 45, "culturas": ["milho", "trigo"]},
        "Oxamyl": {"dose_ml_ha": 1000, "intervalo_seguranca": 21, "culturas": ["tomate", "batata"]},
        "Paecilomyces lilacinus": {"dose_kg_ha": 5, "intervalo_seguranca": 0, "culturas": ["todas"]},
        "Adubação verde": {"dose_kg_ha": 20000, "intervalo_seguranca": 0, "culturas": ["todas"]}
    }
    
    def __init__(self, config: ConfigAgronomiaNematoides):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def gerar_plano_controle(self, resultado_analise: ResultadoNematoides) -> PlanoControle:
        """
        Gera plano de controle integrado baseado na análise de nematoides.
        
        Args:
            resultado_analise: Resultado completo da análise
            
        Returns:
            Plano de controle detalhado
        """
        # Cal custo total estimado
        custo_total = self._calcular_custo_total(resultado_analise)
        
        # Gerar tratamentos recomendados
        tratamentos = self._gerar_tratamentos(resultado_analise)
        
        # Programar monitoramentos
        monitoramentos = self._programar_monitoramentos(resultado_analise)
        
        # Definir prazos de execução
        prazos = self._definir_prazos_execucao(resultado_analise, tratamentos)
        
        # Calcular impacto esperado
        impacto = self._calcular_impacto_esperado(resultado_analise, tratamentos)
        
        return PlanoControle(
            cultura=self.config.cultura,
            tipo_solo=self.config.tipo_solo,
            risco_global=resultado_analise.risco_global,
            custo_total_estimado=custo_total,
            tratamentos_recomendados=tratamentos,
            monitoramentos_programados=monitoramentos,
            prazos_execucao=prazos,
            impacto_esperado=impacto
        )
    
    def _calcular_custo_total(self, resultado_analise: ResultadoNematoides) -> float:
        """Calcula custo total estimado do plano de controle."""
        custo_total = 0.0
        
        # Custo por zona
        for zona in resultado_analise.resultado_zoneamento.zonas_risco:
            if zona.risco_classificacao in [NivelRiscoNematoides.CRITICO, NivelRiscoNematoides.ALTO]:
                custo_total += zona.area_hectares * 300.0  # tratamento intenso
            elif zona.risco_classificacao == NivelRiscoNematoides.MODERADO:
                custo_total += zona.area_hectares * 150.0  # tratamento moderado
            else:
                custo_total += zona.area_hectares * 50.0   # tratamento leve
        
        # Adicionar custo de monitoramento
        custo_total += resultado_analise.area_total_analisada * 20.0  # R$20/ha para monitoramento
        
        return min(custo_total, self.config.custo_maximo_hectare * resultado_analise.area_total_analisada)
    
    def _gerar_tratamentos(self, resultado_analise: ResultadoNematoides) -> List[RecomendacaoAgronomica]:
        """Gera tratamentos recomendados por zona."""
        tratamentos = []
        
        for zona in resultado_analise.resultado_zoneamento.zonas_risco:
            # Determinar tipo de tratamento baseado no risco
            if zona.risco_classificacao == NivelRiscoNematoides.CRITICO:
                tratamentos.extend(self._gerar_tratamentos_criticos(zona))
            elif zona.risco_classificacao == NivelRiscoNematoides.ALTO:
                tratamentos.extend(self._gerar_tratamentos_altos(zona))
            elif zona.risco_classificacao == NivelRiscoNematoides.MODERADO:
                tratamentos.extend(self._gerar_tratamentos_moderados(zona))
            else:
                tratamentos.extend(self._gerar_tratamentos_baixos(zona))
        
        return tratamentos
    
    def _gerar_tratamentos_criticos(self, zona: ZonaRiscoNematoides) -> List[RecomendacaoAgronomica]:
        """Gera tratamentos para risco crítico."""
        tratamentos = []
        
        # Tratamento químico imediato
        quimico = RecomendacaoAgronomica(
            tipo="tratamento",
            descricao=f"Tratamento químico obrigatório para zona {zona.zona_id} - risco crítico",
            cultura_alvo=self.config.cultura,
            custo_estimado_hectare=350.0,
            eficacia_esperada=0.85,
            urgencia="imediata",
            produtos_recomendados=["Fenamiphos", "Carbofuran"],
            metodos_implementacao=["Aplicação via sulcamento", "Incorporação ao solo"],
            monitoramento_recomendado="Monitorar população em 15 dias"
        )
        tratamentos.append(quimico)
        
        # Controle biológico complementar
        biologico = RecomendacaoAgronomica(
            tipo="tratamento",
            descricao=f"Controle biológico complementar para zona {zona.zona_id}",
            cultura_alvo=self.config.cultura,
            custo_estimado_hectare=80.0,
            eficacia_esperada=0.60,
            urgencia="semanal",
            produtos_recomendados=["Paecilomyces lilacinus"],
            metodos_implementacao="Aplicação via pulverização",
            monitoramento_recomendado="Avaliar sobrevivência do agente biológico"
        )
        tratamentos.append(biologico)
        
        # Rotação de culturas
        cultural = RecomendacaoAgronomica(
            tipo="prevencao",
            descricao=f"Rotação de culturas para zona {zona.zona_id}",
            cultura_alvo=self.config.cultura,
            custo_estimado_hectare=100.0,
            eficacia_esperada=0.90,
            urgencia="mensal",
            produtos_recomendados=["Milho não-hospedeiro", "Sorgo"],
            metodos_implementacao="Planejamento de rotação",
            monitoramento_recomendado="Monitorar população após cultivo de rotação"
        )
        tratamentos.append(cultural)
        
        return tratamentos
    
    def _gerar_tratamentos_altos(self, zona: ZonaRiscoNematoides) -> List[RecomendacaoAgronomica]:
        """Gera tratamentos para risco alto."""
        tratamentos = []
        
        # Tratamento químico
        quimico = RecomendacaoAgronomica(
            tipo="tratamento",
            descricao=f"Tratamento químico recomendado para zona {zona.zona_id} - risco alto",
            cultura_alvo=self.config.cultura,
            custo_estimado_hectare=250.0,
            eficacia_esperada=0.80,
            urgencia="semanal",
            produtos_recomendados=["Oxamyl", "Abamectin"],
            metodos_implementacao=["Aplicação via irrigação", "Pulverização foliar"],
            monitoramento_recomendado="Monitorar população em 30 dias"
        )
        tratamentos.append(quimico)
        
        # Adubação verde
        verde = RecomendacaoAgronomica(
            tipo="prevencao",
            descricao=f"Adubação verde para zona {zona.zona_id}",
            cultura_alvo=self.config.cultura,
            custo_estimado_hectare=120.0,
            eficacia_esperada=0.70,
            urgencia="mensal",
            produtos_recomendados=["Crotalaria", "Mucuna"],
            metodos_implementacao="Semeadura e incorporação",
            monitoramento_recomendado="Avaliar matéria seca produzida"
        )
        tratamentos.append(verde)
        
        return tratamentos
    
    def _gerar_tratamentos_moderados(self, zona: ZonaRiscoNematoides) -> List[RecomendacaoAgronomica]:
        """Gera tratamentos para risco moderado."""
        tratamentos = []
        
        # Controle biológico
        biologico = RecomendacaoAgronomica(
            tipo="tratamento",
            descricao=f"Controle biológico para zona {zona.zona_id} - risco moderado",
            cultura_alvo=self.config.cultura,
            custo_estimado_hectare=60.0,
            eficacia_esperada=0.65,
            urgencia="mensal",
            produtos_recomendados=["Trichoderma harzianum", "Purpureocillium lilacinum"],
            metodos_implementacao="Aplicação via solo",
            monitoramento_recomendado="Monitorar população em 60 dias"
        )
        tratamentos.append(biologico)
        
        # Práticas culturais
        cultural = RecomendacaoAgronomica(
            tipo="prevencao",
            descricao=f"Práticas culturais para zona {zona.zona_id}",
            cultura_alvo=self.config.cultura,
            custo_estimado_hectare=40.0,
            eficacia_esperada=0.50,
            urgencia="anual",
            produtos_recomendados=["Resíduos culturais", "Material de cobertura"],
            metodos_implementacao="Manejo de resíduos, higiene",
            monitoramento_recomendado="Amostragem anual"
        )
        tratamentos.append(cultural)
        
        return tratamentos
    
    def _gerar_tratamentos_baixos(self, zona: ZonaRiscoNematoides) -> List[RecomendacaoAgronomica]:
        """Gera tratamentos para risco baixo."""
        tratamentos = []
        
        # Monitoramento
        monitoramento = RecomendacaoAgronomica(
            tipo="monitoramento",
            descricao=f"Monitoramento regular para zona {zona.zona_id} - risco baixo",
            cultura_alvo=self.config.cultura,
            custo_estimado_hectare=20.0,
            eficacia_esperada=0.30,
            urgencia="anual",
            produtos_recomendados=["Kit de amostragem"],
            metodos_implementacao="Amostragem sistemática",
            monitoramento_recomendado="Amostragem bianual"
        )
        tratamentos.append(monitoramento)
        
        return tratamentos
    
    def _programar_monitoramentos(self, resultado_analise: ResultadoNematoides) -> List[Dict[str, Any]]:
        """Programa monitoramentos baseados no risco."""
        monitoramentos = []
        
        # Monitoramento imediato para zonas críticas
        for zona in resultado_analise.resultado_zoneamento.zonas_risco:
            if zona.risco_classificacao == NivelRiscoNematoides.CRITICO:
                monitoramentos.append({
                    "tipo": "imediato",
                    "descricao": f"Monitoramento pós-tratamento zona {zona.zona_id}",
                    "zona_id": zona.zona_id,
                    "intervalo_dias": 15,
                    "profundidade": ["0-20cm", "20-40cm"],
                    "amostras": 10,
                    "urgencia": "alta"
                })
            elif zona.risco_classificacao == NivelRiscoNematoides.ALTO:
                monitoramentos.append({
                    "tipo": "periodico",
                    "descricao": f"Monitoramento mensal zona {zona.zona_id}",
                    "zona_id": zona.zona_id,
                    "intervalo_dias": 30,
                    "profundidade": ["0-20cm", "20-40cm"],
                    "amostras": 5,
                    "urgencia": "media"
                })
        
        # Monitoramento geral
        monitoramentos.append({
            "tipo": "geral",
            "descricao": "Monitoramento geral da área",
            "intervalo_dias": 180,
            "profundidade": ["0-20cm"],
            "amostras": 3,
            "urgencia": "baixa"
        })
        
        return monitoramentos
    
    def _definir_prazos_execucao(self, resultado_analise: ResultadoNematoides, 
                               tratamentos: List[RecomendacaoAgronomica]) -> Dict[str, datetime]:
        """Define prazos de execução para tratamentos."""
        prazos = {}
        data_base = datetime.now()
        
        # Tratamentos imediatos
        for tratamento in tratamentos:
            if tratamento.urgencia == "imediata":
                prazos[tratamento.descricao] = data_base
            elif tratamento.urgencia == "semanal":
                prazos[tratamento.descricao] = data_base + timedelta(days=7)
            elif tratamento.urgencia == "mensal":
                prazos[tratamento.descricao] = data_base + timedelta(days=30)
            elif tratamento.urgencia == "anual":
                prazos[tratamento.descricao] = data_base + timedelta(days=365)
        
        return prazos
    
    def _calcular_impacto_esperado(self, resultado_analise: ResultadoNematoides, 
                                 tratamentos: List[RecomendacaoAgronomica]) -> Dict[str, float]:
        """Calcula impacto esperado do plano de controle."""
        impacto = {
            "reducao_populacao_esperada": 0.0,
            "aumento_produtividade_esperado": 0.0,
            "retorno_investimento": 0.0,
            "sustentabilidade_ambiental": 0.0
        }
        
        # Redução esperada de população
        reducao_total = sum(t.eficacia_esperada for t in tratamentos if t.tipo == "tratamento")
        impacto["reducao_populacao_esperada"] = min(reducao_total / len(tratamentos), 0.95)
        
        # Aumento esperado de produtividade (baseado em redução de nematoides)
        impacto["aumento_produtividade_esperado"] = impacto["reducao_populacao_esperada"] * 0.15
        
        # Retorno sobre investimento
        custo_tratamentos = sum(t.custo_estimado_hectare for t in tratamentos)
        ganho_produtividade = resultado_analise.area_total_analisada * impacto["aumento_produtividade_esperado"] * 500.0  # R$500/ha de produtividade
        impacto["retorno_investimento"] = ganho_produtividade / max(custo_tratamentos, 1.0)
        
        # Sustentabilidade ambiental
        tratamentos_quimicos = len([t for t in tratamentos if "quimico" in t.produtos_recomendados])
        tratamentos_biologicos = len([t for t in tratamentos if "biologico" in t.produtos_recomendados])
        impacto["sustentabilidade_ambiental"] = tratamentos_biologicos / max(tratamentos_quimicos + tratamentos_biologicos, 1.0)
        
        return impacto