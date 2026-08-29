"""
Testes unitários para o módulo de Compactação do Solo.

Executar com pytest:
    pytest tests/test_compactacao_service.py -v

Ou com cobertura:
    pytest tests/test_compactacao_service.py -v --cov=services.compactacao_service
"""

import pytest
import io
import csv
from unittest.mock import AsyncMock, MagicMock


# Ajustar path para importar módulos do projeto
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from schemas.compactacao import (
    CSVColumnMapping,
    ResumoEstatistico,
    FlagEscarificacao,
)
from services.compactacao_service import CompactacaoService
from models.compactacao import (
    AnaliseCompactacao,
)


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def csv_valido():
    """Retorna conteúdo binário de um CSV válido de penetrometria."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ponto_id", "latitude", "longitude", "rp_0_10", "rp_10_20", "rp_20_30", "rp_30_40"])
    # Ponto 1: Solo apto (baixa resistência)
    writer.writerow(["P001", "-22.1234", "-47.5678", "1.2", "1.5", "1.8", "1.9"])
    # Ponto 2: Restrição moderada
    writer.writerow(["P002", "-22.1240", "-47.5680", "2.1", "2.3", "2.4", "2.5"])
    # Ponto 3: Impedimento severo
    writer.writerow(["P003", "-22.1245", "-47.5685", "2.8", "3.2", "3.5", "3.8"])
    # Ponto 4: Misto (apto -> severo)
    writer.writerow(["P004", "-22.1250", "-47.5690", "1.5", "2.2", "2.7", "3.1"])
    return output.getvalue().encode("utf-8")


@pytest.fixture
def csv_sem_coordenadas():
    """CSV sem colunas de latitude/longitude."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ponto_id", "rp_0_10", "rp_10_20", "rp_20_30", "rp_30_40"])
    writer.writerow(["P001", "1.2", "1.5", "1.8", "1.9"])
    writer.writerow(["P002", "2.8", "3.2", "3.5", "3.8"])
    return output.getvalue().encode("utf-8")


@pytest.fixture
def csv_colunas_custom():
    """CSV com nomes de colunas customizados."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "lat", "lon", "rp0", "rp1", "rp2", "rp3"])
    writer.writerow(["A1", "-22.1", "-47.5", "1.5", "1.8", "2.0", "2.2"])
    writer.writerow(["A2", "-22.2", "-47.6", "3.0", "3.5", "4.0", "4.5"])
    return output.getvalue().encode("utf-8")


@pytest.fixture
def csv_vazio():
    """CSV vazio (apenas header)."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ponto_id", "rp_0_10", "rp_10_20"])
    return output.getvalue().encode("utf-8")


@pytest.fixture
def csv_invalido():
    """CSV com dados inválidos (resistência não numérica)."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ponto_id", "rp_0_10", "rp_10_20"])
    writer.writerow(["P001", "abc", "def"])
    return output.getvalue().encode("utf-8")


@pytest.fixture
def mock_db():
    """Mock de sessão assíncrona do SQLAlchemy."""
    db = AsyncMock()
    db.commit = AsyncMock()
    db.add = MagicMock()
    db.delete = AsyncMock()
    return db


@pytest.fixture
def service(mock_db):
    """Instância do serviço com banco mockado."""
    return CompactacaoService(mock_db)


@pytest.fixture
def mapeamento_padrao():
    """Mapeamento padrão de colunas."""
    return CSVColumnMapping()


@pytest.fixture
def mapeamento_custom():
    """Mapeamento customizado de colunas."""
    return CSVColumnMapping(
        coluna_ponto_id="id",
        coluna_latitude="lat",
        coluna_longitude="lon",
        colunas_profundidade={
            "0_10": "rp0",
            "10_20": "rp1",
            "20_30": "rp2",
            "30_40": "rp3",
        }
    )


# ============================================================
# TESTES: Leitura e Parse de CSV
# ============================================================

class TestLerCSV:
    """Testes para o método _ler_csv."""

    def test_ler_csv_valido(self, service, csv_valido, mapeamento_padrao):
        """Deve ler CSV válido e retornar DataFrame correto."""
        df = service._ler_csv(csv_valido, mapeamento_padrao)

        assert len(df) == 4
        assert "ponto_id" in df.columns
        assert "rp_0_10" in df.columns
        assert "latitude" in df.columns
        assert df["rp_0_10"].dtype == float

    def test_ler_csv_sem_coordenadas(self, service, csv_sem_coordenadas, mapeamento_padrao):
        """Deve ler CSV sem coordenadas corretamente."""
        df = service._ler_csv(csv_sem_coordenadas, mapeamento_padrao)

        assert len(df) == 2
        assert "latitude" not in df.columns

    def test_ler_csv_colunas_custom(self, service, csv_colunas_custom, mapeamento_custom):
        """Deve ler CSV com mapeamento customizado."""
        df = service._ler_csv(csv_colunas_custom, mapeamento_custom)

        assert len(df) == 2
        assert "id" in df.columns
        assert "rp0" in df.columns

    def test_ler_csv_vazio(self, service, csv_vazio, mapeamento_padrao):
        """Deve retornar DataFrame vazio para CSV sem dados."""
        df = service._ler_csv(csv_vazio, mapeamento_padrao)

        assert len(df) == 0

    def test_ler_csv_colunas_faltantes(self, service, csv_valido):
        """Deve lançar erro se colunas obrigatórias faltarem."""
        mapeamento_errado = CSVColumnMapping(
            colunas_profundidade={"0_10": "nao_existe"}
        )

        with pytest.raises(ValueError, match="Colunas obrigatórias faltantes"):
            service._ler_csv(csv_valido, mapeamento_errado)

    def test_ler_csv_invalido(self, service, csv_invalido, mapeamento_padrao):
        """Deve converter valores inválidos para NaN."""
        df = service._ler_csv(csv_invalido, mapeamento_padrao)

        # Valores não numéricos devem ser NaN
        assert df["rp_0_10"].isna().all()
        # Linha sem dados válidos deve ser removida pelo dropna
        assert len(df) == 0


# ============================================================
# TESTES: Conversão DataFrame -> Perfis do Core
# ============================================================

class TestDataframeParaPerfis:
    """Testes para o método _dataframe_para_perfis."""

    def test_converter_csv_para_perfis(self, service, csv_valido, mapeamento_padrao):
        """Deve converter CSV válido em lista de PerfilCompactacao."""
        df = service._ler_csv(csv_valido, mapeamento_padrao)
        perfis = service._dataframe_para_perfis(df, mapeamento_padrao)

        assert len(perfis) == 4
        # Verificar classificações
        classificacoes = [p.classificacao_geral for p in perfis]
        assert "Apto" in classificacoes
        assert "Restricao" in classificacoes
        assert "Impedimento Severo" in classificacoes

    def test_ponto_com_impedimento(self, service, csv_valido, mapeamento_padrao):
        """Ponto com alta resistência deve ter impedimento severo."""
        df = service._ler_csv(csv_valido, mapeamento_padrao)
        perfis = service._dataframe_para_perfis(df, mapeamento_padrao)

        ponto_severo = next(p for p in perfis if p.ponto_id == "P003")
        assert ponto_severo.classificacao_geral == "Impedimento Severo"
        assert ponto_severo.necessita_escarificacao is True
        assert ponto_severo.profundidade_maxima_restricao is not None

    def test_ponto_apto(self, service, csv_valido, mapeamento_padrao):
        """Ponto com baixa resistência deve estar apto."""
        df = service._ler_csv(csv_valido, mapeamento_padrao)
        perfis = service._dataframe_para_perfis(df, mapeamento_padrao)

        ponto_apto = next(p for p in perfis if p.ponto_id == "P001")
        assert ponto_apto.classificacao_geral == "Apto"
        assert ponto_apto.necessita_escarificacao is False

    def test_coordenadas_nos_perfis(self, service, csv_valido, mapeamento_padrao):
        """Coordenadas devem estar presentes nos dados do gráfico."""
        df = service._ler_csv(csv_valido, mapeamento_padrao)
        perfis = service._dataframe_para_perfis(df, mapeamento_padrao)

        ponto = next(p for p in perfis if p.ponto_id == "P001")
        assert ponto.dados_grafico["latitude"] == pytest.approx(-22.1234)
        assert ponto.dados_grafico["longitude"] == pytest.approx(-47.5678)

    def test_sem_coordenadas(self, service, csv_sem_coordenadas, mapeamento_padrao):
        """Perfis sem coordenadas devem ter latitude/longitude None."""
        df = service._ler_csv(csv_sem_coordenadas, mapeamento_padrao)
        perfis = service._dataframe_para_perfis(df, mapeamento_padrao)

        assert len(perfis) == 2
        assert perfis[0].dados_grafico["latitude"] is None
        assert perfis[0].dados_grafico["longitude"] is None


# ============================================================
# TESTES: Resumo Estatístico
# ============================================================

class TestResumoEstatistico:
    """Testes para cálculo de resumo estatístico."""

    def test_resumo_com_impedimento(self, service, csv_valido, mapeamento_padrao):
        """Resumo deve indicar impedimento quando presente."""
        df = service._ler_csv(csv_valido, mapeamento_padrao)
        perfis = service._dataframe_para_perfis(df, mapeamento_padrao)
        resumo = service.analisador.resumo_talhao(perfis)

        assert resumo["total_pontos_amostrais"] == 4
        assert resumo["pontos_com_impedimento_severo"] >= 1
        assert resumo["percentual_impedimento"] > 0
        assert resumo["classificacao_predominante"] in [
            "Apto", "Restricao", "Impedimento Severo"
        ]

    def test_recomendacao_escarificacao(self, service, csv_valido, mapeamento_padrao):
        """Deve recomendar escarificação quando há impedimento."""
        df = service._ler_csv(csv_valido, mapeamento_padrao)
        perfis = service._dataframe_para_perfis(df, mapeamento_padrao)
        resumo = service.analisador.resumo_talhao(perfis)

        # Como há pelo menos 1 ponto com impedimento, a recomendação deve mencionar escarificação
        assert "escarificação" in resumo["recomendacao_geral"].lower() or                "manutenção" in resumo["recomendacao_geral"].lower()


# ============================================================
# TESTES: Flags de Escarificação
# ============================================================

class TestFlagsEscarificacao:
    """Testes para geração de flags."""

    def test_flags_ponto_severo(self, service, csv_valido, mapeamento_padrao):
        """Ponto com impedimento severo deve gerar flag obrigatória."""
        df = service._ler_csv(csv_valido, mapeamento_padrao)
        perfis = service._dataframe_para_perfis(df, mapeamento_padrao)
        flags = service.analisador.gerar_flags_escarificacao(perfis)

        flags_severas = [f for f in flags if f["tipo"] == "ESCARIFICACAO_OBRIGATORIA"]
        assert len(flags_severas) >= 1

    def test_flags_ponto_apto(self, service, csv_valido, mapeamento_padrao):
        """Ponto apto deve gerar flag de monitorar."""
        df = service._ler_csv(csv_valido, mapeamento_padrao)
        perfis = service._dataframe_para_perfis(df, mapeamento_padrao)
        flags = service.analisador.gerar_flags_escarificacao(perfis)

        flags_monitorar = [f for f in flags if f["tipo"] == "COMPACTACAO_MONITORAR"]
        assert len(flags_monitorar) >= 1

    def test_flag_contem_dados_tecnicos(self, service, csv_valido, mapeamento_padrao):
        """Flags devem conter dados técnicos completos."""
        df = service._ler_csv(csv_valido, mapeamento_padrao)
        perfis = service._dataframe_para_perfis(df, mapeamento_padrao)
        flags = service.analisador.gerar_flags_escarificacao(perfis)

        for flag in flags:
            assert "dados_tecnicos" in flag
            assert "limite_apto_mpa" in flag["dados_tecnicos"]
            assert "limite_restricao_mpa" in flag["dados_tecnicos"]
            assert "resistencia_maxima_observada" in flag["dados_tecnicos"]


# ============================================================
# TESTES: Construção de Resumo Schema
# ============================================================

class TestConstruirResumo:
    """Testes para _construir_resumo."""

    def test_construir_resumo_completo(self, service, csv_valido, mapeamento_padrao):
        """Deve construir ResumoEstatistico completo a partir do core."""
        df = service._ler_csv(csv_valido, mapeamento_padrao)
        perfis = service._dataframe_para_perfis(df, mapeamento_padrao)
        resumo_core = service.analisador.resumo_talhao(perfis)
        resumo = service._construir_resumo(resumo_core)

        assert isinstance(resumo, ResumoEstatistico)
        assert resumo.total_pontos == 4
        assert 0 <= resumo.percentual_impedimento <= 100
        assert 0 <= resumo.percentual_restricao <= 100
        assert 0 <= resumo.percentual_apto <= 100
        assert resumo.classificacao_predominante in [
            "Apto", "Restricao", "Impedimento Severo"
        ]

    def test_soma_percentuais_100(self, service, csv_valido, mapeamento_padrao):
        """Soma dos percentuais deve ser aproximadamente 100%."""
        df = service._ler_csv(csv_valido, mapeamento_padrao)
        perfis = service._dataframe_para_perfis(df, mapeamento_padrao)
        resumo_core = service.analisador.resumo_talhao(perfis)
        resumo = service._construir_resumo(resumo_core)

        soma = resumo.percentual_impedimento + resumo.percentual_restricao + resumo.percentual_apto
        assert soma == pytest.approx(100.0, abs=0.1)


# ============================================================
# TESTES: Construção de Flags Schema
# ============================================================

class TestConstruirFlags:
    """Testes para _construir_flags."""

    def test_construir_flags(self, service, csv_valido, mapeamento_padrao):
        """Deve construir lista de FlagEscarificacao a partir do core."""
        df = service._ler_csv(csv_valido, mapeamento_padrao)
        perfis = service._dataframe_para_perfis(df, mapeamento_padrao)
        flags_core = service.analisador.gerar_flags_escarificacao(perfis)
        flags = service._construir_flags(flags_core)

        assert isinstance(flags, list)
        assert len(flags) == len(flags_core)

        for flag in flags:
            assert isinstance(flag, FlagEscarificacao)
            assert flag.ponto_id != ""
            assert flag.mensagem != ""
            assert flag.severidade in ["ALTA", "MEDIA", "BAIXA"]


# ============================================================
# TESTES: Criação de Análise
# ============================================================

class TestCriarAnalise:
    """Testes para _criar_analise."""

    def test_criar_analise_completa(self, service, csv_valido, mapeamento_padrao):
        """Deve criar AnaliseCompactacao com todos os campos."""
        df = service._ler_csv(csv_valido, mapeamento_padrao)
        perfis = service._dataframe_para_perfis(df, mapeamento_padrao)
        resumo_core = service.analisador.resumo_talhao(perfis)

        analise = service._criar_analise(
            perfis=perfis,
            resumo=resumo_core,
            talhao_id=1,
            propriedade_id=2,
            usuario_id=3,
            nome_arquivo="teste.csv",
        )

        assert isinstance(analise, AnaliseCompactacao)
        assert analise.id is not None
        assert len(analise.id) == 36  # UUID
        assert analise.talhao_id == 1
        assert analise.propriedade_id == 2
        assert analise.usuario_id == 3
        assert analise.arquivo_csv_origem == "teste.csv"
        assert analise.classificacao_geral == resumo_core["classificacao_predominante"]

    def test_profundidade_maxima_restricao(self, service, csv_valido, mapeamento_padrao):
        """Deve calcular profundidade máxima de restrição corretamente."""
        df = service._ler_csv(csv_valido, mapeamento_padrao)
        perfis = service._dataframe_para_perfis(df, mapeamento_padrao)
        resumo_core = service.analisador.resumo_talhao(perfis)

        analise = service._criar_analise(
            perfis=perfis,
            resumo=resumo_core,
            talhao_id=1,
            propriedade_id=None,
            usuario_id=None,
            nome_arquivo=None,
        )

        # Se há pontos com impedimento, profundidade_maxima_restricao deve ser preenchida
        if any(p.necessita_escarificacao for p in perfis):
            assert analise.profundidade_maxima_restricao is not None
            assert analise.profundidade_maxima_restricao > 0


# ============================================================
# TESTES: GeoJSON
# ============================================================

class TestGeoJSON:
    """Testes para geração de GeoJSON."""

    def test_cores_classificacao(self, service):
        """Cores devem estar mapeadas corretamente."""
        assert service.CORES_CLASSIFICACAO["Apto"] == "#32CD32"
        assert service.CORES_CLASSIFICACAO["Restricao"] == "#FFD700"
        assert service.CORES_CLASSIFICACAO["Impedimento Severo"] == "#DC143C"


# ============================================================
# TESTES: Mapeamento de Colunas
# ============================================================

class TestMapeamentoColunas:
    """Testes para mapeamento flexível de colunas do CSV."""

    def test_mapeamento_padrao(self):
        """Mapeamento padrão deve ter colunas esperadas."""
        mapeamento = CSVColumnMapping()

        assert mapeamento.coluna_ponto_id == "ponto_id"
        assert mapeamento.coluna_latitude == "latitude"
        assert mapeamento.coluna_longitude == "longitude"
        assert "0_10" in mapeamento.colunas_profundidade
        assert mapeamento.colunas_profundidade["0_10"] == "rp_0_10"

    def test_mapeamento_customizado(self):
        """Mapeamento customizado deve aceitar nomes diferentes."""
        mapeamento = CSVColumnMapping(
            coluna_ponto_id="codigo",
            colunas_profundidade={"0_10": "resistencia_0_10"}
        )

        assert mapeamento.coluna_ponto_id == "codigo"
        assert mapeamento.colunas_profundidade["0_10"] == "resistencia_0_10"


# ============================================================
# TESTES: Casos de Borda
# ============================================================

class TestCasosBorda:
    """Testes para casos de borda e cenários extremos."""

    def test_csv_com_valores_negativos(self, service):
        """Valores negativos devem ser tratados como inválidos."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ponto_id", "rp_0_10", "rp_10_20"])
        writer.writerow(["P001", "-1.0", "-2.0"])
        csv_bytes = output.getvalue().encode("utf-8")

        df = service._ler_csv(csv_bytes, CSVColumnMapping())
        # Valores negativos permanecem no DataFrame (validação é do core)
        assert len(df) == 1

    def test_csv_com_valores_extremos(self, service):
        """Valores extremos de resistência devem ser processados."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ponto_id", "rp_0_10", "rp_10_20"])
        writer.writerow(["P001", "0.1", "10.0"])
        csv_bytes = output.getvalue().encode("utf-8")

        df = service._ler_csv(csv_bytes, CSVColumnMapping())
        perfis = service._dataframe_para_perfis(df, CSVColumnMapping())

        assert len(perfis) == 1
        # Valor 10.0 MPa é extremamente alto -> impedimento severo
        assert perfis[0].classificacao_geral == "Impedimento Severo"

    def test_csv_com_ponto_unico(self, service):
        """CSV com apenas um ponto deve funcionar."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ponto_id", "rp_0_10", "rp_10_20"])
        writer.writerow(["P001", "1.5", "1.8"])
        csv_bytes = output.getvalue().encode("utf-8")

        df = service._ler_csv(csv_bytes, CSVColumnMapping())
        perfis = service._dataframe_para_perfis(df, CSVColumnMapping())
        resumo = service.analisador.resumo_talhao(perfis)

        assert resumo["total_pontos_amostrais"] == 1
        assert resumo["percentual_apto"] == 100.0

    def test_csv_com_camadas_incompletas(self, service):
        """CSV com menos camadas que o padrão deve usar camadas disponíveis."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ponto_id", "rp_0_10", "rp_10_20"])
        writer.writerow(["P001", "1.5", "2.8"])
        csv_bytes = output.getvalue().encode("utf-8")

        df = service._ler_csv(csv_bytes, CSVColumnMapping())
        perfis = service._dataframe_para_perfis(df, CSVColumnMapping())

        assert len(perfis) == 1
        assert len(perfis[0].camadas) == 2


# ============================================================
# TESTES: Integração Assíncrona (Mock)
# ============================================================

class TestIntegracaoAsync:
    """Testes de integração assíncrona com banco mockado."""

    @pytest.mark.asyncio
    async def test_processar_csv_completo(self, service, csv_valido, mapeamento_padrao):
        """Deve processar CSV e retornar resposta completa."""
        resultado = await service.processar_csv(
            arquivo_csv=csv_valido,
            talhao_id=1,
            propriedade_id=2,
            usuario_id=3,
            mapeamento_colunas=mapeamento_padrao,
            nome_arquivo="penetrometria.csv",
        )

        assert resultado.analise_id is not None
        assert resultado.resumo.total_pontos == 4
        assert len(resultado.flags) == 4  # Um flag por ponto
        assert "sucesso" in resultado.mensagem.lower()

    @pytest.mark.asyncio
    async def test_processar_csv_vazio(self, service, csv_vazio, mapeamento_padrao):
        """Deve lançar erro para CSV vazio."""
        with pytest.raises(ValueError, match="vazio"):
            await service.processar_csv(
                arquivo_csv=csv_vazio,
                mapeamento_colunas=mapeamento_padrao,
            )

    @pytest.mark.asyncio
    async def test_buscar_analise_nao_encontrada(self, service):
        """Deve retornar None para análise inexistente."""
        service.db.execute.return_value = MagicMock(
            scalar_one_or_none=MagicMock(return_value=None)
        )

        resultado = await service.buscar_analise("nao-existe")
        assert resultado is None
