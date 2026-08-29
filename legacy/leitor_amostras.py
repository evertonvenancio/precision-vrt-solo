"""
Leitor de amostras de solo - suporta CSV e Excel com mapeamento de colunas
"""

import pandas as pd
from pathlib import Path

# ============================================================
# MAPEAMENTO PADRAO DE COLUNAS
# ============================================================
COLUNAS_PADRAO = {
    "id": ["id", "ID", "codigo", "Codigo", "amostra", "Amostra", "ponto", "Ponto"],
    "latitude": ["latitude", "lat", "Latitude", "Lat", "y", "Y"],
    "longitude": ["longitude", "lon", "Long", "Longitude", "Lng", "x", "X"],
    "ph": ["ph", "pH", "PH", "Ph"],
    "p_mg_dm3": ["p", "P", "fosforo", "Fosforo", "p_mg", "P_mg", "p_mg_dm3", "P_mg_dm3"],
    "k_mg_dm3": ["k", "K", "potassio", "Potassio", "k_mg", "K_mg", "k_mg_dm3", "K_mg_dm3"],
    "ca_mg_dm3": ["ca", "Ca", "calcio", "Calcio", "ca_mg", "Ca_mg", "ca_mg_dm3", "Ca_mg_dm3"],
    "mg_mg_dm3": ["mg", "Mg", "magnesio", "Magnesio", "mg_mg", "Mg_mg", "mg_mg_dm3", "Mg_mg_dm3"],
    "al_mg_dm3": ["al", "Al", "aluminio", "Aluminio", "al_mg", "Al_mg", "al_mg_dm3", "Al_mg_dm3"],
    "mo_percent": ["mo", "MO", "materia_organica", "Materia_Organica", "mo_percent", "MO_percent"],
    "argila_percent": ["argila", "Argila", "argila_percent", "clay"],
    "v_percent": ["v", "V", "saturacao_bases", "V_percent", "SB"],
    "ctc": ["ctc", "CTC", "capacidade_troca", "T"],
}

def detectar_colunas(df):
    """
    Detecta automaticamente quais colunas do DataFrame correspondem ao padrao.
    Retorna dict: {campo_padrao: nome_coluna_encontrada}
    """
    mapeamento = {}
    colunas_df = list(df.columns)
    colunas_usadas = set()
    
    for campo, alternativas in COLUNAS_PADRAO.items():
        for alt in alternativas:
            if alt in colunas_df and alt not in colunas_usadas:
                mapeamento[campo] = alt
                colunas_usadas.add(alt)
                break
    
    return mapeamento

def ler_arquivo(caminho):
    """
    Le CSV ou Excel e retorna DataFrame.
    """
    caminho = Path(caminho)
    ext = caminho.suffix.lower()
    
    if ext == ".csv":
        # Tenta diferentes separadores e encodings
        for sep in [";", ",", "\t"]:
            for enc in ["utf-8", "latin1", "cp1252"]:
                try:
                    df = pd.read_csv(caminho, sep=sep, encoding=enc)
                    if len(df.columns) > 1:
                        return df
                except:
                    continue
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(caminho)
        return df
    
    raise ValueError(f"Formato nao suportado: {ext}")

def converter_para_dict(df, mapeamento):
    """
    Converte DataFrame para lista de dicts usando o mapeamento.
    """
    amostras = []
    for _, row in df.iterrows():
        amostra = {}
        for campo, coluna in mapeamento.items():
            val = row.get(coluna)
            # Converte para numero se possivel
            try:
                amostra[campo] = float(val) if pd.notna(val) else 0
            except:
                amostra[campo] = str(val) if pd.notna(val) else ""
        amostras.append(amostra)
    return amostras

def resumo_amostras(amostras):
    """
    Retorna resumo estatistico das amostras.
    """
    if not amostras:
        return {}
    
    numericos = ["ph", "p_mg_dm3", "k_mg_dm3", "ca_mg_dm3", "mg_mg_dm3", "mo_percent"]
    resumo = {}
    
    for campo in numericos:
        vals = [a.get(campo, 0) for a in amostras if isinstance(a.get(campo), (int, float))]
        if vals:
            resumo[campo] = {
                "min": round(min(vals), 2),
                "max": round(max(vals), 2),
                "media": round(sum(vals)/len(vals), 2),
                "n": len(vals)
            }
    
    return resumo
