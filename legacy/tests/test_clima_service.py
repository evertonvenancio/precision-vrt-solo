"""
Testes unitários do ClimaService com simulação (mock) das respostas da API.
"""

from datetime import date, datetime, timezone
from typing import Any
from unittest.mock import patch

import pytest

from config.clima_config import ConfiguracaoClima
from schemas.clima import PrevisaoDiariaSchema, PrevisaoResponseSchema
from services.clima_service import ClimaService, _cache


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def limpar_cache():
    """Garante cache limpo antes de cada teste."""
    _cache.clear()
    yield
    _cache.clear()


@pytest.fixture
def config() -> ConfiguracaoClima:
    return ConfiguracaoClima()


@pytest.fixture
def service(config: ConfiguracaoClima) -> ClimaService:
    return ClimaService(api_key="FAKE_KEY", config=config)


def _previsao_json(
    precipitacao: float = 0.0,
    vento_ms: float = 2.0,
    temp: float = 25.0,
    umidade: int = 70,
) -> dict[str, Any]:
    """Monta um JSON de resposta da API forecast com um único período de 3h."""
    return {
        "city": {"name": "Ribeirão Preto"},
        "list": [
            {
                "dt": int(datetime(2024, 6, 15, 12, tzinfo=timezone.utc).timestamp()),
                "main": {
                    "temp": temp,
                    "temp_min": temp - 3,
                    "temp_max": temp + 3,
                    "humidity": umidade,
                },
                "wind": {"speed": vento_ms},
                "rain": {"3h": precipitacao},
                "weather": [{"description": "céu limpo", "icon": "01d"}],
            }
        ],
    }


# ---------------------------------------------------------------------------
# buscar_previsao
# ---------------------------------------------------------------------------

class TestBuscarPrevisao:
    def test_retorna_previsao_com_sucesso(self, service: ClimaService) -> None:
        """Deve parsear e retornar previsão quando a API responde corretamente."""
        payload = _previsao_json(precipitacao=5.0, vento_ms=3.0, temp=28.0)

        with patch.object(service, "_requisitar_previsao", return_value=payload):
            resultado = service.buscar_previsao(lat=-21.17, lon=-47.80)

        assert isinstance(resultado, PrevisaoResponseSchema)
        assert len(resultado.dias) == 1
        assert resultado.cidade == "Ribeirão Preto"
        assert resultado.dias[0].precipitacao_mm == pytest.approx(5.0)
        assert resultado.dias[0].velocidade_vento_kmh == pytest.approx(3.0 * 3.6, rel=0.01)

    def test_retorna_previsao_vazia_se_api_falhar(self, service: ClimaService) -> None:
        """Se a API lançar exceção, deve retornar previsão com lista vazia — nunca travar."""
        with patch.object(
            service, "_requisitar_previsao", side_effect=Exception("timeout")
        ):
            resultado = service.buscar_previsao(lat=-21.17, lon=-47.80)

        assert resultado.dias == []
        assert resultado.fonte == "indisponível"

    def test_cache_evita_segunda_chamada_http(self, service: ClimaService) -> None:
        """Segunda chamada com mesmas coordenadas deve usar cache sem nova requisição."""
        payload = _previsao_json()

        with patch.object(
            service, "_requisitar_previsao", return_value=payload
        ) as mock_req:
            service.buscar_previsao(lat=-21.17, lon=-47.80)
            service.buscar_previsao(lat=-21.17, lon=-47.80)

        assert mock_req.call_count == 1

    def test_cache_separado_por_coordenadas(self, service: ClimaService) -> None:
        """Coordenadas diferentes devem gerar entradas de cache independentes."""
        payload = _previsao_json()

        with patch.object(
            service, "_requisitar_previsao", return_value=payload
        ) as mock_req:
            service.buscar_previsao(lat=-21.17, lon=-47.80)
            service.buscar_previsao(lat=-15.00, lon=-47.00)

        assert mock_req.call_count == 2


# ---------------------------------------------------------------------------
# gerar_alertas_aplicacao — Ureia
# ---------------------------------------------------------------------------

class TestAlertasUreia:
    def _chamar_com_previsao(
        self, service: ClimaService, dia: PrevisaoDiariaSchema
    ):
        previsao = PrevisaoResponseSchema(
            lat=-21.17,
            lon=-47.80,
            dias=[dia],
            consultado_em=datetime.now(tz=timezone.utc),
        )
        with patch.object(service, "buscar_previsao", return_value=previsao):
            return service.gerar_alertas_aplicacao(-21.17, -47.80, "ureia")

    def _dia(self, **kwargs) -> PrevisaoDiariaSchema:
        defaults = dict(
            data=date(2024, 6, 15),
            temp_min=18.0,
            temp_max=28.0,
            precipitacao_mm=0.0,
            umidade_relativa_pct=70.0,
            velocidade_vento_kmh=5.0,
            descricao="céu limpo",
        )
        defaults.update(kwargs)
        return PrevisaoDiariaSchema(**defaults)

    def test_pode_aplicar_sem_alertas_de_perigo(self, service: ClimaService) -> None:
        """Condições favoráveis devem resultar em pode_aplicar=True."""
        resultado = self._chamar_com_previsao(service, self._dia())
        assert resultado.pode_aplicar is True
        assert resultado.tipo_aplicacao == "ureia"

    def test_alerta_perigo_chuva_excessiva(self, service: ClimaService) -> None:
        """Chuva acima de 20 mm deve gerar alerta de perigo e bloquear aplicação."""
        resultado = self._chamar_com_previsao(
            service, self._dia(precipitacao_mm=25.0)
        )
        assert resultado.pode_aplicar is False
        tipos = [a.tipo for a in resultado.alertas]
        assert "perigo" in tipos
        parametros = [a.parametro for a in resultado.alertas]
        assert "precipitacao" in parametros

    def test_alerta_atencao_chuva_moderada(self, service: ClimaService) -> None:
        """Chuva entre o limite ideal e o limite máximo deve gerar 'atencao', não 'perigo'."""
        resultado = self._chamar_com_previsao(
            service, self._dia(precipitacao_mm=17.0)
        )
        assert resultado.pode_aplicar is True
        alertas_precipitacao = [
            a for a in resultado.alertas if a.parametro == "precipitacao"
        ]
        assert alertas_precipitacao[0].tipo == "atencao"

    def test_alerta_temperatura_alta(self, service: ClimaService) -> None:
        """Temperatura máxima acima de 35°C deve gerar alerta de atenção."""
        resultado = self._chamar_com_previsao(
            service, self._dia(temp_max=37.0)
        )
        parametros = [a.parametro for a in resultado.alertas]
        assert "temperatura" in parametros

    def test_alerta_umidade_baixa(self, service: ClimaService) -> None:
        """Umidade abaixo de 40% deve gerar alerta de atenção."""
        resultado = self._chamar_com_previsao(
            service, self._dia(umidade_relativa_pct=35.0)
        )
        parametros = [a.parametro for a in resultado.alertas]
        assert "umidade_relativa" in parametros


# ---------------------------------------------------------------------------
# gerar_alertas_aplicacao — Foliar
# ---------------------------------------------------------------------------

class TestAlertasFoliar:
    def _chamar(self, service: ClimaService, **kwargs):
        defaults = dict(
            data=date(2024, 6, 15),
            temp_min=18.0,
            temp_max=26.0,
            precipitacao_mm=0.0,
            umidade_relativa_pct=65.0,
            velocidade_vento_kmh=5.0,
            descricao="céu limpo",
        )
        defaults.update(kwargs)
        dia = PrevisaoDiariaSchema(**defaults)
        previsao = PrevisaoResponseSchema(
            lat=-21.17, lon=-47.80, dias=[dia],
            consultado_em=datetime.now(tz=timezone.utc),
        )
        with patch.object(service, "buscar_previsao", return_value=previsao):
            return service.gerar_alertas_aplicacao(-21.17, -47.80, "foliar")

    def test_vento_alto_impede_aplicacao(self, service: ClimaService) -> None:
        """Vento acima de 10 km/h deve bloquear aplicação foliar."""
        resultado = self._chamar(service, velocidade_vento_kmh=15.0)
        assert resultado.pode_aplicar is False

    def test_vento_baixo_permite_aplicacao(self, service: ClimaService) -> None:
        """Vento abaixo de 10 km/h deve permitir aplicação foliar."""
        resultado = self._chamar(service, velocidade_vento_kmh=6.0)
        assert resultado.pode_aplicar is True

    def test_chuva_impede_aplicacao_foliar(self, service: ClimaService) -> None:
        """Chuva acima do limite previsto deve bloquear aplicação foliar."""
        resultado = self._chamar(service, precipitacao_mm=10.0)
        assert resultado.pode_aplicar is False


# ---------------------------------------------------------------------------
# gerar_alertas_aplicacao — Herbicida
# ---------------------------------------------------------------------------

class TestAlertasHerbicida:
    def _chamar(self, service: ClimaService, **kwargs):
        defaults = dict(
            data=date(2024, 6, 15),
            temp_min=15.0,
            temp_max=30.0,
            precipitacao_mm=0.0,
            umidade_relativa_pct=60.0,
            velocidade_vento_kmh=8.0,
            descricao="céu limpo",
        )
        defaults.update(kwargs)
        dia = PrevisaoDiariaSchema(**defaults)
        previsao = PrevisaoResponseSchema(
            lat=-21.17, lon=-47.80, dias=[dia],
            consultado_em=datetime.now(tz=timezone.utc),
        )
        with patch.object(service, "buscar_previsao", return_value=previsao):
            return service.gerar_alertas_aplicacao(-21.17, -47.80, "herbicida")

    def test_condicoes_favoraveis(self, service: ClimaService) -> None:
        resultado = self._chamar(service)
        assert resultado.pode_aplicar is True

    def test_vento_excessivo(self, service: ClimaService) -> None:
        resultado = self._chamar(service, velocidade_vento_kmh=20.0)
        assert resultado.pode_aplicar is False

    def test_temperatura_minima_baixa_gera_atencao(self, service: ClimaService) -> None:
        resultado = self._chamar(service, temp_min=2.0)
        parametros = [a.parametro for a in resultado.alertas]
        assert "temperatura_minima" in parametros


# ---------------------------------------------------------------------------
# Tipo de aplicação inválido
# ---------------------------------------------------------------------------

class TestTipoInvalido:
    def test_tipo_desconhecido_retorna_alertas_vazios(self, service: ClimaService) -> None:
        """Tipo de aplicação desconhecido não deve lançar exceção — retorna lista vazia."""
        dia = PrevisaoDiariaSchema(
            data=date(2024, 6, 15),
            temp_min=18.0, temp_max=28.0,
            precipitacao_mm=0.0, umidade_relativa_pct=70.0,
            velocidade_vento_kmh=5.0, descricao="céu limpo",
        )
        previsao = PrevisaoResponseSchema(
            lat=-21.17, lon=-47.80, dias=[dia],
            consultado_em=datetime.now(tz=timezone.utc),
        )
        with patch.object(service, "buscar_previsao", return_value=previsao):
            resultado = service.gerar_alertas_aplicacao(-21.17, -47.80, "xyz_invalido")

        assert resultado.alertas == []


# ---------------------------------------------------------------------------
# Previsão indisponível
# ---------------------------------------------------------------------------

class TestClimaIndisponivel:
    def test_sem_dias_de_previsao_retorna_nao_pode_aplicar(
        self, service: ClimaService
    ) -> None:
        """Sem dados de previsão, o sistema deve recomendar cautela."""
        previsao_vazia = PrevisaoResponseSchema(
            lat=-21.17, lon=-47.80, dias=[],
            consultado_em=datetime.now(tz=timezone.utc),
            fonte="indisponível",
        )
        with patch.object(service, "buscar_previsao", return_value=previsao_vazia):
            resultado = service.gerar_alertas_aplicacao(-21.17, -47.80, "ureia")

        assert resultado.pode_aplicar is False
        assert "indisponível" in resultado.resumo.lower() or "indisponivel" in resultado.resumo.lower()
