"""
Configuracao de regras de guardrails para validacao de prescricoes.

Este modulo contem os limites, mensagens e parametros configuraveis para
cada regra de seguranca juridica e agronomica. Permite customizacao por
tenant ou por cultura sem alterar o codigo do motor.

Typical usage:
    >>> from config.guardrails_rules import REGRAS_PADRAO, RegraGuardrail
    >>> regra = REGRAS_PADRAO["ENV_P_MAX"]
    >>> logging.info(regra.mensagem_block)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TipoRegra(str, Enum):
    """Categorias de regras de guardrail."""
    AMBIENTAL = "ambiental"
    FISIOLOGICO = "fisiologico"
    FISICO = "fisico"
    QUIMICO = "quimico"
    LEGAL = "legal"


class AcaoRegra(str, Enum):
    """Acoes possiveis ao disparar uma regra."""
    BLOCK = "BLOCK"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass(frozen=True)
class RegraGuardrail:
    """Define uma regra de guardrail com parametros configuraveis.

    Attributes:
        regra_id: Identificador unico da regra (ex: "ENV_P_MAX").
        tipo: Categoria da regra (ambiental, fisiologico, etc.).
        nutriente_afetado: Nutriente ou parametro afetado (ex: "P2O5", "CaO", "GERAL").
        acao: Acao padrao (BLOCK, WARNING, INFO).
        limite: Valor limite numerico para disparo.
        operador: Funcao de comparacao (ex: lambda x, lim: x > lim).
        mensagem: Mensagem padrao para o usuario.
        mensagem_detalhada: Mensagem tecnica detalhada.
        referencia_legal: Referencia normativa (ex: "CONAMA 357/2005").
        mitigacao: Sugestao de mitigacao.
        ativa: Se a regra esta ativa.
        parametros_extra: Parametros adicionais especificos da regra.
    """
    regra_id: str
    tipo: TipoRegra
    nutriente_afetado: str
    acao: AcaoRegra
    limite: float
    operador: str  # ">", "<", ">=", "<=", "==", "!="
    mensagem: str
    mensagem_detalhada: Optional[str] = None
    referencia_legal: Optional[str] = None
    mitigacao: Optional[str] = None
    ativa: bool = True
    parametros_extra: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Valida consistencia da regra."""
        if self.operador not in (">", "<", ">=", "<=", "==", "!="):
            raise ValueError(f"Operador invalido: {self.operador}")

    def avaliar(self, valor: float) -> bool:
        """Avalia se o valor dispara a regra.

        Args:
            valor: Valor medido a ser comparado.

        Returns:
            True se a regra foi disparada.
        """
        ops = {
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
        }
        return ops[self.operador](valor, self.limite)

    def formatar_mensagem(self, valor_atual: Optional[float] = None) -> str:
        """Formata a mensagem substituindo placeholders.

        Args:
            valor_atual: Valor medido para substituir {valor} na mensagem.

        Returns:
            Mensagem formatada.
        """
        msg = self.mensagem
        if valor_atual is not None:
            msg = msg.replace("{valor}", f"{valor_atual:.2f}")
        msg = msg.replace("{limite}", f"{self.limite:.2f}")
        return msg


# ============================================================
# REGRAS PADRAO
# ============================================================

REGRAS_PADRAO: Dict[str, RegraGuardrail] = {
    # ============================================================
    # REGRAS AMBIENTAIS
    # ============================================================
    "ENV_P_MAX": RegraGuardrail(
        regra_id="ENV_P_MAX",
        tipo=TipoRegra.AMBIENTAL,
        nutriente_afetado="P2O5",
        acao=AcaoRegra.BLOCK,
        limite=40.0,
        operador=">",
        mensagem=(
            "⚠️ ALERTA AMBIENTAL: Teor de P muito alto ({valor} mg/dm³). "
            "Risco de eutrofizacao e multa (CONAMA). Aplicacao de P2O5 BLOQUEADA."
        ),
        mensagem_detalhada=(
            "O teor de fosforo no solo excede 40 mg/dm³ (Mehlich), indicando "
            "saturacao do sistema. Adicao de fontes de P2O5 pode causar lixiviacao "
            "para corpos d'agua, gerando eutrofizacao e exposicao a multas ambientais "
            "(CONAMA 357/2005, art. 16)."
        ),
        referencia_legal="CONAMA 357/2005",
        mitigacao=(
            "1. Nao aplicar fontes de P2O5 nesta zona. "
            "2. Considerar culturas extrativas de P (ex: braquiaria). "
            "3. Monitorar corpos d'agua proximos."
        ),
    ),
    "ENV_P_WARNING": RegraGuardrail(
        regra_id="ENV_P_WARNING",
        tipo=TipoRegra.AMBIENTAL,
        nutriente_afetado="P2O5",
        acao=AcaoRegra.WARNING,
        limite=30.0,
        operador=">",
        mensagem=(
            "⚠️ ATENCAO: Teor de P elevado ({valor} mg/dm³). "
            "Proximo ao limite ambiental. Justificativa obrigatoria para aplicar P2O5."
        ),
        mensagem_detalhada=(
            "Teor de fosforo acima de 30 mg/dm³ indica acumulo significativo. "
            "Aplicacao de P2O5 requer justificativa tecnica detalhada."
        ),
        referencia_legal="CONAMA 357/2005",
        mitigacao="Reduzir dose de P2O5 em 50% ou usar fontes de liberacao lenta.",
    ),

    # ============================================================
    # REGRAS FISIOLOGICAS - CALAGEM
    # ============================================================
    "SAT_BASES_BLOCK": RegraGuardrail(
        regra_id="SAT_BASES_BLOCK",
        tipo=TipoRegra.FISIOLOGICO,
        nutriente_afetado="CaO",
        acao=AcaoRegra.BLOCK,
        limite=70.0,
        operador=">",
        mensagem=(
            "🚫 Saturacao por bases (V%) ja adequada/elevada ({valor}%). "
            "Calagem BLOQUEADA nesta zona."
        ),
        mensagem_detalhada=(
            "A saturacao por bases (V%) excede 70%, indicando solo ja corrigido. "
            "Aplicacao de calcario pode elevar o pH acima do ideal, reduzindo "
            "a disponibilidade de micronutrientes (Fe, Mn, Zn, Cu) e causando "
            "deficiencias nutricionais."
        ),
        referencia_legal="Manual de Adubacao e Calagem - SBCS",
        mitigacao=(
            "1. Nao aplicar calcario. "
            "2. Monitorar micronutrientes foliar. "
            "3. Se pH > 6.8, considerar aplicacao de enxofre elementar."
        ),
    ),
    "SAT_BASES_WARNING": RegraGuardrail(
        regra_id="SAT_BASES_WARNING",
        tipo=TipoRegra.FISIOLOGICO,
        nutriente_afetado="CaO",
        acao=AcaoRegra.WARNING,
        limite=60.0,
        operador=">",
        mensagem=(
            "⚠️ Saturacao por bases (V%) proxima do limite ({valor}%). "
            "Calagem pode ser desnecessaria. Justificativa obrigatoria."
        ),
        mitigacao="Avaliar necessidade real via analise foliar e produtividade historica.",
    ),

    # ============================================================
    # REGRAS DE pH
    # ============================================================
    "PH_ALTO_BLOCK": RegraGuardrail(
        regra_id="PH_ALTO_BLOCK",
        tipo=TipoRegra.FISIOLOGICO,
        nutriente_afetado="CaO",
        acao=AcaoRegra.BLOCK,
        limite=6.5,
        operador=">",
        mensagem=(
            "🚫 pH do solo elevado ({valor}). Calagem BLOQUEADA. "
            "pH acima de 6.5 compromete a eficiencia da calagem."
        ),
        mensagem_detalhada=(
            "pH acima de 6.5 indica solo ja neutro a levemente alcalino. "
            "Aplicacao de calcario pode elevar o pH acima de 7.0, causando "
            "precipitacao de fosforo, ferro, manganes, zinco e cobre."
        ),
        referencia_legal="Manual de Adubacao e Calagem - SBCS",
        mitigacao=(
            "1. Nao aplicar calcario. "
            "2. Se pH > 7.0, monitorar micronutrientes e considerar "
            "aplicacao foliar de Fe, Mn, Zn."
        ),
    ),
    "PH_MUITO_ALTO_WARNING": RegraGuardrail(
        regra_id="PH_MUITO_ALTO_WARNING",
        tipo=TipoRegra.FISIOLOGICO,
        nutriente_afetado="GERAL",
        acao=AcaoRegra.WARNING,
        limite=7.0,
        operador=">",
        mensagem=(
            "⚠️ pH muito alto ({valor}). Risco de indisponibilidade de "
            "micronutrientes (Fe, Mn, Zn, Cu). Justificativa obrigatoria."
        ),
        mensagem_detalhada=(
            "pH acima de 7.0 reduz drasticamente a solubilidade de Fe, Mn, Zn e Cu. "
            "Pode causar clorose ferrica e deficiencias de manganes e zinco. "
            "Recomenda-se aplicacao foliar ou uso de quelatos."
        ),
        mitigacao=(
            "1. Evitar calagem. "
            "2. Aplicar micronutrientes via foliar (Fe-EDDHA, Zn-EDTA). "
            "3. Considerar enxofre elementar para reducao gradual do pH."
        ),
    ),
    "PH_BAIXO_BLOCK": RegraGuardrail(
        regra_id="PH_BAIXO_BLOCK",
        tipo=TipoRegra.FISIOLOGICO,
        nutriente_afetado="GERAL",
        acao=AcaoRegra.INFO,
        limite=4.5,
        operador="<",
        mensagem=(
            "ℹ️ pH muito baixo ({valor}). Solo fortemente acido. "
            "Toxicidade de Al³+ provavel. Calagem URGENTE recomendada."
        ),
        mensagem_detalhada=(
            "pH abaixo de 4.5 indica alta saturacao por aluminio (provavelmente > 30%). "
            "Risco de toxicidade de Al³+ para raizes. Calagem e prioridade maxima."
        ),
        mitigacao="Aplicar calcario dolomitico com PRNT >= 80% e incorporar 20cm.",
    ),

    # ============================================================
    # REGRAS DE ANTAGONISMO K/(Ca+Mg)
    # ============================================================
    "ANTAGONISMO_K_BLOCK": RegraGuardrail(
        regra_id="ANTAGONISMO_K_BLOCK",
        tipo=TipoRegra.FISIOLOGICO,
        nutriente_afetado="K2O",
        acao=AcaoRegra.BLOCK,
        limite=0.5,
        operador=">",
        mensagem=(
            "🚫 Relacao K/(Ca+Mg) muito alta ({valor}). "
            "Risco de inibicao competitiva e toxicidade de K. "
            "Aplicacao de K2O BLOQUEADA."
        ),
        mensagem_detalhada=(
            "Relacao K/(Ca+Mg) > 0.5 indica desequilibrio ionico. "
            "Excesso de K inibe a absorcao de Ca e Mg, causando "
            "blossom-end rot em tomate, tip-burn em alface, e "
            "clorose marginal em soja."
        ),
        referencia_legal="Manual de Nutricao Mineral de Plantas - Malavolta",
        mitigacao=(
            "1. Nao aplicar K2O nesta zona. "
            "2. Aplicar calcario dolomitico para elevar Ca e Mg. "
            "3. Monitorar sintomas de deficiencia de Ca/Mg nas folhas."
        ),
    ),
    "ANTAGONISMO_K_WARNING": RegraGuardrail(
        regra_id="ANTAGONISMO_K_WARNING",
        tipo=TipoRegra.FISIOLOGICO,
        nutriente_afetado="K2O",
        acao=AcaoRegra.WARNING,
        limite=0.3,
        operador=">",
        mensagem=(
            "⚠️ Relacao K/(Ca+Mg) elevada ({valor}). "
            "Risco de antagonismo K-Ca-Mg. Justificativa obrigatoria para K2O."
        ),
        mitigacao="Reduzir dose de K2O em 30-50% e acompanhar analise foliar.",
    ),

    # ============================================================
    # REGRAS FISICAS - LIMITES ABSURDOS
    # ============================================================
    "FIS_PH_IMPOSSIVEL": RegraGuardrail(
        regra_id="FIS_PH_IMPOSSIVEL",
        tipo=TipoRegra.FISICO,
        nutriente_afetado="GERAL",
        acao=AcaoRegra.BLOCK,
        limite=14.0,
        operador=">",
        mensagem=(
            "🚫 ERRO DE LABORATORIO: pH = {valor} e fisicamente impossivel. "
            "Verificar laudo do laboratorio. Calculo BLOQUEADO."
        ),
        mensagem_detalhada="pH do solo nao pode exceder 14. Valor indica erro analitico.",
        mitigacao="Solicitar nova analise ao laboratorio credenciado.",
    ),
    "FIS_PH_NEGATIVO": RegraGuardrail(
        regra_id="FIS_PH_NEGATIVO",
        tipo=TipoRegra.FISICO,
        nutriente_afetado="GERAL",
        acao=AcaoRegra.BLOCK,
        limite=0.0,
        operador="<",
        mensagem=(
            "🚫 ERRO DE LABORATORIO: pH negativo ({valor}). "
            "Verificar laudo. Calculo BLOQUEADO."
        ),
        mitigacao="Solicitar nova analise ao laboratorio.",
    ),
    "FIS_P_EXTREMO": RegraGuardrail(
        regra_id="FIS_P_EXTREMO",
        tipo=TipoRegra.FISICO,
        nutriente_afetado="P2O5",
        acao=AcaoRegra.BLOCK,
        limite=200.0,
        operador=">",
        mensagem=(
            "🚫 ERRO DE LABORATORIO: Fosforo = {valor} mg/dm³ e extremamente alto. "
            "Verificar laudo. Calculo de P2O5 BLOQUEADO."
        ),
        mensagem_detalhada="Teores de P acima de 200 mg/dm³ sao fisicamente improvaveis em solos tropicais.",
        mitigacao="Verificar unidade de medida e solicitar nova analise.",
    ),
    "FIS_K_EXTREMO": RegraGuardrail(
        regra_id="FIS_K_EXTREMO",
        tipo=TipoRegra.FISICO,
        nutriente_afetado="K2O",
        acao=AcaoRegra.BLOCK,
        limite=800.0,
        operador=">",
        mensagem=(
            "🚫 ERRO DE LABORATORIO: Potassio = {valor} mg/dm³ e extremamente alto. "
            "Verificar laudo. Calculo de K2O BLOQUEADO."
        ),
        mitigacao="Verificar unidade de medida (pode estar em cmolc/dm3 em vez de mg/dm3).",
    ),
    "FIS_ARGILA_IMPOSSIVEL": RegraGuardrail(
        regra_id="FIS_ARGILA_IMPOSSIVEL",
        tipo=TipoRegra.FISICO,
        nutriente_afetado="GERAL",
        acao=AcaoRegra.BLOCK,
        limite=100.0,
        operador=">",
        mensagem=(
            "🚫 ERRO DE LABORATORIO: Argila = {valor}% e impossivel. "
            "Soma das fracoes texturais deve ser 100%. Verificar laudo."
        ),
        mitigacao="Verificar analise granulometrica.",
    ),

    # ============================================================
    # REGRAS QUIMICAS - MICRONUTRIENTES
    # ============================================================
    "MICRO_B_ALTO": RegraGuardrail(
        regra_id="MICRO_B_ALTO",
        tipo=TipoRegra.QUIMICO,
        nutriente_afetado="B",
        acao=AcaoRegra.WARNING,
        limite=3.0,
        operador=">",
        mensagem=(
            "⚠️ Teor de Boro elevado ({valor} mg/dm³). "
            "Risco de toxicidade para culturas sensiveis (citrus, soja)."
        ),
        mensagem_detalhada=(
            "Boro em excesso causa necrose marginal das folhas, clorose e "
            "reducao do crescimento radicular. Culturas sensiveis: citrus, "
            "soja, feijao, tomate."
        ),
        mitigacao="Evitar fontes de B na adubacao. Aplicar calcario para reduzir disponibilidade.",
    ),
    "MICRO_ZN_BAIXO": RegraGuardrail(
        regra_id="MICRO_ZN_BAIXO",
        tipo=TipoRegra.QUIMICO,
        nutriente_afetado="Zn",
        acao=AcaoRegra.INFO,
        limite=0.5,
        operador="<",
        mensagem=(
            "ℹ️ Teor de Zinco baixo ({valor} mg/dm³). "
            "Recomendada aplicacao de Zn na adubacao."
        ),
        mitigacao="Aplicar 2-4 kg/ha de Zn (sulfato ou quelato) ou 20 kg/ha de fritas.",
    ),

    # ============================================================
    # REGRAS LEGAIS - CERTIFICACAO
    # ============================================================
    "LEG_RT_AUSENTE": RegraGuardrail(
        regra_id="LEG_RT_AUSENTE",
        tipo=TipoRegra.LEGAL,
        nutriente_afetado="GERAL",
        acao=AcaoRegra.BLOCK,
        limite=0.0,
        operador="==",
        mensagem=(
            "🚫 Responsavel Tecnico (RT) nao vinculado a esta prescricao. "
            "Laudo nao pode ser emitido sem assinatura do RT."
        ),
        referencia_legal="Lei 13.021/2014 (Lei dos Agronomos)",
        mitigacao="Vincular RT credenciado no CRA antes de emitir laudo.",
        parametros_extra={"requer_rt": True},
    ),
}


# ============================================================
# AGRUPAMENTOS DE REGRAS POR CATEGORIA
# ============================================================

REGRAS_AMBIENTAIS = [r for r in REGRAS_PADRAO.values() if r.tipo == TipoRegra.AMBIENTAL]
REGRAS_FISIOLOGICAS = [r for r in REGRAS_PADRAO.values() if r.tipo == TipoRegra.FISIOLOGICO]
REGRAS_FISICAS = [r for r in REGRAS_PADRAO.values() if r.tipo == TipoRegra.FISICO]
REGRAS_QUIMICAS = [r for r in REGRAS_PADRAO.values() if r.tipo == TipoRegra.QUIMICO]
REGRAS_LEGais = [r for r in REGRAS_PADRAO.values() if r.tipo == TipoRegra.LEGAL]


def get_regra(regra_id: str) -> Optional[RegraGuardrail]:
    """Retorna uma regra pelo ID.

    Args:
        regra_id: Identificador da regra.

    Returns:
        RegraGuardrail ou None se nao encontrada.
    """
    return REGRAS_PADRAO.get(regra_id)


def get_regras_por_tipo(tipo: TipoRegra) -> List[RegraGuardrail]:
    """Retorna todas as regras de um tipo especifico."""
    return [r for r in REGRAS_PADRAO.values() if r.tipo == tipo]


def get_regras_por_nutriente(nutriente: str) -> List[RegraGuardrail]:
    """Retorna todas as regras que afetam um nutriente."""
    return [r for r in REGRAS_PADRAO.values() if r.nutriente_afetado == nutriente.upper()]


def get_regras_ativas() -> List[RegraGuardrail]:
    """Retorna apenas regras ativas."""
    return [r for r in REGRAS_PADRAO.values() if r.ativa]


def criar_config_customizada(
    overrides: Dict[str, Dict[str, Any]]
) -> Dict[str, RegraGuardrail]:
    """Cria uma configuracao customizada a partir das regras padrao.

    Args:
        overrides: Dicionario com overrides por regra_id.
            Ex: {"ENV_P_MAX": {"limite": 35.0, "acao": "WARNING"}}

    Returns:
        Novo dicionario de regras com overrides aplicados.
    """
    from copy import deepcopy
    custom = deepcopy(REGRAS_PADRAO)

    for regra_id, params in overrides.items():
        if regra_id not in custom:
            logger.warning("Regra %s nao encontrada para override.", regra_id)
            continue
        regra_atual = custom[regra_id]
        # Criar nova regra com parametros modificados
        kwargs = {
            "regra_id": regra_atual.regra_id,
            "tipo": regra_atual.tipo,
            "nutriente_afetado": regra_atual.nutriente_afetado,
            "acao": params.get("acao", regra_atual.acao),
            "limite": params.get("limite", regra_atual.limite),
            "operador": params.get("operador", regra_atual.operador),
            "mensagem": params.get("mensagem", regra_atual.mensagem),
            "mensagem_detalhada": params.get("mensagem_detalhada", regra_atual.mensagem_detalhada),
            "referencia_legal": params.get("referencia_legal", regra_atual.referencia_legal),
            "mitigacao": params.get("mitigacao", regra_atual.mitigacao),
            "ativa": params.get("ativa", regra_atual.ativa),
            "parametros_extra": params.get("parametros_extra", regra_atual.parametros_extra),
        }
        custom[regra_id] = RegraGuardrail(**kwargs)
        logger.info("Regra %s customizada: %s", regra_id, params)

    return custom


