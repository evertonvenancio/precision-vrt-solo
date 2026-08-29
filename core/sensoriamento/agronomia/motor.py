"""
Precision VRT Solo — Motor de Agronomia de Sensoriamento

Aplica regras e processos agronômicos específicos para imagens
de sensoriamento remoto e análise de culturas.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from ..satelites.contratos import (
    CamadaMesclada, MapaTematico, ConfigTemas, ResultadoProcessamento
)

logger = logging.getLogger(__name__)


class MotorAgronomiaSensoriamento:
    """Motor para aplicação de regras agronômicas em dados de sensoriamento."""
    
    def __init__(self):
        logger.info("MotorAgronomiaSensoriamento inicializado")
        
        # Bancos de dados agronômicos
        self._limites_vegetacao = self._criar_limites_vegetacao()
        self._classificadores_cultura = self._criar_classificadores_cultura()
        self._paletas_cores = self._criar_paletas_cores()
        
        # Cache de mapas gerados
        self._mapas_cache: Dict[str, MapaTematico] = {}
        
        # Contadores
        self._mapas_gerados = 0
        self._analises_realizadas = 0
    
    def _criar_limites_vegetacao(self) -> Dict[str, Dict[str, float]]:
        """Criar limites agronômicos para índices de vegetação."""
        return {
            "ndvi": {
                "min_ideal": 0.3,
                "max_ideal": 0.8,
                "min_critico": 0.0,
                "max_critico": 1.0,
                "faixas": {
                    "ausente": [0.0, 0.2],
                    "reduzida": [0.2, 0.4],
                    "moderada": [0.4, 0.6],
                    "alta": [0.6, 0.8],
                    "muito_alta": [0.8, 1.0]
                }
            },
            "ndre": {
                "min_ideal": 0.2,
                "max_ideal": 0.7,
                "min_critico": 0.0,
                "max_critico": 1.0,
                "faixas": {
                    "ausente": [0.0, 0.1],
                    "reduzida": [0.1, 0.3],
                    "moderada": [0.3, 0.5],
                    "alta": [0.5, 0.7],
                    "muito_alta": [0.7, 1.0]
                }
            },
            "gndvi": {
                "min_ideal": 0.4,
                "max_ideal": 0.8,
                "min_critico": 0.0,
                "max_critico": 1.0,
                "faixas": {
                    "ausente": [0.0, 0.3],
                    "reduzida": [0.3, 0.5],
                    "moderada": [0.5, 0.7],
                    "alta": [0.7, 0.9],
                    "muito_alta": [0.9, 1.0]
                }
            }
        }
    
    def _criar_classificadores_cultura(self) -> Dict[str, Dict[str, Any]]:
        """Criar classificadores por tipo de cultura."""
        return {
            "milho": {
                "ciclo_vegetativo": [120, 150],
                "fases_criticas": [30, 60, 90, 120],
                "limites_ndvi": {
                    "plantio": [0.1, 0.3],
                    "inicial": [0.3, 0.5],
                    "desenvolvimento": [0.5, 0.7],
                    "florecimento": [0.6, 0.8],
                    "maturacao": [0.4, 0.6],
                    "colheita": [0.1, 0.3]
                },
                "indices_prioritarios": ["ndvi", "ndre", "gndvi"]
            },
            "soja": {
                "ciclo_vegetativo": [110, 140],
                "fases_criticas": [25, 50, 75, 100],
                "limites_ndvi": {
                    "plantio": [0.05, 0.2],
                    "inicial": [0.2, 0.4],
                    "desenvolvimento": [0.4, 0.6],
                    "florecimento": [0.5, 0.7],
                    "maturacao": [0.3, 0.5],
                    "colheita": [0.05, 0.2]
                },
                "indices_prioritarios": ["ndvi", "savi", "msavi"]
            },
            "trigo": {
                "ciclo_vegetativo": [180, 220],
                "fases_criticas": [30, 60, 90, 120, 150],
                "limites_ndvi": {
                    "plantio": [0.1, 0.3],
                    "inicial": [0.3, 0.5],
                    "desenvolvimento": [0.4, 0.6],
                    "florecimento": [0.5, 0.7],
                    "maturacao": [0.6, 0.8],
                    "colheita": [0.1, 0.3]
                },
                "indices_prioritarios": ["ndvi", "evi", "nbr"]
            },
            "cafe": {
                "ciclo_vegetativo": [365, 730],
                "fases_criticas": [90, 180, 270, 365],
                "limites_ndvi": {
                    "brotação": [0.3, 0.5],
                    "floração": [0.5, 0.7],
                    "carga": [0.6, 0.8],
                    "maturação": [0.4, 0.6]
                },
                "indices_prioritarios": ["ndvi", "pri", "psri"]
            }
        }
    
    def _criar_paletas_cores(self) -> Dict[str, List[str]]:
        """Criar paletas de cores para diferentes temas."""
        return {
            "vegetacao": [
                "#8B4513", "#A0522D", "#D2691E", "#F4A460", 
                "#90EE90", "#32CD32", "#228B22", "#006400"
            ],
            "umidade": [
                "#FFF8DC", "#FFE4B5", "#FFD700", "#FFA500", 
                "#FF8C00", "#FF6347", "#DC143C", "#8B0000"
            ],
            "temperatura": [
                "#000080", "#0000FF", "#00FFFF", "#00FF00", 
                "#FFFF00", "#FF8000", "#FF0000", "#800000"
            ],
            "fertilidade": [
                "#8B4513", "#D2691E", "#F4A460", "#90EE90", 
                "#32CD32", "#228B22", "#006400", "#000080"
            ],
            "geral": [
                "#E6E6FA", "#DDA0DD", "#DA70D6", "#BA55D3", 
                "#9370DB", "#8A2BE2", "#7B68EE", "#6A5ACD"
            ]
        }
    
    def gerar_mapas_tematicos(self, camadas_mescladas: List[CamadaMesclada],
                            config_temas: ConfigTemas) -> List[MapaTematico]:
        """
        Gerar mapas temáticos a partir de camadas mescladas.
        
        Args:
            camadas_mescladas: Lista de camadas mescladas
            config_temas: Configuração de temas
        
        Returns:
            Lista de mapas temáticos gerados
        """
        logger.info(f"Gerando mapas temáticos para {len(camadas_mescladas)} camadas")
        
        mapas_gerados = []
        
        for camada in camadas_mescladas:
            # Gerar mapa para tema principal
            mapa_principal = self._gerar_mapa_tematico(
                camada, config_temas.tema_principal, config_temas
            )
            if mapa_principal:
                mapas_gerados.append(mapa_principal)
                self._mapas_cache[mapa_principal.mapa_id] = mapa_principal
            
            # Gerar mapas para temas secundários
            for tema_secundario in config_temas.temas_secundarios:
                mapa_secundario = self._gerar_mapa_tematico(
                    camada, tema_secundario, config_temas
                )
                if mapa_secundario:
                    mapas_gerados.append(mapa_secundario)
                    self._mapas_cache[mapa_secundario.mapa_id] = mapa_secundario
        
        self._mapas_gerados += len(mapas_gerados)
        logger.info(f"Gerados {len(mapas_gerados)} mapas temáticos")
        return mapas_gerados
    
    def _gerar_mapa_tematico(self, camada_mesclada: CamadaMesclada, tema: str,
                           config_temas: ConfigTemas) -> Optional[MapaTematico]:
        """Gerar mapa temático específico."""
        logger.info(f"Gerando mapa temático: {tema}")
        
        try:
            # Identificar tipo de tema
            tipo_tema = self._classificar_tipo_tema(tema)
            
            # Aplicar regras agronômicas
            regras_aplicadas = self._aplicar_regras_agronomicas(
                camada_mesclada, tipo_tema
            )
            
            # Gerar mapa temático
            mapa_tematico = MapaTematico(
                mapa_id=f"mapa_{tema}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                tema=tema,
                caminho_arquivo=f"mapas/{tema}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tif",
                formato="geotiff",
                resolucao_m=config_temas.resolucao_saida,
                data_geracao=datetime.now().isoformat(),
                legenda=self._gerar_legenda(tema, regras_aplicadas),
                metadados={
                    "tema": tema,
                    "tipo_tema": tipo_tema,
                    "regras_aplicadas": regras_aplicadas,
                    "resolucao_saida": config_temas.resolucao_saida,
                    "paleta_cores": self._selecionar_paleta_cores(tema, config_temas)
                }
            )
            
            # Salvar mapa
            self._salvar_mapa_tematico(mapa_tematico)
            
            return mapa_tematico
            
        except Exception as e:
            logger.error(f"Erro ao gerar mapa temático {tema}: {e}")
            return None
    
    def _classificar_tipo_tema(self, tema: str) -> str:
        """Classificar tema por tipo de análise agronômica."""
        temas_vegetacao = ["vegetacao", "saude_vegetal", "desempenho_cultura"]
        temas_agricola = ["umidade", "temperatura", "fertilidade"]
        temas_ambiental = ["clima", "solo", "agua"]
        temas_produtividade = ["produtividade", "rendimento", "qualidade"]
        
        if tema.lower() in temas_vegetacao:
            return "vegetacao"
        elif tema.lower() in temas_agricola:
            return "agricola"
        elif tema.lower() in temas_ambiental:
            return "ambiental"
        elif tema.lower() in temas_produtividade:
            return "produtividade"
        else:
            return "geral"
    
    def _aplicar_regras_agronomicas(self, camada_mesclada: CamadaMesclada,
                                  tipo_tema: str) -> Dict[str, Any]:
        """Aplicar regras agronômicas específicas por tipo de tema."""
        logger.info(f"Aplicando regras agronômicas para tema: {tipo_tema}")
        
        regras_aplicadas = {
            "tipo_tema": tipo_tema,
            "data_aplicacao": datetime.now().isoformat(),
            "analises_realizadas": self._analises_realizadas + 1
        }
        
        try:
            # Obter estatísticas da camada
            estatisticas = camada_mesclada.metadados.get("estatisticas", {})
            
            # Aplicar regras específicas por tipo
            if tipo_tema == "vegetacao":
                regras_vegetacao = self._aplicar_regras_vegetacao(camada_mesclada, estatisticas)
                regras_aplicadas.update(regras_vegetacao)
            
            elif tipo_tema == "agricola":
                regras_agricola = self._aplicar_regras_agricolas(camada_mesclada, estatisticas)
                regras_aplicadas.update(regras_agricola)
            
            elif tipo_tema == "ambiental":
                regras_ambiental = self._aplicar_regras_ambientais(camada_mesclada, estatisticas)
                regras_aplicadas.update(regras_ambiental)
            
            else:
                regras_geral = self._aplicar_regras_gerais(camada_mesclada, estatisticas)
                regras_aplicadas.update(regras_geral)
            
            # Adicionar recomendações
            regras_aplicadas["recomendacoes"] = self._gerar_recomendacoes(
                regras_aplicadas, tipo_tema
            )
            
            return regras_aplicadas
            
        except Exception as e:
            logger.error(f"Erro ao aplicar regras agronômicas: {e}")
            return {"erro": str(e)}
    
    def _aplicar_regras_vegetacao(self, camada_mesclada: CamadaMesclada,
                                 estatisticas: Dict[str, float]) -> Dict[str, Any]:
        """Aplicar regras específicas para análise de vegetação."""
        regras = {}
        
        try:
            # Analisar NDVI se disponível
            if "mean" in estatisticas:
                ndvi_mean = estatisticas["mean"]
                
                # Classificar saúde vegetal
                limites = self._limites_vegetacao.get("ndvi", {})
                
                if "min_ideal" in limites and "max_ideal" in limites:
                    if ndvi_mean < limites["min_ideal"]:
                        saude = "reduzida"
                        risco = "alto"
                    elif ndvi_mean > limites["max_ideal"]:
                        saude = "muito_alta"
                        risco = "baixo"
                    else:
                        saude = "ideal"
                        risco = "baixo"
                    
                    regras.update({
                        "saude_vegetal": saude,
                        "risco_produtivo": risco,
                        "ndvi_medio": ndvi_mean,
                        "densidade_vegetacao": self._estimar_densidade_vegetacao(ndvi_mean)
                    })
            
            # Análise de variabilidade
            if "std" in estatisticas:
                variabilidade = estatisticas["std"]
                if variabilidade > 0.2:
                    regras["variabilidade_alta"] = True
                    regras["heterogeneidade"] = "alta"
                else:
                    regras["variabilidade_baixa"] = True
                    regras["homogeneidade"] = "alta"
            
            # Estimar estágio fenológico
            regras["estagio_fenologico"] = self._estimar_estagio_fenologico(estatisticas)
            
            return regras
            
        except Exception as e:
            logger.error(f"Erro nas regras de vegetação: {e}")
            return {"erro": str(e)}
    
    def _aplicar_regras_agricolas(self, camada_mesclada: CamadaMesclada,
                                 estatisticas: Dict[str, float]) -> Dict[str, Any]:
        """Aplicar regras específicas para análise agrícola."""
        regras = {}
        
        try:
            # Análise de umidade
            umidade = self._estimar_umidade(estatisticas)
            regras["umidade_solo"] = umidade["nivel"]
            regras["necessidade_irrigacao"] = umidade["irrigacao"]
            
            # Análise de temperatura
            temperatura = self._estimar_temperatura(estatisticas)
            regras["temperatura_estimada"] = temperatura["valor"]
            regras["condicoes_ambientais"] = temperatura["condicoes"]
            
            # Análise de fertilidade
            fertilidade = self._estimar_fertilidade(estatisticas)
            regras["fertilidade_estimada"] = fertilidade["nivel"]
            regras["recomendacao_fertilizacao"] = fertilidade["recomendacao"]
            
            return regras
            
        except Exception as e:
            logger.error(f"Erro nas regras agrícolas: {e}")
            return {"erro": str(e)}
    
    def _aplicar_regras_ambientais(self, camada_mesclada: CamadaMesclada,
                                  estatisticas: Dict[str, float]) -> Dict[str, Any]:
        """Aplicar regras específicas para análise ambiental."""
        regras = {}
        
        try:
            # Análise de condições ambientais
            regras["condicoes_gerais"] = "adequadas"
            regras["riscos_ambientais"] = []
            
            # Verificar limites de estresse
            if "max" in estatisticas:
                maximo = estatisticas["max"]
                if maximo > 0.8:
                    regras["riscos_ambientais"].append("potencial_estresse")
            
            if "min" in estatisticas:
                minimo = estatisticas["min"]
                if minimo < 0.1:
                    regras["riscos_ambientais"].append("potencial_estresse")
            
            # Recomendações
            if not regras["riscos_ambientais"]:
                regras["recomendacoes_ambientais"] = ["manter_monitoramento"]
            else:
                regras["recomendacoes_ambientais"] = ["aumentar_frequencia_monitoramento"]
            
            return regras
            
        except Exception as e:
            logger.error(f"Erro nas regras ambientais: {e}")
            return {"erro": str(e)}
    
    def _aplicar_regras_gerais(self, camada_mesclada: CamadaMesclada,
                              estatisticas: Dict[str, float]) -> Dict[str, Any]:
        """Aplicar regras gerais."""
        regras = {
            "tipo_analise": "geral",
            "condicoes_gerais": "normais",
            "recomendacoes_basicas": ["manter_monitoramento_regular"]
        }
        
        try:
            # Análise estatística básica
            if "mean" in estatisticas:
                regras["valor_medio"] = estatisticas["mean"]
            
            if "std" in estatisticas:
                regras["variabilidade"] = "alta" if estatisticas["std"] > 0.1 else "baixa"
            
            return regras
            
        except Exception as e:
            logger.error(f"Erro nas regras gerais: {e}")
            return {"erro": str(e)}
    
    def _gerar_recomendacoes(self, regras_aplicadas: Dict[str, Any],
                           tipo_tema: str) -> List[str]:
        """Gerar recomendações baseadas nas regras aplicadas."""
        recomendacoes = []
        
        try:
            # Recomendações gerais
            if "erro" in regras_aplicadas:
                recomendacoes.append("Verificar qualidade dos dados de sensoriamento")
            
            # Recomendações por tipo de tema
            if tipo_tema == "vegetacao":
                if regras_aplicadas.get("saude_vegetal") == "reduzida":
                    recomendacoes.append("Avaliar necessidade de correção nutricional")
                if regras_aplicadas.get("variabilidade_alta"):
                    recomendacoes.append("Realizar amostragem dirigida em áreas de baixa performance")
            
            elif tipo_tema == "agricola":
                if regras_aplicadas.get("necessidade_irrigacao") == "alta":
                    recomendacoes.append("Implementar irrigação localizada")
                if regras_aplicadas.get("fertilidade_estimada") == "baixa":
                    recomendacoes.append("Aplicação de fertilizantes de acordo com análise de solo")
            
            elif tipo_tema == "ambiental":
                if "riscos_ambientais" in regras_aplicadas and regras_aplicadas["riscos_ambientais"]:
                    recomendacoes.append("Aumentar frequência de monitoramento")
                    recomendacoes.append("Preparar planos de mitigação de riscos")
            
            # Recomendação padrão
            if not recomendacoes:
                recomendacoes.append("Manter monitoramento regular")
            
            return recomendacoes
            
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {e}")
            return ["Verificar análise"]
    
    def _gerar_legenda(self, tema: str, regras_aplicadas: Dict[str, Any]) -> str:
        """Gerar legenda para o mapa temático."""
        try:
            tema_classificado = self._classificar_tipo_tema(tema)
            
            if tema_classificado == "vegetacao":
                saude = regras_aplicadas.get("saude_vegetal", "desconhecida")
                return f"Saúde Vegetal: {saude.upper()}"
            
            elif tema_classificado == "agricola":
                nivel_umidade = regras_aplicadas.get("umidade_solo", "desconhecido")
                return f"Umidade do Solo: {nivel_umidade.upper()}"
            
            elif tema_classificado == "ambiental":
                condicoes = regras_aplicadas.get("condicoes_gerais", "desconhecidas")
                return f"Condições Ambientais: {condicoes.upper()}"
            
            else:
                return f"Mapa Temático: {tema.upper()}"
            
        except Exception as e:
            logger.error(f"Erro ao gerar legenda: {e}")
            return f"Mapa: {tema.upper()}"
    
    def _selecionar_paleta_cores(self, tema: str, config_temas: ConfigTemas) -> List[str]:
        """Selecionar paleta de cores para o tema."""
        tema_lower = tema.lower()
        
        # Procurar tema específico primeiro
        if tema_lower in self._paletas_cores:
            return self._paletas_cores[tema_lower]
        
        # Procurar tipo de tema
        tema_classificado = self._classificar_tipo_tema(tema_lower)
        if tema_classificado in self._paletas_cores:
            return self._paletas_cores[tema_classificado]
        
        # Retornar paleta geral
        return self._paletas_cores["geral"]
    
    def _salvar_mapa_tematico(self, mapa_tematico: MapaTematico) -> None:
        """Salvar mapa temático em arquivo."""
        try:
            # Criar diretório se não existir
            caminho_saida = Path(mapa_tematico.caminho_arquivo)
            caminho_saida.parent.mkdir(parents=True, exist_ok=True)
            
            # Criar arquivo simulado
            with caminho_saida.open('wb') as f:
                f.write(b"SIMULATED_THEMATIC_MAP_DATA")
            
            # Salvar metadados
            metadados_path = caminho_saida.with_suffix(".json")
            with metadados_path.open('w') as f:
                import json
                json.dump(mapa_tematico.metadados, f, indent=2)
            
            logger.info(f"Mapa temático salvo: {caminho_saida}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar mapa temático: {e}")
    
    # Métodos auxiliares
    
    def _estimar_densidade_vegetacao(self, ndvi_medio: float) -> str:
        """Estimar densidade de vegetação baseado em NDVI."""
        if ndvi_medio < 0.2:
            return "baixa"
        elif ndvi_medio < 0.5:
            return "moderada"
        elif ndvi_medio < 0.7:
            return "alta"
        else:
            return "muito_alta"
    
    def _estimar_estagio_fenologico(self, estatisticas: Dict[str, float]) -> str:
        """Estimar estágio fenológico baseado em estatísticas."""
        # Implementação simplificada - na realidade seria mais complexo
        if "mean" in estatisticas:
            media = estatisticas["mean"]
            if media < 0.3:
                return "inicial"
            elif media < 0.6:
                return "desenvolvimento"
            else:
                return "maturacao"
        else:
            return "desconhecido"
    
    def _estimar_umidade(self, estatisticas: Dict[str, float]) -> Dict[str, str]:
        """Estimar umidade do solo."""
        # Implementação simplificada
        if "mean" in estatisticas:
            media = estatisticas["mean"]
            if media < 0.2:
                return {"nivel": "baixa", "irrigacao": "alta"}
            elif media < 0.5:
                return {"nivel": "moderada", "irrigacao": "moderada"}
            else:
                return {"nivel": "alta", "irrigacao": "baixa"}
        else:
            return {"nivel": "desconhecido", "irrigacao": "desconhecido"}
    
    def _estimar_temperatura(self, estatisticas: Dict[str, float]) -> Dict[str, Any]:
        """Estimar temperatura ambiente."""
        # Implementação simplificada
        return {
            "valor": "25°C",  # Valor fixo para simulação
            "condicoes": "adequadas"
        }
    
    def _estimar_fertilidade(self, estatisticas: Dict[str, float]) -> Dict[str, str]:
        """Estimar fertilidade do solo."""
        # Implementação simplificada
        if "mean" in estatisticas:
            media = estatisticas["mean"]
            if media < 0.3:
                return {"nivel": "baixa", "recomendacao": "fertilizacao"}
            elif media < 0.6:
                return {"nivel": "moderada", "recomendacao": "manutencao"}
            else:
                return {"nivel": "alta", "recomendacao": "monitoramento"}
        else:
            return {"nivel": "desconhecido", "recomendacao": "analise_solo"}
    
    # Métodos públicos
    
    def obter_limites_vegetacao(self) -> Dict[str, Dict[str, float]]:
        """Obter limites de vegetação."""
        return self._limites_vegetacao.copy()
    
    def obter_classificadores_cultura(self) -> Dict[str, Dict[str, Any]]:
        """Obter classificadores por cultura."""
        return self._classificadores_cultura.copy()
    
    def obter_mapas_cache(self) -> Dict[str, MapaTematico]:
        """Obter cache de mapas gerados."""
        return self._mapas_cache.copy()
    
    def limpar_cache_mapas(self) -> bool:
        """Limpar cache de mapas."""
        logger.info("Limpando cache de mapas")
        
        try:
            self._mapas_cache.clear()
            self._mapas_gerados = 0
            logger.info("Cache de mapas limpo com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return False
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obter estatísticas do motor."""
        return {
            "mapas_gerados": self._mapas_gerados,
            "analises_realizadas": self._analises_realizadas,
            "temas_suportados": len(self._paletas_cores),
            "ultimas_analises": list(self._mapas_cache.keys())[-5:] if self._mapas_cache else []
        }