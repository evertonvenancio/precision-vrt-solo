"""
Precision VRT Solo — Módulo de Agronomia da Compactação

Implementa regras e cálculos agronômicos específicos para análise de compactação.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum

from ...tipos.base import ConfigBase
from ..compactacao.contratos import (
    PerfilCompactacao, 
    ResultadoZoneamentoCompactacao,
    ClassificacaoCompactacao
)


class Cultura(str, Enum):
    """Tipos de cultura suportados."""
    SOJA = "soja"
    MILHO = "milho"
    ALGODAO = "algodao"
    CANA_DE_ACUCAR = "cana_de_acucar"
    TRIGO = "trigo"
    CITRUS = "citrus"
    PASTAGEM = "pastagem"


class TipoSolo(str, Enum):
    """Tipos de solo para análise de compactação."""
    ARGILOSO = "argiloso"
    ARENOSO = "arenoso"
    MISTO = "misto"
    ORGANICO = "organico"


@dataclass
class ConfigAgronomiaCompactacao(ConfigBase):
    """Configuração para cálculos agronômicos de compactação."""
    
    # Dados da cultura
    cultura: Cultura = Cultura.SOJA
    tipo_solo: TipoSolo = TipoSolo.MISTO
    idade_cultura_meses: int = 3
    
    # Parâmetros agronômicos
    resistencia_critica_cultura: float = 2.0  # MPa
    resistencia_maxima_tolerada: float = 3.0  # MPa
    
    # Parâmetros de escarificação
    profundidade_escarficacao_padrao: float = 30.0  # cm
    densidade_escarficacao_ideal: int = 25  # espacamento entre sulcos por metro
    
    # Parâmetros de recomendação
    tolerancia_varianza: float = 0.2
    minimo_pontos_amostrais: int = 10
    
    def __post_init__(self):
        """Valida configuração."""
        if self.idade_cultura_meses < 0 or self.idade_cultura_meses > 24:
            raise ValueError("Idade da cultura deve estar entre 0 e 24 meses")
        
        if self.resistencia_critica_cultura > self.resistencia_maxima_tolerada:
            raise ValueError("Resistência crítica não pode ser maior que resistência máxima tolerada")


@dataclass
class RecomendacaoAgronomica:
    """Recomendação agronômica para compactação."""
    
    # Campos obrigatórios primeiro
    tipo: str  # "ESCARIFICACAO", "MONITORAMENTO", "MANEJO_NORMAL"
    urgencia: str  # "ALTA", "MEDIA", "BAIXA"
    descricao: str
    
    # Campos opcionais
    profundidade_recomendada_cm: Optional[float] = None
    densidade_escarficacao: Optional[int] = None
    proxima_amostragem_meses: Optional[int] = None
    riscos_ignorar: List[str] = field(default_factory=list)
    beneficios_agir: List[str] = field(default_factory=list)
    custo_estimado: Optional[float] = None


@dataclass
class AnaliseAgronomica:
    """Resultado da análise agronômica de compactação."""
    
    perfis_analisados: int
    areas_afetadas: Dict[str, float]  # hectares por classificacao
    recomendacoes: List[RecomendacaoAgronomica]
    indice_risco_global: float  # 0.0 a 1.0
    custo_total_estimado: Optional[float] = None
    impacto_producao: Optional[Dict[str, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte resultado para dicionário serializável."""
        return {
            "perfis_analisados": self.perfis_analisados,
            "areas_afetadas": self.areas_afetadas,
            "recomendacoes": [
                {
                    "tipo": r.tipo,
                    "urgencia": r.urgencia,
                    "descricao": r.descricao,
                    "profundidade_recomendada_cm": r.profundidade_recomendada_cm,
                    "densidade_escarficacao": r.densidade_escarficacao,
                    "proxima_amostragem_meses": r.proxima_amostragem_meses
                }
                for r in self.recomendacoes
            ],
            "indice_risco_global": self.indice_risco_global,
            "custo_total_estimado": self.custo_total_estimado,
            "impacto_producao": self.impacto_producao
        }


class MotorAgronomiaCompactacao:
    """
    Motor de agronomia específico para compactação do solo.
    
    Implementa regras e cálculos agronômicos para análise
    de compactação com base em cultura, tipo de solo e época do ano.
    """
    
    # Base de dados de resistência crítica por cultura (MPa)
    RESISTENCIA_CRITICA_POR_CULTURA = {
        Cultura.SOJA: 1.8,
        Cultura.MILHO: 2.0,
        Cultura.ALGODAO: 2.2,
        Cultura.CANA_DE_ACUCAR: 2.5,
        Cultura.TRIGO: 1.6,
        Cultura.CITRUS: 2.3,
        Cultura.PASTAGEM: 2.8
    }
    
    # Resposta à escarificação por tipo de solo
    RESPOSTA_ESCARIFICACAO = {
        TipoSolo.ARGILOSO: 0.8,  # Alta resposta
        TipoSolo.ARENOSO: 0.3,  # Baixa resposta
        TipoSolo.MISTO: 0.6,     # Resposta média
        TipoSolo.ORGANICO: 0.9  # Muito alta resposta
    }
    
    # Custo estimado por hectare (USD)
    CUSTO_ESCARIFICACAO_POR_HA = {
        Cultura.SOJA: 45.0,
        Cultura.MILHO: 50.0,
        Cultura.ALGODAO: 55.0,
        Cultura.CANA_DE_ACUCAR: 40.0,
        Cultura.TRIGO: 35.0,
        Cultura.CITRUS: 70.0,
        Cultura.PASTAGEM: 30.0
    }
    
    def __init__(self, config: ConfigAgronomiaCompactacao):
        self.config = config
        self.resultado: Optional[AnaliseAgronomica] = None
    
    def analisar(self, perfis: List[PerfilCompactacao], 
                resultado_zoneamento: Optional[ResultadoZoneamentoCompactacao] = None) -> AnaliseAgronomica:
        """
        Realiza análise agronômica completa da compactação.
        
        Args:
            perfis: Lista de perfis de compactação
            resultado_zoneamento: Resultado do zoneamento (opcional)
            
        Returns:
            Análise agronômica com recomendações
        """
        if not perfis:
            raise ValueError("Nenhum perfil disponível para análise")
        
        # Calcular áreas afetadas
        areas_afetadas = self._calcular_areas_afetadas(perfis, resultado_zoneamento)
        
        # Gerar recomendações
        recomendacoes = self._gerar_recomendacoes(perfis, resultado_zoneamento)
        
        # Calcular índice de risco global
        indice_risco = self._calcular_indice_risco_global(perfis, resultado_zoneamento)
        
        # Estimar custo total
        custo_total = self._estimar_custo_total(recomendacoes)
        
        # Estimar impacto na produção
        impacto_producao = self._estimar_impacto_producao(perfis, resultado_zoneamento)
        
        self.resultado = AnaliseAgronomica(
            perfis_analisados=len(perfis),
            areas_afetadas=areas_afetadas,
            recomendacoes=recomendacoes,
            indice_risco_global=indice_risco,
            custo_total_estimado=custo_total,
            impacto_producao=impacto_producao
        )
        
        return self.resultado
    
    def _calcular_areas_afetadas(self, perfis: List[PerfilCompactacao], 
                               resultado_zoneamento: Optional[ResultadoZoneamentoCompactacao]) -> Dict[str, float]:
        """Calcula áreas afetadas por classificação."""
        areas = {
            "impedimento_severo": 0.0,
            "restricao": 0.0,
            "apto": 0.0
        }
        
        if resultado_zoneamento:
            # Usar dados do zoneamento
            for zona in resultado_zoneamento.zonas:
                if zona.classificacao_predominante == "impedimento_severo":
                    areas["impedimento_severo"] += zona.area_ha
                elif zona.classificacao_predominante == "restricao":
                    areas["restricao"] += zona.area_ha
                else:
                    areas["apto"] += zona.area_ha
        else:
            # Estimar a partir de perfis
            for perfil in perfis:
                if perfil.necessita_escarificacao:
                    areas["impedimento_severo"] += 1.0  # Estimar 1ha por perfil
                elif perfil.classificacao_geral == ClassificacaoCompactacao.RESTRICAO.value:
                    areas["restricao"] += 1.0
                else:
                    areas["apto"] += 1.0
        
        return areas
    
    def _gerar_recomendacoes(self, perfis: List[PerfilCompactacao], 
                            resultado_zoneamento: Optional[ResultadoZoneamentoCompactacao]) -> List[RecomendacaoAgronomica]:
        """Gera recomendações agronômicas."""
        recomendacoes = []
        
        # Recomendação principal baseada na situação geral
        situacao_geral = self._avaliar_situacao_geral(perfis, resultado_zoneamento)
        
        if situacao_geral == "CRITICA":
            recomendacao = self._gerar_recomendacao_critica(perfis, resultado_zoneamento)
        elif situacao_geral == "RESTRITA":
            recomendacao = self._gerar_recomendacao_restrita(perfis, resultado_zoneamento)
        else:
            recomendacao = self._gerar_recomendacao_normal(perfis, resultado_zoneamento)
        
        recomendacoes.append(recomendacao)
        
        # Recomendações específicas por perfil (somente para perfis críticos)
        perfis_criticos = [p for p in perfis if p.necessita_escarificacao]
        if len(perfis_criticos) > 0:
            recomendacoes.extend(self._gerar_recomendacoes_especificas(perfis_criticos))
        
        return recomendacoes
    
    def _avaliar_situacao_geral(self, perfis: List[PerfilCompactacao], 
                               resultado_zoneamento: Optional[ResultadoZoneamentoCompactacao]) -> str:
        """Avalia situação geral da compactação."""
        perfis_criticos = sum(1 for p in perfis if p.necessita_escarificacao)
        percentual_criticos = (perfis_criticos / len(perfis)) * 100
        
        if resultado_zoneamento:
            percentual_impedimento = resultado_zoneamento.percentual_impedimento
            if percentual_impedimento >= 30 or percentual_criticos >= 40:
                return "CRITICA"
            elif percentual_impedimento >= 15 or percentual_criticos >= 20:
                return "RESTRITA"
            else:
                return "NORMAL"
        else:
            if percentual_criticos >= 30:
                return "CRITICA"
            elif percentual_criticos >= 15:
                return "RESTRITA"
            else:
                return "NORMAL"
    
    def _gerar_recomendacao_critica(self, perfis: List[PerfilCompactacao], 
                                  resultado_zoneamento: Optional[ResultadoZoneamentoCompactacao]) -> RecomendacaoAgronomica:
        """Gera recomendação para situação crítica."""
        tipo = "ESCARIFICACAO"
        urgencia = "ALTA"
        
        if resultado_zoneamento and resultado_zoneamento.percentual_impedimento >= 30:
            descricao = (
                f"Situção crítica detectada com {resultado_zoneamento.percentual_impedimento}% da área "
                f"com impedimento severo. Recomenda-se escarificação mecanizada completa do talhão "
                f"com profundidade de {self.config.profundidade_escarficacao_padrao}cm e "
                f"densidade de {self.config.densidade_escarficacao_ideal} sulcos por metro."
            )
        else:
            descricao = (
                "Situção crítica detectada em múltiplos pontos de amostragem. "
                "Recomenda-se escarificação mecanizada nos pontos críticos e monitoramento "
                "intensivo nas áreas restritas."
            )
        
        return RecomendacaoAgronomica(
            tipo=tipo,
            urgencia=urgencia,
            descricao=descricao,
            profundidade_recomendada_cm=self.config.profundidade_escarficacao_padrao,
            densidade_escarficacao=self.config.densidade_escarficacao_ideal,
            proxima_amostragem_meses=3,
            riscos_ignorar=[
                "Redução significativa de produtividade",
                "Aumento de custos com mecanização",
                "Degradação estrutural do solo a longo prazo"
            ],
            beneficios_agir=[
                "Restabelecimento da estrutura do solo",
                "Melhora na infiltração de água",
                "Aumento da eficiência de nutrientes",
                "Redução de custos operacionais futuros"
            ],
            custo_estimado=self._estimar_custo_escarificacao(resultado_zoneamento)
        )
    
    def _gerar_recomendacao_restrita(self, perfis: List[PerfilCompactacao], 
                                   resultado_zoneamento: Optional[ResultadoZoneamentoCompactacao]) -> RecomendacaoAgronomica:
        """Gera recomendação para situação restrita."""
        tipo = "ESCARIFICACAO"
        urgencia = "MEDIA"
        
        if resultado_zoneamento:
            descricao = (
                f"Situação restrita com {resultado_zoneamento.percentual_restricao}% da área "
                f"com restrição de compactação. Recomenda-se escarificação localizada "
                f"nos pontos críticos com monitoramento."
            )
        else:
            descricao = (
                "Situação restrita detectada em alguns pontos de amostragem. "
                "Recomenda-se monitoramento próximo com possibilidade de escarificação localizada."
            )
        
        return RecomendacaoAgronomica(
            tipo=tipo,
            urgencia=urgencia,
            descricao=descricao,
            profundidade_recomendada_cm=self.config.profundidade_escarficacao_padrao * 0.8,
            densidade_escarficacao=self.config.densidade_escarficacao_ideal,
            proxima_amostragem_meses=6,
            riscos_ignorar=[
                "Piora gradual da compactação",
                "Redução moderada de produtividade"
            ],
            beneficios_agir=[
                "Prevenção de piora da situação",
                "Manutenção da produtividade atual",
                "Economia em relação à escarificação completa"
            ],
            custo_estimado=self._estimar_custo_escarificacao(resultado_zoneamento) * 0.5
        )
    
    def _gerar_recomendacao_normal(self, perfis: List[PerfilCompactacao], 
                                 resultado_zoneamento: Optional[ResultadoZoneamentoCompactacao]) -> RecomendacaoAgronomica:
        """Gera recomendação para situação normal."""
        tipo = "MONITORAMENTO"
        urgencia = "BAIXA"
        
        descricao = (
            "Situação normal da compactação. Recomenda-se manutenção do manejo atual "
            "com amostragem periódica para monitoramento."
        )
        
        return RecomendacaoAgronomica(
            tipo=tipo,
            urgencia=urgencia,
            descricao=descricao,
            proxima_amostragem_meses=12,
            riscos_ignorar=[
                "Manutenção do status quo"
            ],
            beneficios_agir=[
                "Custo mínimo de monitoramento",
                "Detecção precoce de problemas futuros",
                "Manutenção da produtividade atual"
            ]
        )
    
    def _gerar_recomendacoes_especificas(self, perfis_criticos: List[PerfilCompactacao]) -> List[RecomendacaoAgronomica]:
        """Gera recomendações específicas para perfis críticos."""
        recomendacoes = []
        
        for perfil in perfis_criticos:
            recomendacao = RecomendacaoAgronomica(
                tipo="ESCARIFICACAO",
                urgencia="ALTA" if perfil.classificacao_geral == ClassificacaoCompactacao.IMPEDIMENTO_SEVERO.value else "MEDIA",
                descricao=(
                    f"Ponto crítico {perfil.ponto_id} requer atenção especial. "
                    f"Profundidade máxima de restrição: {perfil.profundidade_maxima_restricao}cm. "
                    f"Recomenda-se intervenção localizada."
                ),
                profundidade_recomendada_cm=perfil.profundidade_maxima_restricao or self.config.profundidade_escarficacao_padrao,
                densidade_escarficacao=self.config.densidade_escarficacao_ideal,
                proxima_amostragem_meses=3
            )
            recomendacoes.append(recomendacao)
        
        return recomendacoes
    
    def _calcular_indice_risco_global(self, perfis: List[PerfilCompactacao], 
                                     resultado_zoneamento: Optional[ResultadoZoneamentoCompactacao]) -> float:
        """Calcula índice de risco global (0.0 a 1.0)."""
        # Baseado em percentual de pontos críticos
        perfis_criticos = sum(1 for p in perfis if p.necessita_escarificacao)
        percentual_criticos = (perfis_criticos / len(perfis)) if perfis else 0
        
        # Ajustar por dados do zoneamento, se disponível
        if resultado_zoneamento:
            percentual_impedimento = resultado_zoneamento.percentual_impedimento / 100
            percentual_restricao = resultado_zoneamento.percentual_restricao / 100
            indice = (percentual_impedimento * 0.7) + (percentual_restricao * 0.3) + (percentual_criticos * 0.5)
        else:
            indice = percentual_criticos
        
        return min(indice, 1.0)
    
    def _estimar_custo_total(self, recomendacoes: List[RecomendacaoAgronomica]) -> Optional[float]:
        """Estima custo total das intervenções recomendadas."""
        custos = [r.custo_estimado for r in recomendacoes if r.custo_estimado]
        return sum(custos) if custos else None
    
    def _estimar_custo_escarificacao(self, resultado_zoneamento: Optional[ResultadoZoneamentoCompactacao]) -> float:
        """Estima custo de escarificação baseado na área."""
        if resultado_zoneamento:
            area_total = sum(z.area_ha for z in resultado_zoneamento.zonas)
        else:
            # Estimativa baseada em perfis
            area_total = 10.0  # 10 hectares por padrão
        
        custo_ha = self.CUSTO_ESCARIFICACAO_POR_HA.get(self.config.cultura, 50.0)
        return area_total * custo_ha
    
    def _estimar_impacto_producao(self, perfis: List[PerfilCompactacao], 
                                resultado_zoneamento: Optional[ResultadoZoneamentoCompactacao]) -> Optional[Dict[str, float]]:
        """Estima impacto na produção baseado na compactação."""
        # Resposta à compactação por cultura (redução percentual estimada)
        resposta_cultura = {
            Cultura.SOJA: 0.15,   # 15% de redução
            Cultura.MILHO: 0.12,  # 12% de redução
            Cultura.ALGODAO: 0.18, # 18% de redução
            Cultura.CANA_DE_ACUCAR: 0.08,  # 8% de redução
            Cultura.TRIGO: 0.10,   # 10% de redução
            Cultura.CITRUS: 0.20,  # 20% de redução
            Cultura.PASTAGEM: 0.05 # 5% de redução
        }
        
        # Baseado na situação geral
        indice_risco = self._calcular_indice_risco_global(perfis, resultado_zoneamento)
        reducao_producao = resposta_cultura.get(self.config.cultura, 0.1) * indice_risco
        
        return {
            "reducao_percentual_estimada": round(reducao_producao * 100, 1),
            "risco_perda_produtividade": round(indice_risco * 100, 1),
            "cultura_afetada": self.config.cultura.value,
            "tipo_solo": self.config.tipo_solo.value
        }
    
    def obter_tolerancias(self) -> Dict[str, float]:
        """Obtém tolerâncias específicas para a cultura e tipo de solo."""
        return {
            "resistencia_critica_mpa": self.RESISTENCIA_CRITICA_POR_CULTURA.get(self.config.cultura, 2.0),
            "resposta_escarificacao": self.RESPOSTA_ESCARIFICACAO.get(self.config.tipo_solo, 0.6),
            "tolerancia_varianza": self.config.tolerancia_varianza
        }