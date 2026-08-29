"""
Precision VRT Solo — Camada de Validação do Módulo de Prescrição

Funções de validação de entrada, consistência de dados e verificações
preliminares para a prescrição agronômica.
"""

from typing import Any, Dict, List, Optional

from config.exportacao_nutrientes import EXPORTACAO_NUTRIENTES
from config.fertilizantes import EFICIENCIA_FERTILIZANTES, CONVERSAO_COMERCIAL, PRECO_REFERENCIA
from config.metodologias import PARAMETROS_CALAGEM, PARAMETROS_GESSAGEM, PARAMETROS_MACRO, TEORES_CRITICOS
from .configuracao import LIMITES_MICRO
from .contratos import StatusNutriente


__all__ = [
    "calcular_exportacao",
    "get_parametros_metodo",
    "classificar_status_nutriente",
    "calcular_dose_corrigida",
    "calcular_custo_nutriente",
    "CULTURAS_SUPORTADAS",
    "METODOLOGIAS_SUPORTADAS",
    "validar_cultura",
    "validar_metodologia",
    "validar_produtividade",
    "validar_teor_argila",
    "validar_perfis_zonas",
    "validar_mapas_auxiliares",
    "validar_safras",
    "validar_safra",
    "validar_configuracao_inicial",
    "validar_dados_prescricao",
]


# =============================================================================
# FUNCOES AUXILIARES AGRONOMICAS
# =============================================================================

def calcular_exportacao(cultura: str, produtividade: float) -> Dict[str, float]:
    """
    Calcula a exportacao total de nutrientes com base na cultura e produtividade.

    A exportacao e o produto da produtividade (t/ha de grao seco) pelos teores
    de nutrientes por tonelada de grao, conforme tabelas do IAC e Embrapa.

    Args:
        cultura: Nome da cultura (soja, milho, cafe, cana, trigo).
        produtividade: Produtividade em t/ha de grao seco.

    Returns:
        Dict com exportacao de cada nutriente em kg/ha.
    """
    cultura_norm = cultura.lower().strip()
    base = EXPORTACAO_NUTRIENTES.get(cultura_norm, EXPORTACAO_NUTRIENTES["soja"])

    exportacao = {}
    for nutriente, kg_por_t in base.items():
        exportacao[nutriente] = kg_por_t * produtividade

    return exportacao


def get_parametros_metodo(metodo_id: str) -> Dict[str, Any]:
    """
    Retorna os parametros agronomicos do metodo selecionado.

    Args:
        metodo_id: Identificador da metodologia (IAC_Graos, CFSEMG, etc.).

    Returns:
        Dict com parametros de calagem, gessagem e macronutrientes.
    """
    calagem = PARAMETROS_CALAGEM.get(metodo_id, PARAMETROS_CALAGEM["IAC_Graos"])
    gessagem = PARAMETROS_GESSAGEM.get(metodo_id, PARAMETROS_GESSAGEM["IAC_Graos"])
    macro = PARAMETROS_MACRO.get(metodo_id, PARAMETROS_MACRO["IAC_Graos"])

    return {
        "calagem": calagem,
        "gessagem": gessagem,
        "macro": macro,
    }


def classificar_status_nutriente(dose: float, nutriente: str) -> str:
    """
    Classifica o status do nutriente com base na dose calculada.

    Args:
        dose: Dose calculada em kg/ha.
        nutriente: Codigo do nutriente (N, P, K, Ca, Mg, S).

    Returns:
        Status descritivo do nutriente.
    """
    if dose <= 0:
        return StatusNutriente.ADEQUADO.value

    limites = TEORES_CRITICOS.get(nutriente, TEORES_CRITICOS["N"])

    if dose < limites["muito_baixo"]:
        return StatusNutriente.ADEQUADO.value
    elif dose < limites["baixo"]:
        return StatusNutriente.MUITO_BAIXO.value
    elif dose < limites["medio"]:
        return StatusNutriente.BAIXO.value
    elif dose < limites["alto"]:
        return StatusNutriente.MEDIO.value
    else:
        return StatusNutriente.NECESSITA_ADUBACAO.value


def calcular_dose_corrigida(
    dose_necessaria: float,
    eficiencia_percent: float,
) -> float:
    """
    Ajusta a dose necessaria pelo fator de eficiencia do fertilizante.

    Formula: Dose_corrigida = Dose_necessaria / (eficiencia / 100)

    Args:
        dose_necessaria: Dose teorica necessaria (kg/ha).
        eficiencia_percent: Eficiencia do fertilizante (%).

    Returns:
        Dose corrigida em kg/ha.
    """
    if dose_necessaria <= 0:
        return 0.0

    eficiencia_decimal = eficiencia_percent / 100.0
    if eficiencia_decimal <= 0:
        return dose_necessaria

    return dose_necessaria / eficiencia_decimal


def calcular_custo_nutriente(dose_kg_ha: float, preco_kg: float) -> float:
    """
    Calcula o custo de um nutriente em R$/ha.

    Args:
        dose_kg_ha: Dose em kg/ha.
        preco_kg: Preco em R$/kg.

    Returns:
        Custo em R$/ha.
    """
    return dose_kg_ha * preco_kg


# =============================================================================
# VALIDACAO DE ENTRADA
# =============================================================================

CULTURAS_SUPORTADAS = frozenset(EXPORTACAO_NUTRIENTES.keys())
METODOLOGIAS_SUPORTADAS = frozenset(PARAMETROS_CALAGEM.keys())


def validar_cultura(cultura: str) -> str:
    """
    Valida e normaliza o nome da cultura.

    Args:
        cultura: Nome da cultura informado.

    Returns:
        Nome da cultura normalizado (lower-case, stripped).

    Raises:
        ValueError: Se a cultura não for suportada.
    """
    cultura_norm = cultura.lower().strip()
    if cultura_norm not in CULTURAS_SUPORTADAS:
        raise ValueError(
            f"Cultura '{cultura}' nao suportada. "
            f"Suportadas: {sorted(CULTURAS_SUPORTADAS)}"
        )
    return cultura_norm


def validar_metodologia(metodo_id: str) -> str:
    """
    Valida o identificador da metodologia.

    Args:
        metodo_id: Identificador da metodologia.

    Returns:
        metodo_id validado.

    Raises:
        ValueError: Se a metodologia não for suportada.
    """
    if metodo_id not in METODOLOGIAS_SUPORTADAS:
        raise ValueError(
            f"Metodologia '{metodo_id}' nao suportada. "
            f"Suportadas: {sorted(METODOLOGIAS_SUPORTADAS)}"
        )
    return metodo_id


def validar_produtividade(produtividade: float) -> float:
    """
    Valida o valor de produtividade.

    Args:
        produtividade: Produtividade em t/ha.

    Returns:
        produtividade validada.

    Raises:
        ValueError: Se produtividade for negativa ou zero.
    """
    if produtividade <= 0:
        raise ValueError(f"Produtividade deve ser positiva. Recebido: {produtividade}")
    return float(produtividade)


def validar_teor_argila(teor_argila: float) -> float:
    """
    Valida o teor de argila do solo.

    Args:
        teor_argila: Teor de argila (%).

    Returns:
        teor_argila validado.

    Raises:
        ValueError: Se o teor de argila estiver fora do intervalo [0, 100].
    """
    if not (0.0 <= teor_argila <= 100.0):
        raise ValueError(
            f"Teor de argila deve estar entre 0 e 100. Recebido: {teor_argila}"
        )
    return float(teor_argila)


def validar_perfis_zonas(perfis_zonas: Dict[str, Dict[str, Any]]) -> None:
    """
    Valida a estrutura dos perfis de zonas recebidos do Zoneamento.

    Args:
        perfis_zonas: formato {zona_id: {atributo: {"media": float, ...}}}

    Raises:
        ValueError: Se perfis_zonas for vazio ou estruturalmente inválido.
    """
    if not perfis_zonas:
        raise ValueError("perfis_zonas nao pode ser vazio")

    if not isinstance(perfis_zonas, dict):
        raise ValueError(f"perfis_zonas deve ser dict. Recebido: {type(perfis_zonas).__name__}")

    for zona_id, perfil in perfis_zonas.items():
        if not isinstance(perfil, dict):
            raise ValueError(
                f"Perfil da zona '{zona_id}' deve ser dict. "
                f"Recebido: {type(perfil).__name__}"
            )


def validar_mapas_auxiliares(mapas_auxiliares: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Valida e normaliza os mapas auxiliares.

    Args:
        mapas_auxiliares: Dict com mapas auxiliares.

    Returns:
        mapas_auxiliares validados (dict vazio se None).
    """
    if mapas_auxiliares is None:
        return {}
    if not isinstance(mapas_auxiliares, dict):
        raise ValueError(
            f"mapas_auxiliares deve ser dict ou None. Recebido: {type(mapas_auxiliares).__name__}"
        )
    return mapas_auxiliares


def validar_safras(safras: Optional[List[str]]) -> List[str]:
    """
    Valida e normaliza a lista de safras.

    Args:
        safras: Lista de safras adicionais.

    Returns:
        Lista de safras validada.
    """
    if safras is None:
        return []
    if not isinstance(safras, list):
        raise ValueError(f"safras deve ser list ou None. Recebido: {type(safras).__name__}")
    return [str(s).strip() for s in safras if s]


def validar_safra(safra: Optional[str]) -> Optional[str]:
    """
    Valida e normaliza a safra principal.

    Args:
        safra: Identificador da safra principal.

    Returns:
        safra validada ou None.
    """
    if safra is None:
        return None
    safra_str = str(safra).strip()
    return safra_str if safra_str else None


def validar_configuracao_inicial(
    cultura: str,
    produtividade: float,
    teor_argila: float,
    metodo_id: str,
    safra: Optional[str] = None,
    safras: Optional[List[str]] = None,
    mapas_auxiliares: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Valida todos os parâmetros de inicialização do MotorPrescricao.

    Retorna um dict com os valores validados e normalizados.

    Raises:
        ValueError: Se qualquer parâmetro for inválido.
    """
    return {
        "cultura": validar_cultura(cultura),
        "produtividade": validar_produtividade(produtividade),
        "teor_argila": validar_teor_argila(teor_argila),
        "metodo_id": validar_metodologia(metodo_id),
        "safra": validar_safra(safra),
        "safras": validar_safras(safras),
        "mapas_auxiliares": validar_mapas_auxiliares(mapas_auxiliares),
    }


def validar_dados_prescricao(
    perfis_zonas: Dict[str, Dict[str, Any]],
    cultura: str,
    metodo_id: str,
) -> None:
    """
    Valida consistência dos dados necessários para geração da prescrição.

    Executado imediatamente antes dos cálculos.

    Args:
        perfis_zonas: Perfis das zonas de manejo.
        cultura: Cultura validada.
        metodo_id: Metodologia validada.

    Raises:
        ValueError: Se houver inconsistência nos dados.
    """
    validar_perfis_zonas(perfis_zonas)
    validar_cultura(cultura)
    validar_metodologia(metodo_id)
