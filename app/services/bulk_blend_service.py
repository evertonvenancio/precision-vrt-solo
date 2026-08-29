"""
Precision VRT Solo - Servico de Bulk Blend

Orquestrador do modulo de Bulk Blend (mistura de fertilizantes).
Responsavel apenas por validar entradas e chamar o Core.
"""

import logging
from typing import List, Dict, Any, Optional

from core.otimizacao.bulk_blend import (
    OtimizadorBulkBlend,
    FertilizanteDisponivel,
    RecomendacaoNutricional,
    ResultadoMistura,
)
from core.seguranca.permissions import get_permissoes

logger = logging.getLogger(__name__)


class BulkBlendService:
    """
    Servico de orquestracao para Bulk Blend.
    Nao contem logica de negocio, apenas coordena chamadas ao Core.
    """

    def __init__(self, db=None, tenant_id: str = 'default'):
        self.db = db
        self.tenant_id = tenant_id

    def buscar_permissoes(self) -> dict:
        """Busca as permissoes do usuario no banco."""
        return get_permissoes(self.db)

    # ------------------------------------------------------------------
    # Otimizacao de mistura
    # ------------------------------------------------------------------

    def otimizar_mistura(
        self,
        demanda: Dict[str, float],
        area_ha: float,
        fertilizantes: List[Dict[str, Any]],
        usar_pulp: bool = True,
        capacidade_lote_kg: float = 5000.0,
    ) -> Dict[str, Any]:
        """
        Executa a otimizacao de uma mistura de fertilizantes.

        Args:
            demanda: Demanda nutricional {"N": kg/ha, "P2O5": kg/ha, "K2O": kg/ha}
            area_ha: Area do talhao em hectares
            fertilizantes: Lista de fertilizantes disponiveis no estoque
            usar_pulp: Se True, tenta otimizacao via PuLP primeiro
            capacidade_lote_kg: Capacidade maxima de cada lote (kg)

        Returns:
            Dicionario com composicao, custo, lotes e metadados.
        """
        try:
            recomendacao = RecomendacaoNutricional(
                n_kg_ha=demanda.get("N", 0.0),
                p2o5_kg_ha=demanda.get("P2O5", 0.0),
                k2o_kg_ha=demanda.get("K2O", 0.0),
                area_ha=area_ha,
            )

            fertilizantes_disponiveis = [
                FertilizanteDisponivel(
                    nome=f["nome"],
                    custo_kg=float(f.get("custo_kg", 0.0)),
                    composicao=f.get("composicao", {}),
                    sgn=float(f.get("sgn", 220.0)),
                    densidade=float(f.get("densidade", 1.0)),
                    inclusao_min_pct=float(f.get("inclusao_min_pct", 0.0)),
                    inclusao_max_pct=float(f.get("inclusao_max_pct", 100.0)),
                )
                for f in fertilizantes
            ]

            otimizador = OtimizadorBulkBlend(
                fertilizantes=fertilizantes_disponiveis,
                usar_pulp=usar_pulp,
                capacidade_lote_kg=capacidade_lote_kg,
            )

            resultado = otimizador.otimizar(recomendacao)

            return self._resultado_para_dict(resultado)

        except Exception as e:
            logger.error(f"Erro ao otimizar mistura: {e}")
            return {
                "success": False,
                "error": str(e),
                "mensagem": "Falha ao otimizar mistura",
            }

    def _resultado_para_dict(self, resultado: ResultadoMistura) -> Dict[str, Any]:
        """Converte um ResultadoMistura em dicionario serializavel."""
        return {
            "success": True,
            "composicao": resultado.composicao,
            "custo_total": resultado.custo_total,
            "nutrientes_totais": resultado.nutrientes_totais,
            "pct_inclusao": resultado.pct_inclusao,
            "metodo": resultado.metodo,
            "status": resultado.status,
            "compatibilidade": resultado.compatibilidade,
            "lotes": resultado.lotes,
            "mensagem": "Mistura otimizada com sucesso",
        }

    def verificar_compatibilidade(
        self, composicao: Dict[str, float], fertilizantes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verifica a compatibilidade fisica de uma composicao ja definida.

        Args:
            composicao: Dict[nome, kg]
            fertilizantes: Lista de fertilizantes (para parametros SGN/densidade)

        Returns:
            Dicionario com nota de compatibilidade.
        """
        try:
            fertilizantes_disponiveis = [
                FertilizanteDisponivel(
                    nome=f["nome"],
                    custo_kg=float(f.get("custo_kg", 0.0)),
                    composicao=f.get("composicao", {}),
                    sgn=float(f.get("sgn", 220.0)),
                    densidade=float(f.get("densidade", 1.0)),
                    inclusao_min_pct=float(f.get("inclusao_min_pct", 0.0)),
                    inclusao_max_pct=float(f.get("inclusao_max_pct", 100.0)),
                )
                for f in fertilizantes
            ]

            otimizador = OtimizadorBulkBlend(fertilizantes=fertilizantes_disponiveis)
            nota = otimizador._calcular_compatibilidade(composicao)

            return {
                "success": True,
                "compatibilidade": nota,
                "mensagem": "Compatibilidade calculada",
            }

        except Exception as e:
            logger.error(f"Erro ao calcular compatibilidade: {e}")
            return {
                "success": False,
                "error": str(e),
                "mensagem": "Falha ao calcular compatibilidade",
            }