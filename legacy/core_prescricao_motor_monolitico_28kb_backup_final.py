"""
Precision VRT Solo — Motor de Prescricao Agronomica

Calcula recomendacoes de fertilizantes e corretivos por zona de manejo
com base em metodologias tecnicas brasileiras consolidadas:
  • IAC — Boletim Tecnico 100 (van Raij et al., 1996)
  • CFSEMG — Comissao de Fertilidade do Solo do Estado de Minas Gerais
  • Embrapa — Manuais regionais de adubacao e calagem
  • CONAMA 357/2005 — Guardrail ambiental para fosforo

Suporta:
  • Macronutrientes: N, P2O5, K2O, Ca, Mg, S
  • Micronutrientes: B, Cu, Fe, Mn, Zn
  • Corretivos: calagem, gessagem
  • Qualquer cultura e metodologia cadastrada em CONFIG
  • Qualquer quantidade de zonas geradas pelo Zoneador
  • Multiplas safras
  • Mapas auxiliares (NDVI, produtividade, compactacao, umidade, CE)
  • Analises laboratoriais padronizadas

Guardrail ambiental: P > 40 mg/dm3 bloqueia P2O5 (CONAMA 357/2005).
"""

import logging
from typing import Any, Dict, List, Optional

from .configuracao import ConfigPrescricao, LIMITES_MICRO
from .contratos import NotasTecnicas, ResumoPrescricao, StatusNutriente
from .validacao import (
    calcular_custo_nutriente,
    calcular_dose_corrigida,
    calcular_exportacao,
    classificar_status_nutriente,
    get_parametros_metodo,
)

logger = logging.getLogger(__name__)


# =============================================================================
# CLASSE PRINCIPAL
# =============================================================================

class MotorPrescricao:
    """
    Motor de prescrição de fertilizantes e corretivos por zona de manejo.

    Implementa metodologias agronomicas consolidadas brasileiras
    cadastradas em config/formulas.py.

    A classe e projetada para ser modular, permitindo a adicao de novas
    metodologias, culturas e fontes de dados via camada config/ sem
    alteracoes estruturais no motor.
    """

    def __init__(
        self,
        cultura: str = "soja",
        produtividade: float = 3.0,
        teor_argila: float = 20.0,
        metodo_id: str = "IAC_Graos",
        safra: Optional[str] = None,
        safras: Optional[List[str]] = None,
        mapas_auxiliares: Optional[Dict[str, Any]] = None,
        config: Optional[ConfigPrescricao] = None,
    ):
        """
        Inicializa o Motor de Prescricao.

        Args:
            cultura: Nome da cultura (soja, milho, cafe, cana, trigo).
            produtividade: Produtividade alvo em t/ha de grao seco.
            teor_argila: Teor de argila do solo (%).
            metodo_id: Metodologia de adubacao (IAC_Graos, CFSEMG, etc.).
            safra: Safra principal.
            safras: Lista de safras adicionais.
            mapas_auxiliares: Dict com mapas auxiliares para ajuste de doses.
            config: Configuracao avancada opcional.
        """
        self.config = config or ConfigPrescricao(
            cultura=cultura,
            produtividade=produtividade,
            teor_argila=teor_argila,
            metodo_id=metodo_id,
            safra=safra,
            safras=safras or [],
            mapas_auxiliares=mapas_auxiliares or {},
        )

        self.cultura = self.config.cultura
        self.produtividade = self.config.produtividade
        self.teor_argila = self.config.teor_argila
        self.metodo_id = self.config.metodo_id
        self.safra = self.config.safra
        self.safras = self.config.safras
        self.mapas_auxiliares = self.config.mapas_auxiliares
        self.parametros = get_parametros_metodo(self.metodo_id)

        logger.info(
            "MotorPrescricao inicializado: cultura=%s, metodo=%s, safra=%s, safras=%s",
            self.cultura,
            self.metodo_id,
            self.safra,
            self.safras,
        )

    def prescrever_todas_zonas(
        self,
        perfis_zonas: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Calcula prescricoes para cada zona de manejo.

        Retorna um UNICO valor de dose por zona e por nutriente,
        baseado no perfil medio da zona.

        Args:
            perfis_zonas: formato {zona_id: {atributo: {"media": float, ...}}}

        Returns:
            dict com "prescricoes", "resumo" e "notas_tecnicas".
        """
        if not perfis_zonas:
            raise ValueError("perfis_zonas nao pode ser vazio")

        prescricoes: Dict[str, Dict[str, Any]] = {}
        custos: List[float] = []

        exportacao = calcular_exportacao(self.cultura, self.produtividade)

        for zona_id, perfil in perfis_zonas.items():
            zona_key = str(zona_id)
            presc = self._prescrever_zona_unica(zona_key, perfil, exportacao)
            prescricoes[zona_key] = presc
            custos.append(presc.get("custo_estimado_ha", 0.0))

        resumo = ResumoPrescricao(
            n_zonas=len(prescricoes),
            custo_medio_ha=round(sum(custos) / len(custos), 2) if custos else 0.0,
            custo_min_ha=round(min(custos), 2) if custos else 0.0,
            custo_max_ha=round(max(custos), 2) if custos else 0.0,
            economia_vrt=round(max(custos) - min(custos), 2) if custos else 0.0,
        )

        notas_tecnicas = self._gerar_notas_tecnicas(resumo)

        return {
            "prescricoes": prescricoes,
            "resumo": resumo.to_dict(),
            "notas_tecnicas": notas_tecnicas.to_dict(),
        }

    def _prescrever_zona_unica(
        self,
        zona_id: str,
        perfil: Dict[str, Any],
        exportacao: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Prescreve para uma unica zona baseada no perfil medio.

        Retorna UMA dose unica por nutriente para a zona inteira,
        integrando dados de mapas auxiliares quando disponiveis.
        """

        def get_media(attr: str) -> float:
            return perfil.get(attr, {}).get("media", 0.0)

        ph = get_media("ph")
        v_percent = get_media("v_percent")
        argila = get_media("argila_percent") or self.teor_argila
        p_mg = get_media("p_mg_dm3")
        ca_mg = get_media("ca_mg_dm3")
        mg_mg = get_media("mg_mg_dm3")
        s_mg = get_media("s_mg_dm3")
        ctc = get_media("ctc")

        # Fatores de ajuste por mapas auxiliares
        fator_produtividade = self._obter_fator_mapa(zona_id, "produtividade", 1.0)
        fator_ndvi = self._obter_fator_mapa(zona_id, "ndvi", 1.0)
        fator_compactacao = self._obter_fator_mapa(zona_id, "compactacao", 1.0)
        fator_umidade = self._obter_fator_mapa(zona_id, "umidade", 1.0)
        fator_condutividade = self._obter_fator_mapa(zona_id, "condutividade", 1.0)
        fator_fertilidade = self._obter_fator_mapa(zona_id, "fertilidade", 1.0)

        # --- CALAGEM ---
        calagem = self._calcular_calagem(ph, v_percent, argila, ctc)

        # --- GESSAGEM ---
        gessagem = self._calcular_gessagem(argila)

        # --- NITROGENIO ---
        n_exportacao = exportacao.get("N", 0.0)
        n_dose_necessaria = n_exportacao * fator_produtividade * fator_ndvi
        if v_percent < 40.0:
            n_dose_necessaria *= 1.2
        n_dose = calcular_dose_corrigida(n_dose_necessaria, self.config.eficiencia_n)
        n_status = classificar_status_nutriente(n_dose, "N")

        # --- FOSFORO (P2O5) — COM GUARDRAIL AMBIENTAL ---
        p2o5_exportacao = exportacao.get("P2O5", 0.0)
        p2o5_dose_necessaria = p2o5_exportacao * fator_fertilidade
        p_bloqueado = False
        p_alerta = None

        if ph < 5.5:
            p2o5_dose_necessaria *= 1.15

        # GUARDRAIL: P > 40 mg/dm3 bloqueia aplicacao de P2O5
        if p_mg > self.config.guardrail_p_max:
            p2o5_dose_necessaria = 0.0
            p_bloqueado = True
            p_alerta = (
                "ALERTA AMBIENTAL: Teor de P muito alto (%.1f mg/dm3). "
                "Aplicacao de P2O5 bloqueada por risco de eutrofizacao (CONAMA 357/2005)."
            ) % p_mg

        p2o5_dose = calcular_dose_corrigida(p2o5_dose_necessaria, self.config.eficiencia_p2o5)
        p_status = (
            StatusNutriente.BLOQUEADO.value
            if p_bloqueado
            else classificar_status_nutriente(p2o5_dose, "P")
        )

        # --- POTASSIO (K2O) ---
        k2o_exportacao = exportacao.get("K2O", 0.0)
        k2o_dose_necessaria = k2o_exportacao * fator_condutividade
        k2o_dose = calcular_dose_corrigida(k2o_dose_necessaria, self.config.eficiencia_k2o)
        k_status = classificar_status_nutriente(k2o_dose, "K")

        # --- CALCIO (Ca) ---
        ca_dose_necessaria = self._calcular_ca_necessidade(ca_mg, v_percent)
        ca_dose_necessaria *= fator_compactacao
        ca_dose = calcular_dose_corrigida(ca_dose_necessaria, self.config.eficiencia_ca)
        ca_status = classificar_status_nutriente(ca_dose, "Ca")

        # --- MAGNESIO (Mg) ---
        mg_dose_necessaria = self._calcular_mg_necessidade(mg_mg, v_percent)
        mg_dose_necessaria *= fator_umidade
        mg_dose = calcular_dose_corrigida(mg_dose_necessaria, self.config.eficiencia_mg)
        mg_status = classificar_status_nutriente(mg_dose, "Mg")

        # --- ENXOFRE (S) ---
        s_dose_necessaria = self._calcular_s_necessidade(s_mg, exportacao.get("S", 0.0))
        s_dose_necessaria *= fator_umidade
        s_dose = calcular_dose_corrigida(s_dose_necessaria, self.config.eficiencia_s)
        s_status = classificar_status_nutriente(s_dose, "S")

        # --- MICRONUTRIENTES ---
        micro_resultados = self._calcular_micronutrientes(perfil, exportacao)

        # Custo estimado (R$/ha)
        custo = (
            calcular_custo_nutriente(calagem.get("dose_t_ha", 0.0), self.config.preco_cal / 1000.0)
            + calcular_custo_nutriente(gessagem.get("dose_t_ha", 0.0), self.config.preco_gesso / 1000.0)
            + calcular_custo_nutriente(n_dose, self.config.preco_n)
            + calcular_custo_nutriente(p2o5_dose, self.config.preco_p2o5)
            + calcular_custo_nutriente(k2o_dose, self.config.preco_k2o)
            + calcular_custo_nutriente(ca_dose, self.config.preco_ca)
            + calcular_custo_nutriente(mg_dose, self.config.preco_mg)
            + calcular_custo_nutriente(s_dose, self.config.preco_s)
            + calcular_custo_nutriente(micro_resultados["b"]["dose"], self.config.preco_micro)
            + calcular_custo_nutriente(micro_resultados["cu"]["dose"], self.config.preco_micro)
            + calcular_custo_nutriente(micro_resultados["fe"]["dose"], self.config.preco_fe)
            + calcular_custo_nutriente(micro_resultados["mn"]["dose"], self.config.preco_mn)
            + calcular_custo_nutriente(micro_resultados["zn"]["dose"], self.config.preco_micro)
        )

        return {
            "calagem": calagem,
            "gessagem": gessagem,
            "nitrogenio": {
                "dose_kg_ha": round(n_dose, 2),
                "status": n_status,
                "forma": "N",
            },
            "fosforo": {
                "dose_kg_ha": round(p2o5_dose, 2),
                "status": p_status,
                "forma": "P2O5",
                "bloqueado": p_bloqueado,
                "alerta": p_alerta,
            },
            "potassio": {
                "dose_kg_ha": round(k2o_dose, 2),
                "status": k_status,
                "forma": "K2O",
            },
            "calcio": {
                "dose_kg_ha": round(ca_dose, 2),
                "status": ca_status,
                "forma": "Ca",
            },
            "magnesio": {
                "dose_kg_ha": round(mg_dose, 2),
                "status": mg_status,
                "forma": "Mg",
            },
            "enxofre": {
                "dose_kg_ha": round(s_dose, 2),
                "status": s_status,
                "forma": "S",
            },
            "boro": {
                "dose_kg_ha": round(micro_resultados["b"]["dose"], 3),
                "status": micro_resultados["b"]["status"],
                "forma": "B",
            },
            "cobre": {
                "dose_kg_ha": round(micro_resultados["cu"]["dose"], 3),
                "status": micro_resultados["cu"]["status"],
                "forma": "Cu",
            },
            "ferro": {
                "dose_kg_ha": round(micro_resultados["fe"]["dose"], 3),
                "status": micro_resultados["fe"]["status"],
                "forma": "Fe",
            },
            "manganes": {
                "dose_kg_ha": round(micro_resultados["mn"]["dose"], 3),
                "status": micro_resultados["mn"]["status"],
                "forma": "Mn",
            },
            "zinco": {
                "dose_kg_ha": round(micro_resultados["zn"]["dose"], 3),
                "status": micro_resultados["zn"]["status"],
                "forma": "Zn",
            },
            "custo_estimado_ha": round(custo, 2),
        }

    def _calcular_calagem(
        self,
        ph: float,
        v_percent: float,
        argila: float,
        ctc: float,
    ) -> Dict[str, Any]:
        """
        Calcula a necessidade de calagem conforme metodologia selecionada.

        Formula base (metodo V% — IAC BT-100):
            NC (t/ha) = (V2 - V1) * CTC / 100 * fator_dg * profundidade / PRNT

        Onde:
            V2 = saturacao por bases desejada (%)
            V1 = saturacao por bases atual (%)
            CTC = capacidade de troca cationica efetiva (cmolc/dm3)
            fator_dg = fator de densidade do solo
            profundidade = profundidade de incorporacao (cm)
            PRNT = poder relativo de neutralizacao total (%)

        Args:
            ph: pH do solo (agua 1:2.5).
            v_percent: Saturacao por bases atual (%).
            argila: Teor de argila (%).
            ctc: CTC efetiva (cmolc/dm3).

        Returns:
            Dict com dose, status, metodo e observacoes.
        """
        params = self.parametros["calagem"]
        meta_v = params["meta_v_percent"]
        fator_prnt = params["fator_prnt"]
        profundidade_cm = params["fator_profundidade_cm"]
        fator_dg = params["fator_dg"]
        ph_minimo = params["ph_minimo"]
        ph_alvo = params["ph_alvo"]
        v_minimo = params["v_minimo"]

        # Verificar se calagem e necessaria
        if v_percent >= meta_v and ph >= ph_minimo:
            return {
                "dose_t_ha": 0.0,
                "status": "Nao necessario",
                "metodo": "V%",
                "meta_v_percent": meta_v,
                "criterio": "Solo dentro dos parametros desejados",
                "observacao": (
                    f"pH={ph:.1f} >= {ph_minimo} e V%={v_percent:.1f}% >= {meta_v}%. "
                    "Calagem nao necessaria."
                ),
            }

        # Calcular necessidade de calagem
        # Formula: NC = (V_meta - V_atual) * CTC / 100 * dg * prof / PRNT
        delta_v = max(0.0, meta_v - v_percent)

        if delta_v <= 0:
            return {
                "dose_t_ha": 0.0,
                "status": "Nao necessario",
                "metodo": "V%",
                "meta_v_percent": meta_v,
                "criterio": "Saturacao por bases adequada",
                "observacao": f"V%={v_percent:.1f}% ja atinge a meta de {meta_v}%.",
            }

        # CTC em cmolc/dm3; se nao disponivel, usar estimativa baseada em argila
        ctc_efetiva = ctc if ctc > 0 else argila * 0.15

        # Dose em t/ha de calcario com PRNT = 100%
        # NC = delta_v * CTC / 100 * dg * prof / PRNT
        nc_base = (
            delta_v
            * ctc_efetiva
            / 100.0
            * fator_dg
            * (profundidade_cm / 20.0)  # Normalizado para 20 cm
        )

        # Ajustar pelo PRNT do calcario (PRNT padrao = 67%)
        prnt_usuario = self.config.prnt_percent / 100.0
        nc_corrigida = nc_base / prnt_usuario if prnt_usuario > 0 else nc_base

        # Ajustes por pH
        if ph < 5.0:
            nc_corrigida *= 1.3
        elif ph < 5.5:
            nc_corrigida *= 1.1

        # Ajuste por argila (solos argilosos necessitam mais calcario)
        if argila > 40.0:
            nc_corrigida *= 1.2

        dose_final = round(nc_corrigida, 2)

        return {
            "dose_t_ha": dose_final,
            "status": "Necessario" if dose_final > 0 else "Nao necessario",
            "metodo": "V%",
            "meta_v_percent": meta_v,
            "criterio": "Saturacao por bases",
            "observacao": (
                f"Calagem para elevar V% de {v_percent:.1f}% para {meta_v}%. "
                f"CTC={ctc_efetiva:.1f} cmolc/dm3, PRNT={self.config.prnt_percent:.0f}%, "
                f"Profundidade={profundidade_cm:.0f} cm."
            ),
        }

    def _calcular_gessagem(self, argila: float) -> Dict[str, Any]:
        """
        Calcula a necessidade de gessagem conforme metodologia selecionada.

        Formula (Embrapa / IAC):
            Dose (t/ha) = argila (%) * fator_dose

        Limites:
            - Argila minima para recomendacao: 30%
            - Dose minima: 0.5 t/ha
            - Dose maxima: 3.0 t/ha

        Args:
            argila: Teor de argila do solo (%).

        Returns:
            Dict com dose, status, criterio e observacoes.
        """
        params = self.parametros["gessagem"]
        argila_minima = params["argila_minima_percent"]
        fator_dose = params["fator_dose"]
        dose_maxima = params["dose_maxima_t_ha"]
        dose_minima = params["dose_minima_t_ha"]

        if argila < argila_minima:
            return {
                "dose_t_ha": 0.0,
                "status": "Nao necessario",
                "criterio": "Teor de argila",
                "observacao": (
                    f"Gessagem nao recomendada: argila={argila:.1f}% < "
                    f"minimo={argila_minima:.0f}%."
                ),
            }

        # Dose proporcional ao teor de argila
        dose = argila * fator_dose

        # Aplicar limites
        dose = max(dose_minima, min(dose, dose_maxima))

        return {
            "dose_t_ha": round(dose, 2),
            "status": "Necessario",
            "criterio": "Condicionamento de subsolo",
            "observacao": (
                f"Gessagem recomendada para argila={argila:.1f}%. "
                f"Dose calculada: {dose:.2f} t/ha (limites: {dose_minima}-{dose_maxima} t/ha)."
            ),
        }

    def _calcular_ca_necessidade(self, ca_mg: float, v_percent: float) -> float:
        """
        Calcula a necessidade de calcio em kg/ha.

        Criterio: Ca adequado se > 4.0 cmolc/dm3 e V% > 50%.
        Meta: 3.0 cmolc/dm3 (minimo desejavel).

        Args:
            ca_mg: Calcio trocavel (cmolc/dm3).
            v_percent: Saturacao por bases (%).

        Returns:
            Dose de Ca em kg/ha (0.0 se adequado).
        """
        if ca_mg > 4.0 and v_percent > 50.0:
            return 0.0

        meta_ca = 3.0  # cmolc/dm3
        if ca_mg >= meta_ca:
            return 0.0

        # Deficit em cmolc/dm3 -> kg/ha
        # 1 cmolc/dm3 de Ca = 400 kg/ha (aproximado para camada de 20 cm)
        deficit = meta_ca - ca_mg
        dose_kg_ha = deficit * 400.0

        return max(0.0, dose_kg_ha)

    def _calcular_mg_necessidade(self, mg_mg: float, v_percent: float) -> float:
        """
        Calcula a necessidade de magnesio em kg/ha.

        Criterio: Mg adequado se > 1.0 cmolc/dm3 e V% > 50%.
        Meta: 0.8 cmolc/dm3 (minimo desejavel).

        Args:
            mg_mg: Magnesio trocavel (cmolc/dm3).
            v_percent: Saturacao por bases (%).

        Returns:
            Dose de Mg em kg/ha (0.0 se adequado).
        """
        if mg_mg > 1.0 and v_percent > 50.0:
            return 0.0

        meta_mg = 0.8  # cmolc/dm3
        if mg_mg >= meta_mg:
            return 0.0

        # Deficit em cmolc/dm3 -> kg/ha
        # 1 cmolc/dm3 de Mg = 240 kg/ha (aproximado para camada de 20 cm)
        deficit = meta_mg - mg_mg
        dose_kg_ha = deficit * 240.0

        return max(0.0, dose_kg_ha)

    def _calcular_s_necessidade(self, s_mg: float, exportacao_s: float) -> float:
        """
        Calcula a necessidade de enxofre em kg/ha.

        Criterio: S adequado se > 10 mg/dm3.
        Se baixo: dose baseada na exportacao, com ajuste por nivel.

        Args:
            s_mg: Enxofre disponivel (mg/dm3).
            exportacao_s: Exportacao de S pela cultura (kg/ha).

        Returns:
            Dose de S em kg/ha.
        """
        if s_mg > 10.0:
            return 0.0

        dose = exportacao_s if exportacao_s > 0 else 10.0

        if s_mg < 5.0:
            dose *= 1.5

        return max(0.0, dose)

    def _calcular_micronutrientes(
        self,
        perfil: Dict[str, Any],
        exportacao: Dict[str, float],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calcula doses e status para todos os micronutrientes de uma zona.

        Args:
            perfil: Perfil da zona com medias dos atributos.
            exportacao: Exportacao de nutrientes pela cultura.

        Returns:
            Dict com dose e status para cada micronutriente.
        """
        def get_media(attr: str) -> float:
            return perfil.get(attr, {}).get("media", 0.0)

        micros = {
            "b": ("b_mg_dm3", "B"),
            "cu": ("cu_mg_dm3", "Cu"),
            "fe": ("fe_mg_dm3", "Fe"),
            "mn": ("mn_mg_dm3", "Mn"),
            "zn": ("zn_mg_dm3", "Zn"),
        }

        resultados: Dict[str, Dict[str, Any]] = {}
        for key, (col, nutriente) in micros.items():
            valor_mg = get_media(col)
            exp = exportacao.get(nutriente, 0.0)
            dose = self._calcular_micronutriente_individual(valor_mg, exp, nutriente)
            status = self._classificar_status_micronutriente(valor_mg, nutriente)
            resultados[key] = {"dose": dose, "status": status}

        return resultados

    def _calcular_micronutriente_individual(
        self,
        valor_mg: float,
        exportacao: float,
        nutriente: str,
    ) -> float:
        """
        Calcula dose para um micronutriente individual.

        Criterios:
            - Se valor > adequado * 2: nao necessita (solo suficiente)
            - Se valor >= adequado: manutencao (exportacao)
            - Se valor < adequado: correcao (exportacao * 1.5)

        Args:
            valor_mg: Teor do micronutriente no solo (mg/dm3).
            exportacao: Exportacao pela cultura (kg/ha).
            nutriente: Codigo do nutriente (B, Cu, Fe, Mn, Zn).

        Returns:
            Dose em kg/ha.
        """
        limites = LIMITES_MICRO.get(nutriente, LIMITES_MICRO["B"])
        adequado = limites["adequado"]

        if valor_mg > adequado * 2.0:
            return 0.0

        if valor_mg >= adequado:
            return exportacao if exportacao > 0 else 0.5

        return (exportacao if exportacao > 0 else 1.0) * 1.5

    def _classificar_status_micronutriente(self, valor_mg: float, nutriente: str) -> str:
        """
        Classifica o status de um micronutriente com base no teor no solo.

        Args:
            valor_mg: Teor do micronutriente (mg/dm3).
            nutriente: Codigo do nutriente.

        Returns:
            Status descritivo.
        """
        limites = LIMITES_MICRO.get(nutriente, LIMITES_MICRO["B"])

        if valor_mg < limites["baixo"]:
            return StatusNutriente.MUITO_BAIXO.value
        elif valor_mg < limites["adequado"]:
            return StatusNutriente.BAIXO.value
        elif valor_mg < limites["alto"]:
            return StatusNutriente.ADEQUADO.value
        else:
            return StatusNutriente.ALTO.value

    def _obter_fator_mapa(
        self,
        zona_id: str,
        tipo_mapa: str,
        padrao: float = 1.0,
    ) -> float:
        """
        Obtem fator de ajuste de um mapa auxiliar para a zona especificada.

        Args:
            zona_id: Identificador da zona.
            tipo_mapa: Tipo do mapa auxiliar.
            padrao: Valor padrao caso nao exista mapa.

        Returns:
            Fator de ajuste (float).
        """
        mapa = self.mapas_auxiliares.get(tipo_mapa)
        if mapa is None:
            return padrao

        valor = mapa.get(zona_id)
        if valor is None:
            return padrao

        try:
            fator = float(valor)
            if fator <= 0:
                return padrao
            return round(fator, 3)
        except (TypeError, ValueError):
            return padrao

    def _gerar_notas_tecnicas(self, resumo: ResumoPrescricao) -> NotasTecnicas:
        """
        Gera notas tecnicas complementares para a prescrição.

        Args:
            resumo: Resumo da prescrição com custos e zonas.

        Returns:
            NotasTecnicas com embasamento, bibliografia e referencia legal.
        """
        cultura_nome = self.cultura.capitalize()
        metodo_nome = self.metodo_id.replace("_", " ")

        embasamento = (
            f"Prescricao gerada para {cultura_nome} com metodologia {metodo_nome}. "
            f"O sistema considerou {resumo.n_zonas} zonas de manejo homogeneas, "
            f"com custo medio estimado de R$ {resumo.custo_medio_ha:.2f}/ha. "
            f"A economia potencial com aplicacao de taxa variavel (VRT) e de "
            f"R$ {resumo.economia_vrt:.2f}/ha em relacao a aplicacao uniforme. "
            f"As doses foram calculadas com base na exportacao de nutrientes pela cultura, "
            f"corrigidas pelos fatores de eficiencia dos fertilizantes e ajustadas "
            f"pelos atributos do solo em cada zona."
        )

        bibliografia = (
            "van Raij, B. et al. (1996). Recomendacoes de adubacao e calagem para o Estado de Sao Paulo. "
            "Boletim Tecnico 100, Instituto Agronomico de Campinas (IAC). "
            "Embrapa Solos (2017). Manual de adubacao e calagem para os Estados do Rio Grande do Sul e Santa Catarina. "
            "CFSEMG (1999). Comissao de Fertilidade do Solo do Estado de Minas Gerais. "
            "Boletim Tecnico, Universidade Federal de Lavras (UFLA)."
        )

        referencia_legal = (
            "CONAMA Resolucao n 357, de 17 de marco de 2005. "
            "Dispoe sobre a classificacao dos corpos de agua e diretrizes ambientais para o seu enquadramento, "
            "bem como sobre o lancamento de efluentes. "
            "Guardrail de fosforo ativado quando P > 40 mg/dm3, conforme limites para eutrofizacao. "
            "Resolucao CONAMA 430/2011: condicoes e padroes de lancamento de efluentes."
        )

        return NotasTecnicas(
            embasamento=embasamento,
            bibliografia=bibliografia,
            referencia_legal=referencia_legal,
        )

    def executar(self, perfis_zonas: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Alias para compatibilidade com o pipeline.

        Mantido para retrocompatibilidade com chamadas existentes.
        """
        return self.prescrever_todas_zonas(perfis_zonas)

    def obter_configuracao(self) -> ConfigPrescricao:
        """Retorna a configuracao atual do motor."""
        return self.config

    def atualizar_configuracao(self, **kwargs: Any) -> None:
        """Atualiza a configuracao do motor."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        if "cultura" in kwargs:
            self.cultura = kwargs["cultura"]
        if "produtividade" in kwargs:
            self.produtividade = kwargs["produtividade"]
        if "teor_argila" in kwargs:
            self.teor_argila = kwargs["teor_argila"]
        if "metodo_id" in kwargs:
            self.metodo_id = kwargs["metodo_id"]
            self.parametros = get_parametros_metodo(self.metodo_id)
        if "safra" in kwargs:
            self.safra = kwargs["safra"]
        if "safras" in kwargs:
            self.safras = kwargs["safras"]
        if "mapas_auxiliares" in kwargs:
            self.mapas_auxiliares = kwargs["mapas_auxiliares"]

    def adicionar_mapa_auxiliar(self, tipo: str, dados: Dict[str, Any]) -> None:
        """Adiciona um mapa auxiliar ao motor."""
        self.mapas_auxiliares[tipo] = dados
        self.config.mapas_auxiliares[tipo] = dados

    def remover_mapa_auxiliar(self, tipo: str) -> None:
        """Remove um mapa auxiliar do motor."""
        self.mapas_auxiliares.pop(tipo, None)
        self.config.mapas_auxiliares.pop(tipo, None)

    def listar_mapas_auxiliares(self) -> List[str]:
        """Lista os tipos de mapas auxiliares disponiveis."""
        return list(self.mapas_auxiliares.keys())
