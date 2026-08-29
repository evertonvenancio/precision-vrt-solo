"""
Precision VRT Solo — Cálculos de Dose de Fertilizantes e Corretivos

Implementa cálculos de dose conforme metodologias agronômicas.
"""

from typing import Any, Dict
from ..configuracao import LIMITES_MICRO
from ..contratos import ResultadoCorretivo, StatusNutriente, ResultadoNutriente
from ..validacao import calcular_dose_corrigida


def _calcular_calagem(
    ph: float,
    v_percent: float,
    argila: float,
    ctc: float,
    config: Dict[str, Any],
    parametros: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Calcula a necessidade de calagem conforme metodologia selecionada.
    
    Formula base (metodo V% — IAC BT-100):
        NC (t/ha) = (V2 - V1) * CTC / 100 * fator_dg * profundidade / PRNT
    
    Onde:
        V2 = saturacao por bases desejada (%)
        V1 = saturacao por bases atual (%)
        CTC = capacidade de troca cationica efetiva (cmolc/dm3)
        fator_dg = fator de densidade do solo
        profundidade = profundidade de incorporacao (cm)
        PRNT = poder relativo de neutralizacao total (%)
    
    Args:
        ph: pH do solo (agua 1:2.5).
        v_percent: Saturacao por bases atual (%).
        argila: Teor de argila (%).
        ctc: CTC efetiva (cmolc/dm3).
        config: Configuração do motor.
        parametros: Parâmetros do método.
    
    Returns:
        Dict com dose, status, metodo e observacoes.
    """
    params = parametros["calagem"]
    meta_v = params["meta_v_percent"]
    fator_prnt = params["fator_prnt"]
    profundidade_cm = params["fator_profundidade_cm"]
    fator_dg = params["fator_dg"]
    ph_minimo = params["ph_minimo"]
    ph_alvo = params["ph_alvo"]
    v_minimo = params["v_minimo"]
    
    # Verificar se calagem e necessaria
    if v_percent >= meta_v and ph >= ph_minimo:
        return {
            "dose_t_ha": 0.0,
            "status": "Nao necessario",
            "metodo": "V%",
            "meta_v_percent": meta_v,
            "criterio": "Solo dentro dos parametros desejados",
            "observacao": (
                f"pH={ph:.1f} >= {ph_minimo} e V%={v_percent:.1f}% >= {meta_v}%. "
                "Calagem nao necessaria."
            ),
        }
    
    # Calcular necessidade de calagem
    # Formula: NC = (V_meta - V_atual) * CTC / 100 * dg * prof / PRNT
    delta_v = max(0.0, meta_v - v_percent)
    
    if delta_v <= 0:
        return {
            "dose_t_ha": 0.0,
            "status": "Nao necessario",
            "metodo": "V%",
            "meta_v_percent": meta_v,
            "criterio": "Saturacao por bases adequada",
            "observacao": f"V%={v_percent:.1f}% ja atinge a meta de {meta_v}%.",
        }
    
    # CTC em cmolc/dm3; se nao disponivel, usar estimativa baseada em argila
    ctc_efetiva = ctc if ctc > 0 else argila * 0.15
    
    # Dose em t/ha de calcario com PRNT = 100%
    # NC = delta_v * CTC / 100 * dg * prof / PRNT
    nc_base = (
        delta_v
        * ctc_efetiva
        / 100.0
        * fator_dg
        * (profundidade_cm / 20.0)  # Normalizado para 20 cm
    )
    
    # Ajustar pelo PRNT do calcario (PRNT padrao = 67%)
    prnt_usuario = config["prnt_percent"] / 100.0
    nc_corrigida = nc_base / prnt_usuario if prnt_usuario > 0 else nc_base
    
    # Ajustes por pH
    if ph < 5.0:
        nc_corrigida *= 1.3
    elif ph < 5.5:
        nc_corrigida *= 1.1
    
    # Ajuste por argila (solos argilosos necessitam mais calcario)
    if argila > 40.0:
        nc_corrigida *= 1.2
    
    dose_final = round(nc_corrigida, 2)
    
    return {
        "dose_t_ha": dose_final,
        "status": "Necessario" if dose_final > 0 else "Nao necessario",
        "metodo": "V%",
        "meta_v_percent": meta_v,
        "criterio": "Saturacao por bases",
        "observacao": (
            f"Calagem para elevar V% de {v_percent:.1f}% para {meta_v}%. "
            f"CTC={ctc_efetiva:.1f} cmolc/dm3, PRNT={config['prnt_percent']:.0f}%, "
            f"Profundidade={profundidade_cm:.0f} cm."
        ),
    }


def _calcular_gessagem(
    argila: float, 
    parametros: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calcula a necessidade de gessagem conforme metodologia selecionada.
    
    Formula (Embrapa / IAC):
        Dose (t/ha) = argila (%) * fator_dose
    
    Limites:
        - Argila minima para recomendacao: 30%
        - Dose minima: 0.5 t/ha
        - Dose maxima: 3.0 t/ha
    
    Args:
        argila: Teor de argila do solo (%).
        parametros: Parâmetros do método.
    
    Returns:
        Dict com dose, status, criterio e observacoes.
    """
    params = parametros["gessagem"]
    argila_minima = params["argila_minima_percent"]
    fator_dose = params["fator_dose"]
    dose_maxima = params["dose_maxima_t_ha"]
    dose_minima = params["dose_minima_t_ha"]
    
    if argila < argila_minima:
        return {
            "dose_t_ha": 0.0,
            "status": "Nao necessario",
            "criterio": "Teor de argila",
            "observacao": (
                f"Gessagem nao recomendada: argila={argila:.1f}% < "
                f"minimo={argila_minima:.0f}%."
            ),
        }
    
    # Dose proporcional ao teor de argila
    dose = argila * fator_dose
    
    # Aplicar limites
    dose = max(dose_minima, min(dose, dose_maxima))
    
    return {
        "dose_t_ha": round(dose, 2),
        "status": "Necessario",
        "criterio": "Condicionamento de subsolo",
        "observacao": (
            f"Gessagem recomendada para argila={argila:.1f}%. "
            f"Dose calculada: {dose:.2f} t/ha (limites: {dose_minima}-{dose_maxima} t/ha)."
        ),
    }


def _calcular_ca_necessidade(
    ca_mg: float, 
    v_percent: float
) -> float:
    """
    Calcula a necessidade de calcio em kg/ha.
    
    Criterio: Ca adequado se > 4.0 cmolc/dm3 e V% > 50%.
    Meta: 3.0 cmolc/dm3 (minimo desejavel).
    
    Args:
        ca_mg: Calcio trocavel (cmolc/dm3).
        v_percent: Saturacao por bases (%).
    
    Returns:
        Dose de Ca em kg/ha (0.0 se adequado).
    """
    if ca_mg > 4.0 and v_percent > 50.0:
        return 0.0
    
    meta_ca = 3.0  # cmolc/dm3
    if ca_mg >= meta_ca:
        return 0.0
    
    # Deficit em cmolc/dm3 -> kg/ha
    # 1 cmolc/dm3 de Ca = 400 kg/ha (aproximado para camada de 20 cm)
    deficit = meta_ca - ca_mg
    dose_kg_ha = deficit * 400.0
    
    return max(0.0, dose_kg_ha)


def _calcular_mg_necessidade(
    mg_mg: float, 
    v_percent: float
) -> float:
    """
    Calcula a necessidade de magnesio em kg/ha.
    
    Criterio: Mg adequado se > 1.0 cmolc/dm3 e V% > 50%.
    Meta: 0.8 cmolc/dm3 (minimo desejavel).
    
    Args:
        mg_mg: Magnesio trocavel (cmolc/dm3).
        v_percent: Saturacao por bases (%).
    
    Returns:
        Dose de Mg em kg/ha (0.0 se adequado).
    """
    if mg_mg > 1.0 and v_percent > 50.0:
        return 0.0
    
    meta_mg = 0.8  # cmolc/dm3
    if mg_mg >= meta_mg:
        return 0.0
    
    # Deficit em cmolc/dm3 -> kg/ha
    # 1 cmolc/dm3 de Mg = 240 kg/ha (aproximado para camada de 20 cm)
    deficit = meta_mg - mg_mg
    dose_kg_ha = deficit * 240.0
    
    return max(0.0, dose_kg_ha)


def _calcular_s_necessidade(
    s_mg: float, 
    exportacao_s: float
) -> float:
    """
    Calcula a necessidade de enxofre em kg/ha.
    
    Criterio: S adequado se > 10 mg/dm3.
    Se baixo: dose baseada na exportacao, com ajuste por nivel.
    
    Args:
        s_mg: Enxofre disponivel (mg/dm3).
        exportacao_s: Exportacao de S pela cultura (kg/ha).
    
    Returns:
        Dose de S em kg/ha.
    """
    if s_mg > 10.0:
        return 0.0
    
    dose = exportacao_s if exportacao_s > 0 else 10.0
    
    if s_mg < 5.0:
        dose *= 1.5
    
    return max(0.0, dose)


def _calcular_micronutrientes(
    perfil: Dict[str, Any],
    exportacao: Dict[str, float],
    config: Dict[str, Any],
    parametros: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """
    Calcula doses e status para todos os micronutrientes de uma zona.
    
    Args:
        perfil: Perfil da zona com medias dos atributos.
        exportacao: Exportacao de nutrientes pela cultura.
        config: Configuração do motor.
        parametros: Parâmetros do método.
    
    Returns:
        Dict com dose e status para cada micronutriente.
    """
    def get_media(attr: str) -> float:
        return perfil.get(attr, {}).get("media", 0.0)
    
    micros = {
        "b": ("b_mg_dm3", "B"),
        "cu": ("cu_mg_dm3", "Cu"),
        "fe": ("fe_mg_dm3", "Fe"),
        "mn": ("mn_mg_dm3", "Mn"),
        "zn": ("zn_mg_dm3", "Zn"),
    }
    
    resultados: Dict[str, Dict[str, Any]] = {}
    for key, (col, nutriente) in micros.items():
        valor_mg = get_media(col)
        exp = exportacao.get(nutriente, 0.0)
        dose = _calcular_micronutriente_individual(valor_mg, exp, nutriente)
        status = _classificar_status_micronutriente(valor_mg, nutriente)
        resultados[key] = {"dose": dose, "status": status}
    
    return resultados


def _calcular_micronutriente_individual(
    valor_mg: float,
    exportacao: float,
    nutriente: str,
) -> float:
    """
    Calcula dose para um micronutriente individual.
    
    Criterios:
        - Se valor > adequado * 2: nao necessita (solo suficiente)
        - Se valor >= adequado: manutencao (exportacao)
        - Se valor < adequado: correcao (exportacao * 1.5)
    
    Args:
        valor_mg: Teor do micronutriente no solo (mg/dm3).
        exportacao: Exportacao pela cultura (kg/ha).
        nutriente: Codigo do nutriente (B, Cu, Fe, Mn, Zn).
    
    Returns:
        Dose em kg/ha.
    """
    limites = LIMITES_MICRO.get(nutriente, LIMITES_MICRO["B"])
    adequado = limites["adequado"]
    
    if valor_mg > adequado * 2.0:
        return 0.0
    
    if valor_mg >= adequado:
        return exportacao if exportacao > 0 else 0.5
    
    return (exportacao if exportacao > 0 else 1.0) * 1.5