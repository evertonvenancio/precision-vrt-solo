"""
Precision VRT Solo — Módulo de Comparação Temporal

Implementa funcionalidades para comparação temporal de imagens,
detecção de mudanças e análise de evolução temporal.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging

from core.tipos.base import ConfigBase
from ..contratos import (
    ImagemMonitoramento,
    SerieTemporalVigor,
    AnomaliaMonitoramento,
    ResultadoComparacao,
    ConfigComparacaoTemporal,
    TipoIntervalo,
    TipoComparacao
)

logger = logging.getLogger(__name__)


class AnalisadorComparacao:
    """
    Analisa e compara imagens ao longo do tempo.
    """
    
    def __init__(self):
        self.resultados_comparacao: List[ResultadoComparacao] = []
        self.anomalias_detectadas: List[AnomaliaMonitoramento] = []
        
    def comparar_series(self, serie_base: SerieTemporalVigor, 
                       serie_comparada: SerieTemporalVigor,
                       config: ConfigComparacaoTemporal) -> ResultadoComparacao:
        """
        Compara duas séries temporais de vigor.
        
        Args:
            serie_base: Série temporal de referência
            serie_comparada: Série temporal para comparação
            config: Configuração da comparação
            
        Returns:
            Resultado da comparação
        """
        # Calcular estatísticas comparativas
        anomalias = []
        estatisticas_comparacao = {}
        
        for indice in serie_base.valores_medios:
            if indice in serie_comparada.valores_medios:
                valores_base = serie_base.valores_medios[indice]
                valores_comparada = serie_comparada.valores_medios[indice]
                
                # Verificar se temos pontos suficientes
                if len(valores_base) >= 2 and len(valores_comparada) >= 2:
                    
                    # Calcular diferença média
                    diff_medio = np.mean(valores_comparada) - np.mean(valores_base)
                    desvio_diff = np.std(valores_comparada) - np.std(valores_base)
                    percentual_diff = (diff_medio / np.mean(valores_base)) * 100 if np.mean(valores_base) != 0 else 0
                    
                    # Detectar anomalias
                    if abs(percentual_diff) > config.limite_tolerancia_desvio * 100:
                        tipo = 'positiva' if percentual_diff > 0 else 'negativa'
                        severidade = self._classificar_severidade(abs(percentual_diff))
                        
                        anomalia = AnomaliaMonitoramento(
                            zona_id=serie_base.zona_id,
                            data=serie_comparada.datas[-1] if serie_comparada.datas else datetime.now().isoformat(),
                            indice=indice,
                            valor_observado=np.mean(valores_comparada),
                            valor_esperado=np.mean(valores_base),
                            desvio_percentual=percentual_diff,
                            tipo=tipo,
                            severidade=severidade,
                            possiveis_causas=self._inferir_causas_comparacao(tipo, severidade, indice),
                            contexto={
                                'serie_base': serie_base,
                                'serie_comparada': serie_comparada,
                                'diferencia_absoluta': diff_medio,
                                'variacao_desvio': desvio_diff
                            }
                        )
                        anomalias.append(anomalia)
                        self.anomalias_detectadas.append(anomalia)
                    
                    # Estatísticas da comparação
                    estatisticas_comparacao[indice] = {
                        'media_base': np.mean(valores_base),
                        'media_comparada': np.mean(valores_comparada),
                        'diferencia_media': diff_medio,
                        'diferencia_percentual': percentual_diff,
                        'desvio_base': np.std(valores_base),
                        'desvio_comparada': np.std(valores_comparada),
                        'variacao_desvio': desvio_diff,
                        'correlacao': np.corrcoef(valores_base, valores_comparada)[0, 1] if len(valores_base) > 1 else 0
                    }
        
        # Calcular intervalo em dias
        if serie_base.datas and serie_comparada.datas:
            data_inicio = datetime.fromisoformat(serie_base.datas[0])
            data_fim = datetime.fromisoformat(serie_comparada.datas[-1])
            intervalo_dias = (data_fim - data_inicio).days
        else:
            intervalo_dias = 0
        
        # Criar resultado da comparação
        resultado = ResultadoComparacao(
            imagem_base_id=f"serie_{serie_base.zona_id}",
            imagem_comparada_id=f"serie_{serie_comparada.zona_id}",
            intervalo_dias=intervalo_dias,
            indice_analisado=config.indice_padrao.value,
            diferenca_media=np.mean([stats['diferencia_media'] for stats in estatisticas_comparacao.values()]),
            diferenca_maxima=max([stats['diferencia_percentual'] for stats in estatisticas_comparacao.values()], default=0),
            diferenca_minima=min([stats['diferencia_percentual'] for stats in estatisticas_comparacao.values()], default=0),
            areas_mudancas={'total_anomalias': len(anomalias)},
            estatisticas=estatisticas_comparacao,
            anomalias_detectadas=anomalias,
            data_comparacao=datetime.now().isoformat()
        )
        
        self.resultados_comparacao.append(resultado)
        return resultado
    
    def detectar_tendencias(self, serie_temporal: SerieTemporalVigor, 
                           indice: str) -> Dict[str, Any]:
        """
        Detecta tendências em uma série temporal.
        
        Args:
            serie_temporal: Série temporal para análise
            indice: Índice a ser analisado
            
        Returns:
            Informações sobre a tendência detectada
        """
        if indice not in serie_temporal.valores_medios:
            return {'tendencia': 'nao_disponivel', 'mensagem': f'Índice {indice} não encontrado na série'}
        
        valores = serie_temporal.valores_medios[indice]
        
        if len(valores) < 3:
            return {'tendencia': 'dados_insuficientes', 'mensagem': 'Poucos dados para análise de tendência'}
        
        # Cálculo da tendência (simples linear regression)
        x = np.arange(len(valores))
        y = np.array(valores)
        
        # Calcular inclinação da linha de tendência
        inclinacao = np.polyfit(x, y, 1)[0]
        
        # Classificar tendência
        if abs(inclinacao) < 0.01:
            tendencia = 'estavel'
        elif inclinacao > 0:
            tendencia = 'crescente'
        else:
            tendencia = 'decrescente'
        
        # Intensidade da tendência
        intensidade = 'leve' if abs(inclinacao) < 0.05 else 'moderada' if abs(inclinacao) < 0.1 else 'forte'
        
        return {
            'tendencia': tendencia,
            'intensidade': intensidade,
            'inclinacao': float(inclinacao),
            'media_final': float(np.mean(valores[-3:])),  # Média dos últimos 3 pontos
            'media_inicial': float(np.mean(valores[:3])),  # Média dos primeiros 3 pontos
            'variacao_total': float((valores[-1] - valores[0]) / valores[0] * 100) if valores[0] != 0 else 0,
            'volatilidade': float(np.std(valores))
        }
    
    def _classificar_severidade(self, percentual_diff: float) -> str:
        """
        Classifica a severidade da anomalia baseado na variação percentual.
        
        Args:
            percentual_diff: Variação percentual
            
        Returns:
            Nível de severidade
        """
        if abs(percentual_diff) > 300:
            return 'grave'
        elif abs(percentual_diff) > 200:
            return 'moderada'
        else:
            return 'leve'
    
    def _inferir_causas_comparacao(self, tipo: str, severidade: str, indice: str) -> List[str]:
        """
        Infere possíveis causas baseado na comparação.
        
        Args:
            tipo: Tipo de mudança (positiva/negativa)
            severidade: Nível de severidade
            indice: Índice analisado
            
        Returns:
            Lista de possíveis causas
        """
        causas = []
        
        if tipo == 'negativa':
            causas.extend([
                'Déficit hídrico',
                'Estresse nutricional', 
                'Problemas fitossanitários',
                'Condições climáticas adversas',
                'Compactação do solo'
            ])
            
            if indice == 'NDVI':
                causas.append('Redução da atividade fotossintética')
            elif indice in ['NDWI', 'NDSI']:
                causas.append('Aumento da cobertura de água ou gelo')
                
        else:  # positiva
            causas.extend([
                'Melhoria na condição hídrica',
                'Aplicação de fertilizantes',
                'Melhora na saúde do solo',
                'Condições climáticas favoráveis',
                'Controle de pragas/doenças'
            ])
        
        if severidade == 'grave':
            causas.append('Requer atenção técnica imediata')
        
        return causas


class AgrupadorTemporal:
    """
    Agrupa dados por intervalos temporais.
    """
    
    def agrupar_por_intervalo(self, imagens: List[ImagemMonitoramento],
                               intervalo: TipoIntervalo) -> Dict[str, List[ImagemMonitoramento]]:
        """
        Agrupa imagens por intervalo temporal.
        
        Args:
            imagens: Lista de imagens
            intervalo: Tipo de intervalo
            
        Returns:
            Dicionário com imagens agrupadas
        """
        agrupadas = {}
        
        for imagem in imagens:
            data_obj = datetime.fromisoformat(imagem.data_captura)
            
            if intervalo == TipoIntervalo.DIA:
                chave = data_obj.strftime('%Y-%m-%d')
            elif intervalo == TipoIntervalo.SEMANA:
                chave = f"{data_obj.year}-S{data_obj.strftime('%U')}"
            elif intervalo == TipoIntervalo.MES:
                chave = data_obj.strftime('%Y-%m')
            elif intervalo == TipoIntervalo.SAFRA:
                chave = f"{data_obj.year if data_obj.month >= 7 else data_obj.year - 1}-{data_obj.year}"
            elif intervalo == TipoIntervalo.ANO:
                chave = str(data_obj.year)
            else:
                chave = data_obj.strftime('%Y-%m')
            
            if chave not in agrupadas:
                agrupadas[chave] = []
            agrupadas[chave].append(imagem)
        
        return agrupadas
    
    def calcular_intervalos_temporais(self, datas: List[str]) -> Dict[str, Any]:
        """
        Calcula estatísticas sobre intervalos temporais.
        
        Args:
            datas: Lista de datas em formato ISO
            
        Returns:
            Estatísticas dos intervalos
        """
        if len(datas) < 2:
            return {'intervalos': [], 'media_dias': 0, 'desvio_dias': 0}
        
        # Converter para objetos datetime
        datas_obj = [datetime.fromisoformat(data) for data in datas]
        datas_obj.sort()
        
        # Calcular intervalos em dias
        intervalos = []
        for i in range(1, len(datas_obj)):
            delta = datas_obj[i] - datas_obj[i-1]
            intervalos.append(delta.days)
        
        return {
            'intervalos': intervalos,
            'media_dias': float(np.mean(intervalos)),
            'desvio_dias': float(np.std(intervalos)),
            'minimo_dias': min(intervalos),
            'maximo_dios': max(intervalos),
            'mediana_dias': float(np.median(intervalos))
        }


class GerenciadorAlertas:
    """
    Gerencia alertas baseados em comparações temporais.
    """
    
    def __init__(self):
        self.alertas_configurados: List[Dict] = []
        self.alertas_disparados: List[Dict] = []
    
    def configurar_alerta(self, tipo_alerta: str, condicao: str, 
                         limite_inferior: Optional[float] = None,
                         limite_superior: Optional[float] = None,
                         severidade: str = 'moderada') -> bool:
        """
        Configura um novo alerta.
        
        Args:
            tipo_alerta: Tipo de alerta
            condicao: Condição do alerta
            limite_inferior: Limite inferior (opcional)
            limite_superior: Limite superior (opcional)
            severidade: Nível de severidade
            
        Returns:
            True se configurado com sucesso
        """
        alerta = {
            'tipo_alerta': tipo_alerta,
            'condicao': condicao,
            'limite_inferior': limite_inferior,
            'limite_superior': limite_superior,
            'severidade': severidade,
            'ativo': True,
            'data_configuracao': datetime.now().isoformat(),
            'historico_disparos': []
        }
        
        self.alertas_configurados.append(alerta)
        return True
    
    def verificar_alertas(self, anomalias: List[AnomaliaMonitoramento]) -> List[Dict]:
        """
        Verifica anomalias em relação aos alertas configurados.
        
        Args:
            anomalias: Lista de anomalias detectadas
            
        Returns:
            Lista de alertas disparados
        """
        alertas_disparados = []
        
        for alerta in self.alertas_configurados:
            if not alerta['ativo']:
                continue
            
            for anomalia in anomalias:
                # Verificar se a anomalia atende aos critérios do alerta
                if alerta['tipo_alerta'] == anomalia.tipo and alerta['condicao'] == anomalia.severidade:
                    if alerta['limite_inferior'] is not None and anomalia.desvio_percentual < alerta['limite_inferior']:
                        continue
                    if alerta['limite_superior'] is not None and anomalia.desvio_percentual > alerta['limite_superior']:
                        continue
                    
                    # Disparar alerta
                    alerta_disparado = {
                        'tipo_alerta': alerta['tipo_alerta'],
                        'condicao': alerta['condicao'],
                        'anomalia': anomalia,
                        'data_disparo': datetime.now().isoformat(),
                        'severidade': alerta['severidade'],
                        'mensagem': self._gerar_mensagem_alerta(anomalia, alerta)
                    }
                    
                    alertas_disparados.append(alerta_disparado)
                    alerta['historico_disparos'].append(alerta_disparado)
                    self.alertas_disparados.append(alerta_disparado)
        
        return alertas_disparados
    
    def _gerar_mensagem_alerta(self, anomalia: AnomaliaMonitoramento, 
                               alerta: Dict) -> str:
        """
        Gera mensagem para o alerta.
        
        Args:
            anomalia: Anomalia que disparou o alerta
            alerta: Alerta configurado
            
        Returns:
            Mensagem formatada
        """
        tipo_desc = "aumento" if anomalia.tipo == "positiva" else "redução"
        
        mensagem = f"Alerta de {alerta['tipo_alerta']}: {tipo_desc} de {anomalia.indice} "
        mensagem += f"em {anomalia.desvio_percentual:.2f}% ({anomalia.severidade})"
        
        return mensagem
    
    def obter_alertas_disponiveis(self) -> List[Dict]:
        """
        Lista todos os alertas disponíveis.
        
        Returns:
            Lista de alertas
        """
        return self.alertas_configurados
    
    def obter_historico_alertas(self, tipo_alerta: Optional[str] = None) -> List[Dict]:
        """
        Obtém histórico de alertas disparados.
        
        Args:
            tipo_alerta: Tipo específico de alerta (opcional)
            
        Returns:
            Lista de alertas disparados
        """
        if tipo_alerta:
            return [alerta for alerta in self.alertas_disparados 
                   if alerta['tipo_alerta'] == tipo_alerta]
        return self.alertas_disparados