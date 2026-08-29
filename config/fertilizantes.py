"""
Precision VRT Solo — Dados de Domínio: Fertilizantes, Eficiências e Preços

Dados de domínio agronômico movidos de core/prescricao/configuracao.py para isolar
o core científico das informações específicas de mercado e tecnologia.
"""

# ---------------------------------------------------------------------------#
# Fatores de eficiência de fertilizantes (tecnica brasileira consolidada)     #
# Fonte: IAC BT-100; Embrapa manuais regionais; CFSEMG                       #
# ---------------------------------------------------------------------------#
EFICIENCIA_FERTILIZANTES = {
    "N": {"fonte": "Ureia/MAP", "eficiencia_percent": 60.0},
    "P2O5": {"fonte": "Superfosfato Triplo", "eficiencia_percent": 20.0},
    "K2O": {"fonte": "KCl", "eficiencia_percent": 50.0},
    "Ca": {"fonte": "Calcario", "eficiencia_percent": 80.0},
    "Mg": {"fonte": "Dolomitico", "eficiencia_percent": 80.0},
    "S": {"fonte": "Gesso Agricola", "eficiencia_percent": 70.0},
}

# ---------------------------------------------------------------------------#
# Fatores de conversão de nutriente -> forma comercial                       #
# ---------------------------------------------------------------------------#
CONVERSAO_COMERCIAL = {
    "P_para_P2O5": 2.29,      # P x 2.29 = P2O5
    "K_para_K2O": 1.20,       # K x 1.20 = K2O
    "Ca_para_CaO": 1.40,      # Ca x 1.40 = CaO
    "Mg_para_MgO": 1.66,      # Mg x 1.66 = MgO
    "S_para_SO4": 3.00,       # S x 3.00 = SO4 (aproximado para gesso)
}

# ---------------------------------------------------------------------------#
# Preços de referência (R$) — atualizáveis via config                       #
# ---------------------------------------------------------------------------#
PRECO_REFERENCIA = {
    "cal": 150.0,             # R$/t — calcario dolomitico
    "gesso": 200.0,           # R$/t — gesso agricola
    "N": 8.0,                 # R$/kg N
    "P2O5": 6.0,              # R$/kg P2O5
    "K2O": 5.0,               # R$/kg K2O
    "Ca": 3.0,                # R$/kg Ca
    "Mg": 4.0,                # R$/kg Mg
    "S": 5.0,                 # R$/kg S
    "micro": 50.0,            # R$/kg micronutriente (B, Cu, Zn)
    "Fe": 30.0,               # R$/kg Fe
    "Mn": 30.0,               # R$/kg Mn
}