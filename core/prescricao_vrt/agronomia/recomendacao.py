"""
Recomendação de adubação e calagem - cálculo de necessidade de corretivos.
"""
from typing import Any, Dict, List, Optional

from .contratos import InterpretacaoNutriente


def recomendar_calagem(
    ph: float,
    v_percent: float,
    ctc: float,
    meta_v_percent: float = 70.0,
    fator_calagem: float = 0.5,
    ph_limite_1: float = 5.0,
    ph_limite_2: float = 5.5,
    fator_ph_1: float = 1.3,
    fator_ph_2: float = 1.1,
    argila_limite: float = 40.0,
) -> Dict[str, Any]:
    """
    Recomenda calagem com base nos parâmetros da metodologia.
    
    Args:
        ph: pH do solo
        v_percent: Saturação por bases (%)
        ctc: CTC do solo (cmolc/dm³)
        meta_v_percent: Meta de saturação por bases (%)
        fator_calagem: Fator de calagem
        ph_limite_1, ph_limite_2: Limites de pH para ajuste
        fator_ph_1, fator_ph_2: Fatores de ajuste por pH
        argila_limite: Limite de argila para ajuste
    
    Returns:
        Dicionário com recomendação de calagem
    """
    recomendacao = {
        "necesidade_cal": 0.0,
        "tipo_cal": "",
        "dose_cal": 0.0,
        "justificativa": "",
        "urgencia": "",
    }
    
    # Ajustar por pH
    if ph < ph_limite_1:
        fator_ph = fator_ph_1
    elif ph < ph_limite_2:
        fator_ph = fator_ph_2
    else:
        fator_ph = 1.0
    
    # Calcular necessidade de calagem
    if v_percent < meta_v_percent:
        # Calcular déficit de V%
        deficit_v = meta_v_percent - v_percent
        
        # Calcular necessidade (kg/ha)
        recomendacao["necesidade_cal"] = deficit_v * ctc * fator_calagem * fator_ph
        
        # Determinar tipo de cal
        if ph < 5.0:
            recomendacao["tipo_cal"] = "carbonato de cálcio (CaCO3)"
            recomendacao["urgencia"] = "Urgente"
        elif ph < 5.5:
            recomendacao["tipo_cal"] = "carbonato de cálcio (CaCO3)"
            recomendacao["urgencia"] = "Necessária"
        else:
            recomendacao["tipo_cal"] = "carbonato de cálcio ou dolomita"
            recomendacao["urgencia"] = "Opcional"
        
        # Justificativa
        recomendacao["justificativa"] = (
            f"V% atual ({v_percent:.1f}) abaixo da meta ({meta_v_percent:.1f}). "
            f"Deficit de {deficit_v:.1f} pontos percentuais. "
            f"Ajustado por fator pH ({fator_ph:.2f})"
        )
    else:
        recomendacao["justificativa"] = "V% adequado para a cultura"
        recomendacao["urgencia"] = "Não necessária"
    
    return recomendacao


def recomendar_adubacao(
    nutriente: str,
    teor_atual: float,
    exportacao: float,
    eficiencia: float,
    parametros: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Recomenda adubação para um nutriente específico.
    
    Args:
        nutriente: Nome do nutriente (ex: "p_mg", "k_mg")
        teor_atual: Teor atual do solo
        exportacao: Exportação do nutriente (kg/ha)
        eficiencia: Fator de eficiência (0-1)
        parametros: Parâmetros do nutriente
    
    Returns:
        Dicionário com recomendação de adubação
    """
    recomendacao = {
        "nutriente": nutriente,
        "teor_atual": teor_atual,
        "exportacao": exportacao,
        "eficiencia": eficiencia,
        "dose_adubacao": 0.0,
        "forma_aplicacao": "",
        "justificativa": "",
        "urgencia": "",
    }
    
    # Cálculo básico de necessidade
    necessidade_adubacao = (exportacao - (teor_atual * 0.5)) / eficiencia
    
    if necessidade_adubacao > 0:
        recomendacao["dose_adubacao"] = necessidade_adubacao
        recomendacao["urgencia"] = "Necessária"
        
        # Determinar forma de aplicação
        if nutriente == "p_mg":
            recomendacao["forma_aplicacao"] = "adubado via solo (fosfato)"
        elif nutriente == "k_mg":
            recomendacao["forma_aplicacao"] = "adubado via solo (cloreto ou sulfato de K)"
        elif nutriente == "ca_cmolc":
            recomendacao["forma_aplicacao"] = "adubado via solo (gesso ou calcário)"
        elif nutriente == "mg_cmolc":
            recomendacao["forma_aplicacao"] = "adubado via solo (sulfato de Mg)"
        else:
            recomendacao["forma_aplicacao"] = "adubado via solo"
        
        # Justificativa
        recomendacao["justificativa"] = (
            f"Necessidade de adubação: {necessidade_adubacao:.1f} kg/ha "
            f"para compensar exportação de {exportacao:.1f} kg/ha"
        )
    else:
        recomendacao["justificativa"] = "Teor adequado para a cultura"
        recomendacao["urgencia"] = "Não necessária"
    
    return recomendacao


def recomendar_gessagem(
    argila_percent: float,
    al_percent: float,
    profundidade: float,
    parametros: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Recomenda gessagem com base nos parâmetros.
    
    Args:
        argila_percent: Percentual de argila no solo
        al_percent: Percentual de alumínio trocável
        profundidade: Profundidade de amostragem (cm)
        parametros: Parâmetros de gessagem
    
    Returns:
        Dicionário com recomendação de gessagem
    """
    recomendacao = {
        "necessidade_gesso": 0.0,
        "dose_gesso": 0.0,
        "profundidade_recomendada": profundidade,
        "justificativa": "",
        "urgencia": "",
    }
    
    # Obter parâmetros
    argila_minima_percent = parametros.get("argila_minima_percent", 30.0)
    fator_dose = parametros.get("fator_dose", 0.5)
    dose_maxima_t_ha = parametros.get("dose_maxima_t_ha", 3.0)
    dose_minima_t_ha = parametros.get("dose_minima_t_ha", 0.5)
    
    # Verificar necessidade
    if (argila_percent >= argila_minima_percent and al_percent > 0.2):
        # Calcular dose de gesso
        dose_base = (al_percent * fator_dose) * (argila_percent / 100)
        
        # Limitar dose
        dose_gesso = min(dose_base, dose_maxima_t_ha)
        dose_gesso = max(dose_gesso, dose_minima_t_ha)
        
        # Converter para kg/ha
        recomendacao["dose_gesso"] = dose_gesso * 1000
        recomendacao["necessidade_gesso"] = dose_gesso
        
        recomendacao["justificativa"] = (
            f"Alumínio trocável ({al_percent:.1f}%) em solo argiloso ({argila_percent:.1f}%). "
            f"Necessidade de gessagem para melhorar drenagem e reduzir toxidez de Al"
        )
        recomendacao["urgencia"] = "Necessária"
        
        # Ajustar profundidade recomendada
        if dose_gesso > 2.0:
            recomendacao["profundidade_recomendada"] = 30.0
        else:
            recomendacao["profundidade_recomendada"] = 20.0
    else:
        recomendacao["justificativa"] = (
            f"Sem necessidade de gessagem. "
            f"Argila ({argila_percent:.1f}%) ou alumínio ({al_percent:.1f}%) abaixo do limite crítico"
        )
        recomendacao["urgencia"] = "Não necessária"
    
    return recomendacao


def calcular_dose_fosforo(
    p_mg: float,
    textura: str,
    parametros: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Calcula dose de fósforo com base na textura e teor atual.
    
    Args:
        p_mg: Teor de P no solo (mg/dm³)
        textura: Classe textural (arenoso, medio, argiloso)
        parametros: Parâmetros de fósforo
    
    Returns:
        Dicionário com dose de P2O5 recomendada
    """
    recomendacao = {
        "p_atual": p_mg,
        "textura": textura,
        "dose_p2o5": 0.0,
        "justificativa": "",
        "classificacao": "",
    }
    
    # Obter parâmetros
    fatores_textura = parametros.get("fatores_textura", {})
    ph_minimo = parametros.get("ph_minimo", 5.5)
    fator_ph_baixo = parametros.get("fator_ph_baixo", 1.15)
    
    # Classificar o teor de P
    if p_mg < 5:
        classe = "Muito baixo"
        dose_base = 150
    elif p_mg < 10:
        classe = "Baixo"
        dose_base = 100
    elif p_mg < 20:
        classe = "Médio"
        dose_base = 50
    else:
        classe = "Alto"
        dose_base = 0
    
    # Ajustar por textura
    fator_textura = fatores_textura.get(textura, 1.0)
    
    # Ajustar por pH
    ph = 6.0  # Valor padrão, poderia vir do input
    if ph < ph_minimo:
        fator_ph = fator_ph_baixo
    else:
        fator_ph = 1.0
    
    # Calcular dose final
    dose_final = dose_base * fator_textura * fator_ph
    
    recomendacao["dose_p2o5"] = dose_final
    recomendacao["classificacao"] = classe
    recomendacao["justificativa"] = (
        f"Teor P atual: {p_mg:.1f} mg/dm³ ({classe}). "
        f"Ajustado por textura ({textura}: {fator_textura:.2f}) e pH ({fator_ph:.2f})"
    )
    
    return recomendacao


def gerar_recomendacoes_completas(
    teores: Dict[str, float],
    exportacao: Dict[str, float],
    eficiencias: Dict[str, float],
    parametros_calagem: Dict[str, Any],
    parametros_adubacao: Dict[str, Any],
    parametros_gessagem: Dict[str, Any],
    cultura: str = "soja",
    produtividade: float = 3.0,
) -> Dict[str, Any]:
    """
    Gera recomendações completas de calagem, adubação e gessagem.
    
    Args:
        teores: Teores do solo
        exportacao: Exportação de nutrientes
        eficiencias: Fatores de eficiência
        parametros_calagem: Parâmetros de calagem
        parametros_adubacao: Parâmetros de adubação
        parametros_gessagem: Parâmetros de gessagem
        cultura: Cultura alvo
        produtividade: Produtividade esperada
    
    Returns:
        Dicionário com todas as recomendações
    """
    resultado = {
        "cultura": cultura,
        "produtividade": produtividade,
        "calagem": {},
        "adubacao": {},
        "gessagem": {},
        "resumo": "",
        "custo_estimado": 0.0,
    }
    
    # Recomendação de calagem
    ph = teores.get("ph", 6.0)
    v_percent = calcular_indices_ubs(teores).get("v_percent", 100.0)
    ctc = calcular_ctc_efetiva(teores).get("ctc_efetiva_cmolc", 10.0)
    
    resultado["calagem"] = recomendar_calagem(ph, v_percent, ctc, parametros_calagem)
    
    # Recomendações de adubação por nutriente
    for nutriente in ["p_mg", "k_mg", "ca_cmolc", "mg_cmolc"]:
        if nutriente in teores and nutriente in exportacao and nutriente in eficiencias:
            resultado["adubacao"][nutriente] = recomendar_adubacao(
                nutriente,
                teores[nutriente],
                exportacao[nutriente],
                eficiencias[nutriente],
                parametros_adubacao.get(nutriente, {})
            )
    
    # Recomendação de gessagem
    argila_percent = teores.get("argila_percent", 20.0)
    al_percent = calcular_indices_aluminio(teores).get("m_percent", 0.0)
    profundidade = teores.get("profundidade_amostra_cm", 20.0)
    
    resultado["gessagem"] = recomendar_gessagem(
        argila_percent, al_percent, profundidade, parametros_gessagem
    )
    
    # Gerar resumo
    resultado["resumo"] = _gerar_resumo_recomendacoes(resultado)
    
    # Calcular custo estimado (simplificado)
    # Estoque de preços de fertilizantes (R$/kg)
    precos = {
        "p2o5": 6.0,
        "k2o": 5.0,
        "cao": 0.15,  # R$/kg calcário
        "cao": 0.20,  # R$/kg gesso
    }
    
    # Calcular custos
    custo_cal = resultado["calagem"].get("dose_cal", 0) * 0.15
    custo_adub = sum(
        recomendacao.get("dose_adubacao", 0) * 5.0
        for recomendacao in resultado["adubacao"].values()
    )
    custo_gesso = resultado["gessagem"].get("dose_gesso", 0) * 0.20
    
    resultado["custo_estimado"] = custo_cal + custo_adub + custo_gesso
    
    return resultado


def _gerar_resumo_recomendacoes(recomendacoes: Dict[str, Any]) -> str:
    """Gera resumo textual das recomendações."""
    resumo = []
    
    # Calagem
    cal = recomendacoes["calagem"]
    if cal["necesidade_cal"] > 0:
        resumo.append(f"Calagem: {cal['necesidade_cal']:.1f} kg/ha de {cal['tipo_cal']}")
    
    # Adubação
    adubacao = recomendacoes["adubacao"]
    for nutriente, rec in adubacao.items():
        if rec["dose_adubacao"] > 0:
            resumo.append(f"{nutriente}: {rec['dose_adubacao']:.1f} kg/ha")
    
    # Gessagem
    gesso = recomendacoes["gessagem"]
    if gesso["dose_gesso"] > 0:
        resumo.append(f"Gessagem: {gesso['dose_gesso']:.1f} kg/ha")
    
    if not resumo:
        return "Nenhuma recomendação necessária"
    
    return " | ".join(resumo)