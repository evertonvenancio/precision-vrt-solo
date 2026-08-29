"""
Precision VRT Solo — Exportação de Nutrientes por Cultura

Exportação de nutrientes por cultura (kg/ha de nutriente por tonelada de produto).
Movido de core/prescricao/configuracao.py.
Fonte canônica para cálculo de exportação no motor de prescrição.
NOTA: config/culturas.py contém dados agronômicos completos com metadados.
      Este arquivo é a interface numérica simplificada usada pelo core.
"""

# ---------------------------------------------------------------------------#
# Exportacao de nutrientes por cultura (kg/t de grao seco)                   #
# Fonte: IAC BT-100; Embrapa Soja, Milho, Cafe, Cana, Trigo                  #
# ---------------------------------------------------------------------------#
EXPORTACAO_NUTRIENTES = {
    "soja": {
        "N": 80.0, "P2O5": 20.0, "K2O": 40.0,
        "Ca": 4.0, "Mg": 2.0, "S": 6.0,
        "B": 0.05, "Cu": 0.02, "Fe": 0.10, "Mn": 0.05, "Zn": 0.03,
    },
    "milho": {
        "N": 120.0, "P2O5": 25.0, "K2O": 30.0,
        "Ca": 3.0, "Mg": 2.5, "S": 8.0,
        "B": 0.04, "Cu": 0.03, "Fe": 0.08, "Mn": 0.04, "Zn": 0.04,
    },
    "cafe": {
        "N": 150.0, "P2O5": 30.0, "K2O": 120.0,
        "Ca": 15.0, "Mg": 10.0, "S": 12.0,
        "B": 0.10, "Cu": 0.05, "Fe": 0.15, "Mn": 0.08, "Zn": 0.05,
    },
    "cana": {
        "N": 100.0, "P2O5": 15.0, "K2O": 100.0,
        "Ca": 20.0, "Mg": 8.0, "S": 15.0,
        "B": 0.06, "Cu": 0.02, "Fe": 0.12, "Mn": 0.06, "Zn": 0.03,
    },
    "trigo": {
        "N": 100.0, "P2O5": 22.0, "K2O": 25.0,
        "Ca": 3.0, "Mg": 2.0, "S": 7.0,
        "B": 0.03, "Cu": 0.02, "Fe": 0.06, "Mn": 0.03, "Zn": 0.03,
    },
}