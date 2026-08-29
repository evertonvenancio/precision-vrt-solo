"""
Precision VRT Solo - Serviço do Módulo Extrator
Toda consulta ao banco e regra de negócio centralizada aqui.
"""
import logging
import pandas as pd
from typing import List, Dict
from sqlalchemy.orm import Session

from models.extrator import PontoExtrator, LeituraExtrator, CurvaNutritiva
from core.seguranca.permissions import get_permissoes

logger = logging.getLogger(__name__)


class ExtratorService:
    """
    Serviço central do módulo Extrator.
    Responsável por toda consulta ao banco e regra de negócio.
    """

    def __init__(self, db: Session):
        self.db = db

    # ──────────────────────────────────────────────────────────────
    # CONSULTAS AO BANCO (Repository Layer interno)
    # ──────────────────────────────────────────────────────────────

    def buscar_permissoes(self) -> Dict:
        """Busca as permissões do usuário no banco."""
        return get_permissoes(self.db)

    # ──────────────────────────────────────────────────────────────
    # REGRAS DE NEGÓCIO
    # ──────────────────────────────────────────────────────────────

    def calcular_historico(self, ponto: PontoExtrator, leituras: List[LeituraExtrator],
                           data_inicio=None, data_fim=None) -> Dict:
        """Calcula o histórico de leituras de um ponto com filtros de data."""
        if not leituras:
            return {
                "ponto_id": ponto.id,
                "ponto_codigo": ponto.codigo,
                "cultura": ponto.cultura,
                "fase_fenologica": ponto.fase_fenologica,
                "total_leituras": 0,
                "data_inicio": None,
                "data_fim": None,
                "leituras": [],
                "ce_media": 0.0,
                "ce_min": 0.0,
                "ce_max": 0.0,
                "ph_media": None
            }

        df = pd.DataFrame([{
            "data": l.data_leitura,
            "ce_ds_m": l.ce_ds_m,
            "ph": l.ph,
            "no3_mg_L": l.no3_mg_L,
            "k_mg_L": l.k_mg_L,
            "ca_mg_L": l.ca_mg_L,
            "mg_mg_L": l.mg_mg_L
        } for l in leituras])

        if data_inicio:
            df = df[df["data"] >= data_inicio]
        if data_fim:
            df = df[df["data"] <= data_fim]

        return {
            "ponto_id": ponto.id,
            "ponto_codigo": ponto.codigo,
            "cultura": ponto.cultura,
            "fase_fenologica": ponto.fase_fenologica,
            "total_leituras": len(df),
            "data_inicio": df["data"].min().isoformat() if not df.empty else None,
            "data_fim": df["data"].max().isoformat() if not df.empty else None,
            "leituras": df.to_dict(orient="records"),
            "ce_media": float(df["ce_ds_m"].mean()) if not df.empty else 0.0,
            "ce_min": float(df["ce_ds_m"].min()) if not df.empty else 0.0,
            "ce_max": float(df["ce_ds_m"].max()) if not df.empty else 0.0,
            "ph_media": float(df["ph"].mean()) if not df.empty and df["ph"].notna().any() else None
        }

    def gerar_diagnostico_completo(self, leitura: LeituraExtrator,
                                   curva: CurvaNutritiva,
                                   historico: List[LeituraExtrator]) -> Dict:
        """Gera o diagnóstico completo de uma leitura com base na curva nutritiva."""

        def get_status(valor, min_val, max_val):
            if valor is None or min_val is None or max_val is None:
                return "Sem Dados"
            if valor < min_val:
                return "Deficiente"
            elif valor > max_val:
                return "Excesso"
            return "Adequado"

        diagnostico = {
            "ponto_id": leitura.ponto_id,
            "data_leitura": leitura.data_leitura.isoformat(),
            "alerta_ce": leitura.ce_ds_m > curva.ce_max_ds_m if curva else False,
            "alerta_ph": (leitura.ph < curva.ph_min or leitura.ph > curva.ph_max) if curva and leitura.ph else False,
            "nivel_risco": "baixo",
            "diagnosticos_macronutrientes": [],
            "diagnosticos_micronutrientes": [],
            "tendencias": [],
            "sais_recomendados": [],
            "compatibilidade_sais": {"compativel": True, "incompatibilidades": []},
            "observacoes_gerais": "Diagnóstico gerado automaticamente.",
            "proxima_leitura_dias": 7
        }

        if diagnostico["alerta_ce"] or diagnostico["alerta_ph"]:
            diagnostico["nivel_risco"] = "medio"

        if curva:
            macros = [
                ("NO3", leitura.no3_mg_L, curva.no3_min_mg_L, curva.no3_max_mg_L),
                ("K", leitura.k_mg_L, curva.k_min_mg_L, curva.k_max_mg_L),
                ("Ca", leitura.ca_mg_L, curva.ca_min_mg_L, curva.ca_max_mg_L),
                ("Mg", leitura.mg_mg_L, curva.mg_min_mg_L, curva.mg_max_mg_L)
            ]
            for nome, val, min_v, max_v in macros:
                diagnostico["diagnosticos_macronutrientes"].append({
                    "nutriente": nome,
                    "valor_atual": val,
                    "faixa_ideal": (min_v, max_v),
                    "status": get_status(val, min_v, max_v)
                })

        return diagnostico


def mapear_colunas_csv(colunas: List[str]) -> Dict[str, str]:
    """Mapeia nomes de colunas CSV para os padrões internos do sistema."""
    sinonimos = {
        "ponto_id": ["ponto_id", "ponto", "id", "codigo"],
        "data_leitura": ["data_leitura", "data", "date"],
        "ce_ds_m": ["ce_ds_m", "ce", "condutividade"],
        "ph": ["ph", "pH"],
        "no3_mg_L": ["no3_mg_L", "no3", "nitrato"],
        "k_mg_L": ["k_mg_L", "k", "potassio"],
        "ca_mg_L": ["ca_mg_L", "ca", "calcio"],
        "mg_mg_L": ["mg_mg_L", "mg", "magnesio"]
    }

    mapeamento = {}
    colunas_lower = [c.lower().strip() for c in colunas]

    for padrao, syns in sinonimos.items():
        for syn in syns:
            if syn.lower() in colunas_lower:
                original = colunas[colunas_lower.index(syn.lower())]
                mapeamento[original] = padrao
                break

    return mapeamento
