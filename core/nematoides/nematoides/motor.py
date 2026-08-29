"""
Precision VRT Solo — Motor Principal de Nematoides

Implementa regras e cálculos específicos para análise de nematoides do solo.
Baseado no módulo legado core_agronomia_nematoides_legado.py
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import logging

from ...tipos.base import ConfigBase, ResultadoBase
from ...tipos.geoespacial import Bounds, Coordenada
from .contratos import (
    NivelRiscoNematoides,
    EspecieNematoides,
    PontoAmostraNematoides,
    ConfigInterpolacaoNematoides,
    ConfigZoneamentoNematoides,
    ConfigExportacaoNematoides,
    ZonaRiscoNematoides,
    ResultadoInterpolacaoNematoides,
    ResultadoZoneamentoNematoides,
    ResultadoNematoides
)


class MotorNematoides:
    """
    Motor principal para análise de nematoides do solo.
    
    Implementa metodologia de amostragem dirigida com cruzamento de dados
    de produtividade e índices de risco de nematoides.
    
    Baseado na metodologia de Mulla (2013) para amostragem dirigida.
    """
    
    # Limites de população de nematoides por 100g de solo (valores referência)
    LIMITE_BAIXO = 100.0
    LIMITE_MODERADO = 500.0
    LIMITE_ALTO = 1000.0
    
    # Fatores de correção por cultura (multiplicadores do limite)
    FATORES_CULTURA = {
        "soja": 0.8,
        "milho": 1.0,
        "cafe": 0.6,
        "cana": 1.2,
        "citros": 0.5,
        "feijao": 0.7,
        "algodao": 0.7,
        "trigo": 1.1,
        "arroz": 1.0,
        "sorgo": 1.0
    }
    
    def __init__(self, cultura: str = "milho"):
        """
        Inicializa o motor de nematoides.
        
        Args:
            cultura: Nome da cultura para ajuste dos limites de risco
        """
        self.cultura = cultura.lower()
        self.fator_cultura = self.FATORES_CULTURA.get(self.cultura, 1.0)
        self.amostras: List[PontoAmostraNematoides] = []
        self.zonas_risco: Dict[int, ZonaRiscoNematoides] = {}
        self.logger = logging.getLogger(__name__)
    
    def adicionar_amostra(self, amostra: PontoAmostraNematoides) -> None:
        """Adiciona uma amostra à coleção."""
        self.amostras.append(amostra)
        self.logger.info(f"Adicionada amostra {amostra.ponto_id} com população {amostra.populacao_nematoides_100g_solo}")
    
    def adicionar_amostras(self, amostras: List[PontoAmostraNematoides]) -> None:
        """Adiciona múltiplas amostras à coleção."""
        self.amostras.extend(amostras)
        self.logger.info(f"Adicionadas {len(amostras)} amostras")
    
    def classificar_risco(self, populacao: float) -> NivelRiscoNematoides:
        """
        Classifica o nível de risco baseado na população de nematoides.
        
        Args:
            populacao: População de nematoides por 100g de solo
            
        Returns:
            Nível de risco classificado
        """
        limite_baixo = self.LIMITE_BAIXO * self.fator_cultura
        limite_moderado = self.LIMITE_MODERADO * self.fator_cultura
        limite_alto = self.LIMITE_ALTO * self.fator_cultura
        
        if populacao < limite_baixo:
            return NivelRiscoNematoides.BAIXO
        elif populacao < limite_moderado:
            return NivelRiscoNematoides.MODERADO
        elif populacao < limite_alto:
            return NivelRiscoNematoides.ALTO
        else:
            return NivelRiscoNematoides.CRITICO
    
    def calcular_indice_risco_zona(self, amostras_zona: List[PontoAmostraNematoides]) -> Dict[str, Any]:
        """
        Calcula índice de risco composto para uma zona de manejo.
        
        Args:
            amostras_zona: Lista de amostras da zona
            
        Returns:
            Dict com estatísticas e classificação de risco
        """
        if not amostras_zona:
            return {"erro": "Nenhuma amostra fornecida"}
        
        populacoes = [a.populacao_nematoides_100g_solo for a in amostras_zona]
        media = float(np.mean(populacoes))
        maxima = float(np.max(populacoes))
        desvio = float(np.std(populacoes, ddof=1))
        
        # Coletar espécies únicas
        especies = list(set(
            a.especie_predominante for a in amostras_zona if a.especie_predominante
        ))
        
        # Índice de risco ponderado (0-100)
        indice_risco = min(100.0, (media / (self.LIMITE_ALTO * self.fator_cultura)) * 100)
        
        return {
            "populacao_media": round(media, 2),
            "populacao_maxima": round(maxima, 2),
            "desvio_padrao": round(desvio, 2),
            "indice_risco": round(indice_risco, 2),
            "especies_detectadas": especies,
            "n_amostras": len(amostras_zona),
            "classificacao_risco": self.classificar_risco(media)
        }
    
    def gerar_recomendacao_manejo(self, classificacao_risco: NivelRiscoNematoides, 
                                  correlacao_produtividade: float = 0.0) -> str:
        """
        Gera recomendação de manejo baseada no risco e correlação.
        
        Args:
            classificacao_risco: Nível de risco classificado
            correlacao_produtividade: Índice de correlação com produtividade
            
        Returns:
            Recomendação de manejo
        """
        indice_composto = correlacao_produtividade
        
        if classificacao_risco == NivelRiscoNematoides.CRITICO:
            if indice_composto > 60:
                return "TRATAMENTO OBRIGATÓRIO: Aplicar nematicida + rotação de culturas. Considerar pousio."
            return "TRATAMENTO OBRIGATÓRIO: Aplicar nematicida. Monitorar produtividade."
        
        elif classificacao_risco == NivelRiscoNematoides.ALTO:
            if indice_composto > 50:
                return "TRATAMENTO RECOMENDADO: Aplicar nematicida + adubação verde."
            return "MONITORAMENTO INTENSIVO: Aumentar frequência de amostragem."
        
        elif classificacao_risco == NivelRiscoNematoides.MODERADO:
            return "PREVENÇÃO: Adubação verde, manejo de resíduos. Amostragem anual."
        
        elif classificacao_risco == NivelRiscoNematoides.BAIXO:
            return "MANEJO PADRÃO: Amostragem bienal para monitoramento."
        
        return "Sem dados suficientes para recomendação."
    
    def calcular_prioridade_acao(self, risco: Dict[str, Any], correlacao: float, area: float) -> str:
        """
        Calcula prioridade de ação baseada em risco, correlação e área.
        
        Args:
            risco: Dados de risco da zona
            correlacao: Índice de correlação com produtividade
            area: Área da zona em hectares
            
        Returns:
            Prioridade da ação
        """
        indice_risco = risco.get("indice_risco", 0)
        indice_composto = correlacao
        
        score = (indice_risco * 0.4) + (indice_composto * 0.4) + (min(area, 50) * 0.2)
        
        if score > 80:
            return "PRIORIDADE 1 - URGENTE"
        elif score > 50:
            return "PRIORIDADE 2 - ALTA"
        elif score > 25:
            return "PRIORIDADE 3 - MÉDIA"
        else:
            return "PRIORIDADE 4 - BAIXA"
    
    def gerar_resultado_final(self, bounds: Bounds, 
                             config_interpolacao: ConfigInterpolacaoNematoides,
                             config_zoneamento: ConfigZoneamentoNematoides) -> ResultadoNematoides:
        """
        Gera resultado completo da análise de nematoides.
        
        Args:
            bounds: Limites espaciais da área
            config_interpolacao: Configuração de interpolação
            config_zoneamento: Configuração de zoneamento
            
        Returns:
            Resultado completo da análise
        """
        if not self.amostras:
            raise ValueError("Nenhuma amostra fornecida para análise")
        
        # Calcular risco global
        todas_populacoes = [a.populacao_nematoides_100g_solo for a in self.amostras]
        populacao_media_global = np.mean(todas_populacoes)
        risco_global = self.classificar_risco(populacao_media_global)
        
        # Gerar recomendações gerais
        recomendacoes_gerais = self._gerar_recomendacoes_gerais(risco_global)
        
        # Calcular custo estimado de tratamento
        custo_estimado = self._estimar_custo_tratamento(risco_global, len(self.amostras))
        
        # Criar resultado final
        resultado = ResultadoNematoides(
            resultado_interpolacao=self._criar_resultado_interpolacao(bounds, config_interpolacao),
            resultado_zoneamento=self._criar_resultado_zoneamento(config_zoneamento),
            recomendacoes_gerais=recomendacoes_gerais,
            risco_global=risco_global,
            area_total_analisada=self._calcular_area_total(bounds),
            custo_estimado_tratamento=custo_estimado
        )
        
        return resultado
    
    def _criar_resultado_interpolacao(self, bounds: Bounds, 
                                     config: ConfigInterpolacaoNematoides) -> ResultadoInterpolacaoNematoides:
        """Cria resultado da interpolação."""
        # Esta seria a implementação real da interpolação
        # Por enquanto, criar estrutura básica
        from .interpolacao.motor import MotorInterpolacaoNematoides
        
        motor_interp = MotorInterpolacaoNematoides(config)
        for amostra in self.amostras:
            motor_interp.adicionar_amostra(amostra)
        
        return motor_interp.interpolar(bounds)
    
    def _criar_resultado_zoneamento(self, config: ConfigZoneamentoNematoides) -> ResultadoZoneamentoNematoides:
        """Cria resultado do zoneamento."""
        # Esta seria a implementação real do zoneamento
        # Por enquanto, criar estrutura básica
        from .zoneamento.motor import MotorZoneamentoNematoides
        
        motor_zone = MotorZoneamentoNematoides(config)
        
        # Agrupar amostras por zona (simplificado)
        n_amostras = len(self.amostras)
        n_zonas = min(config.n_zonas, n_amostras)
        
        # Criar zonas baseadas em população de nematoides
        populacoes = [a.populacao_nematoides_100g_solo for a in self.amostras]
        populacoes_sorted = sorted(populacoes)
        
        zonas_risco = []
        for i in range(n_zonas):
            inicio = i * len(populacoes_sorted) // n_zonas
            fim = (i + 1) * len(populacoes_sorted) // n_zonas
            
            populacoes_zona = populacoes_sorted[inicio:fim]
            amostras_zona_idx = [j for j, pop in enumerate(populacoes) 
                               if inicio <= populacoes_sorted.index(pop) < fim]
            amostras_zona = [self.amostras[j] for j in amostras_zona_idx]
            
            # Calcular estatísticas da zona
            stats = self.calcular_indice_risco_zona(amostras_zona)
            
            zona = ZonaRiscoNematoides(
                zona_id=i + 1,
                risco_classificacao=stats["classificacao_risco"],
                populacao_media=stats["populacao_media"],
                populacao_maxima=stats["populacao_maxima"],
                generos_detectados=stats["especies_detectadas"],
                recomendacao_manejo=self.gerar_recomendacao_manejo(stats["classificacao_risco"]),
                area_hectares=10.0,  # Placeholder
                correlacao_produtividade_risko=0.0,  # Placeholder
                prioridade_acao=self.calcular_prioridade_acao(stats, 0.0, 10.0)
            )
            zonas_risco.append(zona)
        
        from .zoneamento.motor import MotorZoneamentoNematoides
        return MotorZoneamentoNematoides(config).gerar_zoneamento(zonas_risco)
    
    def _gerar_recomendacoes_gerais(self, risco_global: NivelRiscoNematoides) -> List[str]:
        """Gera recomendações gerais baseadas no risco global."""
        recomendacoes = []
        
        if risco_global == NivelRiscoNematoides.CRITICO:
            recomendacoes.extend([
                "Implementar tratamento imediato com nematicidas",
                "Considerar rotação de culturas com não-hospedeiros",
                "Implementar pousio de 6-12 meses",
                "Monitorar frequentemente a população de nematoides"
            ])
        elif risco_global == NivelRiscoNematoides.ALTO:
            recomendacoes.extend([
                "Implementar tratamento com nematicidas",
                "Adicionar adubação verde para controle biológico",
                "Aumentar frequência de amostragem"
            ])
        elif risco_global == NivelRiscoNematoides.MODERADO:
            recomendacoes.extend([
                "Implementar práticas de prevenção",
                "Adicionar adubação verde",
                "Manejo adequado de resíduos culturais"
            ])
        else:
            recomendacoes.append("Manejo padrão com amostragem regular")
        
        return recomendacoes
    
    def _estimar_custo_tratamento(self, risco_global: NivelRiscoNematoides, n_amostras: int) -> float:
        """Estima o custo do tratamento baseado no risco."""
        custo_por_hectare = {
            NivelRiscoNematoides.BAIXO: 50.0,
            NivelRiscoNematoides.MODERADO: 150.0,
            NivelRiscoNematoides.ALTO: 300.0,
            NivelRiscoNematoides.CRITICO: 500.0
        }
        
        area_estimada = n_amostras * 5.0  # Estimativa de 5ha por amostra
        return custo_por_hectare.get(risco_global, 100.0) * area_estimada
    
    def _calcular_area_total(self, bounds: Bounds) -> float:
        """Calcula a área total em hectares."""
        # Cálculo simplificado
        area_m2 = (bounds.maxx - bounds.minx) * (bounds.maxy - bounds.miny)
        return area_m2 / 10000.0  # Converter para hectares