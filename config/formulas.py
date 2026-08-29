# config/formulas.py
# Biblioteca Expandida de Metodologias Agronomicas - Precision VRT Solo

FORMULAS = {
    # --- REGIAO SUDESTE (SP, MG, ES, RJ) ---
    "IAC_Graos": {
        "nome": "IAC - Graos (Milho/Soja)",
        "regiao": "Sudeste",
        "calagem": {"metodo": "V%", "meta_v_padrao": 70, "fator_calagem": 0.5,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 3.0, "medio": 5.0, "argiloso": 8.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 50},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Baseia-se na elevacao da saturacao por bases (V%) ate a meta regional e na reposicao de fosforo conforme a textura do solo. "
            "A calagem corrige a acidez e aumenta a disponibilidade de Ca e Mg, enquanto o P e ajustado por classes de textura."
        ),
        "bibliografia": "RAIJ, B. van; CANTARELLA, H.; QUAGGIO, J. A.; FURLANI, A. M. C. Recomendacao de adubacao e calagem para o Estado de Sao Paulo. 2. ed. Campinas: IAC, 1996. 285 p. (Boletim Tecnico, 100).",
        "referencia_legal": "Resolucao CONAMA 357/2005 - Limites para fosforo em corpos de agua."
    },
    "IAC_Cana": {
        "nome": "IAC - Cana-de-Acucar",
        "regiao": "Sudeste/Nordeste",
        "calagem": {"metodo": "V%", "meta_v_padrao": 60, "fator_calagem": 0.5,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 3.5, "medio": 5.5, "argiloso": 9.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 70},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Adota meta de V% de 60% para cana-de-acucar, considerando a alta exigencia de K e a necessidade de manutencao do Ca no perfil. "
            "O gesso e recomendado em solos com argila > 40% para melhorar a infiltracao de agua e reduzir o Al toxico."
        ),
        "bibliografia": "VAN RAIJ, B. et al. Recomendacao de adubacao e calagem para o Estado de Sao Paulo. 2. ed. Campinas: IAC, 1996. 285 p. (Boletim Tecnico, 100).",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "IAC_Citros": {
        "nome": "IAC - Citros",
        "regiao": "Sudeste",
        "calagem": {"metodo": "V%", "meta_v_padrao": 65, "fator_calagem": 0.5,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 3.5, "medio": 5.5, "argiloso": 9.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 80},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Metodologia especifica para citricultura, com V% meta de 65% e alta tolerancia ao gesso devido a exigencia de Ca para qualidade dos frutos. "
            "O B e o Zn sao micronutrientes criticos nesta metodologia."
        ),
        "bibliografia": "RAIJ, B. van et al. Recomendacao de adubacao e calagem para o Estado de Sao Paulo. 2. ed. Campinas: IAC, 1996. 285 p. (Boletim Tecnico, 100).",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "CFSEMG_Geral": {
        "nome": "CFSEMG - 5a Aproximacao (MG)",
        "regiao": "Minas Gerais",
        "calagem": {"metodo": "V%", "meta_v_padrao": 60, "fator_calagem": 0.55,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 4.0, "medio": 6.0, "argiloso": 10.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 60},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Metodo da Comissao de Fertilidade do Solo do Estado de Minas Gerais (CFSEMG), 5a aproximacao. "
            "Utiliza V% meta de 60% e fatores de calagem levemente superiores ao IAC, adaptados aos solos de cerrado mineiro."
        ),
        "bibliografia": "RIBEIRO, A. C.; GUIMARAES, P. T. G.; ALVAREZ, V. H. Recomendacoes para o uso de corretivos e fertilizantes em Minas Gerais: 5a Aproximacao. Vicosa: CFSEMG, 1999. 359 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "CFSEMG_Cafe": {
        "nome": "CFSEMG - Cafeeiro",
        "regiao": "Minas Gerais",
        "calagem": {"metodo": "V%", "meta_v_padrao": 70, "fator_calagem": 0.55,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 5.0, "medio": 8.0, "argiloso": 12.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 70},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Especifico para cafe em Minas Gerais, com V% meta elevado (70%) devido a alta exigencia de Ca e Mg pelo cafeeiro. "
            "Os fatores de P sao mais conservadores, refletindo a baixa mobilidade do fosforo em solos de cerrado."
        ),
        "bibliografia": "RIBEIRO, A. C. et al. Recomendacoes para o uso de corretivos e fertilizantes em Minas Gerais: 5a Aproximacao. Vicosa: CFSEMG, 1999. 359 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "PESAGRO_RJ": {
        "nome": "PESAGRO-RIO",
        "regiao": "Rio de Janeiro",
        "calagem": {"metodo": "V%", "meta_v_padrao": 65, "fator_calagem": 0.5,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 3.5, "medio": 5.5, "argiloso": 8.5},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 50},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Metodologia desenvolvida pela PESAGRO-RIO para as condicoes florestais do estado do Rio de Janeiro. "
            "Adota V% meta de 65% e fatores de P intermediarios entre IAC e CFSEMG, considerando os solos de mata atlantica."
        ),
        "bibliografia": "PESAGRO-RIO. Manual de Adubacao e Calagem para o Estado do Rio de Janeiro. Seropedica: PESAGRO-RIO, 2003. 198 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "EPAMIG_ES": {
        "nome": "EPAMIG - Espirito Santo",
        "regiao": "Espirito Santo",
        "calagem": {"metodo": "V%", "meta_v_padrao": 65, "fator_calagem": 0.5,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 3.5, "medio": 5.5, "argiloso": 9.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 60},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Metodologia da EPAMIG para o Espirito Santo, com enfase em cafe e fruticultura. "
            "V% meta de 65% e gesso recomendado para solos com argila > 35% no litoral capixaba."
        ),
        "bibliografia": "EPAMIG. Manual de Adubacao e Calagem para o Estado do Espirito Santo. Vitoria: EPAMIG, 2005. 156 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },

    # --- REGIAO CENTRO-OESTE (Cerrado) ---
    "EMBRAPA_Cerrado_Geral": {
        "nome": "Embrapa Cerrado - Geral",
        "regiao": "Centro-Oeste",
        "calagem": {"metodo": "V%", "meta_v_padrao": 50, "fator_calagem": 0.6,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 4.0, "medio": 6.0, "argiloso": 10.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 60},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Metodologia da Embrapa Cerrado para solos acidos e pobres em nutrientes. "
            "V% meta de 50% e fator de calagem mais elevado (0.6) devido a alta saturacao de Al tipica do cerrado."
        ),
        "bibliografia": "SOUZA, D. M. G. de; LOBATO, E. Cerrado: Correcao do solo e adubacao. 2. ed. Planaltina: EMBRAPA Cerrados, 2004. 416 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "EMBRAPA_Cerrado_Alta_Prod": {
        "nome": "Embrapa Cerrado - Alta Produtividade",
        "regiao": "Centro-Oeste",
        "calagem": {"metodo": "V%", "meta_v_padrao": 60, "fator_calagem": 0.6,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 4.5, "medio": 7.0, "argiloso": 11.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 70},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Versao atualizada da Embrapa Cerrado para sistemas de alta produtividade (2020). "
            "V% meta de 60% e fatores de P mais elevados para suportar rendimentos > 10 t/ha de graos."
        ),
        "bibliografia": "EMBRAPA CERRADOS. Sistema de Producao para o Cerrado: Alta Produtividade. Planaltina: EMBRAPA Cerrados, 2020. 248 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "GOIAS_ALGODAO": {
        "nome": "APLA - Algodao (GO/MT)",
        "regiao": "Centro-Oeste",
        "calagem": {"metodo": "V%", "meta_v_padrao": 60, "fator_calagem": 0.6,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 5.0, "medio": 8.0, "argiloso": 12.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 80},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Metodo APLA para algodao no cerrado, com V% meta de 60% e alta exigencia de Ca e S. "
            "O gesso e critico para melhorar a estrutura do solo e suprir demanda de calcio do algodoeiro."
        ),
        "bibliografia": "APLA - Associacao Paulista dos Produtores de Algodao. Manual de Adubacao do Algodoeiro no Cerrado. Campinas: APLA, 2019. 124 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "MATO_GROSSO_SOJA": {
        "nome": "APROSOJA - MT (Indicativo)",
        "regiao": "Mato Grosso",
        "calagem": {"metodo": "V%", "meta_v_padrao": 60, "fator_calagem": 0.55,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 4.0, "medio": 6.5, "argiloso": 10.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 60},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Recomendacoes indicativas da APROSOJA-MT para soja no cerrado mato-grossense. "
            "V% meta de 60% com foco em eficiencia de custos e sustentabilidade da producao."
        ),
        "bibliografia": "APROSOJA-MT. Manual de Boas Praticas Agricolas para Soja em Mato Grosso. Lucas do Rio Verde: APROSOJA-MT, 2022. 180 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "MATO_GROSSO_MILHO": {
        "nome": "APROSOJA/Aprosoja - Milho (MT)",
        "regiao": "Mato Grosso",
        "calagem": {"metodo": "V%", "meta_v_padrao": 65, "fator_calagem": 0.55,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 4.5, "medio": 7.0, "argiloso": 11.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 65},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Recomendacoes para milho safrinha no cerrado mato-grossense. "
            "V% meta de 65% e fatores de P elevados para suportar produtividades > 120 sc/ha."
        ),
        "bibliografia": "APROSOJA-MT. Manual de Boas Praticas Agricolas para Milho em Mato Grosso. Lucas do Rio Verde: APROSOJA-MT, 2022. 156 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },

    # --- REGIAO SUL (PR, SC, RS) ---
    "SBCS_ROLAS_Graos": {
        "nome": "SBCS/ROLAS - Graos (RS/SC)",
        "regiao": "Sul",
        "calagem": {"metodo": "V%", "meta_v_padrao": 70, "fator_calagem": 0.55,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 5.0, "medio": 8.0, "argiloso": 12.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 50},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Manual de Adubacao do Sul do Brasil (SBCS/ROLAS) para graos em geral. "
            "V% meta de 70% e fatores de P elevados devido ao clima frio e baixa mineralizacao do solo."
        ),
        "bibliografia": "SBCS/ROLAS. Manual de Adubacao e de Calagem para os Estados do Rio Grande do Sul e de Santa Catarina. 12. ed. Porto Alegre: SBCS, 2016. 376 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "SBCS_ROLAS_Milho": {
        "nome": "SBCS/ROLAS - Milho",
        "regiao": "Sul",
        "calagem": {"metodo": "V%", "meta_v_padrao": 70, "fator_calagem": 0.55,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 5.5, "medio": 9.0, "argiloso": 13.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 50},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Especifico para milho no Sul do Brasil. V% meta de 70% e fatores de P mais elevados que o geral, "
            "considerando a alta resposta do milho ao fosforo em solos de baixa temperatura."
        ),
        "bibliografia": "SBCS/ROLAS. Manual de Adubacao e de Calagem para os Estados do Rio Grande do Sul e de Santa Catarina. 12. ed. Porto Alegre: SBCS, 2016. 376 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "IAPAR_PR": {
        "nome": "IAPAR - Parana",
        "regiao": "Parana",
        "calagem": {"metodo": "V%", "meta_v_padrao": 70, "fator_calagem": 0.5,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 4.5, "medio": 7.0, "argiloso": 11.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 55},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Metodologia do IAPAR para o Parana, com V% meta de 70% e fatores de P intermediarios. "
            "O gesso e recomendado para solos com argila > 35% no norte do estado."
        ),
        "bibliografia": "IAPAR. Recomendacoes de Adubacao e Calagem para o Estado do Parana. Londrina: IAPAR, 2018. 256 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "EPAGRI_SC": {
        "nome": "EPAGRI - Santa Catarina",
        "regiao": "Santa Catarina",
        "calagem": {"metodo": "V%", "meta_v_padrao": 70, "fator_calagem": 0.55,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 5.0, "medio": 8.0, "argiloso": 12.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 50},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Metodologia da EPAGRI para Santa Catarina, adaptada aos solos de altitude e planicie litoranea. "
            "V% meta de 70% com fatores de P alinhados ao Manual SBCS/ROLAS."
        ),
        "bibliografia": "EPAGRI. Manual de Adubacao e Calagem para Santa Catarina. Florianopolis: EPAGRI, 2017. 312 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "SOSBAI_Arroz": {
        "nome": "SOSBAI - Arroz Irrigado (RS/SC)",
        "regiao": "Sul",
        "calagem": {"metodo": "V%", "meta_v_padrao": 50, "fator_calagem": 0.6,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 4.0, "medio": 6.0, "argiloso": 10.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 0},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Metodologia especifica para arroz irrigado no Sul do Brasil. V% meta de 50% devido a condicao anaerobica do solo alagado. "
            "Gesso nao recomendado em sistema de lavoura de arroz irrigado."
        ),
        "bibliografia": "SOSBAI. Arroz Irrigado: Recomendacoes Tecnicas da Pesquisa para o Sul do Brasil. Bento Goncalves: IRGA, 2024. 196 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "Comite_Trigo": {
        "nome": "Comite Trigo - Sul",
        "regiao": "Sul",
        "calagem": {"metodo": "V%", "meta_v_padrao": 70, "fator_calagem": 0.55,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 4.5, "medio": 7.0, "argiloso": 11.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 50},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Recomendacoes do Comite Sul-Brasileiro de Pesquisa de Trigo. "
            "V% meta de 70% e fatores de P elevados para maximizar o enchimento de graos em condicoes de inverno."
        ),
        "bibliografia": "COMITE TECNICO SUL-BRASILEIRO DE PESQUISA DE TRIGO. Manual de Trigo. Fundacao ABC, 2023. 312 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },

    # --- REGIAO NORDESTE ---
    "EMBRAPA_SEMIARIDO": {
        "nome": "Embrapa Semiarido (BA/PE)",
        "regiao": "Nordeste",
        "calagem": {"metodo": "V%", "meta_v_padrao": 60, "fator_calagem": 0.6,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 3.0, "medio": 5.0, "argiloso": 8.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 40},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Metodologia da Embrapa Semi-Arido para as condicoes de baixa precipitacao do nordeste brasileiro. "
            "V% meta de 60% e gesso com fator reduzido devido a baixa disponibilidade hidrica."
        ),
        "bibliografia": "EMBRAPA SEMI-ARIDO. Recomendacoes de Adubacao e Calagem para o Semi-Arido Brasileiro. Petrolina: EMBRAPA Semi-Arido, 2015. 168 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "IPA_PE": {
        "nome": "IPA - Pernambuco",
        "regiao": "Pernambuco",
        "calagem": {"metodo": "V%", "meta_v_padrao": 60, "fator_calagem": 0.6,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 3.0, "medio": 4.5, "argiloso": 7.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 40},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Metodologia do IPA para Pernambuco, com fatores de P mais conservadores devido aos solos arenosos da zona da mata. "
            "V% meta de 60% e gesso limitado a solos com argila > 30%."
        ),
        "bibliografia": "IPA. Recomendacoes de Adubacao e Calagem para o Estado de Pernambuco. Recife: IPA, 2012. 124 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "EMBRAPA_CACAU": {
        "nome": "Embrapa Cacau (BA)",
        "regiao": "Bahia",
        "calagem": {"metodo": "V%", "meta_v_padrao": 70, "fator_calagem": 0.5,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 4.0, "medio": 6.0, "argiloso": 10.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 60},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Metodologia da CEPLAC/EMBRAPA Cacau para o litoral sul da Bahia. "
            "V% meta de 70% e gesso recomendado para melhorar a drenagem dos solos de tabuleiro."
        ),
        "bibliografia": "CEPLAC/EMBRAPA CACAU. Recomendacoes de Adubacao e Calagem para Cacau na Bahia. Ilheus: CEPLAC, 2016. 92 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "EMBRAPA_TABULEIRO": {
        "nome": "Embrapa Tabuleiro Costeiro (SE/AL)",
        "regiao": "Nordeste",
        "calagem": {"metodo": "V%", "meta_v_padrao": 60, "fator_calagem": 0.55,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 3.5, "medio": 5.5, "argiloso": 9.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 50},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Metodologia da Embrapa Tabuleiro Costeiro para Sergipe e Alagoas. "
            "V% meta de 60% adaptada aos solos de tabuleiro costeiro com alta saturacao de Al."
        ),
        "bibliografia": "EMBRAPA TABULEIRO COSTEIRO. Recomendacoes de Adubacao e Calagem para o Tabuleiro Costeiro. Aracaju: EMBRAPA Tabuleiro Costeiro, 2018. 112 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },

    # --- CULTURAS ESPECIFICAS ---
    "CULTURA_FEIJAO": {
        "nome": "Feijao Comum",
        "regiao": "Nacional",
        "calagem": {"metodo": "V%", "meta_v_padrao": 70, "fator_calagem": 0.5,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 4.0, "medio": 6.5, "argiloso": 11.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 50},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Recomendacoes da Embrapa Arroz e Feijao para feijao comum. "
            "V% meta de 70% e fatores de P elevados para maximizar a fixacao biologica de N2 e produtividade."
        ),
        "bibliografia": "FAGERIA, N. K.; SANTOS, A. B. dos; MORAES, M. F. Nutricao mineral do feijoeiro. Santo Antonio de Goias: EMBRAPA Arroz e Feijao, 2015. 48 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "CULTURA_TRIGO": {
        "nome": "Trigo (Sul)",
        "regiao": "Sul",
        "calagem": {"metodo": "V%", "meta_v_padrao": 70, "fator_calagem": 0.55,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 4.5, "medio": 7.0, "argiloso": 11.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 50},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Recomendacoes especificas do Comite Trigo para trigo no Sul do Brasil. "
            "V% meta de 70% e fatores de P alinhados ao Manual SBCS/ROLAS."
        ),
        "bibliografia": "COMITE TECNICO SUL-BRASILEIRO DE PESQUISA DE TRIGO. Manual de Trigo. Fundacao ABC, 2023. 312 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "CULTURA_PASTAGEM": {
        "nome": "Pastagens (Geral)",
        "regiao": "Nacional",
        "calagem": {"metodo": "V%", "meta_v_padrao": 50, "fator_calagem": 0.5,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 3.0, "medio": 5.0, "argiloso": 8.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 40},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Recomendacoes da Embrapa Gado de Corte para pastagens em geral. "
            "V% meta de 50% e fatores de P conservadores, considerando a baixa resposta economica de pastagens degradadas."
        ),
        "bibliografia": "EUCLIDES, V. P. B. et al. Sistema de Producao de Gado de Corte. Campo Grande: EMBRAPA Gado de Corte, 2018. 156 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "CULTURA_FLORESTAS": {
        "nome": "Florestas Plantadas (Eucalipto/Pinus)",
        "regiao": "Nacional",
        "calagem": {"metodo": "V%", "meta_v_padrao": 50, "fator_calagem": 0.6,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 2.5, "medio": 4.0, "argiloso": 6.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 30},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Recomendacoes do IPEF para florestas plantadas. "
            "V% meta de 50% e fatores de P baixos, considerando o ciclo longo e a eficiencia de uso de nutrientes das especies florestais."
        ),
        "bibliografia": "GONCALVES, J. L. M.; BENEDETTI, V. Nutricao e fertilidade do solo para plantacoes florestais. Piracicaba: IPEF/ESALQ, 2015. 245 p.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "CULTURA_CAFE": {
        "nome": "Cafe - Geral",
        "regiao": "Nacional",
        "calagem": {"metodo": "V%", "meta_v_padrao": 70, "fator_calagem": 0.5,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 5.0, "medio": 8.0, "argiloso": 12.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 70},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Recomendacoes gerais para cafeicultura no Brasil. "
            "V% meta de 70% e alta exigencia de Ca, Mg e micronutrientes (B, Zn) para qualidade da bebida."
        ),
        "bibliografia": "GUIMARAES, R. J.; GARCIA, A. W. R.; MARTINEZ, H. E. P. Nutricao e adubacao do cafeeiro. In: Manual de Cafeicultura. Lavras: EPAMIG/UFV, 2019. p. 287-340.",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
    "CULTURA_CANA": {
        "nome": "Cana-de-Acucar - Geral",
        "regiao": "Nacional",
        "calagem": {"metodo": "V%", "meta_v_padrao": 60, "fator_calagem": 0.5,
            "fator_ctc_argila": 0.15,
            "profundidade_referencia_cm": 20.0,
            "ph_limite_1": 5.0,
            "fator_ph_1": 1.3,
            "ph_limite_2": 5.5,
            "fator_ph_2": 1.1,
            "argila_limite": 40.0,
            "fator_argila": 1.2,
        },
        "fosforo": {"unidade": "mg/dm3", "fatores_textura": {"arenoso": 3.5, "medio": 5.5, "argiloso": 9.0},
            "ph_minimo": 5.5,
            "fator_ph_baixo": 1.15
        },
        "gesso": {"fator_argila": 70},
        "nitrogenio": {
            "v_percent_minimo": 40.0,
            "fator_v_baixo": 1.2,
        },
        "calcio": {
            "adequado_cmolc": 4.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 3.0,
            "fator_kg_por_cmolc": 400.0,
        },
        "magnesio": {
            "adequado_cmolc": 1.0,
            "v_minimo_percent": 50.0,
            "meta_cmolc": 0.8,
            "fator_kg_por_cmolc": 240.0,
        },
        "enxofre": {
            "adequado_mg_dm3": 10.0,
            "dose_default_kg_ha": 10.0,
            "baixo_limite_mg_dm3": 5.0,
            "fator_baixo": 1.5,
        },
        "micronutrientes": {
            "fator_suficiente": 2.0,
            "dose_manutencao_kg_ha": 0.5,
            "dose_correcao_kg_ha": 1.0,
            "fator_correcao": 1.5,
        },
        "embasamento_tecnico": (
            "Recomendacoes gerais para cana-de-acucar. "
            "V% meta de 60% e gesso critico para melhorar a infiltracao de agua e suprir demanda de calcio em solos argilosos."
        ),
        "bibliografia": "VAN RAIJ, B. et al. Recomendacao de adubacao e calagem para o Estado de Sao Paulo. 2. ed. Campinas: IAC, 1996. 285 p. (Boletim Tecnico, 100).",
        "referencia_legal": "Resolucao CONAMA 357/2005."
    },
}


def get_formula(metodo="IAC_Graos"):
    """Retorna os parametros da metodologia escolhida."""
    return FORMULAS.get(metodo, FORMULAS["IAC_Graos"])


def listar_formulas():
    """Retorna lista de nomes para dropdowns."""
    return sorted([(k, v["nome"]) for k, v in FORMULAS.items()])