"""
Validação de entrada para o módulo de agronomia.
"""
from typing import Any, Dict, List, Optional

from .exceptions import TeorInvalido, ParametrosInvalidos


def validar_teores(teores: Dict[str, float]) -> List[str]:
    """
    Valida os teores de nutrientes do solo.
    
    Args:
        teores: Dicionário com teores de nutrientes
    
    Returns:
        Lista de erros encontrados
    """
    erros = []
    
    # Verificar nutrientes obrigatórios
    nutrientes_obrigatorios = ["ph", "p_mg", "k_mg"]
    for nutriente in nutrientes_obrigatorios:
        if nutriente not in teores:
            erros.append(f"Nutriente obrigatório ausente: {nutriente}")
        elif not isinstance(teores[nutriente], (int, float)):
            erros.append(f"Valor inválido para {nutriente}: {teores[nutriente]}")
    
    # Validar ranges
    if "ph" in teores:
        ph = teores["ph"]
        if ph < 0 or ph > 14:
            erros.append(f"pH fora do range válido (0-14): {ph}")
    
    if "p_mg" in teores:
        p_mg = teores["p_mg"]
        if p_mg < 0 or p_mg > 1000:
            erros.append(f"Teor de P fora do range válido (0-1000 mg/dm³): {p_mg}")
    
    if "k_mg" in teores:
        k_mg = teores["k_mg"]
        if k_mg < 0 or k_mg > 1000:
            erros.append(f"Teor de K fora do range válido (0-1000 mg/dm³): {k_mg}")
    
    return erros


def validar_parametros(parametros: Dict[str, Any], metodo: str) -> List[str]:
    """
    Valida os parâmetros da metodologia.
    
    Args:
        parametros: Dicionário com parâmetros
        metodo: Nome do método de análise
    
    Returns:
        Lista de erros encontrados
    """
    erros = []
    
    # Verificar método conhecido
    metodos_conhecidos = [
        "IAC_Graos", "IAC_Cana", "IAC_Citros", "CFSEMG_Geral", 
        "CFSEMG_Cafe", "PESAGRO_RJ", "EPAMIG_ES", 
        "EMBRAPA_Cerrado_Geral", "EMBRAPA_Cerrado_Alta_Prod"
    ]
    
    if metodo not in metodos_conhecidos:
        erros.append(f"Método desconhecido: {metodo}")
    
    # Verificar estrutura mínima de parâmetros
    estrutura_minima = ["calagem", "fosforo", "nitrogenio", "calcio", "magnesio", "enxofre"]
    for chave in estrutura_minima:
        if chave not in parametros:
            erros.append(f"Parâmetro obrigatório ausente: {chave}")
    
    return erros


def validar_cultura(cultura: str, culturas_disponiveis: Dict[str, Any]) -> List[str]:
    """
    Valida a cultura informada.
    
    Args:
        cultura: Nome da cultura
        culturas_disponiveis: Dicionário com culturas disponíveis
    
    Returns:
        Lista de erros encontrados
    """
    erros = []
    
    if cultura not in culturas_disponiveis:
        erros.append(f"Cultura não encontrada: {cultura}")
    
    if cultura in culturas_disponiveis:
        cultura_data = culturas_disponiveis[cultura]
        if "exportacao_nutrientes" not in cultura_data:
            erros.append(f"Exportação de nutrientes ausente para cultura: {cultura}")
        
        if "eficiencia_fertilizante" not in cultura_data:
            erros.append(f"Eficiência de fertilizante ausente para cultura: {cultura}")
    
    return erros


def validar_config(config: Dict[str, Any]) -> List[str]:
    """
    Valida a configuração da análise.
    
    Args:
        config: Dicionário com configuração
    
    Returns:
        Lista de erros encontrados
    """
    erros = []
    
    # Campos obrigatórios
    campos_obrigatorios = ["cultura", "produtividade_alvo", "metodo_id"]
    for campo in campos_obrigatorios:
        if campo not in config:
            erros.append(f"Campo obrigatório ausente: {campo}")
    
    # Validar tipos
    if "cultura" in config and not isinstance(config["cultura"], str):
        erros.append("cultura deve ser uma string")
    
    if "produtividade_alvo" in config:
        try:
            prod = float(config["produtividade_alvo"])
            if prod <= 0:
                erros.append("produtividade_alvo deve ser positivo")
        except (TypeError, ValueError):
            erros.append("produtividade_alvo deve ser um número")
    
    if "metodo_id" in config and not isinstance(config["metodo_id"], str):
        erros.append("metodo_id deve ser uma string")
    
    return erros


def validar_entrada_completa(
    teores: Dict[str, float],
    parametros: Dict[str, Any],
    culturas: Dict[str, Any],
    config: Dict[str, Any]
) -> List[str]:
    """
    Valida todos os dados de entrada da análise agronômica.
    
    Args:
        teores: Teores do solo
        parametros: Parâmetros da metodologia
        culturas: Dados de culturas disponíveis
        config: Configuração da análise
    
    Returns:
        Lista de erros encontrados
    """
    todos_erros = []
    
    # Validar cada componente
    erros_teores = validar_teores(teores)
    todos_erros.extend(erros_teores)
    
    erros_parametros = validar_parametros(parametros, config.get("metodo_id", ""))
    todos_erros.extend(erros_parametros)
    
    erros_cultura = validar_cultura(config.get("cultura", ""), culturas)
    todos_erros.extend(erros_cultura)
    
    erros_config = validar_config(config)
    todos_erros.extend(erros_config)
    
    return todos_erros


def validar_saida(resultado: Dict[str, Any]) -> List[str]:
    """
    Valida a saída da análise agronômica.
    
    Args:
        resultado: Dicionário com resultado da análise
    
    Returns:
        Lista de erros encontrados
    """
    erros = []
    
    # Estrutura mínima esperada
    campos_obrigatorios = ["cultura", "produtividade", "classe_fertilidade"]
    for campo in campos_obrigatorios:
        if campo not in resultado:
            erros.append(f"Campo obrigatório na saída: {campo}")
    
    # Valor numérico para produtividade
    if "produtividade" in resultado:
        try:
            prod = float(resultado["produtividade"])
            if prod <= 0:
                erros.append("produtividade deve ser positivo")
        except (TypeError, ValueError):
            erros.append("produtividade deve ser um número")
    
    return erros