"""
Banco de dados de sais 100% solúveis para fertirrigação e hidroponia.

Este módulo contém informações sobre sais comerciais utilizados em solução nutritiva,
incluindo teores de nutrientes, solubilidade e compatibilidade química.

Referência:
- Manual de Fertirrigação (EMBRAPA)
- International Fertilizer Association (IFA)
"""

from typing import TypedDict


class SalSoluvel(TypedDict):
    """Estrutura de dados para um sal solúvel."""
    nome_comercial: str
    formula_quimica: str
    n_percent: float  # Teor de Nitrogênio (%)
    p2o5_percent: float  # Teor de P2O5 (%)
    k2o_percent: float  # Teor de K2O (%)
    ca_percent: float  # Teor de Cálcio (%)
    mg_percent: float  # Teor de Magnésio (%)
    s_percent: float  # Teor de Enxofre (%)
    fe_percent: float  # Teor de Ferro (%)
    mn_percent: float  # Teor de Manganês (%)
    zn_percent: float  # Teor de Zinco (%)
    b_percent: float  # Teor de Boro (%)
    cu_percent: float  # Teor de Cobre (%)
    mo_percent: float  # Teor de Molibdênio (%)
    solubilidade_g_L_20C: float  # Solubilidade em g/L a 20°C
    ph_solucao: float  # pH aproximado da solução
    ce_dS_m_por_gramo_L: float  # CE gerada por g/L no tanque
    observacoes: str


SAIS_SOLUVEIS: dict[str, SalSoluvel] = {
    # ==================== FONTES DE NITROGÊNIO E POTÁSSIO ====================
    "nitrato_potassio": {
        "nome_comercial": "Nitrato de Potássio",
        "formula_quimica": "KNO3",
        "n_percent": 13.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 46.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 0.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 316.0,
        "ph_solucao": 7.0,
        "ce_dS_m_por_gramo_L": 1.42,
        "observacoes": "Excelente fonte de N e K. Preferido em hidroponia. "
        "Compatível com maioria dos sais.",
    },

    # ==================== FONTES DE FÓSFORO ====================
    "mkp": {
        "nome_comercial": "MKP (Fosfato Monopotássico)",
        "formula_quimica": "KH2PO4",
        "n_percent": 0.0,
        "p2o5_percent": 52.0,
        "k2o_percent": 34.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 0.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 230.0,
        "ph_solucao": 4.5,
        "ce_dS_m_por_gramo_L": 0.95,
        "observacoes": "Fonte pura de P e K. Baixa salinidade. "
        "Ideal para estágios iniciais e enraizamento.",
    },

    "map": {
        "nome_comercial": "MAP (Fosfato Monoamônio)",
        "formula_quimica": "NH4H2PO4",
        "n_percent": 12.0,
        "p2o5_percent": 61.0,
        "k2o_percent": 0.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 0.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 370.0,
        "ph_solucao": 4.2,
        "ce_dS_m_por_gramo_L": 0.85,
        "observacoes": "Fonte de N amoniacal e P. Acidifica solução. "
        "Não misturar com nitrato de cálcio.",
    },

    "dap": {
        "nome_comercial": "DAP (Fosfato Diamônio)",
        "formula_quimica": "(NH4)2HPO4",
        "n_percent": 18.0,
        "p2o5_percent": 46.0,
        "k2o_percent": 0.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 0.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 575.0,
        "ph_solucao": 8.0,
        "ce_dS_m_por_gramo_L": 0.92,
        "observacoes": "Fonte de N amoniacal e P. Alcaliniza solução. "
        "Menos recomendado para hidroponia.",
    },

    # ==================== FONTES DE NITROGÊNIO E CÁLCIO ====================
    "nitrato_calcio": {
        "nome_comercial": "Nitrato de Cálcio",
        "formula_quimica": "Ca(NO3)2·4H2O",
        "n_percent": 15.5,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "ca_percent": 19.0,
        "mg_percent": 0.0,
        "s_percent": 0.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 1290.0,
        "ph_solucao": 5.6,
        "ce_dS_m_por_gramo_L": 1.15,
        "observacoes": "Fonte principal de Ca. Essencial para estrutura celular. "
        "INCOMPATÍVEL com sulfatos e fosfatos.",
    },

    "nitrato_calcio_amoniaco": {
        "nome_comercial": "Nitrato de Cálcio e Amônia (CAN)",
        "formula_quimica": "5Ca(NO3)2·NH4NO3·10H2O",
        "n_percent": 27.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "ca_percent": 10.0,
        "mg_percent": 0.0,
        "s_percent": 0.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 1200.0,
        "ph_solucao": 6.0,
        "ce_dS_m_por_gramo_L": 1.25,
        "observacoes": "Fonte alternativa de N e Ca. "
        "Mesmas incompatibilidades do nitrato de cálcio.",
    },

    # ==================== FONTES DE MAGNÉSIO ====================
    "sulfato_magnesio": {
        "nome_comercial": "Sulfato de Magnésio (Sal de Epsom)",
        "formula_quimica": "MgSO4·7H2O",
        "n_percent": 0.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "ca_percent": 0.0,
        "mg_percent": 10.0,
        "s_percent": 13.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 710.0,
        "ph_solucao": 6.0,
        "ce_dS_m_por_gramo_L": 0.78,
        "observacoes": "Fonte principal de Mg e S. Muito solúvel e seguro. "
        "Compatível com nitrato de cálcio.",
    },

    "magnesio_quelatado": {
        "nome_comercial": "Magnésio Quelatado (EDTA)",
        "formula_quimica": "Mg-EDTA",
        "n_percent": 0.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "ca_percent": 0.0,
        "mg_percent": 6.0,
        "s_percent": 0.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 500.0,
        "ph_solucao": 6.5,
        "ce_dS_m_por_gramo_L": 0.45,
        "observacoes": "Fonte quelatada de Mg para alta biodisponibilidade. "
        "Usado em correções específicas.",
    },

    # ==================== FONTES DE NITROGÊNIO ====================
    "ureia": {
        "nome_comercial": "Ureia",
        "formula_quimica": "CO(NH2)2",
        "n_percent": 46.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 0.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 1079.0,
        "ph_solucao": 7.0,
        "ce_dS_m_por_gramo_L": 0.98,
        "observacoes": "Fonte concentrada de N. Hidrólise pode elevar pH. "
        "Usar com moderação em hidroponia.",
    },

    "nitrato_amonio": {
        "nome_comercial": "Nitrato de Amônio",
        "formula_quimica": "NH4NO3",
        "n_percent": 35.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 0.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 1920.0,
        "ph_solucao": 5.5,
        "ce_dS_m_por_gramo_L": 1.35,
        "observacoes": "Fonte de N nítrico e amoniacal. "
        "ATENÇÃO: Produto controlado. Risco de explosão.",
    },

    "sulfato_amonio": {
        "nome_comercial": "Sulfato de Amônio",
        "formula_quimica": "(NH4)2SO4",
        "n_percent": 21.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 24.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 770.0,
        "ph_solucao": 5.0,
        "ce_dS_m_por_gramo_L": 1.12,
        "observacoes": "Fonte de N e S. Forte acidificante. "
        "Útil em solos alcalinos.",
    },

    # ==================== FONTES DE POTÁSSIO ====================
    "sulfato_potassio": {
        "nome_comercial": "Sulfato de Potássio",
        "formula_quimica": "K2SO4",
        "n_percent": 0.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 50.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 18.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 111.0,
        "ph_solucao": 7.0,
        "ce_dS_m_por_gramo_L": 0.88,
        "observacoes": "Fonte de K e S. Baixa solubilidade. "
        "Usado quando não se desega adicionar N ou Na.",
    },

    "cloreto_potassio": {
        "nome_comercial": "Cloreto de Potássio (KCl)",
        "formula_quimica": "KCl",
        "n_percent": 0.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 60.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 0.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 342.0,
        "ph_solucao": 7.0,
        "ce_dS_m_por_gramo_L": 1.05,
        "observacoes": "Fonte econômica de K. EVITAR em culturas sensíveis a Cl. "
        "Não recomendado para hidroponia.",
    },

    # ==================== MICRONUTRIENTES ====================
    "sulfato_zinco": {
        "nome_comercial": "Sulfato de Zinco",
        "formula_quimica": "ZnSO4·7H2O",
        "n_percent": 0.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 11.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 22.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 965.0,
        "ph_solucao": 5.0,
        "ce_dS_m_por_gramo_L": 0.65,
        "observacoes": "Fonte de Zn. Usado em correções nutricionais. "
        "Compatível com maioria dos sais.",
    },

    "sulfato_manganes": {
        "nome_comercial": "Sulfato de Manganês",
        "formula_quimica": "MnSO4·H2O",
        "n_percent": 0.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 21.0,
        "fe_percent": 0.0,
        "mn_percent": 32.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 985.0,
        "ph_solucao": 5.5,
        "ce_dS_m_por_gramo_L": 0.68,
        "observacoes": "Fonte de Mn. Aplicação foliar ou via fertirrigação. "
        "Evitar excesso.",
    },

    "sulfato_ferro": {
        "nome_comercial": "Sulfato Ferroso",
        "formula_quimica": "FeSO4·7H2O",
        "n_percent": 0.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 11.0,
        "fe_percent": 20.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 290.0,
        "ph_solucao": 3.0,
        "ce_dS_m_por_gramo_L": 0.55,
        "observacoes": "Fonte de Fe. Oxida rapidamente. "
        "Preferir formas quelatadas em hidroponia.",
    },

    "fe_eddha": {
        "nome_comercial": "Fe-EDDHA (Ferro Quelatado)",
        "formula_quimica": "Fe-EDDHA",
        "n_percent": 0.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 0.0,
        "fe_percent": 6.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 100.0,
        "ph_solucao": 7.0,
        "ce_dS_m_por_gramo_L": 0.25,
        "observacoes": "Quelato estável pH 4-9. "
        "Padrão ouro para correção de Fe em solos calcáreos.",
    },

    "fe_edta": {
        "nome_comercial": "Fe-EDTA (Ferro Quelatado)",
        "formula_quimica": "Fe-EDTA",
        "n_percent": 0.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 0.0,
        "fe_percent": 13.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 400.0,
        "ph_solucao": 4.5,
        "ce_dS_m_por_gramo_L": 0.32,
        "observacoes": "Quelato estável até pH 6.5. "
        "Ideal para hidroponia em meio ácido.",
    },

    "sulfato_cobre": {
        "nome_comercial": "Sulfato de Cobre",
        "formula_quimica": "CuSO4·5H2O",
        "n_percent": 0.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 12.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 25.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 230.0,
        "ph_solucao": 4.0,
        "ce_dS_m_por_gramo_L": 0.48,
        "observacoes": "Fonte de Cu. Usar com cautela - toxicidade possível. "
        "Aplicação preferencialmente foliar.",
    },

    "borax": {
        "nome_comercial": "Borax (Tetraborato de Sódio)",
        "formula_quimica": "Na2B4O7·10H2O",
        "n_percent": 0.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 0.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 11.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 25.0,
        "ph_solucao": 9.2,
        "ce_dS_m_por_gramo_L": 0.35,
        "observacoes": "Fonte de B. Baixa solubilidade. CUIDADO: faixa estreita. "
        "Dose correta: 0.5-2 kg/ha. Contém Na.",
    },

    "acido_borico": {
        "nome_comercial": "Ácido Bórico",
        "formula_quimica": "H3BO3",
        "n_percent": 0.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 0.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 17.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 50.0,
        "ph_solucao": 5.1,
        "ce_dS_m_por_gramo_L": 0.28,
        "observacoes": "Fonte de B solúvel. Preferido em hidroponia. "
        "Faixa estreita - toxicidade fácil.",
    },

    "sodium_molibdato": {
        "nome_comercial": "Molibdato de Sódio",
        "formula_quimica": "Na2MoO4·2H2O",
        "n_percent": 0.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 0.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 39.0,
        "solubilidade_g_L_20C": 650.0,
        "ph_solucao": 7.5,
        "ce_dS_m_por_gramo_L": 0.42,
        "observacoes": "Fonte de Mo. Doses muito baixas (50-200 g/ha). "
        "Compatível com maioria dos sais.",
    },

    # ==================== FONTES DE ENXOFRE ====================
    "enxofre_elementar": {
        "nome_comercial": "Enxofre Elementar",
        "formula_quimica": "S",
        "n_percent": 0.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 100.0,
        "fe_percent": 0.0,
        "mn_percent": 0.0,
        "zn_percent": 0.0,
        "b_percent": 0.0,
        "cu_percent": 0.0,
        "mo_percent": 0.0,
        "solubilidade_g_L_20C": 0.0,
        "ph_solucao": 2.0,
        "ce_dS_m_por_gramo_L": 0.0,
        "observacoes": "Fonte pura de S. Insolúvel - aplica-se ao solo. "
        "Requer oxidação por bactérias.",
    },

    # ==================== QUELATO MISTO MICRONUTRIENTES ====================
    "micronutrientes_quelatados": {
        "nome_comercial": "Mix Micronutrientes Quelatados",
        "formula_quimica": "Fe-EDTA + Mn-EDTA + Zn-EDTA + B + Cu + Mo",
        "n_percent": 0.0,
        "p2o5_percent": 0.0,
        "k2o_percent": 0.0,
        "ca_percent": 0.0,
        "mg_percent": 0.0,
        "s_percent": 0.0,
        "fe_percent": 5.0,
        "mn_percent": 2.0,
        "zn_percent": 1.5,
        "b_percent": 0.5,
        "cu_percent": 0.5,
        "mo_percent": 0.1,
        "solubilidade_g_L_20C": 300.0,
        "ph_solucao": 6.0,
        "ce_dS_m_por_gramo_L": 0.55,
        "observacoes": "Formulação comercial padrão para micronutrientes. "
        "Proporções balanceadas para uso geral.",
    },
}

# Incompatibilidades químicas entre sais
# Chave: sal1, Valor: lista de sais incompatíveis (precipitam ou reagem)
INCOMPATIBILIDADES_QUIMICAS: dict[str, list[str]] = {
    "nitrato_calcio": [
        "sulfato_potassio",
        "sulfato_magnesio",
        "sulfato_amonio",
        "map",
        "dap",
        "mkp",
        "sulfato_zinco",
        "sulfato_manganes",
        "sulfato_ferro",
        "sulfato_cobre",
    ],
    "nitrato_calcio_amoniaco": [
        "sulfato_potassio",
        "sulfato_magnesio",
        "sulfato_amonio",
        "map",
        "dap",
        "mkp",
        "sulfato_zinco",
        "sulfato_manganes",
        "sulfato_ferro",
        "sulfato_cobre",
    ],
    "sulfato_magnesio": [
        "nitrato_calcio",
        "nitrato_calcio_amoniaco",
    ],
    "map": [
        "nitrato_calcio",
        "nitrato_calcio_amoniaco",
    ],
    "dap": [
        "nitrato_calcio",
        "nitrato_calcio_amoniaco",
    ],
    "mkp": [
        "nitrato_calcio",
        "nitrato_calcio_amoniaco",
    ],
    "sulfato_potassio": [
        "nitrato_calcio",
        "nitrato_calcio_amoniaco",
    ],
    "sulfato_zinco": [
        "nitrato_calcio",
        "nitrato_calcio_amoniaco",
    ],
    "sulfato_manganes": [
        "nitrato_calcio",
        "nitrato_calcio_amoniaco",
    ],
    "sulfato_ferro": [
        "nitrato_calcio",
        "nitrato_calcio_amoniaco",
    ],
}


def verificar_compatibilidade(sais: list[str]) -> dict[str, list[str] | bool]:
    """
    Verifica compatibilidade química entre uma lista de sais.

    Args:
        sais: Lista de chaves de sais a verificar.

    Returns:
        dict com 'compativel' (bool) e 'incompatibilidades' (list de pares).
    """
    incompatibilidades_encontradas: list[str] = []

    for sal in sais:
        if sal not in SAIS_SOLUVEIS:
            continue
        incompats = INCOMPATIBILIDADES_QUIMICAS.get(sal, [])
        for outro_sal in sais:
            if outro_sal == sal:
                continue
            if outro_sal in incompats:
                par = f"{sal} + {outro_sal}"
                if par not in incompatibilidades_encontradas:
                    incompatibilidades_encontradas.append(par)

    return {
        "compativel": len(incompatibilidades_encontradas) == 0,
        "incompatibilidades": incompatibilidades_encontradas,
    }


def calcular_quantidade_sal(
    sal_chave: str,
    nutrientes_desejados: dict[str, float],
) -> float:
    """
    Calcula quantidade de sal necessária para fornecer nutrientes desejados.

    Args:
        sal_chave: Chave do sal no dicionário SAIS_SOLUVEIS.
        nutrientes_desejados: dict com nutrientes e quantidades em g (ex: {"n": 50}).

    Returns:
        Quantidade de sal em gramas (considera o nutriente limitante).
    """
    if sal_chave not in SAIS_SOLUVEIS:
        raise ValueError(f"Sal '{sal_chave}' não encontrado no banco de dados.")

    sal = SAIS_SOLUVEIS[sal_chave]
    quantidades: list[float] = []

    # Mapeamento de nutrientes para as chaves do sal
    nutrientes_map = {
        "n": "n_percent",
        "p2o5": "p2o5_percent",
        "k2o": "k2o_percent",
        "ca": "ca_percent",
        "mg": "mg_percent",
        "s": "s_percent",
        "fe": "fe_percent",
        "mn": "mn_percent",
        "zn": "zn_percent",
        "b": "b_percent",
        "cu": "cu_percent",
        "mo": "mo_percent",
    }

    for nutriente, quantidade_g in nutrientes_desejados.items():
        if nutriente not in nutrientes_map:
            continue
        teor = sal[nutrientes_map[nutriente]]
        if teor <= 0:
            continue
        # qtd_sal = qtd_nutriente / (teor / 100)
        qtd_sal = quantidade_g / (teor / 100)
        quantidades.append(qtd_sal)

    if not quantidades:
        return 0.0

    # Retorna o maior valor (nutriente limitante)
    return max(quantidades)


def obter_sais_por_nutriente(nutriente: str) -> list[tuple[str, float]]:
    """
    Retorna sais que contêm determinado nutriente, ordenados por teor decrescente.

    Args:
        nutriente: Código do nutriente (n, p2o5, k2o, ca, mg, s, fe, mn, zn, b, cu, mo).

    Returns:
        Lista de tuplas (chave_sal, teor_percentual) ordenada por teor.
    """
    nutrientes_map = {
        "n": "n_percent",
        "p2o5": "p2o5_percent",
        "k2o": "k2o_percent",
        "ca": "ca_percent",
        "mg": "mg_percent",
        "s": "s_percent",
        "fe": "fe_percent",
        "mn": "mn_percent",
        "zn": "zn_percent",
        "b": "b_percent",
        "cu": "cu_percent",
        "mo": "mo_percent",
    }

    if nutriente not in nutrientes_map:
        return []

    chave_teor = nutrientes_map[nutriente]
    resultado: list[tuple[str, float]] = []

    for chave_sal, dados_sal in SAIS_SOLUVEIS.items():
        teor = dados_sal[chave_teor]
        if teor > 0:
            resultado.append((chave_sal, teor))

    resultado.sort(key=lambda x: x[1], reverse=True)
    return resultado