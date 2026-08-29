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
from .calculos import (
    _calcular_calagem,
    _calcular_gessagem,
    _calcular_ca_necessidade,
    _calcular_mg_necessidade,
    _calcular_s_necessidade,
    _calcular_micronutrientes,
    _calcular_micronutriente_individual,
    calcular_guardrail_fosforo,
    _classificar_status_micronutriente,
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
        # Converter ConfigPrescricao para dict para compatibilidade com funções dos submódulos
        config_dict = {
            "prnt_percent": self.config.prnt_percent,
            "fator_dg": self.config.fator_dg,
            "profundidade_cm": self.config.profundidade_cm,
        }
        calagem = _calcular_calagem(ph, v_percent, argila, ctc, config_dict, self.parametros)

        # --- GESSAGEM ---
        gessagem = _calcular_gessagem(argila, self.parametros)

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
        guardrail_p = calcular_guardrail_fosforo(p_mg, self.config.guardrail_p_max, self.config)
        p_bloqueado = guardrail_p["bloqueado"]
        p_alerta = guardrail_p["alerta"]

        if p_bloqueado:
            p2o5_dose_necessaria = 0.0

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
        ca_dose_necessaria = _calcular_ca_necessidade(ca_mg, v_percent)
        ca_dose_necessaria *= fator_compactacao
        ca_dose = calcular_dose_corrigida(ca_dose_necessaria, self.config.eficiencia_ca)
        ca_status = classificar_status_nutriente(ca_dose, "Ca")

        # --- MAGNESIO (Mg) ---
        mg_dose_necessaria = _calcular_mg_necessidade(mg_mg, v_percent)
        mg_dose_necessaria *= fator_umidade
        mg_dose = calcular_dose_corrigida(mg_dose_necessaria, self.config.eficiencia_mg)
        mg_status = classificar_status_nutriente(mg_dose, "Mg")

        # --- ENXOFRE (S) ---
        s_dose_necessaria = _calcular_s_necessidade(s_mg, exportacao.get("S", 0.0))
        s_dose_necessaria *= fator_umidade
        s_dose = calcular_dose_corrigida(s_dose_necessaria, self.config.eficiencia_s)
        s_status = classificar_status_nutriente(s_dose, "S")

        # --- MICRONUTRIENTES ---
        micro_resultados = _calcular_micronutrientes(perfil, exportacao, self.config, self.parametros)

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