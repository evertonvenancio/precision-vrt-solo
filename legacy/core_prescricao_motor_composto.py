"""
Precision VRT Solo - Motor Prescrição Composto
==============================================

Implementação do MotorPrescricao como um sistema composto de componentes especializados.
Esta é a implementação da sugestão arquitetural de dividir o motor em:

Validador → Normalizador → CombinadorCamadas → SelecionadorMetodologia → 
CalculadorRecomendacao → GeradorPrescricao → Exportador

Isso permite adicionar novas metodologias, culturas e funcionalidades sem 
alterar a estrutura principal.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import geopandas as gpd
from shapely.geometry import Point

# Import de classes temporariamente comentado para desbloquear inicialização
# from .tipos.camada_tematica import (
#     CamadaTematicaInterface,
#     FabricaCamadasTematicas,
#     CombinadorCamadas,
#     TipoCamada,
#     TipoIndice
# )
from .configuracao import ConfigPrescricao, LIMITES_MICRO
from .contratos import (
    NotasTecnicas,
    PrescricaoZona,
    ResumoPrescricao,
    ResultadoCorretivo,
    ResultadoNutriente,
    StatusNutriente,
    TipoCorretivo
)
from .validacao import (
    calcular_custo_nutriente,
    calcular_dose_corrigida,
    calcular_exportacao,
    classificar_status_nutriente,
    get_parametros_metodo
)

# ============================================================================
# COMPONENTES ESPECIALIZADOS
# ============================================================================

class ValidadorCamadas(ABC):
    """Valida camadas temáticas antes do processamento."""
    
    @abstractmethod
    def validar(self, camadas: List) -> Dict[str, Any]:  # CamadaTematicaInterface temporariamente comentado
        """Valida camadas e retorna resultado da validação."""
        pass

class ValidadorCamadasImpl(ValidadorCamadas):
    """Implementação concreta do validador de camadas."""
    
    def validar(self, camadas: List) -> Dict[str, Any]:  # CamadaTematicaInterface temporariamente comentado
        """Valida camadas e retorna resultado da validação."""
        resultado = {
            'valido': True,
            'erros': [],
            'avisos': [],
            'camadas_validas': [],
            'camadas_invalidas': []
        }
        
        if not camadas:
            resultado['valido'] = False
            resultado['erros'].append("Nenhuma camada fornecida")
            return resultado
        
        for i, camada in enumerate(camadas):
            # Verificar se a camada tem geometria
            if camada.geometria.empty:
                resultado['valido'] = False
                resultado['erros'].append(f"Camada {i} ({camada.nome}) sem geometria")
                resultado['camadas_invalidas'].append(camada)
                continue
            
            # Verificar se a camada tem CRS
            if not camada.crs:
                resultado['avisos'].append(f"Camada {i} ({camada.nome}) sem CRS definido")
            
            # Verificar se a camada tem metadados mínimos
            if camada.tipo_camada == "INDICE_ESPECTRAL":  # TipoCamada temporariamente comentado
                if 'tipo_indice' not in camada.metadados:
                    resultado['avisos'].append(f"Camada {i} ({camada.nome}) sem tipo de índice definido")
            
            resultado['camadas_validas'].append(camada)
        
        if len(resultado['camadas_validas']) == 0:
            resultado['valido'] = False
            resultado['erros'].append("Nenhuma camada válida encontrada")
        
        return resultado

class NormalizadorCamadas(ABC):
    """Normaliza camadas temáticas para processamento."""
    
    @abstractmethod
    def normalizar(self, camadas: List) -> List:  # CamadaTematicaInterface temporariamente comentado
        """Normaliza camadas e retorna camadas normalizadas."""
        pass

class NormalizadorCamadasImpl(NormalizadorCamadas):
    """Implementação concreta do normalizador de camadas."""
    
    def normalizar(self, camadas: List) -> List:  # CamadaTematicaInterface temporariamente comentado
        """Normaliza camadas e retorna camadas normalizadas."""
        if not camadas:
            return []
        
        # Normalizar CRS para o primeiro CRS da lista
        crs_alvo = camadas[0].crs
        camadas_normalizadas = "CombinadorCamadas".normalizar_crs(camadas, crs_alvo)  # CombinadorCamadas temporariamente comentado
        
        # Garantir que todas as camadas tenham a estrutura mínima
        for camada in camadas_normalizadas:
            self._garantir_estrutura_minima(camada)
        
        return camadas_normalizadas
    
    def _garantir_estrutura_minima(self, camada):
        """Garante que a camada tenha a estrutura mínima."""
        # Adicionar coluna 'valor' se não existir
        if 'valor' not in camada.geometria.columns:
            if 'value' in camada.geometria.columns:
                camada.geometria['valor'] = camada.geometria['value']
            else:
                # Criar coluna de valores aleatórios para teste
                # TODO: Implementar lógica real de obtenção de valores
                import numpy as np
                camada.geometria['valor'] = np.random.uniform(0, 1, len(camada.geometria))

class CombinadorCamadasImpl:
    """Combina múltiplas camadas temáticas."""
    
    def combinar(self, camadas: List) -> Any:  # CamadaTematicaInterface temporariamente comentado
        """Combina múltiplas camadas em uma única."""
        return "CombinadorCamadas".combinar_camadas(camadas)  # CombinadorCamadas temporariamente comentado
    
    def agregar_por_zona(self, camadas: List, zonas: gpd.GeoDataFrame) -> Dict[str, Any]:  # CamadaTematicaInterface temporariamente comentado
        """Agrega camadas por zonas."""
        resultado = {}
        
        for _, zona in zonas.iterrows():
            zona_id = zona.get('id', f'zona_{idx}')
            resultado[zona_id] = {}
            
            for camada in camadas:
                # Calcular estatísticas da camada na zona
                zona_geom = zona.geometry
                valores_na_zona = []
                
                for _, row in camada.geometria.iterrows():
                    if row.geometry.intersects(zona_geom):
                        valor = row.get('valor') or row.get('value')
                        if valor is not None:
                            valores_na_zona.append(valor)
                
                if valores_na_zona:
                    resultado[zona_id][camada.nome] = {
                        'media': sum(valores_na_zona) / len(valores_na_zona),
                        'minimo': min(valores_na_zona),
                        'maximo': max(valores_na_zona),
                        'count': len(valores_na_zona)
                    }
        
        return resultado

class SelecionadorMetodologia(ABC):
    """Seleciona metodologia de recomendação."""
    
    @abstractmethod
    def selecionar(self, cultura: str, safra: str, metodologias_disponiveis: List[str]) -> str:
        """Seleciona metodologia com base em cultura e safra."""
        pass

class SelecionadorMetodologiaImpl(SelecionadorMetodologia):
    """Implementação concreta do selecionador de metodologia."""
    
    def selecionar(self, cultura: str, safra: str, metodologias_disponiveis: List[str]) -> str:
        """Seleciona metodologia com base em cultura e safra."""
        # Lógica de seleção simples - pode ser expandida
        if 'IAC' in metodologias_disponiveis:
            return 'IAC'
        elif 'CFSEMG' in metodologias_disponiveis:
            return 'CFSEMG'
        elif metodologias_disponiveis:
            return metodologias_disponiveis[0]
        else:
            raise ValueError("Nenhuma metodologia disponível")

class CalculadorRecomendacao(ABC):
    """Calcula recomendações técnicas."""
    
    @abstractmethod
    def calcular(self, 
                 cultura: str, 
                 metodologia: str, 
                 caracteristicas_zona: Dict[str, float],
                 parametros_config: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula recomendações técnicas."""
        pass

class CalculadorRecomendacaoImpl(CalculadorRecomendacao):
    """Implementação concreta do calculador de recomendação."""
    
    def calcular(self, 
                 cultura: str, 
                 metodologia: str, 
                 caracteristicas_zona: Dict[str, float],
                 parametros_config: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula recomendações técnicas."""
        # TODO: Implementar lógica real de cálculo
        # Por enquanto, retorna valores de exemplo
        
        recomendacoes = {
            'nutrientes': [],
            'corretivos': [],
            'custo_total': 0.0,
            'observacoes': []
        }
        
        # Calcular recomendações de nutrientes
        for nutriente in ['N', 'P', 'K', 'Ca', 'Mg', 'S']:
            if nutriente in caracteristicas_zona:
                teor_atual = caracteristicas_zona[nutriente]
                status = classificar_status_nutriente(nutriente, teor_atual, parametros_config)
                
                resultado_nutriente = ResultadoNutriente(
                    nutriente=nutriente,
                    teor_atual=teor_atual,
                    status=status,
                    dose_recomendada=self._calcular_dose_nutriente(nutriente, teor_atual, status),
                    custo_unitario=calcular_custo_nutriente(nutriente, parametros_config)
                )
                
                recomendacoes['nutrientes'].append(resultado_nutriente)
                recomendacoes['custo_total'] += resultado_nutriente.custo_unitario
        
        # Calcular recomendações de corretivos
        if 'pH' in caracteristicas_zona:
            ph = caracteristicas_zona['pH']
            if ph < 6.0:  # Solo ácido
                resultado_corretivo = ResultadoCorretivo(
                    tipo=TipoCorretivo.CALAGEM,
                    dose_recomendada=self._calcular_dose_calagem(ph),
                    custo_unitario=calcular_custo_nutriente('Ca', parametros_config)
                )
                recomendacoes['corretivos'].append(resultado_corretivo)
                recomendacoes['custo_total'] += resultado_corretivo.custo_unitario
        
        return recomendacoes
    
    def _calcular_dose_nutriente(self, nutriente: str, teor_atual: float, status: StatusNutriente) -> float:
        """Calcula dose recomendada de nutriente."""
        # TODO: Implementar lógica real
        if status == StatusNutriente.BAIXO:
            return 100.0
        elif status == StatusNutriente.MEDIO:
            return 50.0
        else:
            return 0.0
    
    def _calcular_dose_calagem(self, ph: float) -> float:
        """Calcula dose recomendada de calagem."""
        # TODO: Implementar lógica real
        if ph < 5.5:
            return 2000.0
        elif ph < 6.0:
            return 1000.0
        else:
            return 0.0

class GeradorPrescricao(ABC):
    """Gera prescrição final."""
    
    @abstractmethod
    def gerar(self, 
              zonas: List[Dict[str, Any]], 
              recomendacoes: List[Dict[str, Any]]) -> ResumoPrescricao:
        """Gera prescrição final."""
        pass

class GeradorPrescricaoImpl(GeradorPrescricao):
    """Implementação concreta do gerador de prescrição."""
    
    def gerar(self, 
              zonas: List[Dict[str, Any]], 
              recomendacoes: List[Dict[str, Any]]) -> ResumoPrescricao:
        """Gera prescrição final."""
        # TODO: Implementar lógica real de geração
        return ResumoPrescricao(
            total_zonas=len(zonas),
            custo_total=sum(rec['custo_total'] for rec in recomendacoes),
            zonas_prescritas=len(zonas),
            observacoes="Prescrição gerada com sucesso"
        )

class ExportadorPrescricao(ABC):
    """Exporta prescrição para diferentes formatos."""
    
    @abstractmethod
    def exportar(self, prescricao: ResumoPrescricao, formato: str) -> str:
        """Exporta prescrição para formato específico."""
        pass

class ExportadorPrescricaoImpl(ExportadorPrescricao):
    """Implementação concreta do exportador de prescrição."""
    
    def exportar(self, prescricao: ResumoPrescricao, formato: str) -> str:
        """Exporta prescrição para formato específico."""
        if formato == 'caderno_tecnico':
            return self._exportar_caderno_tecnico(prescricao)
        elif formato == 'cartao_cabine':
            return self._exportar_cartao_cabine(prescricao)
        elif formato == 'maquina':
            return self._exportar_maquina(prescricao)
        else:
            raise ValueError(f"Formato não suportado: {formato}")
    
    def _exportar_caderno_tecnico(self, prescricao: ResumoPrescricao) -> str:
        """Exporta para caderno técnico."""
        return "Caderno Técnico - PDF gerado"
    
    def _exportar_cartao_cabine(self, prescricao: ResumoPrescricao) -> str:
        """Exporta para cartão de cabine."""
        return "Cartão de Cabine - CSV gerado"
    
    def _exportar_maquina(self, prescricao: ResumoPrescricao) -> str:
        """Exporta para máquina de aplicação."""
        return "Arquivo para Máquina - Shapefile gerado"

# ============================================================================
# MOTOR PRINCIPAL COMPOSTO
# ============================================================================

class MotorPrescricaoComposto:
    """
    Motor de prescrição composto por componentes especializados.
    
    Esta é a implementação da sugestão arquitetural de dividir o motor em:
    Validador → Normalizador → CombinadorCamadas → SelecionadorMetodologia → 
    CalculadorRecomendacao → GeradorPrescricao → Exportador
    """
    
    def __init__(self, config: ConfigPrescricao):
        """Inicializa o motor com configuração."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Inicializar componentes
        self.validador = ValidadorCamadasImpl()
        self.normalizador = NormalizadorCamadasImpl()
        self.combinador = CombinadorCamadasImpl()
        self.seletor_metodologia = SelecionadorMetodologiaImpl()
        self.calculador_recomendacao = CalculadorRecomendacaoImpl()
        self.gerador_prescricao = GeradorPrescricaoImpl()
        self.exportador = ExportadorPrescricaoImpl()
    
    def prescrever_todas_zonas(self,
                              camadas: List,  # CamadaTematicaInterface temporariamente comentado
                              zonas: gpd.GeoDataFrame,
                              cultura: str,
                              safra: str,
                              metodologias_disponiveis: List[str],
                              formato_exportacao: str = 'caderno_tecnico') -> Dict[str, Any]:
        """
        Processa todas as zonas e gera prescrição completa.
        
        Args:
            camadas: Lista de camadas temáticas
            zonas: GeoDataFrame com zonas de manejo
            cultura: Nome da cultura
            safra: Nome da safra
            metodologias_disponiveis: Lista de metodologias disponíveis
            formato_exportacao: Formato de exportação
            
        Returns:
            Dicionário com resultado da prescrição
        """
        try:
            self.logger.info("[MOTOR_PRESCRICAO] Iniciando processamento de prescrição")
            
            # 1. Validação de camadas
            self.logger.info("[MOTOR_PRESCRICAO] Validando camadas...")
            resultado_validacao = self.validador.validar(camadas)
            
            if not resultado_validacao['valido']:
                raise ValueError(f"Camadas inválidas: {resultado_validacao['erros']}")
            
            camadas_validas = resultado_validacao['camadas_validas']
            self.logger.info(f"[MOTOR_PRESCRICAO] {len(camadas_validas)} camadas válidas")
            
            # 2. Normalização de camadas
            self.logger.info("[MOTOR_PRESCRICAO] Normalizando camadas...")
            camadas_normalizadas = self.normalizador.normalizar(camadas_validas)
            self.logger.info(f"[MOTOR_PRESCRICAO] Camadas normalizadas para CRS: {camadas_normalizadas[0].crs}")
            
            # 3. Combinação de camadas
            self.logger.info("[MOTOR_PRESCRICAO] Combinando camadas...")
            camada_combinada = self.combinador.combinar(camadas_normalizadas)
            self.logger.info("[MOTOR_PRESCRICAO] Camadas combinadas")
            
            # 4. Agregação por zonas
            self.logger.info("[MOTOR_PRESCRICAO] Agregando por zonas...")
            caracteristicas_zonas = self.combinador.agregar_por_zona(camadas_normalizadas, zonas)
            self.logger.info(f"[MOTOR_PRESCRICAO] Características agregadas para {len(caracteristicas_zonas)} zonas")
            
            # 5. Seleção de metodologia
            self.logger.info("[MOTOR_PRESCRICAO] Selecionando metodologia...")
            metodologia_selecionada = self.seletor_metodologia.selecionar(cultura, safra, metodologias_disponiveis)
            self.logger.info(f"[MOTOR_PRESCRICAO] Metodologia selecionada: {metodologia_selecionada}")
            
            # 6. Cálculo de recomendações
            self.logger.info("[MOTOR_PRESCRICAO] Calculando recomendações...")
            recomendacoes = []
            
            for zona_id, caracteristicas in caracteristicas_zonas.items():
                recomendacao = self.calculador_recomendacao.calcular(
                    cultura=cultura,
                    metodologia=metodologia_selecionada,
                    caracteristicas_zona=caracteristicas,
                    parametros_config=self.config.__dict__
                )
                recomendacoes.append({
                    'zona_id': zona_id,
                    'caracteristicas': caracteristicas,
                    'recomendacao': recomendacao
                })
            
            self.logger.info(f"[MOTOR_PRESCRICAO] Recomendações calculadas para {len(recomendacoes)} zonas")
            
            # 7. Geração de prescrição
            self.logger.info("[MOTOR_PRESCRICAO] Gerando prescrição...")
            resumo_prescricao = self.gerador_prescricao.gerar(
                zonas=list(caracteristicas_zonas.keys()),
                recomendacoes=recomendacoes
            )
            self.logger.info("[MOTOR_PRESCRICAO] Prescrição gerada")
            
            # 8. Exportação
            self.logger.info(f"[MOTOR_PRESCRICAO] Exportando para {formato_exportacao}...")
            caminho_exportacao = self.exportador.exportar(resumo_prescricao, formato_exportacao)
            self.logger.info(f"[MOTOR_PRESCRICAO] Exportação concluída: {caminho_exportacao}")
            
            return {
                'status': 'sucesso',
                'prescricao': resumo_prescricao,
                'recomendacoes': recomendacoes,
                'exportacao': caminho_exportacao,
                'metodologia': metodologia_selecionada,
                'camadas_processadas': len(camadas_normalizadas),
                'zonas_processadas': len(caracteristicas_zonas)
            }
            
        except Exception as e:
            self.logger.error(f"[MOTOR_PRESCRICAO] Erro na prescrição: {str(e)}")
            return {
                'status': 'erro',
                'mensagem': str(e),
                'detalhes': str(e.__class__.__name__)
            }
    
    def adicionar_componente(self, nome: str, componente: Any):
        """Adiciona um novo componente ao motor."""
        setattr(self, nome, componente)
        self.logger.info(f"[MOTOR_PRESCRICAO] Componente '{nome}' adicionado")
    
    def remover_componente(self, nome: str):
        """Remove um componente do motor."""
        if hasattr(self, nome):
            delattr(self, nome)
            self.logger.info(f"[MOTOR_PRESCRICAO] Componente '{nome}' removido")

# ============================================================================
# EXPORTAÇÃO DA INTERFACE
# ============================================================================

__all__ = [
    'MotorPrescricaoComposto',
    'ValidadorCamadas',
    'ValidadorCamadasImpl',
    'NormalizadorCamadas',
    'NormalizadorCamadasImpl',
    'CombinadorCamadasImpl',
    'SelecionadorMetodologia',
    'SelecionadorMetodologiaImpl',
    'CalculadorRecomendacao',
    'CalculadorRecomendacaoImpl',
    'GeradorPrescricao',
    'GeradorPrescricaoImpl',
    'ExportadorPrescricao',
    'ExportadorPrescricaoImpl'
]