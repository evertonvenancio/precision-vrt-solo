"""
Módulo de Análise de Compactação do Solo
Análise de Resistência à Penetração (RP) por profundidade
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ClassificacaoCompactacao(Enum):
    """Classificação da resistência à penetração do solo."""
    APTO = "Apto"
    RESTRICAO = "Restricao"
    IMPEDIMENTO_SEVERO = "Impedimento Severo"


@dataclass
class CamadaCompactacao:
    """Representa uma camada de solo analisada."""
    profundidade_inicio: float  # cm
    profundidade_fim: float     # cm
    resistencia_mpa: float      # MPa
    classificacao: str
    necessita_escarificacao: bool


@dataclass
class PerfilCompactacao:
    """Perfil completo de compactação de um ponto/talhão."""
    ponto_id: str
    camadas: List[CamadaCompactacao]
    classificacao_geral: str
    necessita_escarificacao: bool
    profundidade_maxima_restricao: Optional[float]
    dados_grafico: Dict


class AnalisadorCompactacao:
    """
    Analisador de resistência à penetração do solo.
    
    Classificação:
    - Apto: < 2.0 MPa
    - Restrição: 2.0 - 2.5 MPa
    - Impedimento Severo: > 2.5 MPa
    """
    
    # Limites de classificação em MPa
    LIMITE_APTO = 2.0
    LIMITE_RESTRICAO = 2.5
    
    # Camadas padrão de análise (cm)
    CAMADAS_PADRAO = [
        (0, 10),
        (10, 20),
        (20, 30),
        (30, 40)
    ]
    
    def __init__(self):
        self.resultados = []
    
    def classificar_resistencia(self, resistencia_mpa: float) -> Tuple[str, bool]:
        """
        Classifica a resistência à penetração.
        
        Returns:
            Tuple: (classificacao, necessita_escarificacao)
        """
        if resistencia_mpa < self.LIMITE_APTO:
            return ClassificacaoCompactacao.APTO.value, False
        elif resistencia_mpa <= self.LIMITE_RESTRICAO:
            return ClassificacaoCompactacao.RESTRICAO.value, False
        else:
            return ClassificacaoCompactacao.IMPEDIMENTO_SEVERO.value, True
    
    def analisar_camada(self, profundidade_inicio: float, 
                        profundidade_fim: float,
                        resistencia_mpa: float) -> CamadaCompactacao:
        """
        Analisa uma camada individual de solo.
        """
        classificacao, necessita_escarificacao = self.classificar_resistencia(resistencia_mpa)
        
        return CamadaCompactacao(
            profundidade_inicio=profundidade_inicio,
            profundidade_fim=profundidade_fim,
            resistencia_mpa=round(resistencia_mpa, 2),
            classificacao=classificacao,
            necessita_escarificacao=necessita_escarificacao
        )
    
    def analisar_perfil(self, ponto_id: str,
                        resistencias: List[float],
                        camadas: Optional[List[Tuple[float, float]]] = None) -> PerfilCompactacao:
        """
        Analisa perfil completo de resistência à penetração.
        
        Args:
            ponto_id: Identificador do ponto de amostragem
            resistencias: Lista de resistências em MPa para cada camada
            camadas: Lista de tuplas (inicio, fim) em cm. Usa padrão se None.
            
        Returns:
            PerfilCompactacao com análise completa
        """
        if camadas is None:
            camadas = self.CAMADAS_PADRAO
        
        if len(resistencias) != len(camadas):
            raise ValueError(
                f"Número de resistências ({len(resistencias)}) deve corresponder "
                f"ao número de camadas ({len(camadas)})."
            )
        
        camadas_analisadas = []
        tem_impedimento = False
        profundidade_max_restricao = None
        
        for (inicio, fim), resistencia in zip(camadas, resistencias):
            camada = self.analisar_camada(inicio, fim, resistencia)
            camadas_analisadas.append(camada)
            
            if camada.necessita_escarificacao:
                tem_impedimento = True
                if profundidade_max_restricao is None or fim > profundidade_max_restricao:
                    profundidade_max_restricao = fim
        
        # Determinar classificação geral (pior caso)
        if any(c.classificacao == ClassificacaoCompactacao.IMPEDIMENTO_SEVERO.value 
               for c in camadas_analisadas):
            classificacao_geral = ClassificacaoCompactacao.IMPEDIMENTO_SEVERO.value
        elif any(c.classificacao == ClassificacaoCompactacao.RESTRICAO.value 
                 for c in camadas_analisadas):
            classificacao_geral = ClassificacaoCompactacao.RESTRICAO.value
        else:
            classificacao_geral = ClassificacaoCompactacao.APTO.value
        
        # Preparar dados para gráfico
        dados_grafico = self._preparar_dados_grafico(camadas_analisadas)
        
        perfil = PerfilCompactacao(
            ponto_id=ponto_id,
            camadas=camadas_analisadas,
            classificacao_geral=classificacao_geral,
            necessita_escarificacao=tem_impedimento,
            profundidade_maxima_restricao=profundidade_max_restricao,
            dados_grafico=dados_grafico
        )
        
        self.resultados.append(perfil)
        return perfil
    
    def _preparar_dados_grafico(self, camadas: List[CamadaCompactacao]) -> Dict:
        """
        Prepara dados estruturados para geração de gráfico de perfil.
        Formato otimizado para plotagem em PDF (Fase 4).
        """
        profundidades = []
        resistencias = []
        cores = []
        limites = []
        
        # Cores para cada classificação (RGB 0-1 para matplotlib/reportlab)
        CORES = {
            ClassificacaoCompactacao.APTO.value: (0.2, 0.7, 0.3),           # Verde
            ClassificacaoCompactacao.RESTRICAO.value: (1.0, 0.8, 0.0),      # Amarelo
            ClassificacaoCompactacao.IMPEDIMENTO_SEVERO.value: (0.9, 0.2, 0.2)  # Vermelho
        }
        
        for camada in camadas:
            # Ponto médio da camada para eixo Y (profundidade)
            profundidade_media = (camada.profundidade_inicio + camada.profundidade_fim) / 2
            profundidades.append(profundidade_media)
            resistencias.append(camada.resistencia_mpa)
            cores.append(CORES.get(camada.classificacao, (0.5, 0.5, 0.5)))
            
            # Linhas de limite para referência visual
            limites.append({
                'profundidade': profundidade_media,
                'limite_apto': self.LIMITE_APTO,
                'limite_restricao': self.LIMITE_RESTRICAO
            })
        
        return {
            'profundidades': profundidades,
            'resistencias': resistencias,
            'cores': cores,
            'limites_referencia': limites,
            'camadas': [
                {
                    'inicio': c.profundidade_inicio,
                    'fim': c.profundidade_fim,
                    'resistencia': c.resistencia_mpa,
                    'classificacao': c.classificacao
                }
                for c in camadas
            ],
            'eixo_x_label': 'Resistencia a Penetracao (MPa)',
            'eixo_y_label': 'Profundidade (cm)',
            'titulo': 'Perfil de Resistencia a Penetracao do Solo'
        }
    
    def gerar_flags_escarificacao(self, perfis: List[PerfilCompactacao]) -> List[Dict]:
        """
        Gera flags de necessidade de escarificação para consumo pelo gerador de laudos.
        
        Returns:
            Lista de dicts com flags formatadas para integração com laudos.
        """
        flags = []
        
        for perfil in perfis:
            if perfil.necessita_escarificacao:
                # Identificar camadas com impedimento severo
                camadas_impedimento = [
                    {
                        'profundidade_inicio': c.profundidade_inicio,
                        'profundidade_fim': c.profundidade_fim,
                        'resistencia_mpa': c.resistencia_mpa
                    }
                    for c in perfil.camadas 
                    if c.classificacao == ClassificacaoCompactacao.IMPEDIMENTO_SEVERO.value
                ]
                
                flag = {
                    'ponto_id': perfil.ponto_id,
                    'tipo': 'ESCARIFICACAO_OBRIGATORIA',
                    'severidade': 'ALTA',
                    'mensagem': (
                        f"Impedimento severo detectado em {len(camadas_impedimento)} camada(s). "
                        f"Profundidade máxima afetada: {perfil.profundidade_maxima_restricao} cm. "
                        f"Recomenda-se escarificação mecanizada."
                    ),
                    'camadas_afetadas': camadas_impedimento,
                    'profundidade_recomendada_escarificacao': perfil.profundidade_maxima_restricao,
                    'classificacao_geral': perfil.classificacao_geral,
                    'dados_tecnicos': {
                        'limite_apto_mpa': self.LIMITE_APTO,
                        'limite_restricao_mpa': self.LIMITE_RESTRICAO,
                        'resistencia_maxima_observada': max(
                            c.resistencia_mpa for c in perfil.camadas
                        )
                    }
                }
                flags.append(flag)
            else:
                # Flag informativa mesmo quando não há impedimento
                flag = {
                    'ponto_id': perfil.ponto_id,
                    'tipo': 'COMPACTACAO_MONITORAR',
                    'severidade': 'BAIXA' if perfil.classificacao_geral == ClassificacaoCompactacao.APTO.value else 'MEDIA',
                    'mensagem': (
                        f"Solo classificado como '{perfil.classificacao_geral}'. "
                        f"Monitoramento recomendado para próxima safra."
                    ),
                    'camadas_afetadas': [],
                    'profundidade_recomendada_escarificacao': None,
                    'classificacao_geral': perfil.classificacao_geral,
                    'dados_tecnicos': {
                        'limite_apto_mpa': self.LIMITE_APTO,
                        'limite_restricao_mpa': self.LIMITE_RESTRICAO,
                        'resistencia_maxima_observada': max(
                            c.resistencia_mpa for c in perfil.camadas
                        )
                    }
                }
                flags.append(flag)
        
        return flags
    
    def resumo_talhao(self, perfis: List[PerfilCompactacao]) -> Dict:
        """
        Gera resumo estatístico do talhão/propriedade.
        """
        if not perfis:
            return {}
        
        total_pontos = len(perfis)
        pontos_com_impedimento = sum(1 for p in perfis if p.necessita_escarificacao)
        pontos_com_restricao = sum(
            1 for p in perfis 
            if p.classificacao_geral == ClassificacaoCompactacao.RESTRICAO.value 
            and not p.necessita_escarificacao
        )
        pontos_apto = sum(
            1 for p in perfis 
            if p.classificacao_geral == ClassificacaoCompactacao.APTO.value
        )
        
        # Médias por camada
        medias_por_camada = {}
        for i, (inicio, fim) in enumerate(self.CAMADAS_PADRAO):
            resistencias_camada = [
                p.camadas[i].resistencia_mpa 
                for p in perfis if i < len(p.camadas)
            ]
            if resistencias_camada:
                medias_por_camada[f"{inicio}-{fim}cm"] = {
                    'media': round(np.mean(resistencias_camada), 2),
                    'min': round(min(resistencias_camada), 2),
                    'max': round(max(resistencias_camada), 2),
                    'desvio': round(np.std(resistencias_camada), 2)
                }
        
        return {
            'total_pontos_amostrais': total_pontos,
            'pontos_com_impedimento_severo': pontos_com_impedimento,
            'pontos_com_restricao': pontos_com_restricao,
            'pontos_apto': pontos_apto,
            'percentual_impedimento': round((pontos_com_impedimento / total_pontos) * 100, 1),
            'percentual_restricao': round((pontos_com_restricao / total_pontos) * 100, 1),
            'percentual_apto': round((pontos_apto / total_pontos) * 100, 1),
            'classificacao_predominante': (
                ClassificacaoCompactacao.IMPEDIMENTO_SEVERO.value 
                if pontos_com_impedimento > total_pontos / 2
                else ClassificacaoCompactacao.RESTRICAO.value 
                if pontos_com_restricao > total_pontos / 2
                else ClassificacaoCompactacao.APTO.value
            ),
            'medias_por_camada': medias_por_camada,
            'recomendacao_geral': (
                "Escarificação mecanizada recomendada para todo o talhão."
                if pontos_com_impedimento > total_pontos * 0.3
                else "Escarificação localizada nos pontos críticos."
                if pontos_com_impedimento > 0
                else "Manutenção do manejo atual com monitoramento."
            ),
            'flags_geradas': len([p for p in perfis if p.necessita_escarificacao])
        }


# ============================================================
# FUNÇÕES DE CONVENIÊNCIA
# ============================================================

def analisar_amostra_compactacao(ponto_id: str, 
                                  resistencias_mpa: List[float]) -> PerfilCompactacao:
    """
    Função de conveniência para análise rápida de uma amostra.
    
    Args:
        ponto_id: Identificador do ponto
        resistencias_mpa: Lista de 4 resistências em MPa 
                         [0-10cm, 10-20cm, 20-30cm, 30-40cm]
    
    Returns:
        PerfilCompactacao completo
    """
    analisador = AnalisadorCompactacao()
    return analisador.analisar_perfil(ponto_id, resistencias_mpa)


def classificar_resistencia_simples(resistencia_mpa: float) -> str:
    """
    Classificação simples de um valor de resistência.
    """
    if resistencia_mpa < AnalisadorCompactacao.LIMITE_APTO:
        return ClassificacaoCompactacao.APTO.value
    elif resistencia_mpa <= AnalisadorCompactacao.LIMITE_RESTRICAO:
        return ClassificacaoCompactacao.RESTRICAO.value
    else:
        return ClassificacaoCompactacao.IMPEDIMENTO_SEVERO.value


def verificar_necessidade_escarificacao(resistencias_mpa: List[float]) -> Tuple[bool, List[int]]:
    """
    Verifica se há necessidade de escarificação e retorna índices das camadas afetadas.
    
    Returns:
        Tuple: (necessita_escarificacao, indices_camadas_criticas)
    """
    indices_criticos = [
        i for i, r in enumerate(resistencias_mpa) 
        if r > AnalisadorCompactacao.LIMITE_RESTRICAO
    ]
    return len(indices_criticos) > 0, indices_criticos