"""Motor de otimização matemática de misturas de fertilizantes (PuLP).

Este módulo implementa o cálculo de mistura mínima de custo via
Programação Linear, usado pelo Precision VRT Solo nas estratégias
Bulk Blend e Sais Solúveis. Caso a dependência ``pulp`` não esteja
disponível, expõe a exceção :class:`OtimizadorIndisponivelError`
para que o Service Layer faça fallback para o método heurístico.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Fallback de importação do PuLP
# ---------------------------------------------------------------------------
try:  # pragma: no cover - executado em tempo de import
    import pulp  # type: ignore

    PULP_DISPONIVEL = True
except Exception as exc:  # pragma: no cover
    pulp = None  # type: ignore
    PULP_DISPONIVEL = False
    logger.warning("PuLP indisponível: %s. Usando fallback heurístico.", exc)


class OtimizadorIndisponivelError(RuntimeError):
    """Levantada quando o PuLP não está disponível ou o solver falha."""


# ---------------------------------------------------------------------------
# Estruturas de dados
# ---------------------------------------------------------------------------
NUTRIENTES_PADRAO: Tuple[str, ...] = (
    "N", "P2O5", "K2O", "Ca", "Mg", "S", "Micro",
)


@dataclass(frozen=True)
class Fertilizante:
    """Representa uma fonte fertilizante candidata à mistura.

    Attributes:
        codigo: Identificador único do fertilizante.
        nome: Nome comercial.
        preco_kg: Preço por kg em R$.
        composicao: Mapa nutriente -> teor (% massa, 0 a 100).
        limite_max_pct: Limite máximo de inclusão (% da mistura final),
            opcional. ``None`` significa sem limite.
        categoria: Rótulo livre, usado para regras (ex.: "micro").
    """

    codigo: str
    nome: str
    preco_kg: float
    composicao: Dict[str, float]
    limite_max_pct: Optional[float] = None
    categoria: Optional[str] = None


@dataclass
class ResultadoOtimizacao:
    """Resultado da otimização."""

    status: str
    custo_total: float
    quantidades: Dict[str, float] = field(default_factory=dict)
    atendimento: Dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Otimizador
# ---------------------------------------------------------------------------
class OtimizadorMistura:
    """Otimizador de misturas via Programação Linear (PuLP).

    A função objetivo minimiza o custo total da mistura para atender
    a demanda nutricional (em kg/ha) dentro de uma tolerância
    configurável e respeitando limites e incompatibilidades.
    """

    def __init__(
        self,
        tolerancia: float = 0.05,
        incompatibilidades: Optional[Sequence[Tuple[str, str]]] = None,
        limite_micro_pct: float = 5.0,
    ) -> None:
        """Inicializa o otimizador.

        Args:
            tolerancia: Tolerância simétrica para o atendimento da demanda
                (0.05 = ±5%).
            incompatibilidades: Pares ``(codigo_a, codigo_b)`` que não
                podem coexistir na mistura final.
            limite_micro_pct: Limite máximo (em %) para a soma das
                fontes da categoria ``"micro"``.

        Raises:
            OtimizadorIndisponivelError: Se o PuLP não estiver instalado.
        """
        if not PULP_DISPONIVEL:
            raise OtimizadorIndisponivelError(
                "Biblioteca PuLP indisponível no ambiente."
            )
        self.tolerancia = tolerancia
        self.incompatibilidades = list(incompatibilidades or [])
        self.limite_micro_pct = limite_micro_pct

    # ------------------------------------------------------------------
    def otimizar(
        self,
        demanda_nutricional: Dict[str, float],
        fertilizantes_disponiveis: Iterable[Fertilizante],
    ) -> ResultadoOtimizacao:
        """Resolve o problema de mistura de custo mínimo.

        Args:
            demanda_nutricional: Mapa nutriente -> kg/ha exigido.
            fertilizantes_disponiveis: Coleção de fontes candidatas.

        Returns:
            :class:`ResultadoOtimizacao` com quantidades (kg) por
            fertilizante, custo total e atendimento nutricional.

        Raises:
            OtimizadorIndisponivelError: Falha do solver ou solução
                inviável (cabe ao Service Layer acionar o heurístico).
        """
        fertilizantes = list(fertilizantes_disponiveis)
        if not fertilizantes:
            raise OtimizadorIndisponivelError("Lista de fertilizantes vazia.")

        prob = pulp.LpProblem("mistura_min_custo", pulp.LpMinimize)

        # Variáveis: quantidade (kg) de cada fertilizante
        x = {
            f.codigo: pulp.LpVariable(f"x_{f.codigo}", lowBound=0)
            for f in fertilizantes
        }
        # Variáveis binárias auxiliares para incompatibilidade
        y = {
            f.codigo: pulp.LpVariable(f"y_{f.codigo}", cat="Binary")
            for f in fertilizantes
        }

        # Função objetivo: custo total
        prob += pulp.lpSum(f.preco_kg * x[f.codigo] for f in fertilizantes)

        # Restrições nutricionais (com tolerância)
        for nutriente, demanda in demanda_nutricional.items():
            if demanda <= 0:
                continue
            aporte = pulp.lpSum(
                (f.composicao.get(nutriente, 0.0) / 100.0) * x[f.codigo]
                for f in fertilizantes
            )
            prob += aporte >= demanda * (1 - self.tolerancia), f"min_{nutriente}"
            prob += aporte <= demanda * (1 + self.tolerancia), f"max_{nutriente}"

        # Big-M para vincular x a y (x>0 => y=1)
        big_m = max(demanda_nutricional.values(), default=1.0) * 1000.0 + 1.0
        for f in fertilizantes:
            prob += x[f.codigo] <= big_m * y[f.codigo], f"link_{f.codigo}"

        # Incompatibilidades: y_a + y_b <= 1
        for a, b in self.incompatibilidades:
            if a in y and b in y:
                prob += y[a] + y[b] <= 1, f"incomp_{a}_{b}"

        # Limites máximos individuais (% da mistura)
        total = pulp.lpSum(x[f.codigo] for f in fertilizantes)
        for f in fertilizantes:
            if f.limite_max_pct is not None:
                prob += (
                    x[f.codigo] <= (f.limite_max_pct / 100.0) * total,
                    f"lim_{f.codigo}",
                )

        # Limite agregado para micronutrientes
        micros = [f for f in fertilizantes if (f.categoria or "").lower() == "micro"]
        if micros:
            prob += (
                pulp.lpSum(x[f.codigo] for f in micros)
                <= (self.limite_micro_pct / 100.0) * total,
                "lim_micro_total",
            )

        # Resolução
        try:
            solver = pulp.PULP_CBC_CMD(msg=False)
            prob.solve(solver)
        except Exception as exc:  # pragma: no cover
            logger.exception("Falha ao executar solver PuLP.")
            raise OtimizadorIndisponivelError(str(exc)) from exc

        status = pulp.LpStatus[prob.status]
        if status != "Optimal":
            logger.warning("Otimização não ótima: status=%s", status)
            raise OtimizadorIndisponivelError(f"Solução não ótima: {status}")

        quantidades = {
            f.codigo: float(pulp.value(x[f.codigo]) or 0.0) for f in fertilizantes
        }
        custo_total = float(pulp.value(prob.objective) or 0.0)
        atendimento = {
            nut: sum(
                (f.composicao.get(nut, 0.0) / 100.0) * quantidades[f.codigo]
                for f in fertilizantes
            )
            for nut in demanda_nutricional
        }

        logger.info(
            "Otimização concluída. Custo=%.2f, fontes=%d",
            custo_total,
            sum(1 for q in quantidades.values() if q > 1e-6),
        )
        return ResultadoOtimizacao(
            status=status,
            custo_total=custo_total,
            quantidades=quantidades,
            atendimento=atendimento,
        )


__all__ = [
    "Fertilizante",
    "OtimizadorMistura",
    "OtimizadorIndisponivelError",
    "ResultadoOtimizacao",
    "PULP_DISPONIVEL",
    "NUTRIENTES_PADRAO",
]
