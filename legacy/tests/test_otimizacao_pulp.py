"""Testes unitários do motor de otimização PuLP."""
from __future__ import annotations

import importlib
import sys
from typing import List

import pytest

from core import otimizacao_pulp as mod
from core.otimizacao_pulp import (
    Fertilizante,
    OtimizadorMistura,
)


def _fontes_basicas() -> List[Fertilizante]:
    return [
        Fertilizante("UREIA", "Ureia", preco_kg=3.0, composicao={"N": 45.0}),
        Fertilizante("SAM", "Sulfato de Amônio", preco_kg=2.5,
                     composicao={"N": 21.0, "S": 24.0}),
        Fertilizante("MAP", "MAP", preco_kg=5.0,
                     composicao={"N": 11.0, "P2O5": 52.0}),
    ]


def test_otimizacao_escolhe_fonte_mais_barata_para_n_e_p() -> None:
    otim = OtimizadorMistura(tolerancia=0.05)
    demanda = {"N": 50.0, "P2O5": 40.0}
    res = otim.otimizar(demanda, _fontes_basicas())

    assert res.status == "Optimal"
    # MAP é necessário para o P2O5
    assert res.quantidades["MAP"] > 0
    # Para o N restante, SAM (2,5/kg, 21% N) é mais barato por kg de N
    # do que ureia (3,0/kg, 45% N): 11,9 vs 6,67 -> ureia mais barata por kg-N
    assert res.quantidades["UREIA"] > 0
    # Atendimento dentro da tolerância
    assert 0.95 * 50.0 <= res.atendimento["N"] <= 1.05 * 50.0
    assert 0.95 * 40.0 <= res.atendimento["P2O5"] <= 1.05 * 40.0


def test_incompatibilidade_forca_exclusao_de_uma_fonte() -> None:
    fontes = [
        Fertilizante("NITROCAL", "Nitrato de Cálcio", preco_kg=4.0,
                     composicao={"N": 15.0, "Ca": 19.0}),
        Fertilizante("MAP", "MAP", preco_kg=5.0,
                     composicao={"N": 11.0, "P2O5": 52.0}),
        Fertilizante("UREIA", "Ureia", preco_kg=3.0, composicao={"N": 45.0}),
        Fertilizante("SSP", "Super Simples", preco_kg=2.0,
                     composicao={"P2O5": 18.0, "Ca": 20.0}),
    ]
    otim = OtimizadorMistura(
        tolerancia=0.05,
        incompatibilidades=[("NITROCAL", "MAP")],
    )
    res = otim.otimizar({"N": 40.0, "P2O5": 30.0, "Ca": 20.0}, fontes)

    assert res.status == "Optimal"
    usados = {k for k, v in res.quantidades.items() if v > 1e-3}
    # Não podem coexistir
    assert not ({"NITROCAL", "MAP"} <= usados)


def test_fallback_quando_pulp_indisponivel(monkeypatch: pytest.MonkeyPatch) -> None:
    # Simula ausência do PuLP recarregando o módulo com import bloqueado
    monkeypatch.setitem(sys.modules, "pulp", None)
    recarregado = importlib.reload(mod)
    try:
        assert recarregado.PULP_DISPONIVEL is False
        with pytest.raises(recarregado.OtimizadorIndisponivelError):
            recarregado.OtimizadorMistura()
    finally:
        # Restaura módulo original para os demais testes
        monkeypatch.delitem(sys.modules, "pulp", raising=False)
        importlib.reload(mod)
