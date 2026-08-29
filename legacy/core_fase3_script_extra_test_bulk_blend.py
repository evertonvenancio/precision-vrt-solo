"""
Testes unitarios para o motor de Bulk Blend e otimizacao PuLP.

Valida:
- Otimizacao PuLP retornando solucao otima para demanda padrao
- Fallback para heuristico quando PuLP falha
- Integracao completa do OtimizadorBulkBlend
"""

import logging
import unittest
from typing import Dict, List

# Configura logging para testes
logging.basicConfig(level=logging.DEBUG)

# ---------------------------------------------------------------------------
# Dados de teste
# ---------------------------------------------------------------------------

FERTILIZANTES_TESTE = [
    {
        "nome": "Ureia",
        "custo_kg": 3.50,
        "composicao": {"N": 45.0, "P2O5": 0.0, "K2O": 0.0},
        "sgn": 2.5,
        "densidade": 0.75,
        "inclusao_min_pct": 0.0,
        "inclusao_max_pct": 100.0,
    },
    {
        "nome": "MAP",
        "custo_kg": 8.20,
        "composicao": {"N": 11.0, "P2O5": 52.0, "K2O": 0.0},
        "sgn": 3.0,
        "densidade": 0.90,
        "inclusao_min_pct": 0.0,
        "inclusao_max_pct": 100.0,
    },
    {
        "nome": "Superfosfato Simples",
        "custo_kg": 2.80,
        "composicao": {"N": 0.0, "P2O5": 20.0, "K2O": 0.0},
        "sgn": 2.8,
        "densidade": 0.85,
        "inclusao_min_pct": 0.0,
        "inclusao_max_pct": 100.0,
    },
    {
        "nome": "KCl",
        "custo_kg": 5.00,
        "composicao": {"N": 0.0, "P2O5": 0.0, "K2O": 60.0},
        "sgn": 2.2,
        "densidade": 1.05,
        "inclusao_min_pct": 0.0,
        "inclusao_max_pct": 100.0,
    },
]


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------

class TestOtimizadorMisturaPuLP(unittest.TestCase):
    """Testes para o motor PuLP de otimizacao de mistura."""

    def setUp(self):
        """Configura dados comuns para os testes."""
        try:
            from core.otimizacao_pulp import (
                OtimizadorMistura,
                Fertilizante,
                DemandaNutricional,
            )
            self.pulp_disponivel = True
            self.OtimizadorMistura = OtimizadorMistura
            self.Fertilizante = Fertilizante
            self.DemandaNutricional = DemandaNutricional
        except ImportError:
            self.pulp_disponivel = False
            self.skipTest("PuLP nao esta instalado. Testes de PL serao ignorados.")

    def _criar_fertilizantes(self) -> List:
        """Cria lista de objetos Fertilizante para testes."""
        return [
            self.Fertilizante(
                nome=f["nome"],
                custo_kg=f["custo_kg"],
                composicao=f["composicao"],
                inclusao_min_pct=f["inclusao_min_pct"],
                inclusao_max_pct=f["inclusao_max_pct"],
            )
            for f in FERTILIZANTES_TESTE
        ]

    def test_solucao_otima_demanda_padrao(self):
        """
        Verifica se o PuLP retorna uma solucao viavel para:
        - N = 80 kg
        - P2O5 = 60 kg
        - K2O = 40 kg
        """
        if not self.pulp_disponivel:
            self.skipTest("PuLP nao disponivel")

        fertilizantes = self._criar_fertilizantes()
        demanda = self.DemandaNutricional(
            nutrientes={"N": 80.0, "P2O5": 60.0, "K2O": 40.0},
            tolerancia_pct=5.0,
        )

        motor = self.OtimizadorMistura(
            fertilizantes=fertilizantes,
            demanda=demanda,
        )

        resultado = motor.otimizar()

        # Verifica se retornou resultado
        self.assertIsNotNone(resultado, "Otimizacao retornou None")

        # Verifica status otimo
        self.assertEqual(
            resultado["status"],
            "Optimal",
            f"Status esperado 'Optimal', obtido '{resultado['status']}'"
        )

        # Verifica composicao nao vazia
        self.assertTrue(
            resultado["composicao"],
            "Composicao da mistura esta vazia"
        )

        # Verifica custo positivo
        self.assertGreater(
            resultado["custo_total"],
            0.0,
            "Custo total deve ser positivo"
        )

        # Verifica nutrientes dentro da tolerancia de +/- 5%
        for nutriente, demanda_kg in demanda.nutrientes.items():
            atingido = resultado["nutrientes_totais"].get(nutriente, 0.0)
            tolerancia = demanda_kg * 0.05
            self.assertGreaterEqual(
                atingido,
                demanda_kg - tolerancia,
                f"{nutriente}: atingido {atingido} < minimo {demanda_kg - tolerancia}"
            )
            self.assertLessEqual(
                atingido,
                demanda_kg + tolerancia,
                f"{nutriente}: atingido {atingido} > maximo {demanda_kg + tolerancia}"
            )

        # Verifica que percentuais somam ~100%
        total_pct = sum(resultado["pct_inclusao"].values())
        self.assertAlmostEqual(
            total_pct,
            100.0,
            delta=1.0,
            msg=f"Soma dos percentuais deve ser ~100%, obtido {total_pct}"
        )

        logging.info(f"
[OK] Solucao otima encontrada:")
        logging.info(f"  Status: {resultado['status']}")
        logging.info(f"  Custo Total: R$ {resultado['custo_total']:.2f}")
        logging.info(f"  Composicao: {resultado['composicao']}")
        logging.info(f"  Nutrientes: {resultado['nutrientes_totais']}")
        logging.info(f"  Inclusao %: {resultado['pct_inclusao']}")

    def test_incompatibilidade_quimica(self):
        """
        Verifica se incompatibilidades quimicas sao respeitadas.
        Ureia e Superfosfato Simples nao podem coexistir.
        """
        if not self.pulp_disponivel:
            self.skipTest("PuLP nao disponivel")

        fertilizantes = self._criar_fertilizantes()
        demanda = self.DemandaNutricional(
            nutrientes={"N": 80.0, "P2O5": 60.0, "K2O": 40.0},
            tolerancia_pct=5.0,
        )

        motor = self.OtimizadorMistura(
            fertilizantes=fertilizantes,
            demanda=demanda,
            incompatibilidades=[("Ureia", "Superfosfato Simples")],
        )

        resultado = motor.otimizar()
        self.assertIsNotNone(resultado)

        if resultado["status"] == "Optimal":
            composicao = resultado["composicao"]
            tem_ureia = "Ureia" in composicao and composicao["Ureia"] > 0.001
            tem_super = "Superfosfato Simples" in composicao and composicao["Superfosfato Simples"] > 0.001

            self.assertFalse(
                tem_ureia and tem_super,
                "Ureia e Superfosfato Simples nao devem coexistir na mistura"
            )

            logging.info(f"
[OK] Incompatibilidade respeitada:")
            logging.info(f"  Ureia presente: {tem_ureia}")
            logging.info(f"  Superfosfato presente: {tem_super}")

    def test_limite_inclusao(self):
        """
        Verifica se limites de inclusao maxima sao respeitados.
        """
        if not self.pulp_disponivel:
            self.skipTest("PuLP nao disponivel")

        # Cria fertilizantes com limite maximo de 30%
        fertilizantes = self._criar_fertilizantes()
        for f in fertilizantes:
            f.inclusao_max_pct = 30.0

        demanda = self.DemandaNutricional(
            nutrientes={"N": 80.0, "P2O5": 60.0, "K2O": 40.0},
            tolerancia_pct=5.0,
        )

        motor = self.OtimizadorMistura(
            fertilizantes=fertilizantes,
            demanda=demanda,
        )

        resultado = motor.otimizar()
        self.assertIsNotNone(resultado)

        if resultado["status"] == "Optimal":
            for nome, pct in resultado["pct_inclusao"].items():
                self.assertLessEqual(
                    pct,
                    30.0 + 0.1,  # tolerancia numerica
                    f"{nome}: inclusao {pct}% excede o limite maximo de 30%"
                )

            logging.info(f"
[OK] Limites de inclusao respeitados:")
            logging.info(f"  Percentuais: {resultado['pct_inclusao']}")


class TestOtimizadorBulkBlend(unittest.TestCase):
    """Testes de integracao para o OtimizadorBulkBlend."""

    def setUp(self):
        """Configura o otimizador com dados de teste."""
        try:
            from core.bulk_blend import (
                OtimizadorBulkBlend,
                FertilizanteDisponivel,
                RecomendacaoNutricional,
            )
            self.OtimizadorBulkBlend = OtimizadorBulkBlend
            self.FertilizanteDisponivel = FertilizanteDisponivel
            self.RecomendacaoNutricional = RecomendacaoNutricional
        except ImportError as exc:
            self.skipTest(f"Nao foi possivel importar modulos: {exc}")

    def _criar_fertilizantes(self) -> List:
        """Cria lista de FertilizanteDisponivel para testes."""
        return [
            self.FertilizanteDisponivel(
                nome=f["nome"],
                custo_kg=f["custo_kg"],
                composicao=f["composicao"],
                sgn=f["sgn"],
                densidade=f["densidade"],
                inclusao_min_pct=f["inclusao_min_pct"],
                inclusao_max_pct=f["inclusao_max_pct"],
            )
            for f in FERTILIZANTES_TESTE
        ]

    def test_otimizacao_completa_pulp(self):
        """
        Testa o fluxo completo com PuLP habilitado:
        demanda N=80, P2O5=60, K2O=40 em 1 ha.
        """
        fertilizantes = self._criar_fertilizantes()
        recomendacao = self.RecomendacaoNutricional(
            n_kg_ha=80.0,
            p2o5_kg_ha=60.0,
            k2o_kg_ha=40.0,
            area_ha=1.0,
        )

        otimizador = self.OtimizadorBulkBlend(
            fertilizantes=fertilizantes,
            usar_pulp=True,
            capacidade_lote_kg=5000.0,
        )

        resultado = otimizador.otimizar(recomendacao)

        # Verifica que retornou resultado valido
        self.assertIsNotNone(resultado)
        self.assertIn(
            resultado.status,
            ["Optimal", "Heuristico"],
            f"Status inesperado: {resultado.status}"
        )

        # Verifica composicao
        self.assertTrue(
            resultado.composicao,
            "Composicao nao deve estar vazia"
        )

        # Verifica nutrientes atingidos
        for nutriente in ["N", "P2O5", "K2O"]:
            self.assertIn(
                nutriente,
                resultado.nutrientes_totais,
                f"Nutriente {nutriente} deve estar presente"
            )
            self.assertGreater(
                resultado.nutrientes_totais[nutriente],
                0.0,
                f"Nutriente {nutriente} deve ser positivo"
            )

        # Verifica lotes
        self.assertTrue(
            resultado.lotes,
            "Deve haver pelo menos um lote gerado"
        )

        # Verifica compatibilidade
        self.assertGreaterEqual(
            resultado.compatibilidade,
            0.0,
            "Compatibilidade nao deve ser negativa"
        )

        logging.info(f"
[OK] Otimizacao completa:")
        logging.info(f"  Metodo: {resultado.metodo}")
        logging.info(f"  Status: {resultado.status}")
        logging.info(f"  Custo: R$ {resultado.custo_total:.2f}")
        logging.info(f"  Composicao: {resultado.composicao}")
        logging.info(f"  Nutrientes: {resultado.nutrientes_totais}")
        logging.info(f"  Compatibilidade: {resultado.compatibilidade}%")
        logging.info(f"  Lotes: {len(resultado.lotes)}")

    def test_fallback_heuristico(self):
        """
        Testa que o sistema funciona com fallback heuristico
        quando PuLP esta desabilitado.
        """
        fertilizantes = self._criar_fertilizantes()
        recomendacao = self.RecomendacaoNutricional(
            n_kg_ha=80.0,
            p2o5_kg_ha=60.0,
            k2o_kg_ha=40.0,
            area_ha=1.0,
        )

        otimizador = self.OtimizadorBulkBlend(
            fertilizantes=fertilizantes,
            usar_pulp=False,  # Forca heuristico
            capacidade_lote_kg=5000.0,
        )

        resultado = otimizador.otimizar(recomendacao)

        self.assertEqual(resultado.metodo, "heuristico")
        self.assertEqual(resultado.status, "Heuristico")
        self.assertTrue(resultado.composicao)

        logging.info(f"
[OK] Fallback heuristico funcional:")
        logging.info(f"  Metodo: {resultado.metodo}")
        logging.info(f"  Composicao: {resultado.composicao}")

    def test_composicao_sem_pulp_instalado(self):
        """
        Simula ambiente sem PuLP verificando que o codigo nao quebra.
        """
        # Este teste valida que a classe pode ser instanciada mesmo
        # se o modulo otimizacao_pulp nao estiver disponivel
        fertilizantes = self._criar_fertilizantes()
        recomendacao = self.RecomendacaoNutricional(
            n_kg_ha=80.0,
            p2o5_kg_ha=60.0,
            k2o_kg_ha=40.0,
            area_ha=1.0,
        )

        # Forca usar_pulp=False para simular ambiente sem PuLP
        otimizador = self.OtimizadorBulkBlend(
            fertilizantes=fertilizantes,
            usar_pulp=False,
        )

        resultado = otimizador.otimizar(recomendacao)

        self.assertIsNotNone(resultado)
        self.assertTrue(resultado.composicao)
        logging.info(f"
[OK] Funciona sem PuLP: {resultado.composicao}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
