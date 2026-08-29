"""
Análise de fertilidade do solo - classificação geral e índices.
"""
from typing import Any, Dict, List, Optional

from .contratos import InterpretacaoNutriente
from .nutrientes import interpretar_nutriente


def classificar_fertilidade(
    teores: Dict[str, float],
    parametros: Dict[str, Any],
) -> str:
    """
    Classifica a fertilidade do solo (Baixa, Média, Alta) com base nos teores.
    
    Args:
        teores: Dicionário com teores de nutrientes (ex: {"p_mg": 15.0, "k_mg": 120.0})
        parametros: Parâmetros da metodologia incluindo limites críticos
    
    Returns:
        Classificação: "Baixa", "Média" ou "Alta"
    """
    # Obter interpretações para cada nutriente
    interpretacoes = []
    for nutriente, valor in teores.items():
        if valor > 0:  # Apenas nutrientes com valores positivos
            interpretacao = interpretar_nutriente(nutriente, valor, parametros)
            interpretacoes.append(interpretacao)
    
    # Calcular índice de fertilidade
    indice = _calcular_indice_fertilidade(interpretacoes)
    
    # Classificar com base no índice
    if indice < 0.33:
        return "Baixa"
    elif indice < 0.67:
        return "Média"
    else:
        return "Alta"


def _calcular_indice_fertilidade(interpretacoes: List[InterpretacaoNutriente]) -> float:
    """Calcula índice de fertilidade baseado nas interpretações."""
    if not interpretacoes:
        return 0.0
    
    # Mapeamento de classes para valores
    pesos = {
        "muito_baixo": 0.0,
        "baixo": 0.25,
        "muito_acido": 0.0,
        "acido": 0.25,
        "neutro": 0.5,
        "alcalino": 0.25,
        "medio": 0.5,
        "alto": 0.75,
        "muito_alto": 1.0,
    }
    
    # Calcular média ponderada
    soma = 0.0
    for interpretacao in interpretacoes:
        peso = pesos.get(interpretacao.classe, 0.5)
        soma += peso
    
    return soma / len(interpretacoes)


def calcular_indices_ubs(
    teores: Dict[str, float],
) -> Dict[str, float]:
    """
    Calcula índice de saturação por bases (V%).
    
    Args:
        teores: Dicionário com teores de Ca, Mg, Al, H
    
    Returns:
        Dicionário com índice V%
    """
    try:
        ca = teores.get("ca_cmolc", 0.0)
        mg = teores.get("mg_cmolc", 0.0)
        al = teores.get("al_cmolc", 0.0)
        h = teores.get("h_cmolc", 0.0)
        
        # Somatório de bases (Ca + Mg)
        bases = ca + mg
        
        # Somatório total (bases + Al + H)
        total = bases + al + h
        
        if total == 0:
            return {"v_percent": 0.0}
        
        v_percent = (bases / total) * 100
        
        return {"v_percent": v_percent}
    
    except (TypeError, ZeroDivisionError):
        return {"v_percent": 0.0}


def calcular_indices_aluminio(
    teores: Dict[str, float],
) -> Dict[str, float]:
    """
    Calcula índice de alumínio trocável.
    
    Args:
        teores: Dicionário com teores de Al, Ca, Mg
    
    Returns:
        Dicionário com índice m%
    """
    try:
        al = teores.get("al_cmolc", 0.0)
        ca = teores.get("ca_cmolc", 0.0)
        mg = teores.get("mg_cmolc", 0.0)
        
        # Somatório de bases (Ca + Mg)
        bases = ca + mg
        
        # Somatório total (bases + Al)
        total = bases + al
        
        if total == 0:
            return {"m_percent": 0.0}
        
        m_percent = (al / total) * 100
        
        return {"m_percent": m_percent}
    
    except (TypeError, ZeroDivisionError):
        return {"m_percent": 0.0}


def calcular_ctc_efetiva(
    teores: Dict[str, float],
) -> Dict[str, float]:
    """
    Calcula CTC efetiva (Ca + Mg + Al + H).
    
    Args:
        teores: Dicionário com teores de Ca, Mg, Al, H
    
    Returns:
        Dicionário com CTC efetiva
    """
    ca = teores.get("ca_cmolc", 0.0)
    mg = teores.get("mg_cmolc", 0.0)
    al = teores.get("al_cmolc", 0.0)
    h = teores.get("h_cmolc", 0.0)
    
    ctc_efetiva = ca + mg + al + h
    
    return {"ctc_efetiva_cmolc": ctc_efetiva}


def calcular_saturation_indices(
    teores: Dict[str, float],
) -> Dict[str, float]:
    """
    Calcula múltiplos índices de saturação.
    
    Args:
        teores: Dicionário com todos os teores do solo
    
    Returns:
        Dicionário com todos os índices calculados
    """
    indices = {}
    
    # Índice de saturação por bases (V%)
    v_percent = calcular_indices_ubs(teores)
    indices.update(v_percent)
    
    # Índice de alumínio trocável (m%)
    m_percent = calcular_indices_aluminio(teores)
    indices.update(m_percent)
    
    # CTC efetiva
    ctc_efetiva = calcular_ctc_efetiva(teores)
    indices.update(ctc_efetiva)
    
    return indices


def avaliar_acidez(
    teores: Dict[str, float],
    parametros: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Avalia acidez do solo e recomendações.
    
    Args:
        teores: Dicionário com teores do solo
        parametros: Parâmetros da metodologia
    
    Returns:
        Dicionário com avaliação e recomendações
    """
    resultado = {
        "ph": None,
        "v_percent": None,
        "al_percent": None,
        "classificacao": "",
        "recomendacao": "",
    }
    
    # Obter valores
    ph = teores.get("ph", 6.5)
    al_percent = calcular_indices_aluminio(teores).get("m_percent", 0.0)
    v_percent = calcular_indices_ubs(teores).get("v_percent", 100.0)
    
    resultado["ph"] = ph
    resultado["v_percent"] = v_percent
    resultado["al_percent"] = al_percent
    
    # Classificar acidez
    if ph < 5.0:
        resultado["classificacao"] = "Muito ácido"
        resultado["recomendacao"] = "Calagem urgente necessária"
    elif ph < 5.5:
        resultado["classificacao"] = "Ácido"
        resultado["recomendacao"] = "Calagem recomendada"
    elif ph < 6.5:
        resultado["classificacao"] = "Levemente ácido"
        resultado["recomendacao"] = "Calagem opcional"
    else:
        resultado["classificacao"] = "Neutro a alcalino"
        resultado["recomendacao"] = "Sem necessidade de calagem"
    
    return resultado