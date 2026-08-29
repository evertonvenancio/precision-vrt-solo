"""
Precision VRT Solo — Motor de Interpolação de Nematoides

Implementa interpolação de dados de nematoides sobre uma grade regular.
Utiliza métodos espaciais específicos para análise de risco.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import logging

from ...tipos.geoespacial import Bounds, Coordenada
from ...tipos.base import ConfigBase, ResultadoBase
from ..nematoides.contratos import (
    PontoAmostraNematoides,
    ConfigInterpolacaoNematoides,
    ResultadoInterpolacaoNematoides,
    NivelRiscoNematoides
)


class MotorInterpolacaoNematoides:
    """
    Motor de interpolação específico para nematoides.
    
    Realiza interpolação de população de nematoides sobre uma grade regular,
    considerando especificidades da análise de risco.
    """
    
    def __init__(self, config: ConfigInterpolacaoNematoides):
        self.config = config
        self.amostras: List[PontoAmostraNematoides] = []
        self.logger = logging.getLogger(__name__)
    
    def adicionar_amostra(self, amostra: PontoAmostraNematoides):
        """Adiciona ponto para interpolação."""
        self.amostras.append(amostra)
    
    def adicionar_amostras(self, amostras: List[PontoAmostraNematoides]):
        """Adiciona múltiplos pontos para interpolação."""
        self.amostras.extend(amostras)
    
    def interpolar(self, bounds: Bounds) -> ResultadoInterpolacaoNematoides:
        """
        Realiza interpolação sobre uma grade regular.
        
        Args:
            bounds: Limites espaciais para interpolação
            
        Returns:
            Resultado com grade interpolada
        """
        if not self.amostras:
            raise ValueError("Nenhuma amostra fornecida para interpolação")
        
        # Criar grade regular
        x_min, y_min = bounds.minx, bounds.miny
        x_max, y_max = bounds.maxx, bounds.maxy
        
        nx = int((x_max - x_min) / self.config.resolucao_grade) + 1
        ny = int((y_max - y_min) / self.config.resolucao_grade) + 1
        
        # Gerar coordenadas da grade
        coordenadas_grade = []
        for i in range(nx):
            for j in range(ny):
                x = x_min + i * self.config.resolucao_grade
                y = y_min + j * self.config.resolucao_grade
                coordenadas_grade.append((x, y))
        
        # Realizar interpolação
        if self.config.metodo == "kriging":
            valores_interpolados = self._interpolar_kriging(coordenadas_grade)
        elif self.config.metodo == "idw":
            valores_interpolados = self._interpolar_idw(coordenadas_grade)
        elif self.config.metodo == "natural_neighbor":
            valores_interpolados = self._interpolar_natural_neighbor(coordenadas_grade)
        else:
            raise ValueError(f"Método de interpolação não suportado: {self.config.metodo}")
        
        # Gerar mapa de risco
        mapa_risco = self._gerar_mapa_risco(valores_interpolados)
        
        return ResultadoInterpolacaoNematoides(
            valores_interpolados=valores_interpolados,
            coordenadas_grade=coordenadas_grade,
            pontos_originais=self.amostras,
            configuracao_usada=self.config,
            mapa_risco=mapa_risco
        )
    
    def _interpolar_kriging(self, coordenadas_grade: List[Tuple[float, float]]) -> np.ndarray:
        """
        Implementação simplificada de interpolação por kriging.
        
        Args:
            coordenadas_grade: Coordenadas dos pontos da grade
            
        Returns:
            Valores interpolados
        """
        n_pontos = len(coordenadas_grade)
        resultado = np.zeros(n_pontos)
        
        # Extrair coordenadas e valores das amostras
        amostras_x = [a.coordenada.x for a in self.amostras]
        amostras_y = [a.coordenada.y for a in self.amostras]
        valores = [a.populacao_nematoides_100g_solo for a in self.amostras]
        
        # Interpolação simplificada (na verdade seria kriging real)
        for i, (x_grade, y_grade) in enumerate(coordenadas_grade):
            # Encontrar amostras próximas
            distancias = np.sqrt((np.array(amostras_x) - x_grade)**2 + 
                               (np.array(amostras_y) - y_grade)**2)
            
            # Usar apenas amostras dentro da máxima distância
            mask = distancias <= self.config.max_distancia_interpolacao
            if np.any(mask):
                # Interpolação por distância inversa ponderada (IDW simplificado)
                pesos = 1.0 / (distancias[mask] + 1e-6)
                resultado[i] = np.sum(valores[mask] * pesos) / np.sum(pesos)
            else:
                # Usar valor médio se nenhuma amostra próxima
                resultado[i] = np.mean(valores)
        
        return resultado
    
    def _interpolar_idw(self, coordenadas_grade: List[Tuple[float, float]]) -> np.ndarray:
        """
        Interpolação por Distância Inversa Ponderada (IDW).
        
        Args:
            coordenadas_grade: Coordenadas dos pontos da grade
            
        Returns:
            Valores interpolados
        """
        n_pontos = len(coordenadas_grade)
        resultado = np.zeros(n_pontos)
        
        # Extrair coordenadas e valores das amostras
        amostras_x = [a.coordenada.x for a in self.amostras]
        amostras_y = [a.coordenada.y for a in self.amostras]
        valores = [a.populacao_nematoides_100g_solo for a in self.amostras]
        
        for i, (x_grade, y_grade) in enumerate(coordenadas_grade):
            # Calcular distâncias
            distancias = np.sqrt((np.array(amostras_x) - x_grade)**2 + 
                               (np.array(amostras_y) - y_grade)**2)
            
            # Evitar divisão por zero
            distancias = np.maximum(distancias, 1e-6)
            
            # Calcular pesos (distância inversa ao quadrado)
            pesos = 1.0 / (distancias ** 2)
            
            # Interpolar
            resultado[i] = np.sum(valores * pesos) / np.sum(pesos)
        
        return resultado
    
    def _interpolar_natural_neighbor(self, coordenadas_grade: List[Tuple[float, float]]) -> np.ndarray:
        """
        Interpolação por Vizinho Natural (Natural Neighbor).
        
        Args:
            coordenadas_grade: Coordenados dos pontos da grade
            
        Returns:
            Valores interpolados
        """
        # Implementação simplificada do vizinho natural
        # Na prática usaria bibliotecas como scipy.spatial.Voronoi
        
        n_pontos = len(coordenadas_grade)
        resultado = np.zeros(n_pontos)
        
        # Extrair coordenadas e valores das amostras
        amostras_x = [a.coordenada.x for a in self.amostras]
        amostras_y = [a.coordenada.y for a in self.amostras]
        valores = [a.populacao_nematoides_100g_solo for a in self.amostras]
        
        for i, (x_grade, y_grade) in enumerate(coordenadas_grade):
            # Encontrar os 3 vizinhos mais próximos
            distancias = np.sqrt((np.array(amostras_x) - x_grade)**2 + 
                               (np.array(amostras_y) - y_grade)**2)
            
            # Ordenar por distância
            indices_ordenados = np.argsort(distancias)
            
            # Usar os 3 vizinhos mais próximos com ponderação por área de Voronoi
            n_vizinhos = min(3, len(self.amostras))
            pesos = np.zeros(n_vizinhos)
            
            for j in range(n_vizinhos):
                idx = indices_ordenados[j]
                # Ponderação simplificada pela distância inversa
                pesos[j] = 1.0 / (distancias[idx] + 1e-6)
            
            # Normalizar pesos
            pesos = pesos / np.sum(pesos)
            
            # Interpolar
            resultado[i] = np.sum([valores[indices_ordenados[j]] * pesos[j] 
                                 for j in range(n_vizinhos)])
        
        return resultado
    
    def _gerar_mapa_risco(self, valores_interpolados: np.ndarray) -> np.ndarray:
        """
        Gera mapa de risco classificado a partir dos valores interpolados.
        
        Args:
            valores_interpolados: Valores populacionais interpolados
            
        Returns:
            Mapa de risco classificado
        """
        mapa_risco = np.zeros_like(valores_interpolados, dtype=int)
        
        # Limites de risco
        limite_baixo = MotorNematoides.LIMITE_BAIXO * MotorNematoides.FATORES_CULTURA.get("milho", 1.0)
        limite_moderado = MotorNematoides.LIMITE_MODERADO * MotorNematoides.FATORES_CULTURA.get("milho", 1.0)
        limite_alto = MotorNematoides.LIMITE_ALTO * MotorNematoides.FATORES_CULTURA.get("milho", 1.0)
        
        # Classificar
        mapa_risco[valores_interpolados < limite_baixo] = 0  # BAIXO
        mapa_risco[(valores_interpolados >= limite_baixo) & (valores_interpolados < limite_moderado)] = 1  # MODERADO
        mapa_risco[(valores_interpolados >= limite_moderado) & (valores_interpolados < limite_alto)] = 2  # ALTO
        mapa_risco[valores_interpolados >= limite_alto] = 3  # CRITICO
        
        return mapa_risco