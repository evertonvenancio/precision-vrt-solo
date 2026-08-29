"""
Motor de validacao de guardrails para prescricoes agronomicas.

Este modulo atua como interceptador no pipeline de prescricao, validando
limites fisiologicos, ambientais e de saturacao do solo antes da geracao
da recomendacao final. Protege o Responsavel Tecnico (RT) de erros que
gerem multas ambientais ou problemas agronomicos.

Typical usage:
    >>> from core.guardrails import GuardrailValidator
    >>> from schemas.guardrail import DadosAmostra
    >>> validator = GuardrailValidator()
    >>> amostra = DadosAmostra(ph=5.2, fosforo_mg=45, potassio_mg=80, ...)
    >>> relatorio = validator.validar(amostra, prescricao_id=1, zona_id="A1")
    >>> if relatorio.tem_bloqueio("P2O5"):
    ...     logging.info("Aplicacao de fosforo bloqueada!")
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from schemas.guardrail import (
    DadosAmostra,
    GuardrailResult,
    GuardrailReport,
    SeveridadeGuardrail,
)
from config.guardrails_rules import (
    REGRAS_PADRAO,
    RegraGuardrail,
    TipoRegra,
)

logger = logging.getLogger(__name__)


class GuardrailValidator:
    """Motor de validacao de guardrails para prescricoes agronomicas.

    Valida dados de amostras de solo contra regras configuraveis de seguranca
    juridica, fisiologica e ambiental. Atua como interceptador no pipeline
    de prescricao.

    Args:
        regras: Dicionario de regras customizado. Usa REGRAS_PADRAO se None.
        rt_id: ID do Responsavel Tecnico vinculado (para validacao legal).

    Example:
        >>> validator = GuardrailValidator()
        >>> amostra = DadosAmostra(ph=5.2, fosforo_mg=45, ...)
        >>> relatorio = validator.validar(amostra, prescricao_id=1)
        >>> logging.info(relatorio.status_geral)
    """

    def __init__(
        self,
        regras: Optional[Dict[str, RegraGuardrail]] = None,
        rt_id: Optional[int] = None,
    ):
        self._regras = regras or REGRAS_PADRAO
        self._rt_id = rt_id
        logger.info(
            "GuardrailValidator inicializado com %d regras (RT=%s).",
            len(self._regras),
            rt_id
        )

    # ============================================================
    # METODO PRINCIPAL DE VALIDACAO
    # ============================================================

    def validar(
        self,
        amostra: DadosAmostra,
        prescricao_id: int,
        zona_id: Optional[str] = None,
        dados_extra: Optional[Dict[str, Any]] = None,
    ) -> GuardrailReport:
        """Executa validacao completa de uma amostra contra todas as regras.

        Fluxo:
        1. Validacoes fisicas (erros de laboratorio)
        2. Validacoes ambientais
        3. Validacoes fisiologicas
        4. Validacoes quimicas
        5. Validacoes legais

        Args:
            amostra: Dados da amostra de solo.
            prescricao_id: ID da prescricao sendo validada.
            zona_id: Identificador da zona/talhao.
            dados_extra: Dados adicionais para validacoes especificas.

        Returns:
            GuardrailReport com todos os resultados da validacao.
        """
        logger.info(
            "Validando amostra prescricao=%s zona=%s (pH=%.2f, P=%.1f, K=%.1f)",
            prescricao_id, zona_id, amostra.ph, amostra.fosforo_mg, amostra.potassio_mg
        )

        relatorio = GuardrailReport(
            prescricao_id=prescricao_id,
            zona_id=zona_id,
        )

        # Coletar todos os valores disponiveis da amostra
        valores = self._extrair_valores(amostra)

        # Executar validacoes em ordem de prioridade
        self._validar_fisicas(amostra, relatorio, valores)
        self._validar_ambientais(amostra, relatorio, valores)
        self._validar_fisiologicas(amostra, relatorio, valores)
        self._validar_quimicas(amostra, relatorio, valores)
        self._validar_legais(amostra, relatorio, dados_extra)

        # Atualizar status final
        relatorio._atualizar_status()

        logger.info(
            "Validacao concluida: status=%s, alertas=%d, bloqueios=%d",
            relatorio.status_geral,
            len(relatorio.resultados),
            len(relatorio.nutrientes_bloqueados)
        )
        return relatorio

    def validar_multiplas_amostras(
        self,
        amostras: List[Tuple[DadosAmostra, int, Optional[str]]],
        dados_extra: Optional[Dict[str, Any]] = None,
    ) -> List[GuardrailReport]:
        """Valida multiplas amostras em lote.

        Args:
            amostras: Lista de tuplas (DadosAmostra, prescricao_id, zona_id).
            dados_extra: Dados adicionais compartilhados.

        Returns:
            Lista de GuardrailReport, um por amostra.
        """
        logger.info("Validando %d amostras em lote.", len(amostras))
        relatorios = []
        for amostra, presc_id, zona_id in amostras:
            try:
                rel = self.validar(amostra, presc_id, zona_id, dados_extra)
                relatorios.append(rel)
            except Exception as e:
                logger.exception("Erro ao validar amostra %s: %s", zona_id, e)
                # Criar relatorio de erro
                rel_erro = GuardrailReport(
                    prescricao_id=presc_id,
                    zona_id=zona_id,
                    status_geral="BLOQUEADO",
                )
                rel_erro.adicionar_resultado(GuardrailResult(
                    nutriente_afetado="GERAL",
                    severidade=SeveridadeGuardrail.BLOCK,
                    mensagem=f"Erro interno na validacao: {str(e)}",
                    regra_id="ERRO_INTERNO",
                ))
                relatorios.append(rel_erro)
        return relatorios

    # ============================================================
    # VALIDACOES ESPECIFICAS
    # ============================================================

    def _validar_fisicas(
        self,
        amostra: DadosAmostra,
        relatorio: GuardrailReport,
        valores: Dict[str, float],
    ) -> None:
        """Valida regras fisicas (erros de laboratorio)."""
        regras = [r for r in self._regras.values()
                  if r.tipo == TipoRegra.FISICO and r.ativa]

        for regra in regras:
            valor = valores.get(regra.nutriente_afetado)
            if valor is None:
                # Para regras fisicas gerais, usar pH como referencia
                if regra.regra_id in ("FIS_PH_IMPOSSIVEL", "FIS_PH_NEGATIVO"):
                    valor = amostra.ph
                elif regra.regra_id == "FIS_P_EXTREMO":
                    valor = amostra.fosforo_mg
                elif regra.regra_id == "FIS_K_EXTREMO":
                    valor = amostra.potassio_mg
                elif regra.regra_id == "FIS_ARGILA_IMPOSSIVEL":
                    valor = amostra.argila_pct

            if valor is not None and regra.avaliar(valor):
                resultado = GuardrailResult(
                    nutriente_afetado=regra.nutriente_afetado,
                    severidade=SeveridadeGuardrail(regra.acao.value),
                    mensagem=regra.formatar_mensagem(valor),
                    regra_id=regra.regra_id,
                    valor_atual=valor,
                    valor_limite=regra.limite,
                    zona_id=amostra.zona_id,
                )
                relatorio.adicionar_resultado(resultado)
                logger.warning(
                    "Guardrail FISICO disparado: %s (valor=%.2f, limite=%.2f)",
                    regra.regra_id, valor, regra.limite
                )

    def _validar_ambientais(
        self,
        amostra: DadosAmostra,
        relatorio: GuardrailReport,
        valores: Dict[str, float],
    ) -> None:
        """Valida regras ambientais."""
        regras = [r for r in self._regras.values()
                  if r.tipo == TipoRegra.AMBIENTAL and r.ativa]

        for regra in regras:
            valor = None
            if regra.nutriente_afetado == "P2O5":
                valor = amostra.fosforo_mg

            if valor is not None and regra.avaliar(valor):
                resultado = GuardrailResult(
                    nutriente_afetado=regra.nutriente_afetado,
                    severidade=SeveridadeGuardrail(regra.acao.value),
                    mensagem=regra.formatar_mensagem(valor),
                    regra_id=regra.regra_id,
                    valor_atual=valor,
                    valor_limite=regra.limite,
                    zona_id=amostra.zona_id,
                )
                relatorio.adicionar_resultado(resultado)
                logger.warning(
                    "Guardrail AMBIENTAL disparado: %s (P=%.1f mg/dm3)",
                    regra.regra_id, valor
                )

    def _validar_fisiologicas(
        self,
        amostra: DadosAmostra,
        relatorio: GuardrailReport,
        valores: Dict[str, float],
    ) -> None:
        """Valida regras fisiologicas (pH, saturacao, antagonismo)."""
        regras = [r for r in self._regras.values()
                  if r.tipo == TipoRegra.FISIOLOGICO and r.ativa]

        for regra in regras:
            valor = None

            # pH
            if "PH" in regra.regra_id:
                valor = amostra.ph

            # Saturacao por bases (V%)
            elif "SAT_BASES" in regra.regra_id:
                valor = amostra.saturacao_bases

            # Antagonismo K/(Ca+Mg)
            elif "ANTAGONISMO_K" in regra.regra_id:
                valor = amostra.relacao_k_ca_mg

            if valor is not None and regra.avaliar(valor):
                resultado = GuardrailResult(
                    nutriente_afetado=regra.nutriente_afetado,
                    severidade=SeveridadeGuardrail(regra.acao.value),
                    mensagem=regra.formatar_mensagem(valor),
                    regra_id=regra.regra_id,
                    valor_atual=valor,
                    valor_limite=regra.limite,
                    zona_id=amostra.zona_id,
                )
                relatorio.adicionar_resultado(resultado)
                logger.warning(
                    "Guardrail FISIOLOGICO disparado: %s (valor=%.3f)",
                    regra.regra_id, valor
                )

    def _validar_quimicas(
        self,
        amostra: DadosAmostra,
        relatorio: GuardrailReport,
        valores: Dict[str, float],
    ) -> None:
        """Valida regras quimicas (micronutrientes)."""
        regras = [r for r in self._regras.values()
                  if r.tipo == TipoRegra.QUIMICO and r.ativa]

        for regra in regras:
            # Mapear nutrientes para campos da amostra
            valor = None
            if regra.nutriente_afetado == "B":
                # Boro nao esta no DadosAmostra basico - usar metadata se disponivel
                valor = valores.get("B")
            elif regra.nutriente_afetado == "Zn":
                valor = valores.get("Zn")

            if valor is not None and regra.avaliar(valor):
                resultado = GuardrailResult(
                    nutriente_afetado=regra.nutriente_afetado,
                    severidade=SeveridadeGuardrail(regra.acao.value),
                    mensagem=regra.formatar_mensagem(valor),
                    regra_id=regra.regra_id,
                    valor_atual=valor,
                    valor_limite=regra.limite,
                    zona_id=amostra.zona_id,
                )
                relatorio.adicionar_resultado(resultado)
                logger.warning(
                    "Guardrail QUIMICO disparado: %s (%s=%.2f)",
                    regra.regra_id, regra.nutriente_afetado, valor
                )

    def _validar_legais(
        self,
        amostra: DadosAmostra,
        relatorio: GuardrailReport,
        dados_extra: Optional[Dict[str, Any]],
    ) -> None:
        """Valida regras legais (RT vinculado, certificacao)."""
        regras = [r for r in self._regras.values()
                  if r.tipo == TipoRegra.LEGAL and r.ativa]

        for regra in regras:
            if regra.regra_id == "LEG_RT_AUSENTE":
                # Verificar se RT esta vinculado
                rt_presente = self._rt_id is not None or \
                    (dados_extra and dados_extra.get("rt_id"))
                if not rt_presente:
                    resultado = GuardrailResult(
                        nutriente_afetado="GERAL",
                        severidade=SeveridadeGuardrail.BLOCK,
                        mensagem=regra.mensagem,
                        regra_id=regra.regra_id,
                        zona_id=amostra.zona_id,
                    )
                    relatorio.adicionar_resultado(resultado)
                    logger.warning("Guardrail LEGAL disparado: RT ausente.")

    # ============================================================
    # UTILITARIOS
    # ============================================================

    def _extrair_valores(self, amostra: DadosAmostra) -> Dict[str, float]:
        """Extrai todos os valores numericos da amostra em um dicionario."""
        valores = {
            "PH": amostra.ph,
            "P2O5": amostra.fosforo_mg,
            "K2O": amostra.potassio_mg,
            "CaO": amostra.calcio_cmol,
            "MgO": amostra.magnesio_cmol,
            "ARGILA": amostra.argila_pct,
        }
        if amostra.ctc:
            valores["CTC"] = amostra.ctc
        if amostra.v_pct:
            valores["V_PCT"] = amostra.v_pct
        if amostra.aluminio_cmol:
            valores["AL"] = amostra.aluminio_cmol
        return valores

    def get_nutrientes_permitidos(self, relatorio: GuardrailReport) -> List[str]:
        """Retorna nutrientes que podem ser calculados (sem bloqueio).

        Args:
            relatorio: Relatorio de validacao.

        Returns:
            Lista de nutrientes liberados para calculo.
        """
        nutrientes_padrao = ["N", "P2O5", "K2O", "CaO", "MgO", "S", "B", "Zn", "Mn", "Cu", "Fe", "Mo"]
        bloqueados = set(relatorio.nutrientes_bloqueados)
        return [n for n in nutrientes_padrao if n not in bloqueados]

    def get_nutrientes_bloqueados(self, relatorio: GuardrailReport) -> List[str]:
        """Retorna nutrientes com bloqueio ativo."""
        return relatorio.nutrientes_bloqueados

    def get_resumo_bloqueios(self, relatorio: GuardrailReport) -> Dict[str, List[str]]:
        """Retorna dicionario com bloqueios por nutriente.

        Returns:
            Dict: {nutriente: [mensagens]}.
        """
        resumo = {}
        for r in relatorio.get_por_severidade(SeveridadeGuardrail.BLOCK):
            nut = r.nutriente_afetado
            if nut not in resumo:
                resumo[nut] = []
            resumo[nut].append(r.mensagem)
        return resumo

    def aplicar_justificativa(
        self,
        relatorio: GuardrailReport,
        nutriente: str,
        justificativa: str,
        usuario_id: int,
    ) -> bool:
        """Aplica justificativa manual para um warning.

        Args:
            relatorio: Relatorio a ser modificado.
            nutriente: Nutriente afetado.
            justificativa: Texto da justificativa.
            usuario_id: ID do usuario que forneceu a justificativa.

        Returns:
            True se a justificativa foi aplicada.
        """
        for resultado in relatorio.resultados:
            if (resultado.nutriente_afetado == nutriente.upper() and
                resultado.severidade == SeveridadeGuardrail.WARNING):
                resultado.justificativa = justificativa
                resultado.metadata["justificado_por"] = usuario_id
                resultado.metadata["data_justificativa"] = datetime.now().isoformat()
                logger.info(
                    "Justificativa aplicada para %s por usuario %s: %s",
                    nutriente, usuario_id, justificativa[:50]
                )
                return True
        logger.warning("Nenhum warning encontrado para %s.", nutriente)
        return False

    def exportar_relatorio_json(self, relatorio: GuardrailReport) -> str:
        """Exporta relatorio para JSON string.

        Args:
            relatorio: Relatorio a ser exportado.

        Returns:
            String JSON formatada.
        """
        import json
        return json.dumps(relatorio.to_dict(), indent=2, ensure_ascii=False, default=str)


# ============================================================
# FUNCAO CONVENIENCE
# ============================================================

def validar_prescricao(
    amostra: DadosAmostra,
    prescricao_id: int,
    zona_id: Optional[str] = None,
    rt_id: Optional[int] = None,
    regras_custom: Optional[Dict[str, RegraGuardrail]] = None,
    dados_extra: Optional[Dict[str, Any]] = None,
) -> GuardrailReport:
    """Funcao convenience para validacao rapida.

    Args:
        amostra: Dados da amostra de solo.
        prescricao_id: ID da prescricao.
        zona_id: ID da zona.
        rt_id: ID do Responsavel Tecnico.
        regras_custom: Regras customizadas (opcional).
        dados_extra: Dados adicionais.

    Returns:
        GuardrailReport com resultado da validacao.
    """
    validator = GuardrailValidator(regras=regras_custom, rt_id=rt_id)
    return validator.validar(amostra, prescricao_id, zona_id, dados_extra)


