"""
Balanço nutricional - cálculo de exportação e necessidade de adubação.
"""
from typing import Any, Dict, List, Optional


def calcular_exportacao_nutrientes(
    cultura: str,
    produtividade: float,
    exportacao_base: Dict[str, float],
) -> Dict[str, float]:
    """
    Calcula a exportação total de nutrientes com base na produtividade.
    
    Args:
        cultura: Nome da cultura (ex: "soja", "milho")
        produtividade: Produtividade esperada (t/ha)
        exportacao_base: Exportação base por nutriente (vindo de config/culturas.py)
    
    Returns:
        Dicionário com exportação total por nutriente (kg/ha)
    """
    exportacao_total = {}
    
    # Calcular exportação para cada nutriente
    for nutriente, valor_base in exportacao_base.items():
        # valor_base está em kg/t, multiplicar por produtividade (t/ha)
        exportacao_total[nutriente] = valor_base * produtividade
    
    return exportacao_total


def calcular_balanco(
    teores_atuais: Dict[str, float],
    exportacao: Dict[str, float],
    eficiencias: Dict[str, float],
    profundidade: float = 20.0,
    densidade: float = 1.3,
) -> Dict[str, float]:
    """
    Calcula o balanço nutricional (déficit/superávit) por nutriente.
    
    Args:
        teores_atuais: Teores do solo (mg/dm³ ou cmolc/dm³)
        exportacao: Exportação de nutrientes (kg/ha)
        eficiencias: Fatores de eficiência (0-1)
        profundidade: Profundidade da camada (cm)
        densidade: Densidade do solo (g/cm³)
    
    Returns:
        Dicionário com balanço nutricional (kg/ha)
    """
    balanco = {}
    
    # Constantes para conversão
    profundidade_dm = profundidade / 10  # cm -> dm
    volume_ha = 10000 * profundidade_dm  # dm³/ha
    peso_ha = volume_ha * densidade  # kg/ha
    
    for nutriente, teor in teores_atuais.items():
        # Obter exportação e eficiência
        exp = exportacao.get(nutriente, 0.0)
        eff = eficiencias.get(nutriente, 0.5)
        
        # Calcular disponibilidade no solo
        if "_cmolc" in nutriente:
            # Para bases (Ca, Mg, K), converter para kg/ha
            disponibilidade_solo = teor * peso_ha / 1000  # cmolc/dm³ -> kg/ha
        else:
            # Para outros nutrientes (P, etc.), mg/dm³ -> kg/ha
            disponibilidade_solo = teor * peso_ha / 1000000  # mg/dm³ -> kg/ha
        
        # Calcular necessidade de adubação
        necessidade_adubacao = (exp - disponibilidade_solo) / eff
        
        # Calcular balanço (positivo = disponibilidade > necessidade)
        balanco[nutriente] = disponibilidade_solo - necessidade_adubacao
    
    return balanco


def calcular_necessidade_adubacao(
    teores_atuais: Dict[str, float],
    exportacao: Dict[str, float],
    eficiencias: Dict[str, float],
    profundidade: float = 20.0,
    densidade: float = 1.3,
) -> Dict[str, float]:
    """
    Calcula a necessidade de adubação específica por nutriente.
    
    Args:
        teores_atuais: Teores do solo
        exportacao: Exportação de nutrientes
        eficiencias: Fatores de eficiência
        profundidade: Profundidade da camada (cm)
        densidade: Densidade do solo (g/cm³)
    
    Returns:
        Dicionário com necessidade de adubação (kg/ha)
    """
    balanco = calcular_balanco(
        teores_atuais, exportacao, eficiencias, profundidade, densidade
    )
    
    necessidade = {}
    for nutriente, valor in balanco.items():
        if valor < 0:
            # Déficit - precisa de adubação
            necessidade[nutriente] = abs(valor)
        else:
            # Superávit - não precisa de adubação
            necessidade[nutriente] = 0.0
    
    return necessidade


def calcular_reposicao_nutrientes(
    teores_atuais: Dict[str, float],
    teores_desejados: Dict[str, float],
    eficiencias: Dict[str, float],
    profundidade: float = 20.0,
    densidade: float = 1.3,
) -> Dict[str, float]:
    """
    Calcula a reposição de nutrientes para atingir teores desejados.
    
    Args:
        teores_atuais: Teores atuais do solo
        teores_desejados: Teores desejados do solo
        eficiencias: Fatores de eficiência
        profundidade: Profundidade da camada (cm)
        densidade: Densidade do solo (g/cm³)
    
    Returns:
        Dicionário com reposição necessária (kg/ha)
    """
    reposicao = {}
    
    # Constantes para conversão
    profundidade_dm = profundidade / 10  # cm -> dm
    volume_ha = 10000 * profundidade_dm  # dm³/ha
    peso_ha = volume_ha * densidade  # kg/ha
    
    for nutriente, teor_atual in teores_atuais.items():
        teor_desejado = teores_desejados.get(nutriente, teor_atual)
        eff = eficiencias.get(nutriente, 0.5)
        
        # Cálculo ajustado para bases vs outros nutrientes
        if "_cmolc" in nutriente:
            # Para bases (Ca, Mg, K), converter para kg/ha
            diferenca_cmolc = teor_desejado - teor_atual
            reposicao_kg = (diferenca_cmolc * peso_ha / 1000) / eff
        else:
            # Para outros nutrientes (P, etc.), mg/dm³ -> kg/ha
            diferenca_mg = teor_desejado - teor_atual
            reposicao_kg = (diferenca_mg * peso_ha / 1000000) / eff
        
        reposicao[nutriente] = max(0, reposicao_kg)
    
    return reposicao


def calcular_armazenamento_solo(
    teores: Dict[str, float],
    profundidade: float = 20.0,
    densidade: float = 1.3,
) -> Dict[str, float]:
    """
    Calcula o armazenamento de nutrientes no solo (kg/ha).
    
    Args:
        teores: Teores do solo
        profundidade: Profundidade da camada (cm)
        densidade: Densidade do solo (g/cm³)
    
    Returns:
        Dicionário com armazenamento no solo (kg/ha)
    """
    armazenamento = {}
    
    # Constantes para conversão
    profundidade_dm = profundidade / 10  # cm -> dm
    volume_ha = 10000 * profundidade_dm  # dm³/ha
    peso_ha = volume_ha * densidade  # kg/ha
    
    for nutriente, teor in teores.items():
        if "_cmolc" in nutriente:
            # Para bases (Ca, Mg, K), converter para kg/ha
            armazenamento[nutriente] = teor * peso_ha / 1000  # cmolc/dm³ -> kg/ha
        else:
            # Para outros nutrientes (P, etc.), mg/dm³ -> kg/ha
            armazenamento[nutriente] = teor * peso_ha / 1000000  # mg/dm³ -> kg/ha
    
    return armazenamento


def avaliar_sustentabilidade(
    teores_iniciais: Dict[str, float],
    exportacao_anual: Dict[str, float],
    eficiencias: Dict[str, float],
    profundidade: float = 20.0,
    densidade: float = 1.3,
    anos: int = 5,
) -> Dict[str, Any]:
    """
    Avalia a sustentabilidade do manejo de nutrientes.
    
    Args:
        teores_iniciais: Teores iniciais do solo
        exportacao_anual: Exportação anual de nutrientes
        eficiencias: Fatores de eficiência
        profundidade: Profundidade da camada (cm)
        densidade: Densidade do solo (g/cm³)
        anos: Número de anos para avaliação
    
    Returns:
        Dicionário com avaliação de sustentabilidade
    """
    resultado = {
        "sustentavel": True,
        "nutrientes_criticos": [],
        "recomendacoes": [],
        "projecao_anos": {},
    }
    
    # Calcular armazenamento inicial
    armazenamento_inicial = calcular_armazenamento_solo(
        teores_iniciais, profundidade, densidade
    )
    
    # Projetar para cada ano
    teores_correntes = teores_iniciais.copy()
    
    for ano in range(1, anos + 1):
        # Calcular balanço do ano
        balanco = calcular_balanco(
            teores_correntes, exportacao_anual, eficiencias, profundidade, densidade
        )
        
        # Atualizar teores para próximo ano
        for nutriente in teores_correntes:
            if "_cmolc" in nutriente:
                # Para bases, ajustar em cmolc/dm³
                ajuste = balanco[nutriente] * 1000 / (10000 * (profundidade/10) * densidade)
                teores_correntes[nutriente] = max(0, teores_correntes[nutriente] + ajuste)
            else:
                # Para outros nutrientes, ajustar em mg/dm³
                ajuste = balanco[nutriente] * 1000000 / (10000 * (profundidade/10) * densidade)
                teores_correntes[nutriente] = max(0, teores_correntes[nutriente] + ajuste)
        
        # Verificar se algum nutriente crítico
        nutrientes_criticos = []
        for nutriente, teor in teores_correntes.items():
            if teor < 1.0:  # Limite crítico geral
                nutrientes_criticos.append(nutriente)
        
        # Adicionar à projeção
        resultado["projecao_anos"][ano] = {
            "teores": teores_correntes.copy(),
            "balancos": balanco.copy(),
            "nutrientes_criticos": nutrientes_criticos,
        }
        
        # Se tem nutrientes críticos, marcar como não sustentável
        if nutrientes_criticos:
            resultado["sustentavel"] = False
            resultado["nutrientes_criticos"].extend(nutrientes_criticos)
            resultado["recomendacoes"].append(f"Ano {ano}: Adubar {', '.join(nutrientes_criticos)}")
    
    return resultado