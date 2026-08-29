"""
Servico de alto nivel para calculo de mistura Bulk Blend.

Este modulo atua como facade entre a interface do usuario (Streamlit/app.py)
e o motor de otimizacao (core/bulk_blend.py). Responsavel por:
- Converter prescricoes agronomicas em demandas nutricionais
- Gerenciar configuracoes do tenant (capacidade do misturador)
- Orquestrar o processo de otimizacao
- Persistir resultados e gerar relatorios
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from config.fertilizantes_fisicos import CatalogoFertilizantes
from core.bulk_blend import (
    OtimizadorBulkBlend,
    RecomendacaoNutricional,
    FertilizanteDisponivel,
    ResultadoMistura,
)

logger = logging.getLogger(__name__)


class TipoPrescricao(Enum):
    """Tipos de prescricao suportados."""
    VRT = "vrt"           # Taxa variavel
    UNIFORME = "uniforme" # Dose unica
    ZONADA = "zonada"     # Por zonas de manejo


@dataclass
class PrescricaoNutricional:
    """Representa uma prescricao nutricional convertida para demanda.

    Attributes:
        prescricao_id: ID da prescricao no banco de dados.
        zona_id: Identificador da zona/talhao.
        area_ha: Area em hectares.
        dose_kg_ha: Dose recomendada em kg/ha.
        nutrientes_kg_ha: Demanda de cada nutriente em kg/ha.
        cultura: Nome da cultura.
        metodologia: Metodologia de calculo utilizada.
        fontes_preferenciais: Lista de codigos de fertilizantes preferenciais.
    """
    prescricao_id: int
    zona_id: str
    area_ha: float
    dose_kg_ha: float
    nutrientes_kg_ha: Dict[str, float]
    cultura: str = ""
    metodologia: str = ""
    fontes_preferenciais: List[str] = field(default_factory=list)

    @property
    def peso_total_kg(self) -> float:
        """Peso total necessario em kg."""
        return self.area_ha * self.dose_kg_ha

    @property
    def demanda_por_tonelada(self) -> Dict[str, float]:
        """Converte demanda kg/ha para kg por tonelada de blend.

        Considera que 1 tonelada de blend deve conter os nutrientes
        proporcionais a dose recomendada.
        """
        if self.dose_kg_ha <= 0:
            return {}
        # kg de nutriente por tonelada = (kg/ha / dose_kg_ha) * 1000
        return {
            nut: (quantidade / self.dose_kg_ha) * 1000.0
            for nut, quantidade in self.nutrientes_kg_ha.items()
            if quantidade > 0
        }


@dataclass
class ConfigTenant:
    """Configuracoes fisicas do equipamento do tenant.

    Attributes:
        capacidade_misturador_kg: Capacidade maxima do misturador em kg.
        tempo_mistura_min: Tempo de mistura em minutos.
        tolerancia_nutricional_pct: Tolerancia de atendimento da demanda.
        custo_mao_obra_hora: Custo da mao de obra em R$/hora.
        custo_energia_kwh: Custo da energia em R$/kWh.
        consumo_energia_mistura_kwh: Consumo de energia por mistura em kWh.
        catalogo_customizado: Catalogo de fertilizantes customizado (None = padrao).
    """
    capacidade_misturador_kg: float = 3000.0
    tempo_mistura_min: float = 5.0
    tolerancia_nutricional_pct: float = 5.0
    custo_mao_obra_hora: float = 25.0
    custo_energia_kwh: float = 0.80
    consumo_energia_mistura_kwh: float = 2.5
    catalogo_customizado: Optional[CatalogoFertilizantes] = None

    @property
    def custo_operacional_por_lote(self) -> float:
        """Custo operacional estimado por lote em R$."""
        custo_mo = (self.tempo_mistura_min / 60.0) * self.custo_mao_obra_hora
        custo_energia = self.consumo_energia_mistura_kwh * self.custo_energia_kwh
        return custo_mo + custo_energia


@dataclass
class RelatorioBlend:
    """Relatorio completo do processo de blend.

    Attributes:
        prescricao: Dados da prescricao original.
        config: Configuracoes do tenant utilizadas.
        resultado: Resultado da otimizacao.
        custo_total_incl_operacional: Custo total incluindo operacao.
        data_geracao: Data/hora da geracao.
        observacoes: Observacoes tecnicas.
    """
    prescricao: PrescricaoNutricional
    config: ConfigTenant
    resultado: ResultadoMistura
    custo_total_incl_operacional: float = 0.0
    data_geracao: datetime = field(default_factory=datetime.now)
    observacoes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serializa relatorio para dicionario."""
        return {
            "prescricao": {
                "prescricao_id": self.prescricao.prescricao_id,
                "zona_id": self.prescricao.zona_id,
                "area_ha": self.prescricao.area_ha,
                "dose_kg_ha": self.prescricao.dose_kg_ha,
                "peso_total_kg": self.prescricao.peso_total_kg,
                "nutrientes_kg_ha": self.prescricao.nutrientes_kg_ha,
                "cultura": self.prescricao.cultura,
                "metodologia": self.prescricao.metodologia,
            },
            "config": {
                "capacidade_misturador_kg": self.config.capacidade_misturador_kg,
                "tempo_mistura_min": self.config.tempo_mistura_min,
                "tolerancia_nutricional_pct": self.config.tolerancia_nutricional_pct,
                "custo_operacional_por_lote": round(self.config.custo_operacional_por_lote, 2),
            },
            "resultado": {
                "composicao": self.resultado.composicao,
                "custo_total": self.resultado.custo_total,
                "nutrientes_totais": self.resultado.nutrientes_totais,
                "pct_inclusao": self.resultado.pct_inclusao,
                "metodo": self.resultado.metodo,
                "status": self.resultado.status,
                "compatibilidade": self.resultado.compatibilidade,
                "lotes": self.resultado.lotes,
            },
            "custo_total_incl_operacional": round(self.custo_total_incl_operacional, 2),
            "data_geracao": self.data_geracao.isoformat(),
            "observacoes": self.observacoes,
        }


class BulkBlendService:
    """Servico de alto nivel para calculo de misturas Bulk Blend.

    Responsavel por orquestrar todo o fluxo desde a prescricao nutricional
    ate o relatorio final de blend, incluindo validacoes, otimizacao e
    analise de custos.

    Args:
        config: Configuracoes do tenant. Usa padrao se None.
        catalogo: Catalogo de fertilizantes. Usa padrao se None.

    Example:
        >>> service = BulkBlendService()
        >>> prescricao = PrescricaoNutricional(
        ...     prescricao_id=1,
        ...     zona_id="A1",
        ...     area_ha=50.0,
        ...     dose_kg_ha=500.0,
        ...     nutrientes_kg_ha={"N": 80, "P2O5": 60, "K2O": 40}
        ... )
        >>> relatorio = service.processar_prescricao(prescricao)
    """

    def __init__(
        self,
        config: Optional[ConfigTenant] = None,
        catalogo: Optional[CatalogoFertilizantes] = None,
    ):
        self._config = config or ConfigTenant()
        self._catalogo = catalogo or self._config.catalogo_customizado or CatalogoFertilizantes()
        logger.info(
            "BulkBlendService inicializado. Capacidade=%.1fkg, Catalogo=%d fertilizantes",
            self._config.capacidade_misturador_kg,
            len(self._catalogo.listar_todos())
        )

    # ============================================================
    # METODOS PUBLICOS PRINCIPAIS
    # ============================================================

    def processar_prescricao(
        self,
        prescricao: PrescricaoNutricional,
        usar_fontes_preferenciais: bool = True,
    ) -> RelatorioBlend:
        """Processa uma prescricao nutricional completa.

        Fluxo:
        1. Valida a prescricao
        2. Converte para demanda por tonelada
        3. Filtra fertilizantes (preferenciais ou todos)
        4. Executa otimizacao
        5. Calcula custos operacionais
        6. Gera relatorio com observacoes

        Args:
            prescricao: Dados da prescricao nutricional.
            usar_fontes_preferenciais: Se True, prioriza fertilizantes da lista
                prescricao.fontes_preferenciais.

        Returns:
            RelatorioBlend completo com resultado e metadados.
        """
        logger.info(
            "Processando prescricao %s zona %s: %.1fha @ %.1fkg/ha",
            prescricao.prescricao_id,
            prescricao.zona_id,
            prescricao.area_ha,
            prescricao.dose_kg_ha
        )

        # Validar prescricao
        observacoes = self._validar_prescricao(prescricao)

        # Converter demanda
        demanda = prescricao.demanda_por_tonelada
        if not demanda:
            logger.error("Demanda vazia apos conversao da prescricao.")
            return self._relatorio_erro(
                prescricao,
                "Nao foi possivel converter a prescricao em demanda nutricional. "
                "Verifique dose_kg_ha e nutrientes_kg_ha."
            )

        logger.debug("Demanda por tonelada: %s", demanda)

        # Filtrar fertilizantes
        fontes = self._selecionar_fontes(
            prescricao,
            usar_preferenciais=usar_fontes_preferenciais
        )

        # Converter catalogo para FertilizanteDisponivel
        fertilizantes = self._converter_catalogo(fontes)

        if not fertilizantes:
            return self._relatorio_erro(
                prescricao,
                "Nenhum fertilizante disponivel no catalogo."
            )

        # Executar otimizacao
        otimizador = OtimizadorBulkBlend(
            fertilizantes=fertilizantes,
            usar_pulp=True,
            capacidade_lote_kg=self._config.capacidade_misturador_kg,
        )

        recomendacao = RecomendacaoNutricional(
            n_kg_ha=prescricao.nutrientes_kg_ha.get("N", 0.0),
            p2o5_kg_ha=prescricao.nutrientes_kg_ha.get("P2O5", 0.0),
            k2o_kg_ha=prescricao.nutrientes_kg_ha.get("K2O", 0.0),
            area_ha=prescricao.area_ha,
        )

        resultado = otimizador.otimizar(recomendacao)

        # Calcular custos operacionais
        custo_operacional = self._calcular_custo_operacional(resultado)
        custo_total = resultado.custo_total + custo_operacional

        # Gerar observacoes tecnicas
        observacoes.extend(self._gerar_observacoes(prescricao, resultado))

        relatorio = RelatorioBlend(
            prescricao=prescricao,
            config=self._config,
            resultado=resultado,
            custo_total_incl_operacional=custo_total,
            observacoes=observacoes,
        )

        logger.info(
            "Prescricao %s processada. Status=%s, Lotes=%d, CustoTotal=R$%.2f",
            prescricao.prescricao_id,
            resultado.status,
            len(resultado.lotes),
            custo_total
        )
        return relatorio

    def calcular_blend(
        self,
        prescricao_id: int,
        zona_id: str,
        area_ha: float,
        dose_kg_ha: float,
        nutrientes_kg_ha: Dict[str, float],
        cultura: str = "",
        metodologia: str = "",
        fontes_preferenciais: Optional[List[str]] = None,
    ) -> RelatorioBlend:
        """Metodo convenience que cria a prescricao e processa.

        Args:
            prescricao_id: ID da prescricao.
            zona_id: Identificador da zona.
            area_ha: Area em hectares.
            dose_kg_ha: Dose recomendada em kg/ha.
            nutrientes_kg_ha: Dicionario com nutrientes em kg/ha.
            cultura: Nome da cultura.
            metodologia: Metodologia utilizada.
            fontes_preferenciais: Lista de codigos de fertilizantes preferidos.

        Returns:
            RelatorioBlend completo.
        """
        prescricao = PrescricaoNutricional(
            prescricao_id=prescricao_id,
            zona_id=zona_id,
            area_ha=area_ha,
            dose_kg_ha=dose_kg_ha,
            nutrientes_kg_ha=nutrientes_kg_ha,
            cultura=cultura,
            metodologia=metodologia,
            fontes_preferenciais=fontes_preferenciais or [],
        )
        return self.processar_prescricao(prescricao)

    def calcular_blend_multiplas_zonas(
        self,
        prescricoes: List[PrescricaoNutricional],
    ) -> List[RelatorioBlend]:
        """Processa multiplas prescricoes/zonas em lote.

        Args:
            prescricoes: Lista de prescricoes nutricionais.

        Returns:
            Lista de relatorios, um por prescricao.
        """
        logger.info("Processando %d zonas em lote.", len(prescricoes))
        relatorios = []
        for presc in prescricoes:
            try:
                rel = self.processar_prescricao(presc)
                relatorios.append(rel)
            except Exception as e:
                logger.exception("Erro ao processar zona %s: %s", presc.zona_id, e)
                relatorios.append(self._relatorio_erro(presc, str(e)))
        return relatorios

    def comparar_cenarios(
        self,
        prescricao: PrescricaoNutricional,
        cenarios: List[Dict[str, Any]],
    ) -> List[RelatorioBlend]:
        """Compara multiplos cenarios de configuracao para a mesma prescricao.

        Args:
            prescricao: Prescricao base.
            cenarios: Lista de dicionarios com overrides de ConfigTenant.
                Ex: [{"capacidade_misturador_kg": 1500}, {"capacidade_misturador_kg": 5000}]

        Returns:
            Lista de relatorios, um por cenario.
        """
        relatorios = []
        for i, cenario in enumerate(cenarios):
            logger.info("Processando cenario %d: %s", i + 1, cenario)
            config_override = self._aplicar_override_config(cenario)
            service = BulkBlendService(config=config_override, catalogo=self._catalogo)
            rel = service.processar_prescricao(prescricao)
            rel.observacoes.insert(0, f"[CENARIO {i+1}] Config: {cenario}")
            relatorios.append(rel)
        return relatorios

    def listar_fontes_recomendadas(
        self,
        nutriente: str,
        min_teor: float = 1.0,
        top_n: int = 5,
    ) -> List[Dict[str, Any]]:
        """Lista as fontes mais recomendadas para um nutriente.

        Args:
            nutriente: Sigla do nutriente (ex: "N", "P2O5").
            min_teor: Teor minimo percentual.
            top_n: Numero maximo de resultados.

        Returns:
            Lista de dicionarios com dados dos fertilizantes.
        """
        fontes = self._catalogo.por_nutriente(nutriente, min_teor)
        return [
            {
                "codigo": f.codigo,
                "nome": f.nome,
                f"teor_{nutriente}": f.composicao.get(nutriente, 0.0),
                "custo_kg": f.custo_kg,
                "custo_por_kg_nutriente": round(
                    f.custo_kg / max(f.composicao.get(nutriente, 0.0) / 100.0, 0.001), 2
                ),
                "sgn": f.sgn,
                "densidade": f.densidade_aparente,
            }
            for f in fontes[:top_n]
        ]

    # ============================================================
    # METODOS PRIVADOS
    # ============================================================

    def _converter_catalogo(self, fontes: Optional[List[str]]) -> List[FertilizanteDisponivel]:
        """Converte fertilizantes do catalogo para FertilizanteDisponivel."""
        todos = self._catalogo.listar_todos()
        if fontes:
            todos = [f for f in todos if f.codigo in fontes]

        return [
            FertilizanteDisponivel(
                nome=f.nome,
                custo_kg=f.custo_kg,
                composicao=f.composicao,
                sgn=f.sgn,
                densidade=f.densidade_aparente,
                inclusao_min_pct=0.0,
                inclusao_max_pct=100.0,
            )
            for f in todos
        ]

    def _validar_prescricao(self, prescricao: PrescricaoNutricional) -> List[str]:
        """Valida a prescricao e retorna observacoes."""
        observacoes = []

        if prescricao.area_ha <= 0:
            observacoes.append("ERRO: Area deve ser maior que zero.")
        if prescricao.dose_kg_ha <= 0:
            observacoes.append("ERRO: Dose deve ser maior que zero.")
        if not prescricao.nutrientes_kg_ha:
            observacoes.append("ERRO: Nutrientes nao especificados.")

        peso_total = prescricao.peso_total_kg
        if peso_total > self._config.capacidade_misturador_kg * 10:
            observacoes.append(
                f"ALERTA: Peso total ({peso_total:.0f}kg) muito elevado. "
                f"Serao necessarios {math.ceil(peso_total / self._config.capacidade_misturador_kg)} lotes."
            )

        # Verificar se nutrientes estao dentro de faixas razoaveis
        for nut, val in prescricao.nutrientes_kg_ha.items():
            if val < 0:
                observacoes.append(f"ERRO: {nut} nao pode ser negativo.")
            elif val > 500:
                observacoes.append(f"ALERTA: {nut}={val}kg/ha parece excessivo. Verificar.")

        return observacoes

    def _selecionar_fontes(
        self,
        prescricao: PrescricaoNutricional,
        usar_preferenciais: bool,
    ) -> Optional[List[str]]:
        """Seleciona fontes de fertilizantes disponiveis."""
        if usar_preferenciais and prescricao.fontes_preferenciais:
            # Validar se todos os preferenciais existem
            validos = []
            for cod in prescricao.fontes_preferenciais:
                if self._catalogo.get(cod):
                    validos.append(cod)
                else:
                    logger.warning("Fonte preferencial %s nao encontrada no catalogo.", cod)
            if validos:
                logger.info("Usando %d fontes preferenciais.", len(validos))
                return validos
            logger.warning("Nenhuma fonte preferencial valida. Usando catalogo completo.")
        return None  # None = usar todos

    def _calcular_custo_operacional(self, resultado: ResultadoMistura) -> float:
        """Calcula o custo operacional total (mo + energia)."""
        return self._config.custo_operacional_por_lote * len(resultado.lotes)

    def _gerar_observacoes(
        self,
        prescricao: PrescricaoNutricional,
        resultado: ResultadoMistura,
    ) -> List[str]:
        """Gera observacoes tecnicas baseadas no resultado."""
        obs = []

        # Observacoes sobre o blend
        obs.append(
            f"Blend para {prescricao.cultura or 'cultura nao especificada'} "
            f"- Zona {prescricao.zona_id}"
        )
        obs.append(
            f"Dose: {prescricao.dose_kg_ha:.1f} kg/ha | "
            f"Area: {prescricao.area_ha:.1f} ha | "
            f"Peso total: {prescricao.peso_total_kg:.1f} kg"
        )

        if len(resultado.lotes) > 1:
            obs.append(
                f"Mistura fracionada em {len(resultado.lotes)} lotes."
            )

        # Analise garantida
        if resultado.nutrientes_totais:
            analise_str = ", ".join(
                f"{k}={v:.2f}kg" for k, v in resultado.nutrientes_totais.items()
            )
            obs.append(f"Nutrientes totais: {analise_str}")

        # Custos
        obs.append(
            f"Custo do blend: R$ {resultado.custo_total:,.2f} | "
            f"Metodo: {resultado.metodo} | Status: {resultado.status}"
        )

        custo_op = self._calcular_custo_operacional(resultado)
        obs.append(
            f"Custo operacional (mistura): R$ {custo_op:,.2f} "
            f"({len(resultado.lotes)} lote(s) x R$ {self._config.custo_operacional_por_lote:.2f})"
        )

        # Compatibilidade
        obs.append(
            f"Compatibilidade fisica: {resultado.compatibilidade:.1f}%"
        )

        return obs

    def _relatorio_erro(
        self,
        prescricao: PrescricaoNutricional,
        mensagem: str,
    ) -> RelatorioBlend:
        """Cria um relatorio de erro."""
        resultado_erro = ResultadoMistura(
            status="Erro",
            metodo="nenhum",
        )
        return RelatorioBlend(
            prescricao=prescricao,
            config=self._config,
            resultado=resultado_erro,
            observacoes=[f"ERRO: {mensagem}"],
        )

    def _aplicar_override_config(self, overrides: Dict[str, Any]) -> ConfigTenant:
        """Cria uma nova config com overrides aplicados."""
        import copy
        config = copy.deepcopy(self._config)
        for key, value in overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                logger.warning("Override de config desconhecido: %s", key)
        return config
