"""
Motor de Calculo de Recomendacao Agronomica
Formulas faceis de ajustar ou substituir
"""


# ============================================================
# CONSTANTES AGRONOMICAS (ajustaveis)
# ============================================================
CONSTANTES = {
    "eficiencia_P2O5": 0.20,      # 20% de eficiencia
    "eficiencia_K2O": 0.50,         # 50% de eficiencia
    "eficiencia_N": 0.60,           # 60% de eficiencia
    "fator_correcao_ph": 1.0,       # multiplicador geral de calagem
    "dose_max_calagem": 6.0,        # t/ha maximo
    "dose_min_calagem": 0.0,        # t/ha minimo
    "teor_argila_alto": 35.0,       # % argila para considerar solo argiloso
}

# ============================================================
# METAS DE NUTRIENTES POR CULTURA
# ============================================================
METAS_CULTURA = {
    "milho": {
        "ph_min": 5.5, "ph_ideal": 6.0,
        "p_baixo": 10, "p_medio": 20, "p_alto": 40,
        "k_baixo": 50, "k_medio": 100, "k_alto": 150,
        "ca_min": 20, "mg_min": 10,
        "mo_min": 2.0,
        "n_kg_sc": 1.5,      # kg N por saco
        "p2o5_kg_sc": 0.6,   # kg P2O5 por saco
        "k2o_kg_sc": 1.2,    # kg K2O por saco
    },
    "soja": {
        "ph_min": 5.5, "ph_ideal": 6.0,
        "p_baixo": 8, "p_medio": 15, "p_alto": 30,
        "k_baixo": 40, "k_medio": 80, "k_alto": 120,
        "ca_min": 20, "mg_min": 10,
        "mo_min": 2.0,
        "n_kg_sc": 0,        # soja fixa N
        "p2o5_kg_sc": 0.8,
        "k2o_kg_sc": 1.4,
    },
    "trigo": {
        "ph_min": 5.5, "ph_ideal": 6.0,
        "p_baixo": 8, "p_medio": 16, "p_alto": 32,
        "k_baixo": 45, "k_medio": 90, "k_alto": 140,
        "ca_min": 18, "mg_min": 8,
        "mo_min": 2.0,
        "n_kg_sc": 2.0,
        "p2o5_kg_sc": 0.7,
        "k2o_kg_sc": 1.0,
    },
    "cafe": {
        "ph_min": 5.5, "ph_ideal": 6.0,
        "p_baixo": 6, "p_medio": 12, "p_alto": 25,
        "k_baixo": 40, "k_medio": 80, "k_alto": 120,
        "ca_min": 15, "mg_min": 8,
        "mo_min": 2.5,
        "n_kg_sc": 1.0,
        "p2o5_kg_sc": 0.5,
        "k2o_kg_sc": 1.0,
    },
    "canadeacucar": {
        "ph_min": 5.5, "ph_ideal": 6.0,
        "p_baixo": 8, "p_medio": 15, "p_alto": 30,
        "k_baixo": 60, "k_medio": 120, "k_alto": 180,
        "ca_min": 20, "mg_min": 10,
        "mo_min": 2.0,
        "n_kg_sc": 1.0,
        "p2o5_kg_sc": 0.4,
        "k2o_kg_sc": 1.5,
    },
}

# ============================================================
# FUNCOES DE CALCULO (modulares, faceis de substituir)
# ============================================================

def calcular_necessidade_calagem(ph_atual, ca_mg_dm3, mg_mg_dm3, al_mg_dm3=None, v_atual=None):
    """
    Calcula necessidade de calagem em t/ha.
    Formula: NC = (pH ideal - pH atual) * fator + correcao Ca/Mg
    """
    ph_ideal = 6.0
    if ph_atual >= ph_ideal:
        return 0.0, "Nao necessita"
    
    # Formula base: diferenca de pH * 1.5 t/ha por unidade
    nc = (ph_ideal - ph_atual) * 1.5
    
    # Ajuste por saturacao por bases (se disponivel)
    if v_atual is not None and v_atual < 50:
        nc *= 1.2
    
    # Ajuste por aluminio trocavel
    if al_mg_dm3 and al_mg_dm3 > 1.0:
        nc += al_mg_dm3 * 0.5
    
    # Limites
    nc = max(CONSTANTES["dose_min_calagem"], min(nc, CONSTANTES["dose_max_calagem"]))
    
    status = "Leve" if nc < 2 else "Moderada" if nc < 4 else "Alta"
    return round(nc, 2), status


def calcular_necessidade_fosforo(p_mg_dm3, cultura, produtividade_alvo):
    """
    Calcula necessidade de P2O5 em kg/ha.
    """
    meta = METAS_CULTURA.get(cultura, METAS_CULTURA["milho"])
    
    if p_mg_dm3 >= meta["p_alto"]:
        return 0.0, "Adequado"
    elif p_mg_dm3 >= meta["p_medio"]:
        dose = (meta["p_alto"] - p_mg_dm3) * 1.5
        status = "Manutencao"
    elif p_mg_dm3 >= meta["p_baixo"]:
        dose = (meta["p_medio"] - p_mg_dm3) * 2.0 + (meta["p_alto"] - meta["p_medio"]) * 1.5
        status = "Correcao"
    else:
        dose = (meta["p_baixo"] - p_mg_dm3) * 3.0 + (meta["p_medio"] - meta["p_baixo"]) * 2.0 + (meta["p_alto"] - meta["p_medio"]) * 1.5
        status = "Alta Correcao"
    
    # Ajuste por produtividade
    dose *= (produtividade_alvo / 80.0)
    
    # Correcao de eficiencia
    dose = dose / CONSTANTES["eficiencia_P2O5"]
    
    return round(dose, 1), status


def calcular_necessidade_potassio(k_mg_dm3, cultura, produtividade_alvo):
    """
    Calcula necessidade de K2O em kg/ha.
    """
    meta = METAS_CULTURA.get(cultura, METAS_CULTURA["milho"])
    
    if k_mg_dm3 >= meta["k_alto"]:
        return 0.0, "Adequado"
    elif k_mg_dm3 >= meta["k_medio"]:
        dose = (meta["k_alto"] - k_mg_dm3) * 0.8
        status = "Manutencao"
    elif k_mg_dm3 >= meta["k_baixo"]:
        dose = (meta["k_medio"] - k_mg_dm3) * 1.2 + (meta["k_alto"] - meta["k_medio"]) * 0.8
        status = "Correcao"
    else:
        dose = (meta["k_baixo"] - k_mg_dm3) * 1.8 + (meta["k_medio"] - meta["k_baixo"]) * 1.2 + (meta["k_alto"] - meta["k_medio"]) * 0.8
        status = "Alta Correcao"
    
    dose *= (produtividade_alvo / 80.0)
    dose = dose / CONSTANTES["eficiencia_K2O"]
    
    return round(dose, 1), status


def calcular_necessidade_nitrogenio(cultura, produtividade_alvo, mo_percent=None):
    """
    Calcula necessidade de N em kg/ha.
    """
    meta = METAS_CULTURA.get(cultura, METAS_CULTURA["milho"])
    
    if cultura == "soja":
        return 0.0, "Fixacao biologica"
    
    dose = meta["n_kg_sc"] * produtividade_alvo
    
    # Desconto por materia organica
    if mo_percent and mo_percent > 3.0:
        dose *= 0.85
    
    dose = dose / CONSTANTES["eficiencia_N"]
    
    return round(dose, 1), "Necessario"


def calcular_dose_produto(necessidade_nutriente, teor_produto):
    """
    Calcula dose do produto comercial baseada no teor.
    necessidade_nutriente: kg/ha do nutriente
    teor_produto: % do nutriente no produto
    """
    if teor_produto <= 0:
        return 0.0
    dose = (necessidade_nutriente / (teor_produto / 100.0))
    return round(dose, 1)


def calcular_custo(dose, preco, unidade="kg"):
    """
    Calcula custo por ha.
    dose: kg/ha ou t/ha
    preco: R$ por kg ou por t
    """
    if unidade == "t":
        return round(dose * preco, 2)
    return round((dose / 1000.0) * preco, 2) if preco > 100 else round(dose * preco, 2)


def processar_amostra(amostra, cultura, produtividade_alvo, insumos_selecionados):
    """
    Processa uma amostra e retorna recomendacao completa.
    
    amostra: dict com campos do CSV (ph, p_mg_dm3, k_mg_dm3, ca_mg_dm3, mg_mg_dm3, etc.)
    insumos_selecionados: dict com insumos escolhidos e precos editados
        {
            "corretivo_ph": {"insumo": {...}, "preco_editado": 250.0},
            "fonte_P": {"insumo": {...}, "preco_editado": 5.8},
            "fonte_K": {"insumo": {...}, "preco_editado": 3.2},
            "fonte_N": {"insumo": {...}, "preco_editado": 2.5},
        }
    """
    resultado = {
        "amostra_id": amostra.get("id", "Amostra"),
        "coordenadas": {
            "lat": amostra.get("latitude", 0),
            "lon": amostra.get("longitude", 0)
        },
        "cultura": cultura,
        "produtividade_alvo": produtividade_alvo,
        "analise_solo": {
            "ph": amostra.get("ph", 0),
            "p_mg_dm3": amostra.get("p_mg_dm3", 0),
            "k_mg_dm3": amostra.get("k_mg_dm3", 0),
            "ca_mg_dm3": amostra.get("ca_mg_dm3", 0),
            "mg_mg_dm3": amostra.get("mg_mg_dm3", 0),
            "al_mg_dm3": amostra.get("al_mg_dm3", 0),
            "mo_percent": amostra.get("mo_percent", 0),
            "argila_percent": amostra.get("argila_percent", 0),
        },
        "recomendacoes": [],
        "custo_total_ha": 0.0
    }
    
    # --- CALAGEM ---
    nc, status_calagem = calcular_necessidade_calagem(
        amostra.get("ph", 0),
        amostra.get("ca_mg_dm3", 0),
        amostra.get("mg_mg_dm3", 0),
        amostra.get("al_mg_dm3"),
        amostra.get("v_percent")
    )
    
    if nc > 0 and "corretivo_ph" in insumos_selecionados:
        corr = insumos_selecionados["corretivo_ph"]
        preco = corr.get("preco_editado", corr["insumo"].get("preco_t", 0))
        custo = calcular_custo(nc, preco, "t")
        resultado["recomendacoes"].append({
            "tipo": "Calagem",
            "insumo": corr["insumo"]["nome"],
            "dose": nc,
            "unidade": "t/ha",
            "preco_unidade": preco,
            "custo_ha": custo,
            "status": status_calagem,
            "ajustavel": True
        })
        resultado["custo_total_ha"] += custo
    
    # --- FOSFORO ---
    p2o5, status_p = calcular_necessidade_fosforo(
        amostra.get("p_mg_dm3", 0), cultura, produtividade_alvo
    )
    
    if p2o5 > 0 and "fonte_P" in insumos_selecionados:
        fonte = insumos_selecionados["fonte_P"]
        teor_p = fonte["insumo"]["teores"].get("P", 0)
        if teor_p > 0:
            dose_prod = calcular_dose_produto(p2o5, teor_p)
            preco = fonte.get("preco_editado", fonte["insumo"].get("preco_kg", 0))
            custo = calcular_custo(dose_prod, preco, "kg")
            resultado["recomendacoes"].append({
                "tipo": "Fosforo",
                "insumo": fonte["insumo"]["nome"],
                "dose": dose_prod,
                "unidade": "kg/ha",
                "nutriente": f"P2O5: {p2o5} kg/ha",
                "preco_unidade": preco,
                "custo_ha": custo,
                "status": status_p,
                "ajustavel": True
            })
            resultado["custo_total_ha"] += custo
    
    # --- POTASSIO ---
    k2o, status_k = calcular_necessidade_potassio(
        amostra.get("k_mg_dm3", 0), cultura, produtividade_alvo
    )
    
    if k2o > 0 and "fonte_K" in insumos_selecionados:
        fonte = insumos_selecionados["fonte_K"]
        teor_k = fonte["insumo"]["teores"].get("K", 0)
        if teor_k > 0:
            dose_prod = calcular_dose_produto(k2o, teor_k)
            preco = fonte.get("preco_editado", fonte["insumo"].get("preco_kg", 0))
            custo = calcular_custo(dose_prod, preco, "kg")
            resultado["recomendacoes"].append({
                "tipo": "Potassio",
                "insumo": fonte["insumo"]["nome"],
                "dose": dose_prod,
                "unidade": "kg/ha",
                "nutriente": f"K2O: {k2o} kg/ha",
                "preco_unidade": preco,
                "custo_ha": custo,
                "status": status_k,
                "ajustavel": True
            })
            resultado["custo_total_ha"] += custo
    
    # --- NITROGENIO ---
    n, status_n = calcular_necessidade_nitrogenio(
        cultura, produtividade_alvo, amostra.get("mo_percent")
    )
    
    if n > 0 and "fonte_N" in insumos_selecionados:
        fonte = insumos_selecionados["fonte_N"]
        teor_n = fonte["insumo"]["teores"].get("N", 0)
        if teor_n > 0:
            dose_prod = calcular_dose_produto(n, teor_n)
            preco = fonte.get("preco_editado", fonte["insumo"].get("preco_kg", 0))
            custo = calcular_custo(dose_prod, preco, "kg")
            resultado["recomendacoes"].append({
                "tipo": "Nitrogenio",
                "insumo": fonte["insumo"]["nome"],
                "dose": dose_prod,
                "unidade": "kg/ha",
                "nutriente": f"N: {n} kg/ha",
                "preco_unidade": preco,
                "custo_ha": custo,
                "status": status_n,
                "ajustavel": True
            })
            resultado["custo_total_ha"] += custo
    
    resultado["custo_total_ha"] = round(resultado["custo_total_ha"], 2)
    return resultado


def processar_todas_amostras(amostras, cultura, produtividade_alvo, insumos_selecionados):
    """
    Processa lista de amostras e retorna lista de recomendacoes.
    """
    return [processar_amostra(a, cultura, produtividade_alvo, insumos_selecionados) for a in amostras]
