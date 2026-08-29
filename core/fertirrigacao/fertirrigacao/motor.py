"""
Precision VRT Solo — Motor Principal de Fertirrigação

Módulo principal com lógica de negócio para fertirrigação.
Implementa pipeline completo de amostragem dirigida e recomendação nutricional.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from .contratos import (
    ConfigAreaFertirrigacao,
    ConfigAnaliseSolucao,
    ConfigNutricao,
    ConfigRecomendacao,
    ConfigExportacaoFertirrigacao,
    ConfigAgronomiaFertirrigacao,
    Cultura,
    SistemaIrrigacao,
    MetodoAnalise,
    ModoRecomendacao,
    LeituraSolucao,
    AreaFertirrigacao,
    PrescricaoNutricional,
    ResultadoAnaliseSolucao,
    ResultadoNutricao,
    ResultadoRecomendacao,
    ResultadoFertirrigacao
)
from ...fertirrigacao.interpolacao.motor import MotorInterpolacaoFertirrigacao
from ...fertirrigacao.zoneamento.motor import MotorZoneamentoFertirrigacao
from ...fertirrigacao.exportacao.motor import MotorExportacaoFertirrigacao
from ...fertirrigacao.agronomia.motor import MotorAgronomiaFertirrigacao
from ...otimizacao.bulk_blend import (
    OtimizadorBulkBlend,
    RecomendacaoNutricional,
    FertilizanteDisponivel,
    ResultadoMistura
)
from config.fertilizantes_fisicos import CatalogoFertilizantes

logger = logging.getLogger(__name__)


class MotorFertirrigacao:
    """Motor principal de fertirrigação.
    
    Implementa pipeline completo:
    1. Cadastrar área
    2. Receber análises de solução
    3. Receber parâmetros agronômicos
    4. Interpolação (opcional)
    5. Zoneamento (opcional)
    6. Processamento agronômico
    7. Recomendação (produtos comerciais ou fontes individuais)
    8. Exportação
    """
    
    def __init__(self):
        self.config_geral = ConfigAreaFertirrigacao()
        self.config_analise = ConfigAnaliseSolucao()
        self.config_nutricao = ConfigNutricao()
        self.config_recomendacao = ConfigRecomendacao()
        self.config_exportacao = ConfigExportacaoFertirrigacao()
        self.config_agronomia = ConfigAgronomiaFertirrigacao()
        
        # Módulos especializados
        self.motor_interpolacao = MotorInterpolacaoFertirrigacao()
        self.motor_zoneamento = MotorZoneamentoFertirrigacao()
        self.motor_exportacao = MotorExportacaoFertirrigacao()
        self.motor_agronomia = MotorAgronomiaFertirrigacao()
        
        # Estado interno
        self.area_atual: Optional[AreaFertirrigacao] = None
        self.leituras_solucao: List[LeituraSolucao] = []
        self.resultado_final: Optional[ResultadoFertirrigacao] = None
        
        logger.info("MotorFertirrigacao inicializado")
    
    # ============================================================
    # ETAPA 01: CADASTRO DA ÁREA
    # ============================================================
    
    def cadastrar_area(self, poligono: Dict[str, Any], talhao: str, 
                      cultura: Cultura, sistema_irrigacao: SistemaIrrigacao,
                      area_ha: float, propriedade_id: str = "") -> AreaFertirrigacao:
        """Cadastrar área de fertirrigação.
        
        Args:
            poligono: Dados geoespaciais da área
            talhao: Identificador do talhão
            cultura: Cultura a ser irrigada
            sistema_irrigacao: Sistema de irrigação utilizado
            area_ha: Área em hectares
            propriedade_id: ID da propriedade
        
        Returns:
            AreaFertirrigacao cadastrada
        """
        logger.info(f"Cadastrando área: {talhao} - {cultura.value} - {area_ha}ha")
        
        # Validar parâmetros
        if area_ha <= 0:
            raise ValueError("Área deve ser maior que zero")
        
        # Criar objeto de área
        self.area_atual = AreaFertirrigacao(
            area_id=f"area_{int(time.time())}",
            poligono=poligono,
            talhao=talhao,
            cultura=cultura,
            sistema_irrigacao=sistema_irrigacao,
            area_ha=area_ha,
            propriedade_id=propriedade_id,
            pontos_monitoramento=[]
        )
        
        # Atualizar configuração geral
        self.config_geral.area_id = self.area_atual.area_id
        self.config_geral.poligono = poligono
        self.config_geral.talhao = talhao
        self.config_geral.cultura = cultura
        self.config_geral.sistema_irrigacao = sistema_irrigacao
        self.config_geral.area_ha = area_ha
        self.config_geral.propriedade_id = propriedade_id
        
        logger.info(f"Área cadastrada com sucesso: {self.area_atual.area_id}")
        return self.area_atual
    
    # ============================================================
    # ETAPA 02: RECEBER ANÁLISES DA SOLUÇÃO
    # ============================================================
    
    def adicionar_leituras(self, leituras: Union[LeituraSolucao, List[LeituraSolucao]]) -> int:
        """Adicionar leituras de solução.
        
        Suporta extrator de solução, laboratório, entrada manual e arquivos.
        
        Args:
            leituras: Lista de leituras de solução
        
        Returns:
            Número total de leituras adicionadas
        """
        if isinstance(leituras, LeituraSolucao):
            leituras = [leituras]
        
        logger.info(f"Adicionando {len(leituras)} leituras de solução")
        
        for leitura in leituras:
            # Validar leitura
            self._validar_leitura(leitura)
            
            # Adicionar à lista
            self.leituras_solucao.append(leitura)
            
            # Adicionar ponto ao cadastro da área (se novo)
            if leitura.ponto_id not in self.area_atual.pontos_monitoramento:
                self.area_atual.pontos_monitoramento.append(leitura.ponto_id)
        
        logger.info(f"Total de leituras: {len(self.leituras_solucao)}")
        return len(leituras)
    
    def adicionar_leituras_arquivo(self, arquivo: str, formato: str = "csv") -> int:
        """Adicionar leituras a partir de arquivo CSV ou XLSX.
        
        Args:
            arquivo: Caminho do arquivo
            formato: Formato do arquivo (csv ou xlsx)
        
        Returns:
            Número total de leituras importadas
        """
        logger.info(f"Importando leituras de arquivo: {arquivo} ({formato})")
        
        # Implementar lógica de importação de arquivo
        # (simplificado para demonstração)
        leituras_importadas = []
        
        if formato.lower() == "csv":
            # Implementar leitura CSV
            pass
        elif formato.lower() == "xlsx":
            # Implementar leitura XLSX
            pass
        else:
            raise ValueError(f"Formato não suportado: {formato}")
        
        return self.adicionar_leituras(leituras_importadas)
    
    # ============================================================
    # ETAPA 03: RECEBER PARÂMETROS AGRONÔMICOS
    # ============================================================
    
    def configurar_nutricao(self, objetivos: Dict[str, float]) -> None:
        """Configurar objetivos nutricionais.
        
        Args:
            objetivos: Dicionário com objetivos de nutrientes
        """
        logger.info("Configurando objetivos nutricionais")
        
        # Mapear objetivos para configuração
        self.config_nutricao.objetivo_n_kg_ha = objetivos.get("N", 0.0)
        self.config_nutricao.objetivo_p2o5_kg_ha = objetivos.get("P2O5", 0.0)
        self.config_nutricao.objetivo_k2o_kg_ha = objetivos.get("K2O", 0.0)
        self.config_nutricao.objetivo_ca_mg_L = objetivos.get("Ca", 0.0)
        self.config_nutricao.objetivo_mg_mg_L = objetivos.get("Mg", 0.0)
        self.config_nutricao.objetivo_s_mg_L = objetivos.get("S", 0.0)
        self.config_nutricao.objetivo_fe_mg_L = objetivos.get("Fe", 0.0)
        self.config_nutricao.objetivo_mn_mg_L = objetivos.get("Mn", 0.0)
        self.config_nutricao.objetivo_zn_mg_L = objetivos.get("Zn", 0.0)
        self.config_nutricao.objetivo_cu_mg_L = objetivos.get("Cu", 0.0)
        self.config_nutricao.objetivo_b_mg_L = objetivos.get("B", 0.0)
        self.config_nutricao.objetivo_mo_mg_L = objetivos.get("MO", 0.0)
        
        logger.info(f"Objetivos configurados: {len(objetivos)} nutrientes")
    
    def configurar_agronomia(self, cultura: Cultura, sistema_irrigacao: SistemaIrrigacao,
                           fase_fenologica: str, data_plantio: Optional[str] = None) -> None:
        """Configurar parâmetros agronômicos.
        
        Args:
            cultura: Cultura analisada
            sistema_irrigacao: Sistema de irrigação
            fase_fenologica: Fase fenológica atual
            data_plantio: Data de plantio
        """
        logger.info(f"Configurando agronomia: {cultura.value} - {fase_fenologica}")
        
        self.config_agronomia.cultura = cultura
        self.config_agronomia.sistema_irrigacao = sistema_irrigacao
        self.config_agronomia.fase_atual = fase_fenologica
        self.config_agronomia.data_plantio = data_plantio
        
        logger.info("Parâmetros agronômicos configurados")
    
    # ============================================================
    # ETAPA 04: INTERPOLAÇÃO (OPCIONAL)
    # ============================================================
    
    def executar_interpolacao(self, executar: bool = True) -> Optional[Dict[str, Any]]:
        """Executar interpolação de soluções.
        
        Args:
            executar: Se True, executa interpolação; se False, usa solução média
        
        Returns:
            Resultado da interpolação ou None se não executada
        """
        logger.info(f"Executando interpolação: {'sim' if executar else 'não'}")
        
        if not executar:
            logger.info("Usando solução média (interpolação desativada)")
            return None
        
        if not self.leituras_solucao:
            raise ValueError("Nenhuma leitura de solução disponível para interpolação")
        
        # Executar interpolação
        resultado_interpolacao = self.motor_interpolacao.interpolar_solucoes(
            self.leituras_solucao,
            self.area_atual,
            self.config_analise
        )
        
        # Armazenar resultado
        if hasattr(self.resultado_final, 'mapa_interpolado'):
            self.resultado_final.mapa_interpolado = resultado_interpolacao
        
        logger.info(f"Interpolação concluída: {resultado_interpolacao}")
        return resultado_interpolacao
    
    # ============================================================
    # ETAPA 05: ZONEAMENTO (OPCIONAL)
    # ============================================================
    
    def executar_zoneamento(self, executar: bool = True) -> Optional[List[Dict[str, Any]]]:
        """Executar zoneamento de soluções.
        
        Args:
            executar: Se True, executa zoneamento; se False, usa solução média
        
        Returns:
            Lista de zonas ou None se não executado
        """
        logger.info(f"Executando zoneamento: {'sim' if executar else 'não'}")
        
        if not executar:
            logger.info("Usando solução média (zoneamento desativado)")
            return None
        
        # Zoneamento só faz sentido se houver interpolação
        if not hasattr(self.resultado_final, 'mapa_interpolado') or not self.resultado_final.mapa_interpolado:
            logger.warning("Zoneamento sem interpolação será executado como solução única")
        
        # Executar zoneamento
        zonas = self.motor_zoneamento.zonar_solucoes(
            self.leituras_solucao,
            self.area_atual,
            self.config_analise,
            self.resultado_final.mapa_interpolado if hasattr(self.resultado_final, 'mapa_interpolado') else None
        )
        
        # Armazenar resultado
        if hasattr(self.resultado_final, 'zonas_de_recomendacao'):
            self.resultado_final.zonas_de_recomendacao = zonas
        
        logger.info(f"Zoneamento concluído: {len(zonas)} zonas")
        return zonas
    
    # ============================================================
    # ETAPA 06: PROCESSAMENTO AGRONÔMICO
    # ============================================================
    
    def processar_agronomia(self) -> ResultadoNutricao:
        """Processar análise agronômica das soluções."""
        logger.info("Processando análise agronômica")
        
        # Executar processamento agronômico
        resultado_nutricao = self.motor_agronomia.processar_nutricao(
            self.leituras_solucao,
            self.area_atual,
            self.config_agronomia,
            self.config_nutricao
        )
        
        # Armazenar resultado
        self.resultado_nutricao = resultado_nutricao
        
        logger.info("Processamento agronômico concluído")
        return resultado_nutricao
    
    # ============================================================
    # ETAPA 07: RECOMENDAÇÃO
    # ============================================================
    
    def obter_modo_recomendacao(self) -> ModoRecomendacao:
        """Solicitar ao usuário o modo de recomendação desejado."""
        logger.info("Solicitando modo de recomendação ao usuário")
        
        # Em implementação real, isso seria interativo
        # Para demonstração, usar padrão
        modo = ModoRecomendacao.PRODUTO_COMERCIAL
        
        logger.info(f"Modo selecionado: {modo.value}")
        return modo
    
    def gerar_recomendacao(self, modo: Optional[ModoRecomendacao] = None) -> ResultadoRecomendacao:
        """Gerar recomendação de fertilizantes.
        
        Suporta dois modos:
        - PRODUTO_COMERCIAL: Fórmulas comerciais (06-30-10, 08-28-16, etc.)
        - FONTES_INDIVIDUAIS: Fontes individuais (MAP, DAP, KCl, etc.)
        
        Args:
            modo: Modo de recomendação (se None, solicita ao usuário)
        
        Returns:
            Resultado da recomendação
        """
        if modo is None:
            modo = self.obter_modo_recomendacao()
        
        logger.info(f"Gerando recomendação no modo: {modo.value}")
        
        # Converter resultado nutricional para prescrição
        prescricao = self._criar_prescricao_nutricional()
        
        # Selecionar fontes de fertilizantes
        if modo == ModoRecomendacao.PRODUTO_COMERCIAL:
            fertilizantes = self._selecionar_fertilizantes_comerciais(prescricao)
        else:
            fertilizantes = self._selecionar_fertilizantes_individuais(prescricao)
        
        # Otimizar mistura
        resultado_mistura = self._otimizar_mistura(prescricao, fertilizantes)
        
        # Gerar recomendação final
        resultado_recomendacao = ResultadoRecomendacao(
            timestamp=time.time(),
            tempo_execucao_ms=0,
            config=self.config_recomendacao,
            modo_utilizado=modo,
            recomendacoes=self._formatar_recomendacoes(resultado_mistura, modo),
            composicao_mistura=resultado_mistura.composicao,
            custo_estimado=resultado_mistura.custo_total,
            lotes_aplicacao=resultado_mistura.lotes,
            observacoes_tecnicas=self._gerar_observacoes_tecnicas(resultado_mistura)
        )
        
        # Armazenar resultado
        self.resultado_recomendacao = resultado_recomendacao
        
        logger.info(f"Recomendação gerada: {len(resultado_recomendacao.recomendacoes)} itens")
        return resultado_recomendacao
    
    # ============================================================
    # ETAPA 08: BULK BLEND (integrado na recomendação)
    # ============================================================
    
    def _otimizar_mistura(self, prescricao: PrescricaoNutricional, 
                         fertilizantes: List[FertilizanteDisponivel]) -> ResultadoMistura:
        """Otimizar mistura de fertilizantes usando Bulk Blend."""
        logger.info("Otimizando mistura de fertilizantes")
        
        # Criar otimizador
        otimizador = OtimizadorBulkBlend(
            fertilizantes=fertilizantes,
            usar_pulp=True,
            capacidade_lote_kg=self.config_recomendacao.capacidade_misturador_kg,
        )
        
        # Criar recomendação nutricional
        recomendacao = RecomendacaoNutricional(
            n_kg_ha=prescricao.nutrientes_kg_ha.get("N", 0.0),
            p2o5_kg_ha=prescricao.nutrientes_kg_ha.get("P2O5", 0.0),
            k2o_kg_ha=prescricao.nutrientes_kg_ha.get("K2O", 0.0),
            area_ha=prescricao.area_ha,
        )
        
        # Executar otimização
        resultado = otimizador.otimizar(recomendacao)
        
        logger.info(f"Mistura otimizada: {resultado.status}, custo: R${resultado.custo_total:.2f}")
        return resultado
    
    # ============================================================
    # ETAPA 09: EXPORTAÇÃO
    # ============================================================
    
    def exportar_resultados(self, formatos: Optional[List[str]] = None, 
                          caminho_saida: str = "./exportados") -> Dict[str, str]:
        """Exportar resultados em múltiplos formatos.
        
        Suporta: PDF, CSV, Excel, GeoJSON, Shapefile, GeoTIFF, ISOXML
        
        Args:
            formatos: Lista de formatos desejados
            caminho_saida: Diretório para salvar arquivos
        
        Returns:
            Dicionário com caminhos dos arquivos exportados
        """
        logger.info(f"Exportando resultados em formatos: {formatos or 'todos'}")
        
        if formatos is None:
            formatos = self.config_exportacao.formatos
        
        if self.resultado_final is None:
            raise ValueError("Nenhum resultado para exportar")
        
        # Executar exportação
        arquivos_exportados = self.motor_exportacao.exportar(
            self.resultado_final,
            formatos,
            caminho_saida
        )
        
        logger.info(f"Exportação concluída: {len(arquivos_exportados)} arquivos")
        return arquivos_exportados
    
    # ============================================================
    # MÉTODOS AUXILIARES
    # ============================================================
    
    def _validar_leitura(self, leitura: LeituraSolucao) -> None:
        """Validar leitura de solução."""
        if not leitura.ponto_id:
            raise ValueError("Ponto ID obrigatório")
        
        if leitura.ce_ds_m <= 0:
            raise ValueError("CE deve ser maior que zero")
        
        if leitura.ph is not None and (leitura.ph < 0 or leitura.ph > 14):
            raise ValueError("pH deve estar entre 0 e 14")
    
    def _criar_prescricao_nutricional(self) -> PrescricaoNutricional:
        """Criar prescrição a partir do resultado nutricional."""
        # Simplificado para demonstração
        return PrescricaoNutricional(
            prescricao_id=1,
            zona_id="A1",
            area_ha=self.area_atual.area_ha,
            dose_kg_ha=500.0,
            nutrientes_kg_ha=self.config_nutricao.__dict__,
            cultura=self.config_agronomia.cultura.value,
            metodologia="fertirrigacao",
            fontes_preferenciais=self.config_recomendacao.fontes_preferenciais
        )
    
    def _selecionar_fertilizantes_comerciais(self, prescricao: PrescricaoNutricional) -> List[FertilizanteDisponivel]:
        """Selecionar fertilizantes comerciais."""
        catalogo = CatalogoFertilizantes()
        todos_fertilizantes = catalogo.listar_todos()
        
        # Filtrar pelos produtos comerciais configurados
        fertilizantes_selecionados = []
        for produto in self.config_recomendacao.produtos_comerciais:
            for fertilizante in todos_fertilizantes:
                if produto in fertilizante.nome or fertilizante.codigo == produto:
                    fertilizantes_selecionados.append(fertilizante)
                    break
        
        # Converter para FertilizanteDisponivel
        return [
            FertilizanteDisponivel(
                nome=f.nome,
                custo_kg=f.custo_kg,
                composicao=f.composicao,
                sgn=f.sgn,
                densidade=f.densidade_aparente,
                inclusao_min_pct=0.0,
                inclusao_max_pct=100.0,
            )
            for f in fertilizantes_selecionados
        ]
    
    def _selecionar_fertilizantes_individuais(self, prescricao: PrescricaoNutricional) -> List[FertilizanteDisponivel]:
        """Selecionar fontes individuais de fertilizantes."""
        catalogo = CatalogoFertilizantes()
        todos_fertilizantes = catalogo.listar_todos()
        
        # Filtrar pelas fontes preferenciais
        fertilizantes_selecionados = []
        for fonte in self.config_recomendacao.fontes_preferenciais:
            for fertilizante in todos_fertilizantes:
                if fonte.lower() in fertilizante.nome.lower():
                    fertilizantes_selecionados.append(fertilizante)
                    break
        
        # Converter para FertilizanteDisponivel
        return [
            FertilizanteDisponivel(
                nome=f.nome,
                custo_kg=f.custo_kg,
                composicao=f.composicao,
                sgn=f.sgn,
                densidade=f.densidade_aparente,
                inclusao_min_pct=0.0,
                inclusao_max_pct=100.0,
            )
            for f in fertilizantes_selecionados
        ]
    
    def _formatar_recomendacoes(self, resultado_mistura: ResultadoMistura, modo: ModoRecomendacao) -> List[Dict[str, Any]]:
        """Formatar recomendações para o usuário."""
        recomendacoes = []
        
        for nome_fertilizante, quantidade in resultado_mistura.composicao.items():
            recomendacoes.append({
                "fertilizante": nome_fertilizante,
                "quantidade_kg": round(quantidade, 2),
                "percentual": resultado_mistura.pct_inclusao.get(nome_fertilizante, 0.0),
                "custo_kg": self._calcular_custo_fertilizante(nome_fertilizante),
                "custo_total": round(quantidade * self._calcular_custo_fertilizante(nome_fertilizante), 2)
            })
        
        return recomendacoes
    
    def _calcular_custo_fertilizante(self, nome_fertilizante: str) -> float:
        """Calcular custo do fertilizante por kg."""
        # Simplificado para demonstração
        catalogo = CatalogoFertilizantes()
        fertilizante = catalogo.get(nome_fertilizante)
        return fertilizante.custo_kg if fertilizante else 0.0
    
    def _gerar_observacoes_tecnicas(self, resultado_mistura: ResultadoMistura) -> List[str]:
        """Gerar observações técnicas sobre a mistura."""
        observacoes = []
        
        if resultado_mistura.status == "Optimal":
            observacoes.append("Otimização via programação linear bem-sucedida")
        elif resultado_mistura.status == "Heuristico":
            observacoes.append("Otimização via heurística (fallback)")
        else:
            observacoes.append(f"Status: {resultado_mistura.status}")
        
        if resultado_mistura.compatibilidade < 80:
            observacoes.append(f"Atenção: compatibilidade física baixa ({resultado_mistura.compatibilidade:.1f}%)")
        
        if len(resultado_mistura.lotes) > 1:
            observacoes.append(f"Dividido em {len(resultado_mistura.lotes)} lotes de aplicação")
        
        return observacoes