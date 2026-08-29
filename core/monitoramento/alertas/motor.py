"""
Precision VRT Solo — Módulo de Alertas

Implementa sistema de alertas para monitoramento.
Prepara arquitetura para futuramente identificar possíveis deficiências,
pragas, doenças, falhas e estresses.
"""

import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from core.tipos.base import ConfigBase
from ..contratos import AnomaliaMonitoramento, ConfigAlerta

logger = logging.getLogger(__name__)


class TipoAlerta(Enum):
    """Tipos de alertas suportados."""
    VIGOR_REDUZIDO = "vigor_reduzido"
    VIGOR_AUMENTADO = "vigor_aumentado"
    VARIAÇÃO_ESPECTRAL = "variacao_espectral"
    PADRÃO_ANORMAL = "padrao_anormal"
    DEFICIÊNCIA_NUTRICIONAL = "deficiencia_nutricional"
    ATIVIDADE_PRAGAS = "atividade_pragas"
    DOENças_SUSPEITAS = "doencas_suspeitas"
    ESTRESSE_HIDRICO = "estresse_hidrico"
    ESTRESSE_NUTRICIONAL = "estresse_nutricional"
    FALHA_EQUIPAMENTO = "falha_equipamento"
    CONDIÇÕES_CLIMATICAS = "condicoes_climaticas"


class SeveridadeAlerta(Enum):
    """Níveis de severidade dos alertas."""
    BAIXA = "baixa"
    MODERADA = "moderada"
    ALTA = "alta"
    CRITICA = "critica"


class CanalNotificacao(Enum):
    """Canais de notificação disponíveis."""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    SISTEMA = "sistema"
    APP_MÓVEL = "app_movil"


@dataclass
class AlertaConfigurado:
    """Alerta configurado pelo usuário."""
    
    alerta_id: str
    tipo_alerta: TipoAlerta
    condicao: str
    severidade: SeveridadeAlerta
    limiar_inferior: Optional[float] = None
    limiar_superior: Optional[float] = None
    ativo: bool = True
    canais_notificacao: List[CanalNotificacao] = field(default_factory=list)
    frequencia_disparo: str = "24h"  # Intervalo mínimo entre disparos
    regra_agrupamento: str = "por_tipo"  # Agrupamento de alertas similares
    acoes_automáticas: List[str] = field(default_factory=list)
    historico_disparos: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class AlertaDisparado:
    """Alerta que foi disparado."""
    
    alerta_id: str
    tipo_alerta: TipoAlerta
    severidade: SeveridadeAlerta
    mensagem: str
    contexto: Dict[str, Any]
    anomalias_relacionadas: List[AnomaliaMonitoramento]
    data_disparo: str
    canais_acionados: List[CanalNotificacao]
    status: str = "disparado"
    acoes_realizadas: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=list)


class ConfiguradorAlertas:
    """
    Configura alertas para diferentes cenários de monitoramento.
    """
    
    def __init__(self):
        self.alertas_configurados: List[AlertaConfigurado] = []
        self.padroes_predefinidos: Dict[TipoAlerta, List[AlertaConfigurado]] = {}
        self._carregar_padroes_predefinidos()
    
    def _carregar_padroes_predefinidos(self):
        """Carrega padrões predefinidos de alertas."""
        
        # Alerta de vigor reduzido
        self.padroes_predefinidos[TipoAlerta.VIGOR_REDUZIDO] = [
            AlertaConfigurado(
                alerta_id="vigor_reduzido_leve",
                tipo_alerta=TipoAlerta.VIGOR_REDUZIDO,
                condicao="NDVI < 0.3",
                severidade=SeveridadeAlerta.MODERADA,
                limiar_inferior=0.0,
                limiar_superior=0.3,
                canais_notificacao=[CanalNotificacao.SISTEMA],
                acoes_automáticas=["notificar_tecnico"]
            ),
            AlertaConfigurado(
                alerta_id="vigor_reduzido_critico", 
                tipo_alerta=TipoAlerta.VIGOR_REDUZIDO,
                condicao="NDVI < 0.1",
                severidade=SeveridadeAlerta.CRITICA,
                limiar_inferior=0.0,
                limiar_superior=0.1,
                canais_notificacao=[CanalNotificacao.EMAIL, CanalNotificacao.SISTEMA],
                acoes_automáticas=["notificar_emergencia", "gerar_relatorio"]
            )
        ]
        
        # Alerta de variação espectral anormal
        self.padroes_predefinidos[TipoAlerta.VARIAÇÃO_ESPECTRAL] = [
            AlertaConfigurado(
                alerta_id="variacao_espectral_suspeita",
                tipo_alerta=TipoAlerta.VARIAÇÃO_ESPECTRAL,
                condicao="diferencia_percentual > 50%",
                severidade=SeveridadeAlerta.ALTA,
                limiar_superior=50.0,
                canais_notificacao=[CanalNotificacao.SISTEMA],
                acoes_automáticas=["marcar_para_investigacao"]
            )
        ]
        
        # Alerta de estresse hídrico
        self.padroes_predefinidos[TipoAlerta.ESTRESSE_HIDRICO] = [
            AlertaConfigurado(
                alerta_id="estresse_hidrico_suspeitado",
                tipo_alerta=TipoAlerta.ESTRESSE_HIDRICO,
                condicao="NDWI < -0.2",
                severidade=SeveridadeAlerta.ALTA,
                limiar_inferior=None,
                limiar_superior=-0.2,
                canais_notificacao=[CanalNotificacao.SISTEMA, CanalNotificacao.EMAIL],
                acoes_automáticas=["recomendar_irrigacao", "gerar_mapa_estresse"]
            )
        ]
    
    def configurar_alerta_personalizado(self, 
                                      tipo_alerta: TipoAlerta,
                                      condicao: str,
                                      severidade: SeveridadeAlerta,
                                      limiar_inferior: Optional[float] = None,
                                      limiar_superior: Optional[float] = None,
                                      canais_notificacao: List[CanalNotificacao] = None,
                                      acoes_automáticas: List[str] = None,
                                      alerta_id: Optional[str] = None) -> AlertaConfigurado:
        """
        Configura um alerta personalizado.
        
        Args:
            tipo_alerta: Tipo do alerta
            condicao: Condição do alerta
            severidade: Severidade do alerta
            limiar_inferior: Limiar inferior (opcional)
            limiar_superior: Limiar superior (opcional)
            canais_notificacao: Canais de notificação
            acoes_automáticas: Ações automáticas a serem executadas
            alerta_id: ID personalizado do alerta
            
        Returns:
            Alerta configurado
        """
        if canais_notificacao is None:
            canais_notificacao = [CanalNotificacao.SISTEMA]
        
        if acoes_automáticas is None:
            acoes_automáticas = ["notificar_tecnico"]
        
        if alerta_id is None:
            alerta_id = f"{tipo_alerta.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        alerta = AlertaConfigurado(
            alerta_id=alerta_id,
            tipo_alerta=tipo_alerta,
            condicao=condicao,
            severidade=severidade,
            limiar_inferior=limiar_inferior,
            limiar_superior=limiar_superior,
            canais_notificacao=canais_notificacao,
            acoes_automáticas=acoes_automáticas
        )
        
        self.alertas_configurados.append(alerta)
        logger.info(f"Alerta personalizado configurado: {alerta_id}")
        
        return alerta
    
    def aplicar_padrao_alerta(self, tipo_alerta: TipoAlerta, 
                              variantes: List[str] = None) -> List[AlertaConfigurado]:
        """
        Aplica padrões predefinidos de alertas.
        
        Args:
            tipo_alerta: Tipo de alerta
            variantes: Variantes específicas do padrão
            
        Returns:
            Lista de alertas configurados
        """
        alertas_aplicados = []
        
        if tipo_alerta in self.padroes_predefinidos:
            padroes = self.padroes_predefinidos[tipo_alerta]
            
            for padrao in padroes:
                if variantes and padrao.alerta_id not in variantes:
                    continue
                    
                # Copiar e configurar o padrão
                alerta_copiado = AlertaConfigurado(
                    alerta_id=padrao.alerta_id,
                    tipo_alerta=padrao.tipo_alerta,
                    condicao=padrao.condicao,
                    severidade=padrao.severidade,
                    limiar_inferior=padrao.limiar_inferior,
                    limiar_superior=padrao.limiar_superior,
                    canais_notificacao=padrao.canais_notificacao.copy(),
                    acoes_automáticas=padrao.acoes_automáticas.copy(),
                    frequencia_disparo=padrao.frequencia_disparo,
                    regra_agrupamento=padrao.regra_agrupamento
                )
                
                self.alertas_configurados.append(alerta_copiado)
                alertas_aplicados.append(alerta_copiado)
                
                logger.info(f"Padrão de alerta aplicado: {padrao.alerta_id}")
        
        return alertas_aplicados
    
    def listar_alertas_configurados(self, tipo_alerta: Optional[TipoAlerta] = None) -> List[AlertaConfigurado]:
        """
        Lista alertas configurados.
        
        Args:
            tipo_alerta: Tipo específico de alerta (opcional)
            
        Returns:
            Lista de alertas configurados
        """
        if tipo_alerta:
            return [alerta for alerta in self.alertas_configurados 
                   if alerta.tipo_alerta == tipo_alerta and alerta.ativo]
        return [alerta for alerta in self.alertas_configurados if alerta.ativo]
    
    def modificar_alerta(self, alerta_id: str, **kwargs) -> bool:
        """
        Modifica alerta existente.
        
        Args:
            alerta_id: ID do alerta a ser modificado
            **kwargs: Novos valores para os campos
            
        Returns:
            True se modificado com sucesso
        """
        for alerta in self.alertas_configurados:
            if alerta.alerta_id == alerta_id:
                for campo, valor in kwargs.items():
                    if hasattr(alerta, campo):
                        setattr(alerta, campo, valor)
                logger.info(f"Alerta modificado: {alerta_id}")
                return True
        
        logger.warning(f"Alerta não encontrado: {alerta_id}")
        return False
    
    def desativar_alerta(self, alerta_id: str) -> bool:
        """
        Desativa alerta configurado.
        
        Args:
            alerta_id: ID do alerta a ser desativado
            
        Returns:
            True se desativado com sucesso
        """
        return self.modificar_alerta(alerta_id, ativo=False)
    
    def ativar_alerta(self, alerta_id: str) -> bool:
        """
        Ativa alerta desativado.
        
        Args:
            alerta_id: ID do alerta a ser ativado
            
        Returns:
            True se ativado com sucesso
        """
        return self.modificar_alerta(alerta_id, ativo=True)


class DisparadorAlertas:
    """
    Dispara alertas baseados em anomalias detectadas.
    """
    
    def __init__(self, configurador: ConfiguradorAlertas):
        self.configurador = configurador
        self.alertas_disparados: List[AlertaDisparado] = []
        self.ultimo_disparo_por_tipo: Dict[TipoAlerta, Dict[str, str]] = {}
    
    def verificar_alertas(self, anomalias: List[AnomaliaMonitoramento]) -> List[AlertaDisparado]:
        """
        Verifica anomalias e dispara alertas correspondentes.
        
        Args:
            anomalias: Lista de anomalias detectadas
            
        Returns:
            Lista de alertas disparados
        """
        alertas_disparados = []
        
        for anomalia in anomalias:
            # Identificar tipo de alerta baseado na anomalia
            tipo_alerta = self._identificar_tipo_alerta(anomalia)
            
            if tipo_alerta:
                # Obter alertas configurados para este tipo
                alertas_config = self.configurador.listar_alertas_configurados(tipo_alerta)
                
                for alerta in alertas_config:
                    if self._verificar_condicao_alerta(alerta, anomalia):
                        alerta_disparado = self._disparar_alerta(alerta, anomalia)
                        if alerta_disparado:
                            alertas_disparados.append(alerta_disparado)
        
        return alertas_disparados
    
    def _identificar_tipo_alerta(self, anomalia: AnomaliaMonitoramento) -> Optional[TipoAlerta]:
        """
        Identifica tipo de alerta baseado na anomalia.
        
        Args:
            anomalia: Anomalia detectada
            
        Returns:
            Tipo de alerta correspondente
        """
        if anomalia.indice == "NDVI":
            if anomalia.tipo == "negativa":
                if anomalia.desvio_percentual < -50:
                    return TipoAlerta.VIGOR_REDUZIDO
                elif anomalia.desvio_percentual < -20:
                    return TipoAlerta.ESTRESSE_HIDRICO
            else:
                if anomalia.desvio_percentual > 50:
                    return TipoAlerta.VIGOR_AUMENTADO
        
        elif anomalia.indice == "NDWI":
            if anomalia.tipo == "negativa":
                return TipoAlerta.ESTRESSE_HIDRICO
            else:
                return TipoAlerta.VARIAÇÃO_ESPECTRAL
        
        elif abs(anomalia.desvio_percentual) > 100:
            return TipoAlerta.VARIAÇÃO_ESPECTRAL
        
        return None
    
    def _verificar_condicao_alerta(self, alerta: AlertaConfigurado, 
                                 anomalia: AnomaliaMonitoramento) -> bool:
        """
        Verifica se anomalia atende à condição do alerta.
        
        Args:
            alerta: Alerta configurado
            anomalia: Anomalia detectada
            
        Returns:
            True se condição é atendida
        """
        # Verificar limiares
        if alerta.limiar_inferior is not None:
            if anomalia.desvio_percentual >= alerta.limiar_inferior:
                return False
        
        if alerta.limiar_superior is not None:
            if anomalia.desvio_percentual <= alerta.limiar_superior:
                return False
        
        # Verificar frequência de disparo
        if not self._pode_disparar(alerta, anomalia):
            return False
        
        return True
    
    def _pode_disparar(self, alerta: AlertaConfigurado, 
                      anomalia: AnomaliaMonitoramento) -> bool:
        """
        Verifica se pode disparar alerta baseado na frequência.
        
        Args:
            alerta: Alerta configurado
            anomalia: Anomalia detectada
            
        Returns:
            True se pode disparar
        """
        chave_disparo = f"{alerta.alerta_id}_{anomalia.zona_id}"
        
        if chave_disparo in self.ultimo_disparo_por_tipo.get(alerta.tipo_alerta, {}):
            ultimo_disparo = self.ultimo_disparo_por_tipo[alerta.tipo_alerta][chave_disparo]
            delta_anterior = datetime.now() - datetime.fromisoformat(ultimo_disparo)
            
            # Converter frequência para timedelta
            frequencia = alerta.frequencia_disparo
            if frequencia == "1h":
                delta_max = timedelta(hours=1)
            elif frequencia == "6h":
                delta_max = timedelta(hours=6)
            elif frequencia == "12h":
                delta_max = timedelta(hours=12)
            elif frequencia == "24h":
                delta_max = timedelta(days=1)
            elif frequencia == "48h":
                delta_max = timedelta(days=2)
            else:
                delta_max = timedelta(days=1)  # padrão
            
            if delta_anterior < delta_max:
                return False
        
        return True
    
    def _disparar_alerta(self, alerta: AlertaConfigurado, 
                        anomalia: AnomaliaMonitoramento) -> Optional[AlertaDisparado]:
        """
        Dispara alerta.
        
        Args:
            alerta: Alerta configurado
            anomalia: Anomalia relacionada
            
        Returns:
            Alerta disparado ou None se não puder disparar
        """
        chave_disparo = f"{alerta.alerta_id}_{anomalia.zona_id}"
        
        # Registrar disparo
        if alerta.tipo_alerta not in self.ultimo_disparo_por_tipo:
            self.ultimo_disparo_por_tipo[alerta.tipo_alerta] = {}
        
        self.ultimo_disparo_por_tipo[alerta.tipo_alerta][chave_disparo] = datetime.now().isoformat()
        
        # Adicionar ao histórico do alerta
        disparo_info = {
            'data_disparo': datetime.now().isoformat(),
            'anomalia': anomalia,
            'canais_acionados': alerta.canais_notificacao.copy(),
            'acoes_realizadas': alerta.acoes_automáticas.copy()
        }
        alerta.historico_disparos.append(disparo_info)
        
        # Criar alerta disparado
        alerta_disparado = AlertaDisparado(
            alerta_id=alerta.alerta_id,
            tipo_alerta=alerta.tipo_alerta,
            severidade=alerta.severidade,
            mensagem=self._gerar_mensagem_alerta(alerta, anomalia),
            contexto={
                'condicao': alerta.condicao,
                'anomalia': anomalia,
                'limite_superior': alerta.limiar_superior,
                'limite_inferior': alerta.limiar_inferior
            },
            anomalias_relacionadas=[anomalia],
            data_disparo=datetime.now().isoformat(),
            canais_acionados=alerta.canais_notificacao.copy(),
            acoes_realizadas=alerta.acoes_automáticas.copy()
        )
        
        self.alertas_disparados.append(alerta_disparado)
        
        logger.info(f"Alerta disparado: {alerta.alerta_id} - {alerta_disparado.mensagem}")
        
        return alerta_disparado
    
    def _gerar_mensagem_alerta(self, alerta: AlertaConfigurado, 
                              anomalia: AnomaliaMonitoramento) -> str:
        """
        Gera mensagem formatada para o alerta.
        
        Args:
            alerta: Alerta configurado
            anomalia: Anomalia relacionada
            
        Returns:
            Mensagem formatada
        """
        tipo_desc = {
            TipoAlerta.VIGOR_REDUZIDO: "Vigor Reduzido",
            TipoAlerta.VIGOR_AUMENTADO: "Vigor Aumentado", 
            TipoAlerta.VARIAÇÃO_ESPECTRAL: "Variação Espectral",
            TipoAlerta.PADRÃO_ANORMAL: "Padrão Anormal",
            TipoAlerta.DEFICIÊNCIA_NUTRICIONAL: "Deficiência Nutricional",
            TipoAlerta.ATIVIDADE_PRAGAS: "Atividade de Pragas",
            TipoAlerta.DOENÇAS_SUSPEITAS: "Doenças Suspeitas",
            TipoAlerta.ESTRESSE_HIDRICO: "Estresse Hídrico",
            TipoAlerta.ESTRESSE_NUTRICIONAL: "Estresse Nutricional",
            TipoAlerta.FALHA_EQUIPAMENTO: "Falha de Equipamento",
            TipoAlerta.CONDIÇÕES_CLIMATICAS: "Condições Climáticas"
        }
        
        mensagem = f"[{alerta.severidade.value.upper()}] {tipo_desc.get(alerta.tipo_alerta, alerta.tipo_alerta.value)}\n"
        mensagem += f"Índice: {anomalia.indice} | Variação: {anomalia.desvio_percentual:.2f}%\n"
        mensagem += f"Anomalia: {anomalia.tipo} | Severidade: {anomalia.severidade}\n"
        mensagem += f"Zona: {anomalia.zona_id} | Data: {anomalia.data}\n"
        mensagem += f"Condição: {alerta.condicao}"
        
        return mensagem
    
    def obter_alertas_disponiveis(self) -> List[AlertaConfigurado]:
        """
        Obtém lista de alertas disponíveis para disparo.
        
        Returns:
            Lista de alertas disponíveis
        """
        return self.configurador.listar_alertas_configurados()
    
    def obter_historico_alertas(self, tipo_alerta: Optional[TipoAlerta] = None,
                               data_inicio: Optional[str] = None,
                               data_fim: Optional[str] = None) -> List[AlertaDisparado]:
        """
        Obtém histórico de alertas disparados.
        
        Args:
            tipo_alerta: Tipo específico de alerta (opcional)
            data_inicio: Data inicial para filtro (opcional)
            data_fim: Data final para filtro (opcional)
            
        Returns:
            Lista de alertas disparados
        """
        alertas_filtrados = self.alertas_disparados
        
        if tipo_alerta:
            alertas_filtrados = [a for a in alertas_filtrados if a.tipo_alerta == tipo_alerta]
        
        if data_inicio:
            alertas_filtrados = [a for a in alertas_filtrados if a.data_disparo >= data_inicio]
        
        if data_fim:
            alertas_filtrados = [a for a in alertas_filtrados if a.data_disparo <= data_fim]
        
        return alertas_filtrados


class GerenciadorAlertas:
    """
    Gerencia todo o sistema de alertas.
    """
    
    def __init__(self):
        self.configurador = ConfiguradorAlertas()
        self.disparador = DisparadorAlertas(self.configurador)
    
    def configurar_sistema_alertas(self, tipos_alerta: List[TipoAlerta] = None,
                                  alertas_personalizados: List[AlertaConfigurado] = None) -> bool:
        """
        Configura o sistema de alertas.
        
        Args:
            tipos_alerta: Tipos de alerta a serem habilitados
            alertas_personalizados: Alertas personalizados adicionais
            
        Returns:
            True se configurado com sucesso
        """
        if tipos_alerta:
            for tipo in tipos_alerta:
                self.configurador.aplicar_padrao_alerta(tipo)
        
        if alertas_personalizados:
            for alerta in alertas_personalizados:
                self.configurador.alertas_configurados.append(alerta)
        
        logger.info("Sistema de alertas configurado com sucesso")
        return True
    
    def processar_anomalias(self, anomalias: List[AnomaliaMonitoramento]) -> List[AlertaDisparado]:
        """
        Processa anomalias e dispara alertas correspondentes.
        
        Args:
            anomalias: Lista de anomalias detectadas
            
        Returns:
            Lista de alertas disparados
        """
        return self.disparador.verificar_alertas(anomalias)
    
    def obter_estatisticas_alertas(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do sistema de alertas.
        
        Returns:
            Estatísticas do sistema
        """
        return {
            'alertas_configurados': len(self.configurador.alertas_configurados),
            'alertas_disparados': len(self.disparador.alertas_disparados),
            'tipos_alertas_disponiveis': len(TipoAlerta),
            'tipos_alertas_ativos': len(set([a.tipo_alerta for a in self.configurador.alertas_configurados if a.ativo])),
            'canais_notificacao': list(set([canal for alerta in self.configurador.alertas_configurados 
                                           for canal in alerta.canais_notificacao])),
            'ultimos_disparos': self.disparador.alertas_disparados[-5:] if self.disparador.alertas_disparados else []
        }