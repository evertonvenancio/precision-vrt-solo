"""
Motor de Bulk Blend para composicao de misturas de fertilizantes.

Integra otimizacao via Programacao Linear (PuLP) como metodo principal,
com fallback automatico para o metodo heuristico caso o PuLP falhe
ou nao esteja instalado.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tentativa de importar o motor PuLP (graceful degradation)
# ---------------------------------------------------------------------------
try:
    from .otimizacao_pulp import OtimizadorMistura, Fertilizante, DemandaNutricional
    PULP_DISPONIVEL = True
except ImportError:
    PULP_DISPONIVEL = False
    logger.warning(
        "Modulo otimizacao_pulp nao encontrado. "
        "O sistema operara exclusivamente no modo heuristico."
    )


@dataclass
class RecomendacaoNutricional:
    """Demanda nutricional para um talhao ou lote.

    Attributes:
        n_kg_ha: Nitrogenio desejado (kg/ha).
        p2o5_kg_ha: Fosforo desejado (kg/ha).
        k2o_kg_ha: Potassio desejado (kg/ha).
        area_ha: Area do talhao em hectares.
    """
    n_kg_ha: float
    p2o5_kg_ha: float
    k2o_kg_ha: float
    area_ha: float

    @property
    def demanda_total(self) -> Dict[str, float]:
        """Retorna a demanda total em kg para a area informada."""
        return {
            "N": self.n_kg_ha * self.area_ha,
            "P2O5": self.p2o5_kg_ha * self.area_ha,
            "K2O": self.k2o_kg_ha * self.area_ha,
        }


@dataclass
class FertilizanteDisponivel:
    """Fertilizante disponivel no estoque para blending.

    Attributes:
        nome: Identificador do fertilizante.
        custo_kg: Custo por kg (R$/kg).
        composicao: Teores percentuais (ex: {"N": 45.0, "P2O5": 0.0, "K2O": 0.0}).
        sgn: Indice de compatibilidade fisica (granulometria).
        densidade: Densidade aparente (kg/L).
        inclusao_min_pct: Percentual minimo na mistura.
        inclusao_max_pct: Percentual maximo na mistura.
    """
    nome: str
    custo_kg: float
    composicao: Dict[str, float]
    sgn: float
    densidade: float
    inclusao_min_pct: float = 0.0
    inclusao_max_pct: float = 100.0


@dataclass
class ResultadoMistura:
    """Resultado da otimizacao de mistura.

    Attributes:
        composicao: Dict[nome_fertilizante, kg].
        custo_total: Custo total da mistura (R$).
        nutrientes_totais: Nutrientes totais fornecidos.
        pct_inclusao: Percentual de cada fertilizante na mistura.
        metodo: Metodo usado ("pulp" ou "heuristico").
        status: Status da otimizacao ("Optimal", "Heuristico", "Falha").
        compatibilidade: Nota de compatibilidade fisica (0 a 100).
        lotes: Lista de lotes gerados para aplicacao.
    """
    composicao: Dict[str, float] = field(default_factory=dict)
    custo_total: float = 0.0
    nutrientes_totais: Dict[str, float] = field(default_factory=dict)
    pct_inclusao: Dict[str, float] = field(default_factory=dict)
    metodo: str = "heuristico"
    status: str = "Falha"
    compatibilidade: float = 0.0
    lotes: List[Dict] = field(default_factory=list)


class OtimizadorBulkBlend:
    """Orquestrador de otimizacao de mistura de fertilizantes.

    Por padrao tenta usar o motor PuLP (programacao linear) para minimizar
    o custo. Se o PuLP falhar ou nao estiver disponivel, cai automaticamente
    para o metodo heuristico.

    Args:
        fertilizantes: Lista de fertilizantes disponiveis no estoque.
        usar_pulp: Se True, tenta otimizacao via PuLP primeiro.
        incompatibilidades: Lista de pares (A, B) que nao podem coexistir.
        capacidade_lote_kg: Capacidade maxima de cada lote (kg).
    """

    # Incompatibilidades quimicas padrao no sistema
    INCOMPATIBILIDADES_PADRAO: List[Tuple[str, str]] = [
        ("Ureia", "Superfosfato Simples"),
        ("Ureia", "Super Simples"),
    ]

    def __init__(
        self,
        fertilizantes: List[FertilizanteDisponivel],
        usar_pulp: bool = True,
        incompatibilidades: Optional[List[Tuple[str, str]]] = None,
        capacidade_lote_kg: float = 5000.0,
    ) -> None:
        self._fertilizantes = fertilizantes
        self._usar_pulp = usar_pulp and PULP_DISPONIVEL
        self._incompatibilidades = incompatibilidades or self.INCOMPATIBILIDADES_PADRAO
        self._capacidade_lote_kg = capacidade_lote_kg

    # ------------------------------------------------------------------
    # Metodo publico principal
    # ------------------------------------------------------------------

    def otimizar(
        self,
        recomendacao: RecomendacaoNutricional,
    ) -> ResultadoMistura:
        """Executa a otimizacao da mistura.

        Fluxo:
        1. Se usar_pulp=True e PuLP disponivel, tenta otimizacao via PL.
        2. Se PuLP falhar (status != "Optimal" ou excecao), loga e cai
           para o metodo heuristico.
        3. Apos definir a composicao, aplica validacao de compatibilidade
           fisica (SGN, densidade) e divide em lotes.

        Args:
            recomendacao: Demanda nutricional do talhao.

        Returns:
            ResultadoMistura com composicao, custo, lotes e metadados.
        """
        logger.info(
            "Iniciando otimizacao -- demanda: N=%.1f P2O5=%.1f K2O=%.1f kg | "
            "PuLP habilitado=%s",
            recomendacao.demanda_total.get("N", 0),
            recomendacao.demanda_total.get("P2O5", 0),
            recomendacao.demanda_total.get("K2O", 0),
            self._usar_pulp,
        )

        resultado = ResultadoMistura()

        # -------------------------------------------------------------
        # Tentativa 1: PuLP (se habilitado)
        # -------------------------------------------------------------
        if self._usar_pulp:
            try:
                resultado = self._otimizar_pulp(recomendacao)
                if resultado.status == "Optimal":
                    logger.info("Otimizacao PuLP bem-sucedida. Custo: R$ %.2f", resultado.custo_total)
                    # Aplica pos-processamento (compatibilidade + lotes)
                    resultado = self._pos_processar(resultado, recomendacao)
                    return resultado
                else:
                    logger.warning(
                        "PuLP retornou status '%s'. Caindo para heuristico...",
                        resultado.status,
                    )
            except Exception as exc:
                logger.exception("Falha no motor PuLP: %s. Caindo para heuristico...", exc)

        # -------------------------------------------------------------
        # Tentativa 2: Heuristico (fallback)
        # -------------------------------------------------------------
        logger.info("Executando metodo heuristico...")
        resultado = self._otimizar_heuristico(recomendacao)
        resultado.metodo = "heuristico"
        resultado.status = "Heuristico"

        # Aplica pos-processamento
        resultado = self._pos_processar(resultado, recomendacao)
        return resultado

    # ------------------------------------------------------------------
    # Motor PuLP
    # ------------------------------------------------------------------

    def _otimizar_pulp(
        self,
        recomendacao: RecomendacaoNutricional,
    ) -> ResultadoMistura:
        """Executa otimizacao via Programacao Linear usando PuLP.

        Args:
            recomendacao: Demanda nutricional.

        Returns:
            ResultadoMistura pre-preenchido com dados do PuLP.
        """
        demanda = DemandaNutricional(
            nutrientes=recomendacao.demanda_total,
            tolerancia_pct=5.0,
        )

        # Converte FertilizanteDisponivel -> Fertilizante (otimizacao_pulp)
        fertilizantes_pulp = [
            Fertilizante(
                nome=f.nome,
                custo_kg=f.custo_kg,
                composicao=f.composicao,
                inclusao_min_pct=f.inclusao_min_pct,
                inclusao_max_pct=f.inclusao_max_pct,
            )
            for f in self._fertilizantes
        ]

        motor = OtimizadorMistura(
            fertilizantes=fertilizantes_pulp,
            demanda=demanda,
            incompatibilidades=self._incompatibilidades,
        )

        solucao = motor.otimizar()

        if solucao is None:
            return ResultadoMistura(status="Falha_PuLP")

        return ResultadoMistura(
            composicao=solucao.get("composicao", {}),
            custo_total=solucao.get("custo_total", 0.0),
            nutrientes_totais=solucao.get("nutrientes_totais", {}),
            pct_inclusao=solucao.get("pct_inclusao", {}),
            metodo="pulp",
            status=solucao.get("status", "Desconhecido"),
        )

    # ------------------------------------------------------------------
    # Motor Heuristico (fallback)
    # ------------------------------------------------------------------

    def _otimizar_heuristico(
        self,
        recomendacao: RecomendacaoNutricional,
    ) -> ResultadoMistura:
        """Metodo heuristico de composicao de mistura.

        Algoritmo guloso: prioriza o fertilizante mais barato que supre
        cada nutriente, respeitando limites de inclusao.

        Args:
            recomendacao: Demanda nutricional.

        Returns:
            ResultadoMistura com composicao heuristicamente calculada.
        """
        demanda = recomendacao.demanda_total.copy()
        composicao: Dict[str, float] = {}

        # Ordena fertilizantes por custo/kg (mais baratos primeiro)
        candidatos = sorted(self._fertilizantes, key=lambda f: f.custo_kg)

        for nutriente in ["N", "P2O5", "K2O"]:
            falta = demanda.get(nutriente, 0.0)
            if falta <= 0:
                continue

            for fert in candidatos:
                if falta <= 0:
                    break

                teor = fert.composicao.get(nutriente, 0.0)
                if teor <= 0:
                    continue

                # Verifica incompatibilidades
                if self._tem_incompatibilidade(fert.nome, composicao):
                    continue

                # Calcula quantidade necessaria
                qtd_necessaria = (falta / (teor / 100.0))

                # Verifica limite maximo de inclusao
                total_atual = sum(composicao.values())
                if total_atual > 0:
                    pct_atual = (composicao.get(fert.nome, 0.0) / total_atual) * 100.0
                    pct_nova = ((composicao.get(fert.nome, 0.0) + qtd_necessaria) / (total_atual + qtd_necessaria)) * 100.0
                    if pct_nova > fert.inclusao_max_pct:
                        # Ajusta para respeitar o limite
                        max_qtd = (fert.inclusao_max_pct / 100.0) * total_atual - composicao.get(fert.nome, 0.0)
                        max_qtd = max(0, max_qtd)
                        qtd_necessaria = min(qtd_necessaria, max_qtd)

                if qtd_necessaria <= 0:
                    continue

                # Adiciona a composicao
                composicao[fert.nome] = composicao.get(fert.nome, 0.0) + qtd_necessaria
                falta -= (teor / 100.0) * qtd_necessaria

        # Calcula nutrientes totais atingidos
        nutrientes_totais: Dict[str, float] = {"N": 0.0, "P2O5": 0.0, "K2O": 0.0}
        for nome, qtd in composicao.items():
            fert = next((f for f in self._fertilizantes if f.nome == nome), None)
            if not fert:
                continue
            for nut in nutrientes_totais:
                nutrientes_totais[nut] += (fert.composicao.get(nut, 0.0) / 100.0) * qtd

        # Custo total
        custo_total = 0.0
        for nome, qtd in composicao.items():
            fert = next((f for f in self._fertilizantes if f.nome == nome), None)
            if fert:
                custo_total += fert.custo_kg * qtd

        # Percentuais de inclusao
        total_kg = sum(composicao.values())
        pct_inclusao = {n: round((q / total_kg) * 100.0, 2) for n, q in composicao.items()} if total_kg > 0 else {}

        return ResultadoMistura(
            composicao={k: round(v, 4) for k, v in composicao.items()},
            custo_total=round(custo_total, 2),
            nutrientes_totais={k: round(v, 4) for k, v in nutrientes_totais.items()},
            pct_inclusao=pct_inclusao,
            metodo="heuristico",
            status="Heuristico",
        )

    def _tem_incompatibilidade(
        self,
        nome_fert: str,
        composicao_atual: Dict[str, float],
    ) -> bool:
        """Verifica se adicionar um fertilizante viola incompatibilidades.

        Args:
            nome_fert: Nome do fertilizante candidato.
            composicao_atual: Composicao ja definida.

        Returns:
            True se houver incompatibilidade, False caso contrario.
        """
        for a, b in self._incompatibilidades:
            if nome_fert == a and b in composicao_atual and composicao_atual[b] > 0:
                return True
            if nome_fert == b and a in composicao_atual and composicao_atual[a] > 0:
                return True
        return False

    # ------------------------------------------------------------------
    # Pos-processamento (compatibilidade fisica + lotes)
    # ------------------------------------------------------------------

    def _pos_processar(
        self,
        resultado: ResultadoMistura,
        recomendacao: RecomendacaoNutricional,
    ) -> ResultadoMistura:
        """Aplica validacoes de compatibilidade fisica e divide em lotes.

        Args:
            resultado: Resultado da otimizacao (PuLP ou heuristico).
            recomendacao: Demanda nutricional original.

        Returns:
            ResultadoMistura atualizado com compatibilidade e lotes.
        """
        if not resultado.composicao:
            logger.warning("Composicao vazia apos otimizacao.")
            return resultado

        # Calcula compatibilidade fisica (SGN e densidade)
        resultado.compatibilidade = self._calcular_compatibilidade(resultado.composicao)

        # Divide em lotes
        resultado.lotes = self._dividir_lotes(resultado.composicao)

        logger.info(
            "Pos-processamento concluido -- Compatibilidade: %.1f%% | Lotes: %d",
            resultado.compatibilidade,
            len(resultado.lotes),
        )
        return resultado

    def _calcular_compatibilidade(self, composicao: Dict[str, float]) -> float:
        """Calcula nota de compatibilidade fisica (SGN e densidade).

        Args:
            composicao: Dict[nome, kg].

        Returns:
            Nota de 0 a 100. 100 = perfeita compatibilidade.
        """
        if not composicao:
            return 0.0

        total = sum(composicao.values())
        if total == 0:
            return 0.0

        # Media ponderada de SGN e densidade
        sgn_media = 0.0
        dens_media = 0.0
        for nome, qtd in composicao.items():
            fert = next((f for f in self._fertilizantes if f.nome == nome), None)
            if not fert:
                continue
            peso = qtd / total
            sgn_media += fert.sgn * peso
            dens_media += fert.densidade * peso

        # Coeficiente de variacao de SGN (quanto menor, melhor)
        sgn_vals = []
        for nome, qtd in composicao.items():
            fert = next((f for f in self._fertilizantes if f.nome == nome), None)
            if fert:
                sgn_vals.extend([fert.sgn] * int(qtd / 10 + 1))

        if len(sgn_vals) > 1:
            import statistics
            cv_sgn = (statistics.stdev(sgn_vals) / statistics.mean(sgn_vals)) * 100.0 if statistics.mean(sgn_vals) > 0 else 0.0
        else:
            cv_sgn = 0.0

        # Nota: 100 - penalidade pelo CV do SGN
        nota = max(0.0, 100.0 - cv_sgn * 2.0)
        return round(nota, 1)

    def _dividir_lotes(self, composicao: Dict[str, float]) -> List[Dict]:
        """Divide a mistura total em lotes de aplicacao.

        Args:
            composicao: Dict[nome, kg] da mistura total.

        Returns:
            Lista de lotes, cada um com composicao proporcional.
        """
        total_kg = sum(composicao.values())
        if total_kg == 0:
            return []

        num_lotes = max(1, int(total_kg / self._capacidade_lote_kg) + (1 if total_kg % self._capacidade_lote_kg > 0 else 0))

        lotes = []
        for i in range(num_lotes):
            lote = {
                "lote": i + 1,
                "total_kg": round(total_kg / num_lotes, 2),
                "composicao": {
                    nome: round(qtd / num_lotes, 4) for nome, qtd in composicao.items()
                },
            }
            lotes.append(lote)

        return lotes