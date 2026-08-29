"""
Precision VRT Solo — Módulo de Agronomia de Fertirrigação

Implementa regras e cálculos agronômicos específicos para fertirrigação.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

from ..fertirrigacao.contratos import (
    LeituraSolucao,
    AreaFertirrigacao,
    ConfigAgronomiaFertirrigacao,
    ConfigNutricao,
    ResultadoNutricao
)

logger = logging.getLogger(__name__)


class CulturaFase(str, Enum):
    """Fases fenológicas suportadas."""
    VEGETATIVO = "vegetativo"
    FLORESCIMENTO = "florescimento"
    FRUTIFICACAO = "frutificacao"
    MATURACAO = "maturacao"
    COLHEITA = "colheita"


class StatusNutricao(str, Enum):
    """Status nutricional da cultura."""
    DEFICIENTE = "deficiente"
    ADEQUADO = "adequado"
    EXCESSIVO = "excessivo"


@dataclass
class ConfigCalculoNutricao:
    """Configuração para cálculos nutricionais."""
    
    # Limites de referência
    limites_ce: Dict[str, float] = field(default_factory=dict)
    
    limites_ph: Dict[str, float] = field(default_factory=dict)
    
    limites_nutrientes: Dict[str, Dict[str, float]] = field(default_factory=dict)


@dataclass
class CaracterizacaoNutricional:
    """Caracterização nutricional de um ponto ou área."""
    
    ponto_id: str
    cultura: str
    fase_fenologica: str
    
    # Análises por nutriente
    analises_nutrientes: Dict[str, Dict[str, Any]]
    
    # Status geral
    status_geral: StatusNutricao
    observacoes: List[str] = field(default_factory=list)


@dataclass
class BalancoNutricional:
    """Balanço nutricional completo."""
    
    # Entradas
    entradas_nutrientes: Dict[str, float]
    
    # Saídas (consumo da cultura)
    saidas_nutrientes: Dict[str, float]
    
    # Balanço
    balanco_geral: Dict[str, float]
    status_balanco: str
    
    # Recomendações
    recomendacoes_correcao: List[str]


@dataclass
class CurvaNutritiva:
    """Curva nutritiva de referência."""
    
    cultura: str
    fase_fenologica: str
    
    # Limites ideais
    limites_ce: Dict[str, float]
    limites_ph: Dict[str, float]
    limites_nutrientes: Dict[str, Dict[str, float]]
    
    # Faixas de segurança
    faixas_seguranca: Dict[str, Dict[str, float]]


class MotorAgronomiaFertirrigacao:
    """Motor de agronomia para fertirrigação."""
    
    def __init__(self):
        self.config_calculo = ConfigCalculoNutricao()
        self.curvas_nutritivas = self._carregar_curvas_nutritivas()
        logger.info("MotorAgronomiaFertirrigacao inicializado")
    
    def processar_nutricao(self, leituras: List[LeituraSolucao], 
                          area: AreaFertirrigacao,
                          config_agronomia: ConfigAgronomiaFertirrigacao,
                          config_nutricao: ConfigNutricao) -> ResultadoNutricao:
        """Processar análise agronômica das soluções.
        
        Args:
            leituras: Lista de leituras de solução
            area: Área de fertirrigação
            config_agronomia: Configuração agronômica
            config_nutricao: Configuração nutricional
        
        Returns:
            Resultado da análise nutricional
        """
        logger.info("Processando análise agronômica")
        
        # Extrair macronutrientes das leituras
        macronutrientes = self._extrair_macronutrientes(leituras)
        
        # Extrair micronutrientes das leituras
        micronutrientes = self._extrair_micronutrientes(leituras)
        
        # Calcular balanço nutricional
        balanco_nutricional = self._calcular_balanco_nutricional(
            macronutrientes, micronutrientes, config_nutricao
        )
        
        # Interpretar resultados
        interpretacao = self._interpretar_resultados(macronutrientes, micronutrientes, balanco_nutricional)
        
        # Gerar recomendação de pH
        recomendacao_pH = self._gerar_recomendacao_pH(leituras, config_agronomia)
        
        # Identificar pontos críticos
        pontos_criticos = self._identificar_pontos_criticos(leituras, config_agronomia)
        
        # Criar resultado final
        resultado = ResultadoNutricao(
            timestamp=len(leituras),  # Simplificado para demonstração
            tempo_execucao_ms=0,
            config=config_nutricao,
            macronutrientes_analisados=macronutrientes,
            micronutrientes_analisados=micronutrientes,
            balanco_nutricional=balanco_nutricional.__dict__,
            interpretacao=interpretacao,
            recomendacao_pH=recomendacao_pH,
            pontos_criticos=pontos_criticos
        )
        
        logger.info("Processamento agronômico concluído")
        return resultado
    
    def _extrair_macronutrientes(self, leituras: List[LeituraSolucao]) -> Dict[str, float]:
        """Extrair estatísticas de macronutrientes."""
        logger.info("Extraindo macronutrientes")
        
        macronutrientes = {}
        
        for nutriente in ["no3_mg_L", "k_mg_L", "ca_mg_L", "mg_mg_L", "po4_mg_L", "so4_mg_L"]:
            valores = []
            for leitura in leituras:
                if hasattr(leitura, nutriente):
                    valor = getattr(leitura, nutriente)
                    if valor is not None:
                        valores.append(valor)
            
            if valores:
                macronutrientes[nutriente] = {
                    "min": min(valores),
                    "max": max(valores),
                    "media": np.mean(valores),
                    "mediana": np.median(valores),
                    "desvio_padrao": np.std(valores),
                    "coeficiente_variacao": np.std(valores) / np.mean(valores) * 100 if np.mean(valores) > 0 else 0
                }
            else:
                macronutrientes[nutriente] = None
        
        return macronutrientes
    
    def _extrair_micronutrientes(self, leituras: List[LeituraSolucao]) -> Dict[str, float]:
        """Extrair estatísticas de micronutrientes."""
        logger.info("Extraindo micronutrientes")
        
        micronutrientes = {}
        
        for nutriente in ["b_mg_L", "fe_mg_L", "mn_mg_L", "zn_mg_L", "cu_mg_L"]:
            valores = []
            for leitura in leituras:
                if hasattr(leitura, nutriente):
                    valor = getattr(leitura, nutriente)
                    if valor is not None:
                        valores.append(valor)
            
            if valores:
                micronutrientes[nutriente] = {
                    "min": min(valores),
                    "max": max(valores),
                    "media": np.mean(valores),
                    "mediana": np.median(valores),
                    "desvio_padrao": np.std(valores),
                    "coeficiente_variacao": np.std(valores) / np.mean(valores) * 100 if np.mean(valores) > 0 else 0
                }
            else:
                micronutrientes[nutriente] = None
        
        return micronutrientes
    
    def _calcular_balanco_nutricional(self, macronutrientes: Dict[str, Any], 
                                    micronutrientes: Dict[str, Any],
                                    config_nutricao: ConfigNutricao) -> BalancoNutricional:
        """Calcular balanço nutricional completo."""
        logger.info("Calculando balanço nutricional")
        
        # Montar entradas de nutrientes
        entradas = {}
        for nutriente, dados in macronutrientes.items():
            if dados:
                entradas[nutriente] = dados["media"]
        
        for nutriente, dados in micronutrientes.items():
            if dados:
                entradas[nutriente] = dados["media"]
        
        # Calcular saídas (consumo da cultura) - simplificado
        saidas = self._estimar_consumo_cultura(config_nutricao)
        
        # Calcular balanço
        balanco = {}
        for nutriente in entradas:
            balanco[nutriente] = entradas[nutriente] - saidas.get(nutriente, 0)
        
        # Determinar status do balanço
        status_balanco = self._avaliar_status_balanco(balanco)
        
        # Gerar recomendações de correção
        recomendacoes = self._gerar_recomendacoes_correcao(balanco, entradas, saidas)
        
        return BalancoNutricional(
            entradas_nutrientes=entradas,
            saidas_nutrientes=saidas,
            balanco_geral=balanco,
            status_balanco=status_balanco,
            recomendacoes_correcao=recomendacoes
        )
    
    def _estimar_consumo_cultura(self, config_nutricao: ConfigNutricao) -> Dict[str, float]:
        """Estimar consumo de nutrientes pela cultura."""
        # Simplificado - na prática usaria tabelas específicas por cultura e fase
        consumo = {}
        
        if config_nutricao.objetivo_n_kg_ha > 0:
            consumo["no3_mg_L"] = config_nutricao.objetivo_n_kg_ha * 1000  # Simplificado
        if config_nutricao.objetivo_p2o5_kg_ha > 0:
            consumo["po4_mg_L"] = config_nutricao.objetivo_p2o5_kg_ha * 1000
        if config_nutricao.objetivo_k2o_kg_ha > 0:
            consumo["k_mg_L"] = config_nutricao.objetivo_k2o_kg_ha * 1000
        
        # Micronutrientes
        for nutriente in ["b_mg_L", "fe_mg_L", "mn_mg_L", "zn_mg_L", "cu_mg_L"]:
            attr = f"objetivo_{nutriente}"
            if hasattr(config_nutricao, attr):
                valor = getattr(config_nutricao, attr)
                if valor > 0:
                    consumo[nutriente] = valor
        
        return consumo
    
    def _avaliar_status_balanco(self, balanco: Dict[str, float]) -> str:
        """Avaliar status do balanço nutricional."""
        positivos = sum(1 for v in balanco.values() if v > 0)
        negativos = sum(1 for v in balanco.values() if v < 0)
        
        if positivos > negativos:
            return "positivo"
        elif negativos > positivos:
            return "negativo"
        else:
            return "equilibrado"
    
    def _gerar_recomendacoes_correcao(self, balanco: Dict[str, float], 
                                     entradas: Dict[str, float],
                                     saidas: Dict[str, float]) -> List[str]:
        """Gerar recomendações de correção."""
        recomendacoes = []
        
        for nutriente, valor_balanco in balanco.items():
            if valor_balanco < -10:  # Deficiência significativa
                recomendacoes.append(f"{nutriente}: deficiência significativa, considerar adição")
            elif valor_balanco > 10:  # Excesso significativo
                recomendacoes.append(f"{nutriente}: excesso, considerar redução ou diluição")
        
        return recomendacoes
    
    def _interpretar_resultados(self, macronutrientes: Dict[str, Any], 
                               micronutrientes: Dict[str, Any],
                               balanco_nutricional: BalancoNutricional) -> str:
        """Interpretar resultados da análise nutricional."""
        interpretacao = []
        
        # Analisar CE
        if "no3_mg_L" in macronutrientes and macronutrientes["no3_mg_L"]:
            ce_stats = macronutrientes["no3_mg_L"]
            interpretacao.append(f"CE média: {ce_stats['media']:.2f} dS/m")
            
            if ce_stats['media'] < self.config_calculo.limites_ce["min_ideal"]:
                interpretacao.append("CE abaixo do ideal: pode indicar deficiência de nutrientes")
            elif ce_stats['media'] > self.config_calculo.limites_ce["max_ideal"]:
                interpretacao.append("CE acima do ideal: pode indicar salinização")
        
        # Analisar pH
        if "ph" in macronutrientes and macronutrientes["ph"]:
            ph_stats = macronutrientes["ph"]
            interpretacao.append(f"pH médio: {ph_stats['media']:.2f}")
            
            if ph_stats['media'] < self.config_calculo.limites_ph["min_ideal"]:
                interpretacao.append("pH ácido: pode limitar disponibilidade de nutrientes")
            elif ph_stats['media'] > self.config_calculo.limites_ph["max_ideal"]:
                interpretacao.append("pH alcalino: pode causar deficiência de micronutrientes")
        
        # Analisar balanço geral
        interpretacao.append(f"Balanço nutricional: {balanco_nutricional.status_balanco}")
        
        if balanco_nutricional.status_balanco == "negativo":
            interpretacao.append("Balanço negativo: necessidade de correção de nutrientes")
        elif balanco_nutricional.status_balanco == "positivo":
            interpretacao.append("Balanço positivo: excesso de nutrientes, monitorar possível lixiviação")
        
        return " | ".join(interpretacao)
    
    def _gerar_recomendacao_pH(self, leituras: List[LeituraSolucao], 
                              config_agronomia: ConfigAgronomiaFertirrigacao) -> Optional[str]:
        """Gerar recomendação de pH."""
        ph_valores = [l.ph for l in leituras if l.ph is not None]
        
        if not ph_valores:
            return None
        
        ph_media = np.mean(ph_valores)
        
        if ph_media < config_agronomia.objetivo_pH_min:
            return "pH ácido: recomenda-se correção com calcário ou outras fontes de cálcio"
        elif ph_media > config_agronomia.objetivo_pH_max:
            return "pH alcalino: recomenda-se acidificação com ácido sulfúrico ou outros ácidos"
        else:
            return "pH dentro da faixa ideal para a cultura"
    
    def _identificar_pontos_criticos(self, leituras: List[LeituraSolucao], 
                                    config_agronomia: ConfigAgronomiaFertirrigacao) -> List[str]:
        """Identificar pontos críticos nas leituras."""
        pontos_criticos = []
        
        for leitura in leituras:
            # Verificar CE
            if leitura.ce_ds_m > self.config_calculo.limites_ce["max_critico"]:
                pontos_criticos.append(f"Ponto {leitura.ponto_id}: CE crítica ({leitura.ce_ds_m} dS/m)")
            
            # Verificar pH
            if leitura.ph is not None:
                if leitura.ph < self.config_calculo.limites_ph["min_critico"]:
                    pontos_criticos.append(f"Ponto {leitura.ponto_id}: pH crítica ({leitura.ph})")
                elif leitura.ph > self.config_calculo.limites_ph["max_critico"]:
                    pontos_criticos.append(f"Ponto {leitura.ponto_id}: pH crítica ({leitura.ph})")
            
            # Verificar nutrientes
            for nutriente in ["no3_mg_L", "k_mg_L", "ca_mg_L"]:
                if hasattr(leitura, nutriente) and getattr(leitura, nutriente) is not None:
                    valor = getattr(leitura, nutriente)
                    limites = self.config_calculo.limites_nutrientes.get(nutriente, {})
                    
                    if "max_critico" in limites and valor > limites["max_critico"]:
                        pontos_criticos.append(f"Ponto {leitura.ponto_id}: {nutriente} crítica ({valor} mg/L)")
        
        return pontos_criticos
    
    def _carregar_curvas_nutritivas(self) -> Dict[str, CurvaNutritiva]:
        """Carregar curvas nutritivas de referência."""
        # Simplificado - na prática carregaria de banco de dados ou arquivos
        curvas = {}
        
        # Curva para tomate em fase vegetativa
        curvas["tomate_vegetativo"] = CurvaNutritiva(
            cultura="tomate",
            fase_fenologica="vegetativo",
            limites_ce={"min_ideal": 1.5, "max_ideal": 2.5, "min_critico": 1.0, "max_critico": 4.0},
            limites_ph={"min_ideal": 6.0, "max_ideal": 6.8, "min_critico": 5.5, "max_critico": 7.5},
            limites_nutrientes={
                "no3_mg_L": {"min_ideal": 100, "max_ideal": 200, "min_critico": 50, "max_critico": 300},
                "k_mg_L": {"min_ideal": 100, "max_ideal": 150, "min_critico": 50, "max_critico": 250},
                "ca_mg_L": {"min_ideal": 100, "max_ideal": 200, "min_critico": 60, "max_critico": 300},
                "mg_mg_L": {"min_ideal": 40, "max_ideal": 80, "min_critico": 20, "max_critico": 120}
            },
            faixas_seguranca={
                "no3_mg_L": {"min_seguro": 70, "max_seguro": 250},
                "k_mg_L": {"min_seguro": 80, "max_seguro": 180},
                "ca_mg_L": {"min_seguro": 80, "max_seguro": 250},
                "mg_mg_L": {"min_seguro": 30, "max_seguro": 100}
            }
        )
        
        return curvas