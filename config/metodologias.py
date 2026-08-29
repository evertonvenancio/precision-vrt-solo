"""
Precision VRT Solo — Dados de Domínio: Metodologias de Adubação e Calagem

Dados de domínio agronômico movidos de core/prescricao/configuracao.py para isolar
o core científico das informações específicas de metodologias.
"""

# ---------------------------------------------------------------------------#
# Parâmetros de calagem por metodologia                                     #
# Fonte: IAC BT-100; CFSEMG; Embrapa                                        #
# ---------------------------------------------------------------------------#
PARAMETROS_CALAGEM = {
    "IAC_Graos": {
        "meta_v_percent": 70.0,
        "fator_prnt": 0.67,
        "fator_profundidade_cm": 20.0,
        "fator_dg": 1.0,
        "formula": "SMP",
        "ph_minimo": 5.5,
        "ph_alvo": 6.0,
        "v_minimo": 50.0,
    },
    "CFSEMG": {
        "meta_v_percent": 60.0,
        "fator_prnt": 0.67,
        "fator_profundidade_cm": 20.0,
        "fator_dg": 1.0,
        "formula": "SMP",
        "ph_minimo": 5.5,
        "ph_alvo": 6.0,
        "v_minimo": 50.0,
    },
    "Embrapa_Soja": {
        "meta_v_percent": 65.0,
        "fator_prnt": 0.67,
        "fator_profundidade_cm": 20.0,
        "fator_dg": 1.0,
        "formula": "SMP",
        "ph_minimo": 5.5,
        "ph_alvo": 6.0,
        "v_minimo": 50.0,
    },
    "Embrapa_Milho": {
        "meta_v_percent": 70.0,
        "fator_prnt": 0.67,
        "fator_profundidade_cm": 20.0,
        "fator_dg": 1.0,
        "formula": "SMP",
        "ph_minimo": 5.5,
        "ph_alvo": 6.0,
        "v_minimo": 50.0,
    },
}

# ---------------------------------------------------------------------------#
# Parâmetros de gessagem por metodologia                                    #
# Fonte: Embrapa; IAC                                                       #
# ---------------------------------------------------------------------------#
PARAMETROS_GESSAGEM = {
    "IAC_Graos": {
        "argila_minima_percent": 30.0,
        "fator_dose": 0.5,
        "dose_maxima_t_ha": 3.0,
        "dose_minima_t_ha": 0.5,
    },
    "CFSEMG": {
        "argila_minima_percent": 30.0,
        "fator_dose": 0.5,
        "dose_maxima_t_ha": 3.0,
        "dose_minima_t_ha": 0.5,
    },
    "Embrapa_Soja": {
        "argila_minima_percent": 30.0,
        "fator_dose": 0.5,
        "dose_maxima_t_ha": 3.0,
        "dose_minima_t_ha": 0.5,
    },
    "Embrapa_Milho": {
        "argila_minima_percent": 30.0,
        "fator_dose": 0.5,
        "dose_maxima_t_ha": 3.0,
        "dose_minima_t_ha": 0.5,
    },
}

# ---------------------------------------------------------------------------#
# Parâmetros de macronutrientes por metodologia                             #
# ---------------------------------------------------------------------------#
PARAMETROS_MACRO = {
    "IAC_Graos": {
        "N": {"fator_classe_textural": {"arenoso": 1.2, "medio": 1.0, "argiloso": 0.9}},
        "P": {"fator_mehlich": 1.0, "fator_resina": 1.2},
        "K": {"fator_ctc": 1.0},
    },
    "CFSEMG": {
        "N": {"fator_classe_textural": {"arenoso": 1.2, "medio": 1.0, "argiloso": 0.9}},
        "P": {"fator_mehlich": 1.0, "fator_resina": 1.2},
        "K": {"fator_ctc": 1.0},
    },
    "Embrapa_Soja": {
        "N": {"fator_classe_textural": {"arenoso": 1.2, "medio": 1.0, "argiloso": 0.9}},
        "P": {"fator_mehlich": 1.0, "fator_resina": 1.2},
        "K": {"fator_ctc": 1.0},
    },
    "Embrapa_Milho": {
        "N": {"fator_classe_textural": {"arenoso": 1.2, "medio": 1.0, "argiloso": 0.9}},
        "P": {"fator_mehlich": 1.0, "fator_resina": 1.2},
        "K": {"fator_ctc": 1.0},
    },
}

# ---------------------------------------------------------------------------#
# Teores críticos de macronutrientes (classificação de status)              #
# Fonte: IAC BT-100; CFSEMG                                                 #
# ---------------------------------------------------------------------------#
TEORES_CRITICOS = {
    "N": {"muito_baixo": 0, "baixo": 30, "medio": 60, "alto": 100},
    "P": {"muito_baixo": 0, "baixo": 10, "medio": 20, "alto": 40},
    "K": {"muito_baixo": 0, "baixo": 30, "medio": 60, "alto": 100},
    "Ca": {"muito_baixo": 0, "baixo": 1.5, "medio": 3.0, "alto": 5.0},
    "Mg": {"muito_baixo": 0, "baixo": 0.5, "medio": 1.0, "alto": 2.0},
    "S": {"muito_baixo": 0, "baixo": 5, "medio": 10, "alto": 20},
}