"""
Funções de normalização de dados.
"""
import pandas as pd

def _padronizar_id(serie: pd.Series) -> pd.Series:
    """Padroniza uma série de IDs (remove espaços, uppercase, strip)."""
    return serie.astype(str).str.strip().str.replace(r'\\.0$', '', regex=True)