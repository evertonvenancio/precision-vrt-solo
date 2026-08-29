"""
Motor de Agronomia — orquestrador de análise de solo.
Consome dados de config/ e aplica lógica científica pura.
"""
from typing import Any, Dict, List, Optional

from .contratos import ConfigAgronomia, ResultadoAgronomia, InterpretacaoNutriente
from .nutrientes import interpretar_nutriente
from .fertilidade import classificar_fertilidade, calcular_saturation_indices
from .balanco import calcular_exportacao_nutrientes, calcular_necessidade_adubacao
from .recomendacao import gerar_recomendacoes_completas, recomendar_calagem


class MotorAgronomia:
    """
    Motor de análise agronômica do solo.
    
    NÃO contém dados de culturas/metodologias — recebe tudo via ConfigAgronomia
    e dicionários de parâmetros vindos de config/.
    """
    
    def __init__(self, config: ConfigAgronomia):
        self.config = config
    
    def analisar_solo(
        self,
        teores: Dict[str, float],
        parametros_metodologia: Dict[str, Any],
        exportacao_nutrientes: Dict[str, float],
        eficiencias: Dict[str, float],
    ) -> ResultadoAgronomia:
        """
        Análise completa do solo.
        
        Args:
            teores: Teores de nutrientes no solo (ex: {"p_mg": 15.0, "k_mg": 120.0})
            parametros_metodologia: Limites da metodologia (vindo de config/metodologias.py)
            exportacao_nutrientes: Exportação base por nutriente (vindo de config/culturas.py)
            eficiencias: Fatores de eficiência (vindo de config/fertilizantes.py)
        
        Returns:
            ResultadoAgronomia com toda a análise
        """
        # Criar resultado base
        resultado = ResultadoAgronomia()
        resultado.config = self.config
        
        # 1. Interpretar cada nutriente
        interpretacoes = {}
        for nutriente, valor in teores.items():
            if valor > 0:  # Apenas nutrientes com valores positivos
                interpretacao = interpretar_nutriente(nutriente, valor, parametros_metodologia)
                interpretacoes[nutriente] = interpretacao
        
        resultado.interpretacoes = interpretacoes
        
        # 2. Classificar fertilidade geral
        classe_fertilidade = classificar_fertilidade(teores, parametros_metodologia)
        resultado.classe_fertilidade = classe_fertilidade
        
        # Extrair classes das interpretações para análise simplificada
        classes = [interp.classe for interp in interpretacoes.values()]
        
        # 3. Calcular exportação ajustada pela produtividade
        exportacao_ajustada = calcular_exportacao_nutrientes(
            self.config.cultura, 
            self.config.produtividade_alvo,
            exportacao_nutrientes
        )
        
        # 4. Calcular balanço nutricional
        necessidade_adubacao = calcular_necessidade_adubacao(
            teores, 
            exportacao_ajustada, 
            eficiencias,
            self.config.profundidade_amostra_cm
        )
        
        resultado.balanco_nutricional = necessidade_adubacao
        
        # 5. Gerar recomendações completas
        recomendacoes = gerar_recomendacoes_completas(
            teores,
            exportacao_ajustada,
            eficiencias,
            parametros_metodologia.get("calagem", {}),
            parametros_metodologia.get("adubacao", {}),
            parametros_metodologia.get("gessagem", {}),
            self.config.cultura,
            self.config.produtividade_alvo
        )
        
        resultado.recomendacoes = recomendacoes
        
        return resultado
    
    def analise_rapida(
        self,
        teores: Dict[str, float],
        parametros_metodologia: Dict[str, Any],
        exportacao_nutrientes: Dict[str, float],
        eficiencias: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Análise rápida do solo (resultado simplificado).
        
        Args:
            teores: Teores de nutrientes no solo
            parametros_metodologia: Limites da metodologia
            exportacao_nutrientes: Exportação base por nutriente
            eficiencias: Fatores de eficiência
        
        Returns:
            Dicionário com resultados principais
        """
        resultado_rapido = {}
        
        # Interpretação dos nutrientes
        interpretacoes = {}
        for nutriente, valor in teores.items():
            if valor > 0:
                interpretacao = interpretar_nutriente(nutriente, valor, parametros_metodologia)
                interpretacoes[nutriente] = interpretacao
        
        # Extrair classes das interpretações
        classes = [interp.classe for interp in interpretacoes.values()]
        resultado_rapido["nutrientes"] = classes
        resultado_rapido["classe_fertilidade"] = classificar_fertilidade(teores, parametros_metodologia)
        
        # Calcular necessidade básica
        exportacao_ajustada = calcular_exportacao_nutrientes(
            self.config.cultura, 
            self.config.produtividade_alvo,
            exportacao_nutrientes
        )
        
        necessidade = calcular_necessidade_adubacao(
            teores, exportacao_ajustada, eficiencias, self.config.profundidade_amostra_cm
        )
        
        resultado_rapido["necessidade_adubacao"] = necessidade
        
        # Recomendação rápida
        recomendacao_calagem = recomendar_calagem(
            teores.get("ph", 6.0),
            calcular_saturation_indices(teores).get("v_percent", 100.0),
            calcular_saturation_indices(teores).get("ctc_efetiva_cmolc", 10.0)
        )
        
        resultado_rapido["calagem"] = recomendacao_calagem
        
        return resultado_rapido
    
    def exportar_relatorio(self, resultado: ResultadoAgronomia) -> str:
        """
        Exporta o resultado como relatório textual.
        
        Args:
            resultado: Resultado da análise agronômica
        
        Returns:
            String com relatório formatado
        """
        relatorio = []
        
        # Cabeçalho
        relatorio.append("=" * 60)
        relatorio.append("RELATÓRIO DE ANÁLISE AGRONÔMICA")
        relatorio.append("=" * 60)
        relatorio.append(f" Cultura: {resultado.config.cultura}")
        relatorio.append(f" Produtividade alvo: {resultado.config.produtividade_alvo} t/ha")
        relatorio.append(f" Metodologia: {resultado.config.metodo_id}")
        relatorio.append("")
        
        # Interpretações
        relatorio.append("INTERPRETAÇÃO DE NUTRIENTES")
        relatorio.append("-" * 30)
        for nutriente, interpretacao in resultado.interpretacoes.items():
            relatorio.append(f"{nutriente}: {interpretacao.valor} {interpretacao.unidade} - {interpretacao.classe}")
        relatorio.append("")
        
        # Fertilidade
        relatorio.append("CLASSIFICAÇÃO DA FERTILIDADE")
        relatorio.append("-" * 30)
        relatorio.append(f"Classe: {resultado.classe_fertilidade}")
        relatorio.append("")
        
        # Balanço
        relatorio.append("BALANÇO NUTRICIONAL")
        relatorio.append("-" * 30)
        for nutriente, valor in resultado.balanco_nutricional.items():
            if valor > 0:
                relatorio.append(f"{nutriente}: Déficit de {valor:.1f} kg/ha")
            else:
                relatorio.append(f"{nutriente}: Superávit de {abs(valor):.1f} kg/ha")
        relatorio.append("")
        
        # Recomendações
        relatorio.append("RECOMENDAÇÕES")
        relatorio.append("-" * 30)
        
        # Calagem
        if resultado.recomendacoes.get("calagem", {}).get("necesidade_cal", 0) > 0:
            cal = resultado.recomendacoes["calagem"]
            relatorio.append(f"Calagem: {cal['necesidade_cal']:.1f} kg/ha de {cal['tipo_cal']}")
        
        # Adubação
        for nutriente, rec in resultado.recomendacoes.get("adubacao", {}).items():
            if rec.get("dose_adubacao", 0) > 0:
                relatorio.append(f"{nutriente}: {rec['dose_adubacao']:.1f} kg/ha")
        
        # Gessagem
        if resultado.recomendacoes.get("gessagem", {}).get("dose_gesso", 0) > 0:
            gesso = resultado.recomendacoes["gessagem"]
            relatorio.append(f"Gessagem: {gesso['dose_gesso']:.1f} kg/ha")
        
        relatorio.append("")
        
        # Resumo
        relatorio.append("RESUMO FINAL")
        relatorio.append("-" * 30)
        resumo = resultado.recomendacoes.get("resumo", "Nenhuma recomendação")
        relatorio.append(resumo)
        
        relatorio.append("")
        relatorio.append("=" * 60)
        
        return "\n".join(relatorio)
    
    def validar_entrada(self, teores: Dict[str, float]) -> List[str]:
        """
        Valida os dados de entrada da análise.
        
        Args:
            teores: Dicionário com teores do solo
        
        Returns:
            Lista de erros encontrados (vazio se válido)
        """
        erros = []
        
        # Verificar nutrientes conhecidos
        nutrientes_validos = {
            "ph", "p_mg", "k_mg", "ca_cmolc", "mg_cmolc", 
            "al_cmolc", "h_cmolc", "v_percent", "mo_percent",
            "m_percent", "argila_percent", "silte_percent", "areia_percent"
        }
        
        for nutriente in teores.keys():
            if nutriente not in nutrientes_validos:
                erros.append(f"Nutriente desconhecido: {nutriente}")
        
        # Verificar valores positivos
        for nutriente, valor in teores.items():
            if valor < 0:
                erros.append(f"Valor negativo para {nutriente}: {valor}")
        
        # Verificar pH em range válido
        ph = teores.get("ph", 0)
        if ph < 0 or ph > 14:
            erros.append(f"pH fora do range válido: {ph}")
        
        return erros