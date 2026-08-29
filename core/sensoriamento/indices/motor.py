"""
Precision VRT Solo — Motor de Cálculo de Índices Espectrais

Calcula todos os índices espectrais suportados pelo sistema.
Extensível para aceitar qualquer índice futuro.
"""

import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path

from ..satelites.contratos import (
    ImagemSatelite, ImagemProcessada, CamadaIndice, 
    TipoIndice, ConfigIndicesEspectrais, ConfigMesclagem
)

logger = logging.getLogger(__name__)


class MotorCalculoIndices:
    """Motor para cálculo de índices espectrais e mesclagem de camadas."""
    
    def __init__(self):
        logger.info("MotorCalculoIndices inicializado")
        
        # Banco de índices espectrais disponíveis
        self._indices_disponiveis = self._criar_banco_indices()
        
        # Cache de resultados
        self._camadas_calculadas: Dict[str, CamadaIndice] = {}
        
        # Configurações por índice
        self._configuracoes_indices = {
            TipoIndice.NDVI: {
                "bandas_necessarias": ["nir", "red"],
                "formula": "(nir - red) / (nir + red)",
                "descricao": "Normalized Difference Vegetation Index",
                "intervalo_valido": (-1.0, 1.0),
                "cores_recomendadas": ["brown", "lightgreen", "green", "darkgreen"]
            },
            TipoIndice.NDRE: {
                "bandas_necessarias": ["nir", "red_edge"],
                "formula": "(nir - red_edge) / (nir + red_edge)",
                "descricao": "Normalized Difference Red Edge",
                "intervalo_valido": (-1.0, 1.0),
                "cores_recomendadas": ["brown", "yellow", "green", "darkgreen"]
            },
            TipoIndice.GNDVI: {
                "bandas_necessarias": ["nir", "green"],
                "formula": "(nir - green) / (nir + green)",
                "descricao": "Green Normalized Difference Vegetation Index",
                "intervalo_valido": (-1.0, 1.0),
                "cores_recomendadas": ["brown", "lightgreen", "green", "darkgreen"]
            },
            TipoIndice.SAVI: {
                "bandas_necessarias": ["nir", "red"],
                "formula": "(nir - red) / (nir + red + 0.5)",
                "descricao": "Soil Adjusted Vegetation Index",
                "intervalo_valido": (-1.0, 1.0),
                "cores_recomendadas": ["brown", "lightgreen", "green", "darkgreen"]
            },
            TipoIndice.MSAVI: {
                "bandas_necessarias": ["nir", "red"],
                "formula": "0.5 * (2 * nir + 1 - np.sqrt((2 * nir + 1)**2 - 8 * (nir - red)))",
                "descricao": "Modified Soil Adjusted Vegetation Index",
                "intervalo_valido": (-1.0, 1.0),
                "cores_recomendadas": ["brown", "lightgreen", "green", "darkgreen"]
            },
            TipoIndice.EVI: {
                "bandas_necessarias": ["nir", "red", "blue"],
                "formula": "2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1)",
                "descricao": "Enhanced Vegetation Index",
                "intervalo_valido": (-2.0, 2.0),
                "cores_recomendadas": ["brown", "lightgreen", "green", "darkgreen"]
            },
            TipoIndice.PRI: {
                "bandas_necessarias": ["green", "yellow"],
                "formula": "(yellow - green) / (yellow + green)",
                "descricao": "Photochemical Reflectance Index",
                "intervalo_valido": (-1.0, 1.0),
                "cores_recomendadas": ["brown", "lightgreen", "green", "darkgreen"]
            },
            TipoIndice.NDWI: {
                "bandas_necessarias": ["green", "nir"],
                "formula": "(green - nir) / (green + nir)",
                "descricao": "Normalized Difference Water Index",
                "intervalo_valido": (-1.0, 1.0),
                "cores_recomendadas": ["brown", "lightblue", "blue", "darkblue"]
            },
            TipoIndice.NDBI: {
                "bandas_necessarias": ["swir1", "swir2"],
                "formula": "(swir2 - swir1) / (swir2 + swir1)",
                "descricao": "Normalized Difference Built-up Index",
                "intervalo_valido": (-1.0, 1.0),
                "cores_recomendadas": ["brown", "gray", "lightgray", "white"]
            },
            TipoIndice.NBR: {
                "bandas_necessarias": ["nir", "swir2"],
                "formula": "(nir - swir2) / (nir + swir2)",
                "descricao": "Normalized Burn Ratio",
                "intervalo_valido": (-1.0, 1.0),
                "cores_recomendadas": ["black", "brown", "green", "darkgreen"]
            },
            TipoIndice.PSRI: {
                "bandas_necessarias": ["red", "green", "blue"],
                "formula": "(red - green) / blue",
                "descricao": "Plant Senescence Reflectance Index",
                "intervalo_valido": (-5.0, 5.0),
                "cores_recomendadas": ["brown", "orange", "yellow", "red"]
            },
            TipoIndice.SIPI: {
                "bandas_necessarias": ["nir", "red", "blue"],
                "formula": "(nir - blue) / (nir - red)",
                "descricao": "Structure Insensitive Pigment Index",
                "intervalo_valido": (-2.0, 2.0),
                "cores_recomendadas": ["brown", "orange", "yellow", "green"]
            }
        }
    
    def _criar_banco_indices(self) -> Dict[str, Dict[str, Any]]:
        """Criar banco de índices espectrais disponíveis."""
        return {
            tipo.value: config for tipo, config in self._configuracoes_indices.items()
        }
    
    def calcular_indice(self, imagem_processada: ImagemProcessada,
                       tipo_indice: TipoIndice,
                       config_indices: ConfigIndicesEspectrais) -> CamadaIndice:
        """
        Calcular índice espectral específico para uma imagem processada.
        
        Args:
            imagem_processada: Imagem processada
            tipo_indice: Tipo de índice a calcular
            config_indices: Configuração de índices
        
        Returns:
            Camada do índice calculado
        """
        logger.info(f"Calculando índice: {tipo_indice.value}")
        
        try:
            # Verificar se índice é suportado
            if tipo_indice not in self._configuracoes_indices:
                raise ValueError(f"Índice não suportado: {tipo_indice.value}")
            
            # Obter configuração do índice
            config_indice = self._configuracoes_indices[tipo_indice]
            
            # Verificar se imagem tem bandas necessárias
            self._validar_bandas_imagem(imagem_processada, config_indice["bandas_necessarias"])
            
            # Carregar dados da imagem
            dados_banda = self._carregar_dados_imagem(imagem_processada)
            
            # Calcular índice
            valores_calculados = self._aplicar_formula_indice(
                dados_banda, config_indice["formula"], tipo_indice
            )
            
            # Calcular estatísticas
            estatisticas = self._calcular_estatisticas(valores_calculados)
            
            # Criar camada de índice
            camada_indice = CamadaIndice(
                nome_indice=tipo_indice,
                imagem_origem=imagem_processada.imagem_id,
                caminho_saida=f"indices/{tipo_indice.value}_{imagem_processada.imagem_id}.tif",
                valores={"dados": valores_calculados.tolist()},
                estatisticas=estatisticas,
                data_calculo=datetime.now().isoformat()
            )
            
            # Salvar resultado
            self._salvar_camada_indice(camada_indice)
            
            # Adicionar ao cache
            self._camadas_calculadas[camada_indice.imagem_origem + "_" + tipo_indice.value] = camada_indice
            
            logger.info(f"Índice {tipo_indice.value} calculado com sucesso")
            return camada_indice
            
        except Exception as e:
            logger.error(f"Erro ao calcular índice {tipo_indice.value}: {e}")
            raise
    
    def calcular_lote_indices(self, imagens_processadas: List[ImagemProcessada],
                            config_indices: ConfigIndicesEspectrais) -> List[CamadaIndice]:
        """Calcular índices para múltiplas imagens em lote."""
        logger.info(f"Calculando índices para {len(imagens_processadas)} imagens")
        
        camadas_indices = []
        
        for imagem in imagens_processadas:
            for tipo_indice in config_indices.indices_calcular:
                try:
                    camada = self.calcular_indice(imagem, tipo_indice, config_indices)
                    camadas_indices.append(camada)
                except Exception as e:
                    logger.warning(f"Erro ao calcular índice {tipo_indice.value} para imagem {imagem.imagem_id}: {e}")
                    continue
        
        logger.info(f"Calculados {len(camadas_indices)} índices em lote")
        return camadas_indices
    
    def mesclar_camadas(self, camadas_indices: List[CamadaIndice],
                       config_mesclagem: ConfigMesclagem) -> List[CamadaIndice]:
        """
        Mescamultiplos índices em camadas combinadas.
        
        Args:
            camadas_indices: Lista de camadas de índices
            config_mesclagem: Configuração de mesclagem
        
        Returns:
            Lista de camadas mescladas
        """
        logger.info(f"Mesclando {len(camadas_indices)} camadas")
        
        camadas_mescladas = []
        
        # Agrupar camadas por tema ou critério
        grupos_camadas = self._agrupar_camadas(camadas_indices, config_mesclagem)
        
        for grupo_id, camadas_grupo in grupos_camadas.items():
            if len(camadas_grupo) > 1:
                # Mescam camadas do grupo
                camada_mesclada = self._mesclar_grupo_camadas(
                    camadas_grupo, config_mesclagem
                )
                camadas_mescladas.append(camada_mesclada)
        
        logger.info(f"Mescladas {len(camadas_mescladas)} camadas combinadas")
        return camadas_mescladas
    
    # Métodos auxiliares
    
    def _validar_bandas_imagem(self, imagem_processada: ImagemProcessada,
                             bandas_necessarias: List[str]) -> None:
        """Validar se imagem tem todas bandas necessárias."""
        # Verificar metadados da imagem
        metadados = imagem_processada.metadados
        
        if "bands" not in metadados:
            raise ValueError("Imagem não possui informações de bandas")
        
        bandas_disponiveis = metadados["bands"]
        
        for banda in bandas_necessarias:
            if banda not in bandas_disponiveis:
                raise ValueError(f"Banda '{banda}' não encontrada na imagem. Disponíveis: {bandas_disponiveis}")
    
    def _carregar_dados_imagem(self, imagem_processada: ImagemProcessada) -> Dict[str, np.ndarray]:
        """Carregar dados da imagem processada."""
        try:
            # Na implementação real, carregaria dados reais da imagem
            # Por enquanto, gerar dados simulados
            metadados = imagem_processada.metadados
            
            dados_banda = {}
            for banda in metadados.get("bands", []):
                # Gerar dados aleatórios simulando valores de reflectância
                shape = (100, 100)  # Tamanho padrão
                dados_banda[banda] = np.random.uniform(0.0, 1.0, shape)
            
            return dados_banda
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados da imagem: {e}")
            raise
    
    def _aplicar_formula_indice(self, dados_banda: Dict[str, np.ndarray],
                               formula: str, tipo_indice: TipoIndice) -> np.ndarray:
        """Aplicar fórmula do índice aos dados."""
        try:
            # Avaliar fórmula dinamicamente
            namespace = {"np": np, **dados_banda}
            resultado = eval(formula, {}, namespace)
            
            # Validar resultado
            resultado = np.asarray(resultado)
            
            config = self._configuracoes_indices[tipo_indice]
            min_val, max_val = config["intervalo_valido"]
            
            if np.any(resultado < min_val) or np.any(resultado > max_val):
                logger.warning(f"Valores fora do intervalo válido [{min_val}, {max_val}] para {tipo_indice.value}")
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao aplicar fórmula do índice: {e}")
            raise
    
    def _calcular_estatisticas(self, dados: np.ndarray) -> Dict[str, float]:
        """Calcular estatísticas básicas dos dados."""
        try:
            return {
                "min": float(np.min(dados)),
                "max": float(np.max(dados)),
                "mean": float(np.mean(dados)),
                "std": float(np.std(dados)),
                "median": float(np.median(dados)),
                "q25": float(np.percentile(dados, 25)),
                "q75": float(np.percentile(dados, 75))
            }
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {e}")
            return {}
    
    def _salvar_camada_indice(self, camada_indice: CamadaIndice) -> None:
        """Salvar camada de índice em arquivo."""
        try:
            # Criar diretório se não existir
            caminho_saida = Path(camada_indice.caminho_saida)
            caminho_saida.parent.mkdir(parents=True, exist_ok=True)
            
            # Salvar dados (simulado)
            import json
            dados_salvar = {
                "imagem_origem": camada_indice.imagem_origem,
                "nome_indice": camada_indice.nome_indice.value,
                "estatisticas": camada_indice.estatisticas,
                "data_calculo": camada_indice.data_calculo,
                "valores_shape": camada_indice.valores.get("dados_shape", [100, 100])
            }
            
            with caminho_saida.with_suffix(".json").open('w') as f:
                json.dump(dados_salvar, f, indent=2)
                
        except Exception as e:
            logger.error(f"Erro ao salvar camada de índice: {e}")
            raise
    
    def _agrupar_camadas(self, camadas_indices: List[CamadaIndice],
                        config_mesclagem: ConfigMesclagem) -> Dict[str, List[CamadaIndice]]:
        """Agrupar camadas para mesclagem."""
        grupos = {}
        
        if config_mesclagem.estrategia == "tematica":
            # Agrupar por tipo de índice
            for camada in camadas_indices:
                tema = self._classificar_tema_indice(camada.nome_indice)
                if tema not in grupos:
                    grupos[tema] = []
                grupos[tema].append(camada)
        else:
            # Agrupar por imagem origem
            for camada in camadas_indices:
                origem = camada.imagem_origem
                if origem not in grupos:
                    grupos[origem] = []
                grupos[origem].append(camada)
        
        return grupos
    
    def _classificar_tema_indice(self, tipo_indice: TipoIndice) -> str:
        """Classificar índice por tema."""
        temas_vegetacao = [TipoIndice.NDVI, TipoIndice.NDRE, TipoIndice.GNDVI, 
                          TipoIndice.SAVI, TipoIndice.MSAVI, TipoIndice.EVI]
        temas_agua = [TipoIndice.NDWI]
        temas_urbanas = [TipoIndice.NDBI]
        temas_fogo = [TipoIndice.NBR]
        temas_fotossintese = [TipoIndice.PRI]
        temas_senescencia = [TipoIndice.PSRI, TipoIndice.SIPI]
        
        if tipo_indice in temas_vegetacao:
            return "vegetacao"
        elif tipo_indice in temas_agua:
            return "agua"
        elif tipo_indice in temas_urbanas:
            return "urbana"
        elif tipo_indice in temas_fogo:
            return "fogo"
        elif tipo_indice in temas_fotossintese:
            return "fotossintese"
        elif tipo_indice in temas_senescencia:
            return "senescencia"
        else:
            return "geral"
    
    def _mesclar_grupo_camadas(self, camadas_grupo: List[CamadaIndice],
                              config_mesclagem: ConfigMesclagem) -> CamadaIndice:
        """Mescam um grupo de camadas."""
        logger.info(f"Mesclando grupo de {len(camadas_grupo)} camadas")
        
        # Criar nome para camada mesclada
        nome_grupo = f"mescla_{'_'.join([c.nome_indice.value for c in camadas_grupo])}"
        
        # Combinar estatísticas
        estatisticas_combinadas = self._combinar_estatisticas(camadas_grupo)
        
        # Criar camada mesclada
        camada_mesclada = CamadaIndice(
            nome_indice=TipoIndice.ARBITRARIO,
            imagem_origem=f"mescla_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            caminho_saida=f"indices/{nome_grupo}.tif",
            valores={"camadas_originais": [c.nome_indice.value for c in camadas_grupo]},
            estatisticas=estatisticas_combinadas,
            data_calculo=datetime.now().isoformat()
        )
        
        # Salvar mesclagem
        self._salvar_camada_indice(camada_mesclada)
        
        logger.info(f"Grupo mesclado: {nome_grupo}")
        return camada_mesclada
    
    def _combinar_estatisticas(self, camadas_grupo: List[CamadaIndice]) -> Dict[str, float]:
        """Combinar estatísticas de múltiplas camadas."""
        try:
            # Combinar estatísticas (média)
            estatisticas_combinadas = {}
            
            for key in ["min", "max", "mean", "std", "median"]:
                valores = []
                for camada in camadas_grupo:
                    if key in camada.estatisticas:
                        valores.append(camada.estatisticas[key])
                
                if valores:
                    estatisticas_combinadas[key] = float(np.mean(valores))
            
            return estatisticas_combinadas
            
        except Exception as e:
            logger.error(f"Erro ao combinar estatísticas: {e}")
            return {}
    
    # Métodos públicos
    
    def obter_indices_disponiveis(self) -> List[TipoIndice]:
        """Obter todos índices disponíveis."""
        return list(self._configuracoes_indices.keys())
    
    def obter_configuracao_indice(self, tipo_indice: TipoIndice) -> Dict[str, Any]:
        """Obter configuração de um índice específico."""
        return self._configuracoes_indices.get(tipo_indice, {})
    
    def suporta_indice(self, tipo_indice: TipoIndice) -> bool:
        """Verificar se índice é suportado."""
        return tipo_indice in self._configuracoes_indices
    
    def adicionar_indice_custom(self, nome_indice: str, configuracao: Dict[str, Any]) -> bool:
        """Adicionar índice personalizado ao sistema."""
        logger.info(f"Adicionando índice customizado: {nome_indice}")
        
        try:
            # Validar configuração
            required_keys = ["bandas_necessarias", "formula", "descricao"]
            for key in required_keys:
                if key not in configuracao:
                    raise ValueError(f"Configuração incompleta: faltando {key}")
            
            # Adicionar ao sistema
            self._configuracoes_indices[TipoIndice.ARBITRARIO] = configuracao
            self._indices_disponiveis[nome_indice] = configuracao
            
            logger.info(f"Índice {nome_indice} adicionado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar índice customizado: {e}")
            return False
    
    def remover_indice(self, tipo_indice: TipoIndice) -> bool:
        """Remover índice do sistema."""
        logger.info(f"Removendo índice: {tipo_indice.value}")
        
        try:
            if tipo_indice in self._configuracoes_indices:
                del self._configuracoes_indices[tipo_indice]
                
                # Remover do banco de índices
                if tipo_indice.value in self._indices_disponiveis:
                    del self._indices_disponiveis[tipo_indice.value]
                
                logger.info(f"Índice {tipo_indice.value} removido com sucesso")
                return True
            else:
                logger.warning(f"Índice não encontrado: {tipo_indice.value}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao remover índice: {e}")
            return False