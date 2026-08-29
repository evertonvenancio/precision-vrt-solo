"""
Testes unitarios para o sistema de Guardrails (Seguranca Juridica e Agronomica).

Executar com pytest:
    pytest tests/test_guardrails.py -v

Ou com cobertura:
    pytest tests/test_guardrails.py -v --cov=core.guardrails --cov=schemas.guardrail --cov=config.guardrails_rules
"""

import pytest

import sys
sys.path.insert(0, r"C:\precision_vrt_solo")

from schemas.guardrail import (
    DadosAmostra,
    GuardrailResult,
    GuardrailReport,
    SeveridadeGuardrail,
)
from config.guardrails_rules import (
    REGRAS_PADRAO,
    RegraGuardrail,
    TipoRegra,
    AcaoRegra,
    get_regra,
    get_regras_por_tipo,
    get_regras_ativas,
    criar_config_customizada,
)
from core.guardrails import (
    GuardrailValidator,
    validar_prescricao,
)


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def amostra_normal():
    """Amostra de solo dentro dos parametros normais."""
    return DadosAmostra(
        ph=5.5,
        fosforo_mg=15.0,
        potassio_mg=80.0,
        calcio_cmol=3.0,
        magnesio_cmol=1.0,
        argila_pct=35.0,
        ctc=10.0,
        zona_id="Z1",
        amostra_id="A001",
    )


@pytest.fixture
def amostra_p_alto():
    """Amostra com fosforo muito alto (risco ambiental)."""
    return DadosAmostra(
        ph=5.8,
        fosforo_mg=50.0,
        potassio_mg=80.0,
        calcio_cmol=3.0,
        magnesio_cmol=1.0,
        argila_pct=35.0,
        ctc=10.0,
        zona_id="Z2",
    )


@pytest.fixture
def amostra_ph_alto():
    """Amostra com pH alto (calagem bloqueada)."""
    return DadosAmostra(
        ph=7.2,
        fosforo_mg=15.0,
        potassio_mg=80.0,
        calcio_cmol=5.0,
        magnesio_cmol=2.0,
        argila_pct=35.0,
        ctc=15.0,
        zona_id="Z3",
    )


@pytest.fixture
def amostra_v_alto():
    """Amostra com saturacao por bases alta."""
    return DadosAmostra(
        ph=6.2,
        fosforo_mg=15.0,
        potassio_mg=80.0,
        calcio_cmol=6.0,
        magnesio_cmol=2.0,
        argila_pct=35.0,
        ctc=10.0,  # V% = (6+2+0.2)/10 * 100 = 82%
        zona_id="Z4",
    )


@pytest.fixture
def amostra_k_antagonismo():
    """Amostra com relacao K/(Ca+Mg) alta."""
    return DadosAmostra(
        ph=5.5,
        fosforo_mg=15.0,
        potassio_mg=500.0,  # K alto
        calcio_cmol=1.0,    # Ca baixo
        magnesio_cmol=0.5,  # Mg baixo
        argila_pct=35.0,
        zona_id="Z5",
    )


@pytest.fixture
def amostra_erro_lab():
    """Amostra com erro de laboratorio (pH impossivel)."""
    return DadosAmostra(
        ph=50.0,
        fosforo_mg=15.0,
        potassio_mg=80.0,
        calcio_cmol=3.0,
        magnesio_cmol=1.0,
        argila_pct=35.0,
        zona_id="Z6",
    )


@pytest.fixture
def validator():
    """Instancia padrao do validador."""
    return GuardrailValidator(rt_id=1)


# ============================================================
# TESTES: schemas/guardrail.py
# ============================================================

class TestDadosAmostra:
    """Testes para o modelo de dados de amostra."""

    def test_criacao_basica(self):
        """Deve criar amostra com dados minimos."""
        amostra = DadosAmostra(
            ph=5.5,
            fosforo_mg=15.0,
            potassio_mg=80.0,
            calcio_cmol=3.0,
            magnesio_cmol=1.0,
            argila_pct=35.0,
        )
        assert amostra.ph == 5.5
        assert amostra.fosforo_mg == 15.0

    def test_saturacao_bases_calculada(self):
        """Deve calcular saturacao por bases corretamente."""
        amostra = DadosAmostra(
            ph=5.5,
            fosforo_mg=15.0,
            potassio_mg=78.0,  # ~0.2 cmolc/dm3
            calcio_cmol=3.0,
            magnesio_cmol=1.0,
            argila_pct=35.0,
            ctc=10.0,
        )
        v = amostra.saturacao_bases
        assert v is not None
        # (3.0 + 1.0 + 0.2) / 10.0 * 100 = 42%
        assert 40.0 < v < 45.0

    def test_saturacao_bases_usa_v_pct(self):
        """Deve usar v_pct quando ctc nao disponivel."""
        amostra = DadosAmostra(
            ph=5.5,
            fosforo_mg=15.0,
            potassio_mg=80.0,
            calcio_cmol=3.0,
            magnesio_cmol=1.0,
            argila_pct=35.0,
            v_pct=60.0,
        )
        assert amostra.saturacao_bases == 60.0

    def test_relacao_k_ca_mg(self):
        """Deve calcular relacao K/(Ca+Mg)."""
        amostra = DadosAmostra(
            ph=5.5,
            fosforo_mg=15.0,
            potassio_mg=390.0,  # 1.0 cmolc/dm3
            calcio_cmol=2.0,
            magnesio_cmol=1.0,
            argila_pct=35.0,
        )
        rel = amostra.relacao_k_ca_mg
        assert rel is not None
        assert abs(rel - (1.0 / 3.0)) < 0.01

    def test_relacao_k_ca_mg_none_quando_ca_mg_zero(self):
        """Deve retornar None quando Ca+Mg = 0."""
        amostra = DadosAmostra(
            ph=5.5,
            fosforo_mg=15.0,
            potassio_mg=80.0,
            calcio_cmol=0.0,
            magnesio_cmol=0.0,
            argila_pct=35.0,
        )
        assert amostra.relacao_k_ca_mg is None

    def test_soma_bases(self):
        """Deve calcular soma de bases."""
        amostra = DadosAmostra(
            ph=5.5,
            fosforo_mg=78.0,  # ~0.2 cmolc
            calcio_cmol=3.0,
            magnesio_cmol=1.0,
            argila_pct=35.0,
        )
        assert abs(amostra.soma_bases - 4.2) < 0.1

    def test_validacao_ph_limite(self):
        """Deve rejeitar pH fora do intervalo 0-14."""
        with pytest.raises(ValueError):
            DadosAmostra(
                ph=15.0,
                fosforo_mg=15.0,
                potassio_mg=80.0,
                calcio_cmol=3.0,
                magnesio_cmol=1.0,
                argila_pct=35.0,
            )

    def test_validacao_argila_limite(self):
        """Deve rejeitar argila > 100%."""
        with pytest.raises(ValueError):
            DadosAmostra(
                ph=5.5,
                fosforo_mg=15.0,
                potassio_mg=80.0,
                calcio_cmol=3.0,
                magnesio_cmol=1.0,
                argila_pct=101.0,
            )

    def test_to_dict(self):
        """Deve serializar para dict."""
        amostra = DadosAmostra(
            ph=5.5,
            fosforo_mg=15.0,
            potassio_mg=80.0,
            calcio_cmol=3.0,
            magnesio_cmol=1.0,
            argila_pct=35.0,
        )
        d = amostra.to_dict()
        assert "ph" in d
        assert d["ph"] == 5.5


class TestGuardrailResult:
    """Testes para o modelo de resultado de guardrail."""

    def test_criacao(self):
        """Deve criar resultado basico."""
        r = GuardrailResult(
            nutriente_afetado="P2O5",
            severidade=SeveridadeGuardrail.BLOCK,
            mensagem="P muito alto",
            regra_id="ENV_P_MAX",
        )
        assert r.nutriente_afetado == "P2O5"
        assert r.is_bloqueante()
        assert not r.is_warning()

    def test_nutriente_normalizado_maiusculas(self):
        """Deve normalizar nutriente para maiusculas."""
        r = GuardrailResult(
            nutriente_afetado="p2o5",
            severidade=SeveridadeGuardrail.BLOCK,
            mensagem="teste",
            regra_id="TESTE",
        )
        assert r.nutriente_afetado == "P2O5"

    def test_to_dict(self):
        """Deve serializar para dict."""
        r = GuardrailResult(
            nutriente_afetado="P2O5",
            severidade=SeveridadeGuardrail.WARNING,
            mensagem="Alerta",
            regra_id="TESTE",
            valor_atual=45.0,
            valor_limite=40.0,
        )
        d = r.to_dict()
        assert d["nutriente_afetado"] == "P2O5"
        assert d["valor_atual"] == 45.0


class TestGuardrailReport:
    """Testes para o relatorio de guardrails."""

    def test_criacao_vazia(self):
        """Deve criar relatorio vazio com status APROVADO."""
        report = GuardrailReport(prescricao_id=1)
        assert report.status_geral == "APROVADO"
        assert len(report.resultados) == 0

    def test_adicionar_block_muda_status(self):
        """Adicionar BLOCK deve mudar status para BLOQUEADO."""
        report = GuardrailReport(prescricao_id=1)
        report.adicionar_resultado(GuardrailResult(
            nutriente_afetado="P2O5",
            severidade=SeveridadeGuardrail.BLOCK,
            mensagem="Bloqueio",
            regra_id="TESTE",
        ))
        assert report.status_geral == "BLOQUEADO"
        assert "P2O5" in report.nutrientes_bloqueados

    def test_adicionar_warning_muda_status(self):
        """Adicionar WARNING deve mudar status para APROVADO_COM_RESSALVAS."""
        report = GuardrailReport(prescricao_id=1)
        report.adicionar_resultado(GuardrailResult(
            nutriente_afetado="K2O",
            severidade=SeveridadeGuardrail.WARNING,
            mensagem="Warning",
            regra_id="TESTE",
        ))
        assert report.status_geral == "APROVADO_COM_RESSALVAS"
        assert "K2O" in report.nutrientes_com_warning

    def test_tem_bloqueio(self):
        """Deve detectar bloqueio corretamente."""
        report = GuardrailReport(prescricao_id=1)
        report.adicionar_resultado(GuardrailResult(
            nutriente_afetado="P2O5",
            severidade=SeveridadeGuardrail.BLOCK,
            mensagem="Bloqueio",
            regra_id="TESTE",
        ))
        assert report.tem_bloqueio()
        assert report.tem_bloqueio("P2O5")
        assert not report.tem_bloqueio("K2O")

    def test_tem_warning(self):
        """Deve detectar warning corretamente."""
        report = GuardrailReport(prescricao_id=1)
        report.adicionar_resultado(GuardrailResult(
            nutriente_afetado="K2O",
            severidade=SeveridadeGuardrail.WARNING,
            mensagem="Warning",
            regra_id="TESTE",
        ))
        assert report.tem_warning()
        assert report.tem_warning("K2O")
        assert not report.tem_warning("P2O5")

    def test_get_por_severidade(self):
        """Deve filtrar por severidade."""
        report = GuardrailReport(prescricao_id=1)
        report.adicionar_resultado(GuardrailResult(
            nutriente_afetado="P2O5",
            severidade=SeveridadeGuardrail.BLOCK,
            mensagem="Bloqueio",
            regra_id="TESTE1",
        ))
        report.adicionar_resultado(GuardrailResult(
            nutriente_afetado="K2O",
            severidade=SeveridadeGuardrail.WARNING,
            mensagem="Warning",
            regra_id="TESTE2",
        ))
        blocks = report.get_por_severidade(SeveridadeGuardrail.BLOCK)
        assert len(blocks) == 1
        assert blocks[0].nutriente_afetado == "P2O5"

    def test_get_por_nutriente(self):
        """Deve filtrar por nutriente."""
        report = GuardrailReport(prescricao_id=1)
        report.adicionar_resultado(GuardrailResult(
            nutriente_afetado="P2O5",
            severidade=SeveridadeGuardrail.BLOCK,
            mensagem="Bloqueio",
            regra_id="TESTE",
        ))
        resultados = report.get_por_nutriente("P2O5")
        assert len(resultados) == 1

    def test_nutrientes_liberados(self):
        """Deve listar nutrientes sem bloqueio."""
        report = GuardrailReport(prescricao_id=1)
        report.adicionar_resultado(GuardrailResult(
            nutriente_afetado="P2O5",
            severidade=SeveridadeGuardrail.BLOCK,
            mensagem="Bloqueio",
            regra_id="TESTE",
        ))
        report.adicionar_resultado(GuardrailResult(
            nutriente_afetado="K2O",
            severidade=SeveridadeGuardrail.WARNING,
            mensagem="Warning",
            regra_id="TESTE2",
        ))
        liberados = report.nutrientes_liberados()
        assert "P2O5" not in liberados
        assert "K2O" in liberados  # WARNING nao bloqueia

    def test_resumo_texto(self):
        """Deve gerar resumo textual."""
        report = GuardrailReport(prescricao_id=1)
        report.adicionar_resultado(GuardrailResult(
            nutriente_afetado="P2O5",
            severidade=SeveridadeGuardrail.BLOCK,
            mensagem="Bloqueio",
            regra_id="TESTE",
        ))
        resumo = report.resumo_texto()
        assert "BLOQUEADO" in resumo
        assert "P2O5" in resumo

    def test_to_dict(self):
        """Deve serializar para dict."""
        report = GuardrailReport(prescricao_id=1)
        d = report.to_dict()
        assert "prescricao_id" in d
        assert "status_geral" in d


# ============================================================
# TESTES: config/guardrails_rules.py
# ============================================================

class TestRegrasConfiguracao:
    """Testes para configuracao de regras."""

    def test_regras_padrao_existem(self):
        """Deve ter regras padrao configuradas."""
        assert len(REGRAS_PADRAO) > 0
        assert "ENV_P_MAX" in REGRAS_PADRAO
        assert "SAT_BASES_BLOCK" in REGRAS_PADRAO
        assert "PH_ALTO_BLOCK" in REGRAS_PADRAO

    def test_get_regra_existente(self):
        """Deve retornar regra existente."""
        regra = get_regra("ENV_P_MAX")
        assert regra is not None
        assert regra.regra_id == "ENV_P_MAX"
        assert regra.tipo == TipoRegra.AMBIENTAL

    def test_get_regra_inexistente(self):
        """Deve retornar None para regra inexistente."""
        assert get_regra("INEXISTENTE") is None

    def test_get_regras_por_tipo(self):
        """Deve filtrar regras por tipo."""
        ambientais = get_regras_por_tipo(TipoRegra.AMBIENTAL)
        assert len(ambientais) > 0
        for r in ambientais:
            assert r.tipo == TipoRegra.AMBIENTAL

    def test_get_regras_ativas(self):
        """Deve retornar apenas regras ativas."""
        ativas = get_regras_ativas()
        assert len(ativas) > 0
        for r in ativas:
            assert r.ativa is True

    def test_regra_avaliar_maior(self):
        """Deve avaliar operador > corretamente."""
        regra = get_regra("ENV_P_MAX")
        assert regra.avaliar(50.0) is True   # 50 > 40
        assert regra.avaliar(40.0) is False  # 40 > 40 = False
        assert regra.avaliar(30.0) is False  # 30 > 40 = False

    def test_regra_avaliar_menor(self):
        """Deve avaliar operador < corretamente."""
        regra = get_regra("PH_BAIXO_BLOCK")
        assert regra.avaliar(4.0) is True    # 4 < 4.5
        assert regra.avaliar(4.5) is False  # 4.5 < 4.5 = False
        assert regra.avaliar(5.0) is False  # 5 < 4.5 = False

    def test_regra_formatar_mensagem(self):
        """Deve formatar mensagem com valor."""
        regra = get_regra("ENV_P_MAX")
        msg = regra.formatar_mensagem(50.0)
        assert "50.00" in msg
        assert "40.00" in msg

    def test_criar_config_customizada(self):
        """Deve criar configuracao customizada."""
        overrides = {
            "ENV_P_MAX": {"limite": 35.0, "acao": AcaoRegra.WARNING},
        }
        custom = criar_config_customizada(overrides)
        assert custom["ENV_P_MAX"].limite == 35.0
        assert custom["ENV_P_MAX"].acao == AcaoRegra.WARNING
        # Outras regras devem permanecer inalteradas
        assert custom["SAT_BASES_BLOCK"].limite == 70.0

    def test_regra_validacao_operador(self):
        """Deve rejeitar operador invalido."""
        with pytest.raises(ValueError, match="Operador"):
            RegraGuardrail(
                regra_id="TESTE",
                tipo=TipoRegra.FISICO,
                nutriente_afetado="GERAL",
                acao=AcaoRegra.BLOCK,
                limite=10.0,
                operador="invalido",
                mensagem="teste",
            )


# ============================================================
# TESTES: core/guardrails.py - Validador
# ============================================================

class TestGuardrailValidator:
    """Testes para o motor de validacao."""

    def test_inicializacao(self):
        """Deve inicializar com regras padrao."""
        v = GuardrailValidator(rt_id=1)
        assert v._rt_id == 1

    def test_validar_amostra_normal(self, validator, amostra_normal):
        """Amostra normal nao deve gerar bloqueios."""
        relatorio = validator.validar(amostra_normal, prescricao_id=1)
        assert relatorio.status_geral == "APROVADO"
        assert not relatorio.tem_bloqueio()
        assert relatorio.prescricao_id == 1

    def test_validar_p_alto_bloqueia_p2o5(self, validator, amostra_p_alto):
        """Fosforo alto deve bloquear aplicacao de P2O5."""
        relatorio = validator.validar(amostra_p_alto, prescricao_id=2)
        assert relatorio.tem_bloqueio("P2O5")
        assert relatorio.status_geral == "BLOQUEADO"
        assert any("eutrofizacao" in r.mensagem.lower() or "CONAMA" in r.mensagem
                   for r in relatorio.resultados)

    def test_validar_ph_alto_bloqueia_cao(self, validator, amostra_ph_alto):
        """pH alto deve bloquear calagem (CaO)."""
        relatorio = validator.validar(amostra_ph_alto, prescricao_id=3)
        assert relatorio.tem_bloqueio("CaO")
        assert relatorio.status_geral == "BLOQUEADO"

    def test_validar_ph_alto_warning_geral(self, validator, amostra_ph_alto):
        """pH > 7.0 deve gerar warning geral sobre micronutrientes."""
        relatorio = validator.validar(amostra_ph_alto, prescricao_id=3)
        assert relatorio.tem_warning("GERAL")

    def test_validar_v_alto_bloqueia_cao(self, validator, amostra_v_alto):
        """V% alto deve bloquear calagem."""
        relatorio = validator.validar(amostra_v_alto, prescricao_id=4)
        assert relatorio.tem_bloqueio("CaO")
        # V% = (6+2+0.2)/10 * 100 = 82% > 70%
        assert relatorio.status_geral == "BLOQUEADO"

    def test_validar_k_antagonismo_bloqueia_k2o(self, validator, amostra_k_antagonismo):
        """Relacao K/(Ca+Mg) alta deve bloquear K2O."""
        relatorio = validator.validar(amostra_k_antagonismo, prescricao_id=5)
        assert relatorio.tem_bloqueio("K2O")
        assert relatorio.status_geral == "BLOQUEADO"

    def test_validar_erro_lab_bloqueia_geral(self, validator, amostra_erro_lab):
        """Erro de laboratorio deve bloquear calculo geral."""
        relatorio = validator.validar(amostra_erro_lab, prescricao_id=6)
        assert relatorio.tem_bloqueio("GERAL")
        assert any("ERRO DE LABORATORIO" in r.mensagem for r in relatorio.resultados)

    def test_validar_sem_rt_bloqueia(self, amostra_normal):
        """Sem RT vinculado deve bloquear."""
        v = GuardrailValidator(rt_id=None)
        relatorio = v.validar(amostra_normal, prescricao_id=7)
        assert relatorio.tem_bloqueio("GERAL")
        assert any("Responsavel Tecnico" in r.mensagem for r in relatorio.resultados)

    def test_nutrientes_permitidos(self, validator, amostra_p_alto):
        """Deve listar nutrientes permitidos corretamente."""
        relatorio = validator.validar(amostra_p_alto, prescricao_id=2)
        permitidos = validator.get_nutrientes_permitidos(relatorio)
        assert "P2O5" not in permitidos  # Bloqueado
        assert "N" in permitidos  # Deve estar liberado

    def test_get_resumo_bloqueios(self, validator, amostra_p_alto):
        """Deve gerar resumo de bloqueios por nutriente."""
        relatorio = validator.validar(amostra_p_alto, prescricao_id=2)
        resumo = validator.get_resumo_bloqueios(relatorio)
        assert "P2O5" in resumo
        assert len(resumo["P2O5"]) > 0

    def test_aplicar_justificativa(self, validator, amostra_v_alto):
        """Deve permitir aplicar justificativa em warning."""
        # Criar relatorio com warning
        relatorio = GuardrailReport(prescricao_id=8)
        relatorio.adicionar_resultado(GuardrailResult(
            nutriente_afetado="K2O",
            severidade=SeveridadeGuardrail.WARNING,
            mensagem="Warning teste",
            regra_id="TESTE",
        ))
        ok = validator.aplicar_justificativa(relatorio, "K2O", "Justificativa tecnica", 1)
        assert ok is True
        resultados = relatorio.get_por_nutriente("K2O")
        assert resultados[0].justificativa == "Justificativa tecnica"

    def test_aplicar_justificativa_nao_encontrada(self, validator):
        """Deve retornar False quando warning nao encontrado."""
        relatorio = GuardrailReport(prescricao_id=9)
        ok = validator.aplicar_justificativa(relatorio, "K2O", "Teste", 1)
        assert ok is False

    def test_validar_multiplas_amostras(self, validator):
        """Deve validar multiplas amostras."""
        amostras = [
            (DadosAmostra(ph=5.5, fosforo_mg=15, potassio_mg=80, calcio_cmol=3, magnesio_cmol=1, argila_pct=35), 1, "Z1"),
            (DadosAmostra(ph=7.2, fosforo_mg=15, potassio_mg=80, calcio_cmol=5, magnesio_cmol=2, argila_pct=35), 2, "Z2"),
        ]
        relatorios = validator.validar_multiplas_amostras(amostras)
        assert len(relatorios) == 2
        assert relatorios[0].status_geral == "APROVADO"
        assert relatorios[1].status_geral == "BLOQUEADO"

    def test_validar_multiplas_amostras_erro(self, validator):
        """Deve lidar com erro em uma amostra sem parar todas."""
        # Forcar erro passando None (invalido)
        amostras = [
            (None, 1, "Z1"),  # Isso vai falhar
        ]
        relatorios = validator.validar_multiplas_amostras(amostras)
        assert len(relatorios) == 1
        assert relatorios[0].status_geral == "BLOQUEADO"

    def test_exportar_relatorio_json(self, validator, amostra_normal):
        """Deve exportar relatorio para JSON."""
        relatorio = validator.validar(amostra_normal, prescricao_id=1)
        json_str = validator.exportar_relatorio_json(relatorio)
        assert "APROVADO" in json_str
        assert "prescricao_id" in json_str

    def test_funcao_convenience(self, amostra_p_alto):
        """Funcao convenience deve funcionar."""
        relatorio = validar_prescricao(
            amostra=amostra_p_alto,
            prescricao_id=10,
            zona_id="Z10",
            rt_id=1,
        )
        assert relatorio.prescricao_id == 10
        assert relatorio.zona_id == "Z10"
        assert relatorio.tem_bloqueio("P2O5")

    def test_regras_customizadas(self, amostra_p_alto):
        """Deve usar regras customizadas."""
        overrides = {
            "ENV_P_MAX": {"limite": 60.0},  # Aumentar limite
        }
        regras_custom = criar_config_customizada(overrides)
        v = GuardrailValidator(regras=regras_custom, rt_id=1)
        relatorio = v.validar(amostra_p_alto, prescricao_id=11)
        # Com limite 60, P=50 nao deve mais bloquear
        assert not relatorio.tem_bloqueio("P2O5")

    def test_combinacao_multiplos_bloqueios(self, validator):
        """Deve detectar multiplos bloqueios simultaneos."""
        amostra = DadosAmostra(
            ph=7.5,  # Bloqueia CaO (pH > 6.5)
            fosforo_mg=50.0,  # Bloqueia P2O5 (P > 40)
            potassio_mg=500.0,  # Bloqueia K2O (antagonismo)
            calcio_cmol=1.0,
            magnesio_cmol=0.5,
            argila_pct=35.0,
        )
        relatorio = validator.validar(amostra, prescricao_id=12)
        assert relatorio.tem_bloqueio("CaO")
        assert relatorio.tem_bloqueio("P2O5")
        assert relatorio.tem_bloqueio("K2O")
        assert relatorio.status_geral == "BLOQUEADO"
        assert len(relatorio.nutrientes_bloqueados) >= 3

    def test_info_ph_baixo(self, validator):
        """pH muito baixo deve gerar INFO."""
        amostra = DadosAmostra(
            ph=4.0,
            fosforo_mg=15.0,
            potassio_mg=80.0,
            calcio_cmol=1.0,
            magnesio_cmol=0.5,
            argila_pct=35.0,
        )
        relatorio = validator.validar(amostra, prescricao_id=13)
        infos = relatorio.get_por_severidade(SeveridadeGuardrail.INFO)
        assert len(infos) > 0
        assert any("pH muito baixo" in i.mensagem for i in infos)

    def test_calculo_saturacao_bases(self, validator):
        """Deve calcular V% corretamente quando CTC disponivel."""
        amostra = DadosAmostra(
            ph=6.0,
            fosforo_mg=15.0,
            potassio_mg=78.0,  # ~0.2 cmolc
            calcio_cmol=4.0,
            magnesio_cmol=1.0,
            argila_pct=35.0,
            ctc=10.0,
        )
        # V% = (4.0 + 1.0 + 0.2) / 10.0 * 100 = 52%
        assert amostra.saturacao_bases is not None
        assert 51.0 < amostra.saturacao_bases < 53.0

    def test_relatorio_com_zona_id(self, validator, amostra_normal):
        """Relatorio deve preservar zona_id."""
        relatorio = validator.validar(amostra_normal, prescricao_id=1, zona_id="ZONA_TESTE")
        assert relatorio.zona_id == "ZONA_TESTE"


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

