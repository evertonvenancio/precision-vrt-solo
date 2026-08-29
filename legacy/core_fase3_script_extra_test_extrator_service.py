"""
Testes unitários para o serviço de extrator de solução.

Testa:
- Validação de leituras (limites de CE)
- Análise de tendências
- Diagnóstico nutricional
- Motor de recomendações de sais
- Mapeamento de CSV
"""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock

from config.sais_solucao import verificar_compatibilidade, calcular_quantidade_sal
from models.extrator import CurvaNutritiva, LeituraExtrator, PontoExtrator, get_limite_ce
from schemas.extrator import StatusNutriente, TendenciaNutriente
from services.extrator_service import (
    ExtratorService,
    DiagnosticoNutriente,
    mapear_colunas_csv,
)


# ===================== FIXTURES =====================

@pytest.fixture
def ponto_mock() -> PontoExtrator:
    """Cria um ponto de monitoramento mock."""
    ponto = PontoExtrator(
        id=1,
        codigo="EXT-001",
        nome="Ponto Teste",
        latitude=-23.5,
        longitude=-46.6,
        profundidade_cm=30,
        cultura="tomate",
        fase_fenologica="frutificacao",
        eh_hidroponia=False,
    )
    return ponto


@pytest.fixture
def curva_tomate() -> CurvaNutritiva:
    """Cria curva nutritiva para tomate em frutificação."""
    return CurvaNutritiva(
        id=1,
        cultura="tomate",
        fase_fenologica="frutificacao",
        ph_min=6.0,
        ph_max=6.5,
        ce_min_ds_m=2.0,
        ce_max_ds_m=3.0,
        no3_min_mg_L=150.0,
        no3_max_mg_L=250.0,
        k_min_mg_L=200.0,
        k_max_mg_L=300.0,
        ca_min_mg_L=150.0,
        ca_max_mg_L=200.0,
        mg_min_mg_L=40.0,
        mg_max_mg_L=60.0,
        po4_min_mg_L=30.0,
        po4_max_mg_L=50.0,
        so4_min_mg_L=50.0,
        so4_max_mg_L=100.0,
        b_min_mg_L=0.3,
        b_max_mg_L=0.6,
        fe_min_mg_L=1.0,
        fe_max_mg_L=2.0,
        mn_min_mg_L=0.5,
        mn_max_mg_L=1.0,
        zn_min_mg_L=0.5,
        zn_max_mg_L=1.0,
        cu_min_mg_L=0.02,
        cu_max_mg_L=0.10,
    )


@pytest.fixture
def leitura_completa(ponto_mock: PontoExtrator) -> LeituraExtrator:
    """Cria leitura com todos os nutrientes preenchidos."""
    return LeituraExtrator(
        id=1,
        ponto_id=ponto_mock.id,
        ponto=ponto_mock,
        data_leitura=date.today(),
        ph=6.2,
        ce_ds_m=2.5,
        no3_mg_L=180.0,
        k_mg_L=250.0,
        ca_mg_L=170.0,
        mg_mg_L=50.0,
        po4_mg_L=40.0,
        so4_mg_L=75.0,
        b_mg_L=0.4,
        fe_mg_L=1.5,
        mn_mg_L=0.7,
        zn_mg_L=0.8,
        cu_mg_L=0.05,
    )


@pytest.fixture
def leitura_deficiente(ponto_mock: PontoExtrator) -> LeituraExtrator:
    """Cria leitura com deficiências de N e K."""
    return LeituraExtrator(
        id=2,
        ponto_id=ponto_mock.id,
        ponto=ponto_mock,
        data_leitura=date.today(),
        ph=6.0,
        ce_ds_m=1.8,
        no3_mg_L=80.0,  # Deficiente (< 150)
        k_mg_L=120.0,   # Deficiente (< 200)
        ca_mg_L=170.0,
        mg_mg_L=50.0,
        po4_mg_L=40.0,
        so4_mg_L=75.0,
    )


@pytest.fixture
def leitura_excesso(ponto_mock: PontoExtrator) -> LeituraExtrator:
    """Cria leitura com excesso de K."""
    return LeituraExtrator(
        id=3,
        ponto_id=ponto_mock.id,
        ponto=ponto_mock,
        data_leitura=date.today(),
        ph=6.5,
        ce_ds_m=4.5,  # Acima do limite
        no3_mg_L=200.0,
        k_mg_L=400.0,  # Excesso (> 300)
        ca_mg_L=170.0,
        mg_mg_L=50.0,
        po4_mg_L=40.0,
        so4_mg_L=75.0,
    )


@pytest.fixture
def historico_leituras(ponto_mock: PontoExtrator) -> list[LeituraExtrator]:
    """Cria histórico de leituras para análise de tendência."""
    hoje = date.today()
    return [
        LeituraExtrator(
            id=4,
            ponto_id=ponto_mock.id,
            ponto=ponto_mock,
            data_leitura=hoje,
            no3_mg_L=150.0,  # Atual
            k_mg_L=280.0,
        ),
        LeituraExtrator(
            id=5,
            ponto_id=ponto_mock.id,
            ponto=ponto_mock,
            data_leitura=hoje - timedelta(days=7),
            no3_mg_L=170.0,  # Semana passada
            k_mg_L=260.0,
        ),
        LeituraExtrator(
            id=6,
            ponto_id=ponto_mock.id,
            ponto=ponto_mock,
            data_leitura=hoje - timedelta(days=14),
            no3_mg_L=200.0,  # Duas semanas atrás
            k_mg_L=240.0,
        ),
    ]


# ===================== TESTES DE VALIDAÇÃO =====================

class TestValidacaoLeitura:
    """Testa validação de leituras."""

    def test_validacao_ce_dentro_limite(self, leitura_completa: LeituraExtrator):
        """CE dentro do limite deve passar sem alertas críticos."""
        service = ExtratorService(session=MagicMock())
        valida, alertas = service.validar_leitura(leitura_completa, "tomate")

        assert valida is True
        # Pode ter alertas informativos, mas não deve invalidar
        assert not any("ALERTA" in a and "CE" in a for a in alertas)

    def test_validacao_ce_acima_limite(self, leitura_excesso: LeituraExtrator):
        """CE acima do limite deve gerar alerta."""
        service = ExtratorService(session=MagicMock())
        valida, alertas = service.validar_leitura(leitura_excesso, "tomate")

        # Limite para tomate é 3.0 dS/m
        assert leitura_excesso.ce_ds_m > 3.0
        assert any("ALERTA" in a and "CE" in a for a in alertas)

    def test_validacao_ph_baixo(self, ponto_mock: PontoExtrator):
        """pH muito baixo deve alertar sobre toxicidade de Al."""
        leitura = LeituraExtrator(
            id=10,
            ponto_id=ponto_mock.id,
            ponto=ponto_mock,
            data_leitura=date.today(),
            ph=4.0,  # Muito baixo
            ce_ds_m=2.0,
        )

        service = ExtratorService(session=MagicMock())
        valida, alertas = service.validar_leitura(leitura, "tomate")

        assert any("pH" in a and "baixo" in a.lower() for a in alertas)

    def test_validacao_ph_alto(self, ponto_mock: PontoExtrator):
        """pH alto deve alertar sobre micronutrientes."""
        leitura = LeituraExtrator(
            id=11,
            ponto_id=ponto_mock.id,
            ponto=ponto_mock,
            data_leitura=date.today(),
            ph=8.0,  # Alto
            ce_ds_m=2.0,
        )

        service = ExtratorService(session=MagicMock())
        valida, alertas = service.validar_leitura(leitura, "tomate")

        assert any("pH" in a and "alto" in a.lower() for a in alertas)


# ===================== TESTES DE TENDÊNCIAS =====================

class TestAnaliseTendencias:
    """Testa análise de tendências de nutrientes."""

    def test_tendencia_diminuindo(
        self,
        historico_leituras: list[LeituraExtrator]
    ):
        """NO3 diminuindo ao longo do tempo deve ser detectado."""
        service = ExtratorService(session=MagicMock())
        tendencias = service.analisar_tendencias(historico_leituras, ["no3"])

        # Encontrar tendência de NO3
        no3_tend = next(t for t in tendencias if t.nutriente == "no3")

        assert no3_tend.tendencia == TendenciaNutriente.DIMINUINDO
        assert no3_tend.variacao_percentual is not None
        assert no3_tend.variacao_percentual < 0
        assert no3_tend.alerta is True

    def test_tendencia_aumentando(self, ponto_mock: PontoExtrator):
        """K aumentando ao longo do tempo deve ser detectado."""
        hoje = date.today()
        leituras = [
            LeituraExtrator(
                id=20, ponto_id=ponto_mock.id, ponto=ponto_mock,
                data_leitura=hoje, k_mg_L=300.0
            ),
            LeituraExtrator(
                id=21, ponto_id=ponto_mock.id, ponto=ponto_mock,
                data_leitura=hoje - timedelta(days=7), k_mg_L=250.0
            ),
        ]

        service = ExtratorService(session=MagicMock())
        tendencias = service.analisar_tendencias(leituras, ["k"])

        k_tend = next(t for t in tendencias if t.nutriente == "k")

        assert k_tend.tendencia == TendenciaNutriente.AUMENTANDO
        assert k_tend.variacao_percentual > 10

    def test_tendencia_estavel(self, ponto_mock: PontoExtrator):
        """Valores estáveis devem indicar tendência estável."""
        hoje = date.today()
        leituras = [
            LeituraExtrator(
                id=22, ponto_id=ponto_mock.id, ponto=ponto_mock,
                data_leitura=hoje, k_mg_L=250.0
            ),
            LeituraExtrator(
                id=23, ponto_id=ponto_mock.id, ponto=ponto_mock,
                data_leitura=hoje - timedelta(days=7), k_mg_L=255.0
            ),
        ]

        service = ExtratorService(session=MagicMock())
        tendencias = service.analisar_tendencias(leituras, ["k"])

        k_tend = next(t for t in tendencias if t.nutriente == "k")

        assert k_tend.tendencia == TendenciaNutriente.ESTAVEL

    def test_sem_historico(self, ponto_mock: PontoExtrator):
        """Com menos de 2 leituras, deve retornar sem histórico."""
        leitura = LeituraExtrator(
            id=24, ponto_id=ponto_mock.id, ponto=ponto_mock,
            data_leitura=date.today(), k_mg_L=250.0
        )

        service = ExtratorService(session=MagicMock())
        tendencias = service.analisar_tendencias([leitura], ["k"])

        k_tend = next(t for t in tendencias if t.nutriente == "k")

        assert k_tend.tendencia == TendenciaNutriente.SEM_HISTORICO


# ===================== TESTES DE DIAGNÓSTICO =====================

class TestDiagnosticoNutriente:
    """Testa diagnóstico individual de nutrientes."""

    def test_diagnostico_adequado(self):
        """Valor dentro da faixa deve ser adequado."""
        service = ExtratorService(session=MagicMock())

        diagnostico = service.diagnosticar_nutriente(
            valor_atual=200.0,
            faixa_ideal=(150.0, 250.0),
            nutriente="no3",
        )

        assert diagnostico.status == StatusNutriente.ADEQUADO
        assert diagnostico.diferenca_mg_L is None

    def test_diagnostico_deficiente(self):
        """Valor abaixo do mínimo deve ser deficiente."""
        service = ExtratorService(session=MagicMock())

        diagnostico = service.diagnosticar_nutriente(
            valor_atual=100.0,
            faixa_ideal=(150.0, 250.0),
            nutriente="no3",
        )

        assert diagnostico.status == StatusNutriente.DEFICIENTE
        assert diagnostico.diferenca_mg_L == 50.0  # 150 - 100

    def test_diagnostico_excesso(self):
        """Valor acima do máximo deve ser excesso."""
        service = ExtratorService(session=MagicMock())

        diagnostico = service.diagnosticar_nutriente(
            valor_atual=300.0,
            faixa_ideal=(150.0, 250.0),
            nutriente="k",
        )

        assert diagnostico.status == StatusNutriente.EXCESSO
        assert diagnostico.diferenca_mg_L == 50.0  # 300 - 250

    def test_diagnostico_sem_dados(self):
        """Valor None deve retornar sem dados."""
        service = ExtratorService(session=MagicMock())

        diagnostico = service.diagnosticar_nutriente(
            valor_atual=None,
            faixa_ideal=(150.0, 250.0),
            nutriente="no3",
        )

        assert diagnostico.status == StatusNutriente.SEM_DADOS


# ===================== TESTES DE RECOMENDAÇÕES =====================

class TestRecomendacoesSais:
    """Testa motor de recomendações de sais."""

    def test_recomendacao_deficiencia_n(
        self,
        curva_tomate: CurvaNutritiva,
        leitura_deficiente: LeituraExtrator,
    ):
        """Deficiência de N deve recomendar fonte de N."""
        service = ExtratorService(session=MagicMock())

        # Criar diagnósticos
        diagnosticos = [
            DiagnosticoNutriente(
                nutriente="no3",
                valor_atual=80.0,
                unidade="mg/L",
                faixa_ideal=(150.0, 250.0),
                status=StatusNutriente.DEFICIENTE,
                percentual_ideal=40.0,
                diferenca_mg_L=70.0,  # Precisa de 70 mg/L
            ),
            DiagnosticoNutriente(
                nutriente="k",
                valor_atual=200.0,
                unidade="mg/L",
                faixa_ideal=(200.0, 300.0),
                status=StatusNutriente.ADEQUADO,
                percentual_ideal=50.0,
                diferenca_mg_L=None,
            ),
        ]

        recomendacoes = service.gerar_recomendacoes_sais(
            diagnosticos,
            ce_atual=1.8,
            ce_limite=3.0,
            volume_tanque_L=1000.0,
        )

        # Deve recomendar algum sal
        assert len(recomendacoes) > 0

        # Verificar que o sal recomendado contém N
        rec = recomendacoes[0]
        assert "n" in rec.nutrientes_fornecidos or "N" in str(rec.nome_comercial).upper()

    def test_recomendacao_limite_ce(
        self,
        curva_tomate: CurvaNutritiva,
    ):
        """Não deve recomendar sais que ultrapassem limite de CE."""
        service = ExtratorService(session=MagicMock())

        diagnosticos = [
            DiagnosticoNutriente(
                nutriente="no3",
                valor_atual=50.0,
                unidade="mg/L",
                faixa_ideal=(150.0, 250.0),
                status=StatusNutriente.DEFICIENTE,
                percentual_ideal=20.0,
                diferenca_mg_L=100.0,  # Grande deficiência
            ),
        ]

        # CE atual já alta, margem pequena
        recomendacoes = service.gerar_recomendacoes_sais(
            diagnosticos,
            ce_atual=2.8,
            ce_limite=3.0,  # Margem de apenas 0.2 dS/m
            volume_tanque_L=1000.0,
        )

        if recomendacoes:
            # CE esperada não deve ultrapassar margem
            assert recomendacoes[0].ce_esperada_dS_m <= 0.2


class TestCompatibilidadeSais:
    """Testa verificação de compatibilidade química."""

    def test_nitrato_calcio_incompativel(self):
        """Nitrato de cálcio deve ser incompatível com sulfatos."""
        resultado = verificar_compatibilidade([
            "nitrato_calcio",
            "sulfato_magnesio",
        ])

        assert resultado["compativel"] is False
        assert len(resultado["incompatibilidades"]) > 0

    def test_sais_compativeis(self):
        """Sais compatíveis devem passar."""
        resultado = verificar_compatibilidade([
            "nitrato_potassio",
            "mkp",
            "sulfato_magnesio",
        ])

        assert resultado["compativel"] is True
        assert len(resultado["incompatibilidades"]) == 0

    def test_sais_desconhecidos_ignorados(self):
        """Sais não cadastrados não devem causar erro."""
        resultado = verificar_compatibilidade([
            "sal_inexistente",
            "nitrato_potassio",
        ])

        # Não deve lançar erro
        assert isinstance(resultado, dict)


# ===================== TESTES DE MAPEAMENTO CSV =====================

class TestMapeamentoCSV:
    """Testa mapeamento inteligente de colunas CSV."""

    def test_mapeamento_portugues(self):
        """Deve mapear colunas em português."""
        colunas = ["data", "ce", "nitrato", "potassio", "calcio", "ph"]

        mapeamento = mapear_colunas_csv(colunas)

        assert "data" in mapeamento
        assert mapeamento["data"] == "data_leitura"
        assert mapeamento["ce"] == "ce_ds_m"
        assert mapeamento["nitrato"] == "no3_mg_L"
        assert mapeamento["potassio"] == "k_mg_L"

    def test_mapeamento_ingles(self):
        """Deve mapear colunas em inglês."""
        colunas = ["date", "ec", "nitrate", "potassium", "ph"]

        mapeamento = mapear_colunas_csv(colunas)

        assert mapeamento["date"] == "data_leitura"
        assert mapeamento["ec"] == "ce_ds_m"
        assert mapeamento["nitrate"] == "no3_mg_L"

    def test_mapeamento_case_insensitive(self):
        """Deve ignorar maiúsculas/minúsculas."""
        colunas = ["DATA", "CE_DS_M", "Nitrato", "PH"]

        mapeamento = mapear_colunas_csv(colunas)

        assert mapeamento["DATA"] == "data_leitura"
        assert mapeamento["CE_DS_M"] == "ce_ds_m"

    def test_mapeamento_colunas_desconhecidas(self):
        """Colunas não mapeadas devem ser ignoradas."""
        colunas = ["data", "coluna_x", "coluna_y", "k"]

        mapeamento = mapear_colunas_csv(colunas)

        assert "coluna_x" not in mapeamento
        assert "coluna_y" not in mapeamento
        assert "k" in mapeamento


# ===================== TESTES DE LIMITES DE CE =====================

class TestLimitesCE:
    """Testa limites de CE por cultura."""

    def test_limite_tomate(self):
        """Tomate deve ter limite de 3.0 dS/m."""
        assert get_limite_ce("tomate") == 3.0

    def test_limite_morango(self):
        """Morango deve ter limite de 1.5 dS/m."""
        assert get_limite_ce("morango") == 1.5

    def test_limite_hidroponia(self):
        """Hidroponia deve ter limite específico."""
        assert get_limite_ce("hidroponia_leituga") == 2.0

    def test_limite_default(self):
        """Cultura não cadastrada deve retornar default."""
        assert get_limite_ce("cultura_xyz") == 2.0


# ===================== TESTES DE CÁLCULO DE SAIS =====================

class TestCalculoQuantidadeSal:
    """Testa cálculo de quantidade de sais."""

    def test_calcular_quantidade_nitrato_potassio(self):
        """Deve calcular quantidade correta de nitrato de potássio."""
        # Nitrato de Potássio: 13% N, 46% K2O
        qtd_necessaria = calcular_quantidade_sal(
            "nitrato_potassio",
            {"n": 130.0},  # 130g de N
        )

        # 130g de N / 0.13 = 1000g de KNO3
        assert abs(qtd_necessaria - 1000.0) < 1.0

    def test_calcular_quantidade_mkp(self):
        """Deve calcular quantidade correta de MKP."""
        # MKP: 52% P2O5, 34% K2O
        qtd_necessaria = calcular_quantidade_sal(
            "mkp",
            {"p2o5": 520.0},  # 520g de P2O5
        )

        # 520g / 0.52 = 1000g
        assert abs(qtd_necessaria - 1000.0) < 1.0

    def test_calcular_sal_inexistente(self):
        """Sal inexistente deve lançar erro."""
        with pytest.raises(ValueError):
            calcular_quantidade_sal("sal_fantasia", {"n": 100.0})


# ===================== TESTES INTEGRAÇÃO MODELS =====================

class TestModels:
    """Testa propriedades dos modelos SQLAlchemy."""

    def test_repr_ponto(self, ponto_mock: PontoExtrator):
        """Testa representação string do ponto."""
        repr_str = repr(ponto_mock)
        assert "PontoExtrator" in repr_str
        assert "EXT-001" in repr_str

    def test_get_faixa_curva(self, curva_tomate: CurvaNutritiva):
        """Testa método get_faixa da curva nutritiva."""
        faixa_no3 = curva_tomate.get_faixa("no3")
        assert faixa_no3 == (150.0, 250.0)

        faixa_k = curva_tomate.get_faixa("k")
        assert faixa_k == (200.0, 300.0)

        faixa_inexistente = curva_tomate.get_faixa("xyz")
        assert faixa_inexistente == (0.0, 0.0)


# ===================== TESTES HELPER FUNCTIONS =====================

class TestHelperFunctions:
    """Testa funções auxiliares."""

    def test_observacoes_diagnostico(self):
        """Testa geração de observações textuais."""
        service = ExtratorService(session=MagicMock())

        macros = [
            DiagnosticoNutriente(
                nutriente="no3",
                valor_atual=80.0,
                unidade="mg/L",
                faixa_ideal=(150.0, 250.0),
                status=StatusNutriente.DEFICIENTE,
                percentual_ideal=40.0,
                diferenca_mg_L=70.0,
            ),
        ]

        micros = []

        obs = service._gerar_observacoes(
            macros, micros,
            alerta_ce=False,
            alerta_ph=False,
            nivel_risco="medio",
        )

        assert "NO3" in obs
        assert "Deficiência" in obs or "deficiência" in obs.lower()


# Execução: pytest tests/test_extrator_service.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
