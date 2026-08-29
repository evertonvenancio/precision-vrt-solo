"""
Análise de nutrientes - interpretação de teores do solo.
"""
from typing import Any, Dict, List, Optional

from .contratos import InterpretacaoNutriente


def interpretar_nutriente(
    nutriente: str,
    valor: float,
    parametros: Dict[str, Any],
) -> InterpretacaoNutriente:
    """
    Interpreta o teor de um nutriente com base nos parâmetros da metodologia.
    
    Args:
        nutriente: Nome do nutriente (ex: "p_mg", "k_mg", "ca_cmolc")
        valor: Teor do nutriente no solo
        parametros: Dicionário com limites críticos (ex: TEORES_CRITICOS)
    
    Returns:
        InterpretacaoNutriente com classe de status
    """
    # Criar objeto de interpretação
    interpretacao = InterpretacaoNutriente(
        nutriente=nutriente,
        valor=valor,
        unidade=_get_unidade_nutriente(nutriente)
    )
    
    # Obter limites críticos para o nutriente
    limites = parametros.get(nutriente, {})
    
    # Classificar o teor
    if not limites:
        # Se não tiver limites específicos, usar classificação padrão
        interpretacao.classe = _classificar_padrao(valor, nutriente)
    else:
        # Classificar com base nos limites fornecidos
        interpretacao.classe = _classificar_com_limites(valor, limites)
    
    interpretacao.metodo = parametros.get("metodo", "padrao")
    
    return interpretacao


def _get_unidade_nutriente(nutriente: str) -> str:
    """Retorna unidade padrão para o nutriente."""
    unidades = {
        "p_mg": "mg/dm³",
        "k_mg": "mg/dm³", 
        "ca_cmolc": "cmolc/dm³",
        "mg_cmolc": "cmolc/dm³",
        "al_cmolc": "cmolc/dm³",
        "h_cmolc": "cmolc/dm³",
        "v_percent": "%",
        "ph": "",
        "mo_percent": "%",
        "m_percent": "%",
        "argila_percent": "%",
        "silte_percent": "%",
        "areia_percent": "%",
    }
    return unidades.get(nutriente, "mg/dm³")


def _classificar_com_limites(valor: float, limites: Dict[str, float]) -> str:
    """Classifica o valor com base nos limites críticos."""
    # Formatos possíveis:
    # {"baixo": 10, "medio": 30, "alto": 50}
    # {"muito_baixo": 0, "baixo": 10, "medio": 20, "alto": 40}
    
    keys = sorted(limites.keys(), key=lambda x: limites[x])
    
    for i, status in enumerate(keys):
        if valor <= limites[status]:
            return status
    
    # Se for maior que todos os limites
    return keys[-1]


def _classificar_padrao(valor: float, nutriente: str) -> str:
    """Classificação padrão quando não há limites específicos."""
    # Valores aproximados para classificação geral
    limites_padrao = {
        "p_mg": {"muito_baixo": 5, "baixo": 10, "medio": 20, "alto": 40},
        "k_mg": {"muito_baixo": 30, "baixo": 60, "medio": 120, "alto": 200},
        "ca_cmolc": {"muito_baixo": 0.5, "baixo": 1.0, "medio": 2.0, "alto": 4.0},
        "mg_cmolc": {"muito_baixo": 0.2, "baixo": 0.5, "medio": 1.0, "alto": 2.0},
        "al_cmolc": {"muito_baixo": 0.1, "baixo": 0.3, "medio": 0.8, "alto": 2.0},
        "ph": {"muito_baixo": 4.5, "baixo": 5.0, "medio": 6.0, "alto": 7.0},
    }
    
    if nutriente in limites_padrao:
        return _classificar_com_limites(valor, limites_padrao[nutriente])
    else:
        # Classificação genérica para outros nutrientes
        if valor < 10:
            return "baixo"
        elif valor < 50:
            return "medio"
        else:
            return "alto"


def interpretar_ph(ph: float, metodo: str = "padrao") -> InterpretacaoNutriente:
    """Interpreta o pH do solo."""
    limites_ph = {
        "iac": {"muito_acido": 4.5, "acido": 5.0, "neutro": 6.5, "alcalino": 8.0},
        "cfsemg": {"muito_acido": 4.5, "acido": 5.0, "neutro": 6.5, "alcalino": 8.0},
        "padrao": {"muito_acido": 4.5, "acido": 5.5, "neutro": 6.5, "alcalino": 8.0},
    }
    
    return InterpretacaoNutriente(
        nutriente="ph",
        valor=ph,
        unidade="",
        classe=_classificar_com_limites(ph, limites_ph.get(metodo, limites_ph["padrao"])),
        metodo=metodo
    )


def interpretar_p_mg(p_mg: float, metodo: str = "padrao") -> InterpretacaoNutriente:
    """Interpreta o fósforo (mg/dm³)."""
    limites_p = {
        "iac": {"muito_baixo": 5, "baixo": 10, "medio": 20, "alto": 40},
        "cfsemg": {"muito_baixo": 3, "baixo": 6, "medio": 12, "alto": 24},
        "padrao": {"muito_baixo": 5, "baixo": 10, "medio": 20, "alto": 40},
    }
    
    return InterpretacaoNutriente(
        nutriente="p_mg",
        valor=p_mg,
        unidade="mg/dm³",
        classe=_classificar_com_limites(p_mg, limites_p.get(metodo, limites_p["padrao"])),
        metodo=metodo
    )


def interpretar_k_mg(k_mg: float, metodo: str = "padrao") -> InterpretacaoNutriente:
    """Interpreta o potássio (mg/dm³)."""
    limites_k = {
        "iac": {"muito_baixo": 30, "baixo": 60, "medio": 120, "alto": 200},
        "cfsemg": {"muito_baixo": 20, "baixo": 40, "medio": 80, "alto": 160},
        "padrao": {"muito_baixo": 30, "baixo": 60, "medio": 120, "alto": 200},
    }
    
    return InterpretacaoNutriente(
        nutriente="k_mg",
        valor=k_mg,
        unidade="mg/dm³",
        classe=_classificar_com_limites(k_mg, limites_k.get(metodo, limites_k["padrao"])),
        metodo=metodo
    )


def interpretar_ca_cmolc(ca_cmolc: float, metodo: str = "padrao") -> InterpretacaoNutriente:
    """Interpreta o cálcio (cmolc/dm³)."""
    limites_ca = {
        "iac": {"muito_baixo": 0.5, "baixo": 1.0, "medio": 2.0, "alto": 4.0},
        "cfsemg": {"muito_baixo": 0.5, "baixo": 1.0, "medio": 2.0, "alto": 4.0},
        "padrao": {"muito_baixo": 0.5, "baixo": 1.0, "medio": 2.0, "alto": 4.0},
    }
    
    return InterpretacaoNutriente(
        nutriente="ca_cmolc",
        valor=ca_cmolc,
        unidade="cmolc/dm³",
        classe=_classificar_com_limites(ca_cmolc, limites_ca.get(metodo, limites_ca["padrao"])),
        metodo=metodo
    )


def interpretar_mg_cmolc(mg_cmolc: float, metodo: str = "padrao") -> InterpretacaoNutriente:
    """Interpreta o magnésio (cmolc/dm³)."""
    limites_mg = {
        "iac": {"muito_baixo": 0.2, "baixo": 0.5, "medio": 1.0, "alto": 2.0},
        "cfsemg": {"muito_baixo": 0.2, "baixo": 0.5, "medio": 1.0, "alto": 2.0},
        "padrao": {"muito_baixo": 0.2, "baixo": 0.5, "medio": 1.0, "alto": 2.0},
    }
    
    return InterpretacaoNutriente(
        nutriente="mg_cmolc",
        valor=mg_cmolc,
        unidade="cmolc/dm³",
        classe=_classificar_com_limites(mg_cmolc, limites_mg.get(metodo, limites_mg["padrao"])),
        metodo=metodo
    )