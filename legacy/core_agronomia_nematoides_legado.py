"""
Modulo de Amostragem Dirigida para Nematoides
Cruzamento de dados de produtividade com indices de risco de nematoides.
Preparado para integracao com db_schema.py (SQLite).
"""

import numpy as np
import pandas as pd
import sqlite3
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class NivelRiscoNematoides(Enum):
    """Classificacao de risco de nematoides por zona."""
    BAIXO = "baixo"
    MODERADO = "moderado"
    ALTO = "alto"
    CRITICO = "critico"


@dataclass
class AmostraNematoides:
    """Representa uma amostra de solo analisada para nematoides."""
    ponto_id: str
    latitude: float
    longitude: float
    profundidade_cm: int
    populacao_nematoides_100g_solo: float
    genero_predominante: str
    indice_gall: Optional[float] = None
    indice_meloidogyne: Optional[float] = None
    indice_pratylenchus: Optional[float] = None
    indice_heterodera: Optional[float] = None


@dataclass
class ZonaRisco:
    """Zona de manejo classificada por risco de nematoides."""
    zona_id: int
    risco_classificacao: str
    populacao_media: float
    populacao_maxima: float
    generos_detectados: List[str] = field(default_factory=list)
    recomendacao_manejo: str = ""
    necessita_tratamento: bool = False
    area_hectares: float = 0.0


class AmostragemDirigida:
    """
    Amostragem dirigida para nematoides com cruzamento de dados de produtividade.

    Implementa metodologia de amostragem dirigida por zonas de produtividade,
    cruzando indices de vigor (NDVI) e dados de produtividade historica com
    populacoes de nematoides para identificar areas de risco.

    Referencia:
        Mulla, D.J. (2013). Twenty five years of remote sensing in precision
        agriculture: Key advances and remaining knowledge gaps.
        Biosystems Engineering, 114(4), 358-371.
    """

    # Limites de populacao de nematoides por 100g de solo (valores referencia)
    LIMITE_BAIXO = 100.0
    LIMITE_MODERADO = 500.0
    LIMITE_ALTO = 1000.0

    # Fatores de correcao por cultura (multiplicadores do limite)
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
        Args:
            cultura: Nome da cultura para ajuste dos limites de risco
        """
        self.cultura = cultura.lower()
        self.fator_cultura = self.FATORES_CULTURA.get(self.cultura, 1.0)
        self.amostras: List[AmostraNematoides] = []
        self.zonas_risco: Dict[int, ZonaRisco] = {}

    def adicionar_amostra(self, amostra: AmostraNematoides) -> None:
        """Adiciona uma amostra a colecao."""
        self.amostras.append(amostra)

    def classificar_risco(self, populacao: float) -> str:
        """
        Classifica o nivel de risco baseado na populacao de nematoides.

        Args:
            populacao: Populacao de nematoides por 100g de solo

        Returns:
            String com classificacao do risco
        """
        limite_baixo = self.LIMITE_BAIXO * self.fator_cultura
        limite_moderado = self.LIMITE_MODERADO * self.fator_cultura
        limite_alto = self.LIMITE_ALTO * self.fator_cultura

        if populacao < limite_baixo:
            return NivelRiscoNematoides.BAIXO.value
        elif populacao < limite_moderado:
            return NivelRiscoNematoides.MODERADO.value
        elif populacao < limite_alto:
            return NivelRiscoNematoides.ALTO.value
        else:
            return NivelRiscoNematoides.CRITICO.value

    def calcular_indice_risco_zona(
        self,
        amostras_zona: List[AmostraNematoides]
    ) -> Dict:
        """
        Calcula indice de risco composto para uma zona de manejo.

        Args:
            amostras_zona: Lista de amostras da zona

        Returns:
            Dict com estatisticas e classificacao de risco
        """
        if not amostras_zona:
            return {"erro": "Nenhuma amostra fornecida"}

        populacoes = [a.populacao_nematoides_100g_solo for a in amostras_zona]
        media = float(np.mean(populacoes))
        maxima = float(np.max(populacoes))
        desvio = float(np.std(populacoes, ddof=1))

        # Coletar generos unicos
        generos = list(set(
            a.genero_predominante for a in amostras_zona if a.genero_predominante
        ))

        # Indice de risco ponderado (0-100)
        indice_risco = min(100.0, (media / (self.LIMITE_ALTO * self.fator_cultura)) * 100)

        return {
            "populacao_media": round(media, 2),
            "populacao_maxima": round(maxima, 2),
            "desvio_padrao": round(desvio, 2),
            "indice_risco": round(indice_risco, 2),
            "generos_detectados": generos,
            "n_amostras": len(amostras_zona),
            "classificacao_risco": self.classificar_risco(media)
        }

    def cruzar_produtividade_risco(
        self,
        dados_produtividade: Dict[int, Dict],
        dados_nematoides: Dict[int, List[AmostraNematoides]],
        area_por_zona: Optional[Dict[int, float]] = None
    ) -> Dict[int, Dict]:
        """
        Cruza dados de produtividade com indices de risco de nematoides por zona.

        Args:
            dados_produtividade: Dict {zona_id: {produtividade_sc_ha, ndvi_medio, area_ha}}
            dados_nematoides: Dict {zona_id: [AmostraNematoides]}
            area_por_zona: Dict opcional {zona_id: area_hectares}

        Returns:
            Dict com cruzamento completo por zona
        """
        resultado = {}

        todas_zonas = set(dados_produtividade.keys()) | set(dados_nematoides.keys())

        for zona_id in todas_zonas:
            prod = dados_produtividade.get(zona_id, {})
            amostras = dados_nematoides.get(zona_id, [])

            # Calcular risco
            risco = self.calcular_indice_risco_zona(amostras) if amostras else {
                "populacao_media": 0,
                "populacao_maxima": 0,
                "indice_risco": 0,
                "classificacao_risco": "sem_dados"
            }

            # Cruzamento produtividade x risco
            produtividade = prod.get("produtividade_sc_ha", 0)
            ndvi = prod.get("ndvi_medio", 0)
            area = area_por_zona.get(zona_id, 0) if area_por_zona else prod.get("area_ha", 0)

            # Correlacao inversa: alta populacao + baixa produtividade = risco confirmado
            correlacao = self._avaliar_correlacao(produtividade, risco["populacao_media"], ndvi)

            # Recomendacao de manejo
            recomendacao = self._gerar_recomendacao(risco["classificacao_risco"], correlacao)

            resultado[zona_id] = {
                "zona_id": zona_id,
                "area_hectares": round(area, 2),
                "produtividade_sc_ha": round(produtividade, 2),
                "ndvi_medio": round(ndvi, 4),
                "risco_nematoides": risco,
                "correlacao_produtividade_risco": correlacao,
                "recomendacao_manejo": recomendacao,
                "prioridade_acao": self._calcular_prioridade(risco, correlacao, area)
            }

        return resultado

    def _avaliar_correlacao(
        self,
        produtividade: float,
        populacao_media: float,
        ndvi: float
    ) -> Dict:
        """
        Avalia correlacao entre produtividade, NDVI e populacao de nematoides.

        Returns:
            Dict com indicadores de correlacao
        """
        # Baixa produtividade com alta populacao = confirmacao de dano
        indicador_dano = 0
        if produtividade > 0 and populacao_media > 0:
            # Normalizar: quanto menor a produtividade e maior a populacao, maior o indicador
            indicador_dano = min(100, (populacao_media / 1000) * (1 / max(produtividade / 100, 0.1)) * 10)

        # NDVI baixo com alta populacao = confirmacao visual
        indicador_ndvi = 0
        if ndvi > 0 and populacao_media > 0:
            indicador_ndvi = min(100, (populacao_media / 1000) * ((0.8 - min(ndvi, 0.8)) / 0.8) * 100)

        return {
            "indicador_dano_estimado": round(indicador_dano, 2),
            "indicador_ndvi_risco": round(indicador_ndvi, 2),
            "indice_composto_risco": round((indicador_dano + indicador_ndvi) / 2, 2),
            "interpretacao": self._interpretar_correlacao(indicador_dano, indicador_ndvi)
        }

    def _interpretar_correlacao(self, dano: float, ndvi_risco: float) -> str:
        """Interpreta os indicadores de correlacao."""
        composto = (dano + ndvi_risco) / 2
        if composto > 70:
            return "Alta probabilidade de dano por nematoides confirmado"
        elif composto > 40:
            return "Indicios de dano por nematoides - monitoramento recomendado"
        elif composto > 20:
            return "Baixa correlacao - outros fatores podem estar limitando"
        else:
            return "Sem evidencias de dano por nematoides"

    def _gerar_recomendacao(self, classificacao_risco: str, correlacao: Dict) -> str:
        """Gera recomendacao de manejo baseada no risco e correlacao."""
        indice_composto = correlacao.get("indice_composto_risco", 0)

        if classificacao_risco == NivelRiscoNematoides.CRITICO.value:
            if indice_composto > 60:
                return "TRATAMENTO OBRIGATORIO: Aplicar nematicida + rotacao de culturas. Considerar pousio."
            return "TRATAMENTO OBRIGATORIO: Aplicar nematicida. Monitorar produtividade."

        elif classificacao_risco == NivelRiscoNematoides.ALTO.value:
            if indice_composto > 50:
                return "TRATAMENTO RECOMENDADO: Aplicar nematicida + adubacao verde."
            return "MONITORAMENTO INTENSIVO: Aumentar frequencia de amostragem."

        elif classificacao_risco == NivelRiscoNematoides.MODERADO.value:
            return "PREVENCAO: Adubacao verde, manejo de residuos. Amostragem anual."

        elif classificacao_risco == NivelRiscoNematoides.BAIXO.value:
            return "MANEJO PADRAO: Amostragem bienal para monitoramento."

        return "Sem dados suficientes para recomendacao."

    def _calcular_prioridade(
        self,
        risco: Dict,
        correlacao: Dict,
        area: float
    ) -> str:
        """Calcula prioridade de acao baseada em risco, correlacao e area."""
        indice_risco = risco.get("indice_risco", 0)
        indice_composto = correlacao.get("indice_composto_risco", 0)

        score = (indice_risco * 0.4) + (indice_composto * 0.4) + (min(area, 50) * 0.4)

        if score > 80:
            return "PRIORIDADE 1 - URGENTE"
        elif score > 50:
            return "PRIORIDADE 2 - ALTA"
        elif score > 25:
            return "PRIORIDADE 3 - MEDIA"
        else:
            return "PRIORIDADE 4 - BAIXA"

    def gerar_mapa_risco_zonas(
        self,
        resultado_cruzamento: Dict[int, Dict]
    ) -> pd.DataFrame:
        """
        Gera DataFrame com mapa de risco para exportacao/visualizacao.

        Args:
            resultado_cruzamento: Saida de cruzar_produtividade_risco

        Returns:
            DataFrame com dados por zona
        """
        rows = []
        for zona_id, dados in resultado_cruzamento.items():
            rows.append({
                "zona_id": zona_id,
                "area_ha": dados["area_hectares"],
                "produtividade_sc_ha": dados["produtividade_sc_ha"],
                "ndvi_medio": dados["ndvi_medio"],
                "populacao_nematoides_media": dados["risco_nematoides"].get("populacao_media", 0),
                "indice_risco": dados["risco_nematoides"].get("indice_risco", 0),
                "classificacao_risco": dados["risco_nematoides"].get("classificacao_risco", "sem_dados"),
                "indice_composto_risco": dados["correlacao_produtividade_risco"].get("indice_composto_risco", 0),
                "recomendacao": dados["recomendacao_manejo"],
                "prioridade": dados["prioridade_acao"]
            })

        return pd.DataFrame(rows)

    def salvar_no_banco(
        self,
        conn: sqlite3.Connection,
        talhao_id: int,
        safra: str,
        resultado_cruzamento: Dict[int, Dict]
    ) -> bool:
        """
        Persiste resultados da amostragem dirigida no banco de dados.
        Preparado para integracao com db_schema.py.

        Args:
            conn: Conexao SQLite ativa
            talhao_id: ID do talhao
            safra: Identificacao da safra
            resultado_cruzamento: Dict de cruzar_produtividade_risco

        Returns:
            True se sucesso, False caso contrario
        """
        try:
            cursor = conn.cursor()

            # Criar tabelas se nao existirem
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nematoides_amostragem (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    talhao_id INTEGER,
                    safra TEXT,
                    zona_id INTEGER,
                    area_hectares REAL,
                    produtividade_sc_ha REAL,
                    ndvi_medio REAL,
                    populacao_nematoides_media REAL,
                    indice_risco REAL,
                    classificacao_risco TEXT,
                    indice_composto_risco REAL,
                    recomendacao_manejo TEXT,
                    prioridade_acao TEXT,
                    data_analise TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(talhao_id) REFERENCES talhoes(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nematoides_amostras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    talhao_id INTEGER,
                    ponto_id TEXT,
                    latitude REAL,
                    longitude REAL,
                    profundidade_cm INTEGER,
                    populacao_100g_solo REAL,
                    genero_predominante TEXT,
                    indice_gall REAL,
                    indice_meloidogyne REAL,
                    indice_pratylenchus REAL,
                    indice_heterodera REAL,
                    data_coleta TEXT,
                    FOREIGN KEY(talhao_id) REFERENCES talhoes(id)
                )
            """)

            # Inserir resultados por zona
            for zona_id, dados in resultado_cruzamento.items():
                cursor.execute("""
                    INSERT INTO nematoides_amostragem
                    (talhao_id, safra, zona_id, area_hectares, produtividade_sc_ha, 
                     ndvi_medio, populacao_nematoides_media, indice_risco, 
                     classificacao_risco, indice_composto_risco, recomendacao_manejo, 
                     prioridade_acao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    talhao_id, safra, zona_id,
                    dados.get("area_hectares", 0),
                    dados.get("produtividade_sc_ha", 0),
                    dados.get("ndvi_medio", 0),
                    dados["risco_nematoides"].get("populacao_media", 0),
                    dados["risco_nematoides"].get("indice_risco", 0),
                    dados["risco_nematoides"].get("classificacao_risco", ""),
                    dados["correlacao_produtividade_risco"].get("indice_composto_risco", 0),
                    dados.get("recomendacao_manejo", ""),
                    dados.get("prioridade_acao", "")
                ))

            # Inserir amostras individuais
            for amostra in self.amostras:
                cursor.execute("""
                    INSERT INTO nematoides_amostras
                    (talhao_id, ponto_id, latitude, longitude, profundidade_cm,
                     populacao_100g_solo, genero_predominante, indice_gall,
                     indice_meloidogyne, indice_pratylenchus, indice_heterodera)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    talhao_id, amostra.ponto_id, amostra.latitude, amostra.longitude,
                    amostra.profundidade_cm, amostra.populacao_nematoides_100g_solo,
                    amostra.genero_predominante, amostra.indice_gall,
                    amostra.indice_meloidogyne, amostra.indice_pratylenchus,
                    amostra.indice_heterodera
                ))

            conn.commit()
            return True

        except Exception as e:
            logging.info(f"[ERRO] Falha ao salvar amostragem dirigida: {e}")
            return False

    def exportar_csv(self, caminho_saida: str) -> str:
        """
        Exporta amostras para CSV.

        Args:
            caminho_saida: Caminho do arquivo CSV

        Returns:
            Caminho do arquivo gerado
        """
        if not self.amostras:
            return ""

        dados = []
        for a in self.amostras:
            dados.append({
                "ponto_id": a.ponto_id,
                "latitude": a.latitude,
                "longitude": a.longitude,
                "profundidade_cm": a.profundidade_cm,
                "populacao_100g_solo": a.populacao_nematoides_100g_solo,
                "genero_predominante": a.genero_predominante,
                "risco": self.classificar_risco(a.populacao_nematoides_100g_solo),
                "indice_gall": a.indice_gall,
                "indice_meloidogyne": a.indice_meloidogyne,
                "indice_pratylenchus": a.indice_pratylenchus,
                "indice_heterodera": a.indice_heterodera
            })

        df = pd.DataFrame(dados)
        df.to_csv(caminho_saida, index=False, sep=";", decimal=",")
        return caminho_saida


# ============================================================
# FUNCOES DE CONVENIENCIA
# ============================================================

def criar_amostragem_dirigida(
    cultura: str = "milho"
) -> AmostragemDirigida:
    """
    Cria instancia de AmostragemDirigida.

    Args:
        cultura: Nome da cultura

    Returns:
        Instancia de AmostragemDirigida
    """
    return AmostragemDirigida(cultura=cultura)


def analisar_risco_rapido(
    populacao_nematoides: float,
    cultura: str = "milho"
) -> str:
    """
    Classificacao rapida de risco por populacao.

    Args:
        populacao_nematoides: Populacao por 100g de solo
        cultura: Nome da cultura

    Returns:
        Classificacao de risco
    """
    ad = AmostragemDirigida(cultura)
    return ad.classificar_risco(populacao_nematoides)


def cruzar_dados_zona(
    zona_id: int,
    produtividade_sc_ha: float,
    ndvi_medio: float,
    amostras_nematoides: List[AmostraNematoides],
    area_ha: float = 0,
    cultura: str = "milho"
) -> Dict:
    """
    Funcao de conveniencia para cruzar dados de uma unica zona.

    Args:
        zona_id: ID da zona
        produtividade_sc_ha: Produtividade em sc/ha
        ndvi_medio: NDVI medio da zona
        amostras_nematoides: Lista de amostras
        area_ha: Area em hectares
        cultura: Nome da cultura

    Returns:
        Dict com resultado do cruzamento
    """
    ad = AmostragemDirigida(cultura)
    for a in amostras_nematoides:
        ad.adicionar_amostra(a)

    dados_prod = {zona_id: {"produtividade_sc_ha": produtividade_sc_ha, "ndvi_medio": ndvi_medio, "area_ha": area_ha}}
    dados_nem = {zona_id: amostras_nematoides}

    resultado = ad.cruzar_produtividade_risco(dados_prod, dados_nem)
    return resultado.get(zona_id, {})

