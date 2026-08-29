"""
Módulo de Agronomia — análise científica de solo.
Consome dados de config/ e aplica metodologias técnicas.
"""

from .contratos import ConfigAgronomia, ResultadoAgronomia, InterpretacaoNutriente
from .motor import MotorAgronomia
from .nutrientes import interpretar_nutriente, interpretar_ph, interpretar_p_mg, interpretar_k_mg, interpretar_ca_cmolc, interpretar_mg_cmolc
from .fertilidade import classificar_fertilidade, calcular_indices_ubs, calcular_indices_aluminio, calcular_ctc_efetiva, calcular_saturation_indices, avaliar_acidez
from .balanco import calcular_exportacao_nutrientes, calcular_balanco, calcular_necessidade_adubacao, calcular_reposicao_nutrientes, calcular_armazenamento_solo, avaliar_sustentabilidade
from .recomendacao import recomendar_calagem, recomendar_adubacao, recomendar_gessagem, calcular_dose_fosforo, gerar_recomendacoes_completas
from .exceptions import ErroAgronomia, TeorInvalido, CulturaNaoEncontrada, MetodoNaoEncontrado, ParametrosInvalidos, BalancoInsuficiente
from .validacao import validar_teores, validar_parametros, validar_cultura, validar_config, validar_entrada_completa, validar_saida

__all__ = [
    # Classes principais
    "MotorAgronomia",
    "ConfigAgronomia",
    "ResultadoAgronomia",
    "InterpretacaoNutriente",
    
    # Funções de nutrientes
    "interpretar_nutriente",
    "interpretar_ph",
    "interpretar_p_mg",
    "interpretar_k_mg",
    "interpretar_ca_cmolc",
    "interpretar_mg_cmolc",
    
    # Funções de fertilidade
    "classificar_fertilidade",
    "calcular_indices_ubs",
    "calcular_indices_aluminio",
    "calcular_ctc_efetiva",
    "calcular_saturation_indices",
    "avaliar_acidez",
    
    # Funções de balanço
    "calcular_exportacao_nutrientes",
    "calcular_balanco",
    "calcular_necessidade_adubacao",
    "calcular_reposicao_nutrientes",
    "calcular_armazenamento_solo",
    "avaliar_sustentabilidade",
    
    # Funções de recomendação
    "recomendar_calagem",
    "recomendar_adubacao",
    "recomendar_gessagem",
    "calcular_dose_fosforo",
    "gerar_recomendacoes_completas",
    
    # Exceções
    "ErroAgronomia",
    "TeorInvalido",
    "CulturaNaoEncontrada",
    "MetodoNaoEncontrado",
    "ParametrosInvalidos",
    "BalancoInsuficiente",
    
    # Validação
    "validar_teores",
    "validar_parametros",
    "validar_cultura",
    "validar_config",
    "validar_entrada_completa",
    "validar_saida",
]