"""
Service layer para integracao com API de clima e geracao de alertas agronomicos.
"""

import logging
import time
from datetime import date, datetime, timedelta, timezone
from typing import Dict, Optional, Tuple

import httpx

from config.clima_config import ConfiguracaoClima, clima_config
from core.seguranca.permissions import get_permissoes
from schemas.clima import (
    AlertaAplicacaoSchema,
    JanelaAplicacaoResponseSchema,
    PrevisaoDiariaSchema,
    PrevisaoResponseSchema,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cache em memoria simples (key -> (timestamp, payload))
# ---------------------------------------------------------------------------
_cache: Dict[str, Tuple[float, object]] = {}


def _cache_get(key: str, ttl: int) -> Optional[object]:
    """Retorna valor do cache se ainda valido, senao None.

    Args:
        key: Chave de cache.
        ttl: Tempo de vida em segundos.

    Returns:
        Objeto cacheado ou None.
    """
    entry = _cache.get(key)
    if entry is None:
        return None
    ts, valor = entry
    if time.monotonic() - ts > ttl:
        del _cache[key]
        return None
    return valor


def _cache_set(key: str, valor: object) -> None:
    """Armazena valor no cache com timestamp atual.

    Args:
        key: Chave de cache.
        valor: Objeto a armazenar.
    """
    _cache[key] = (time.monotonic(), valor)


# ---------------------------------------------------------------------------
# Conversoes de unidades
# ---------------------------------------------------------------------------

def _ms_para_kmh(ms: float) -> float:
    """Converte m/s para km/h."""
    return ms * 3.6


# ---------------------------------------------------------------------------
# Servico principal
# ---------------------------------------------------------------------------

class ClimaService:
    """Servico de integracao com OpenWeatherMap para previsao e historico.

    Args:
        api_key: Chave da API OpenWeatherMap.
        config: Instancia de ConfiguracaoClima. Usa o singleton global por padrao.
        base_url: URL base da API. Permite override em testes.
    """

    BASE_URL = "https://api.openweathermap.org/data/2.5"
    GEO_URL = "http://api.openweathermap.org/geo/1.0"

    def __init__(
        self,
        api_key: str,
        config: ConfiguracaoClima = clima_config,
        base_url: Optional[str] = None,
    ) -> None:
        self._api_key = api_key
        self._config = config
        self._base_url = base_url or self.BASE_URL

    # ------------------------------------------------------------------
    # Consultas ao banco (Repository Layer interno)
    # ------------------------------------------------------------------

    def buscar_permissoes(self, db) -> dict:
        """Busca as permissões do usuário no banco."""
        return get_permissoes(db)

    # ------------------------------------------------------------------
    # Geocoding - Busca coordenadas por nome de cidade
    # ------------------------------------------------------------------

    def buscar_coordenadas_por_cidade(self, cidade: str) -> Tuple[float, float]:
        """Resolve o nome de uma cidade em latitude e longitude.

        Utiliza a Geocoding API do OpenWeatherMap para converter o nome
        da cidade em coordenadas geograficas.

        Args:
            cidade: Nome da cidade a buscar (ex: "Londrina, PR").

        Returns:
            Tupla (lat, lon) do primeiro resultado.

        Raises:
            ValueError: Se a cidade nao for encontrada ou a API falhar.
        """
        cache_key = f"geo:{cidade.lower().strip()}"
        cached = _cache_get(cache_key, self._config.cache_ttl_segundos)
        if cached is not None:
            logger.debug("Cache hit para geocoding cidade=%s", cidade)
            return cached  # type: ignore[return-value]

        url = f"{self.GEO_URL}/direct"
        params = {
            "q": cidade,
            "limit": 1,
            "appid": self._api_key,
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                resultados = response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("Erro HTTP na Geocoding API: %s", exc)
            raise ValueError(f"Erro ao consultar Geocoding API: {exc.response.status_code}") from exc
        except Exception as exc:
            logger.error("Erro inesperado na Geocoding API: %s", exc)
            raise ValueError("Erro inesperado ao buscar coordenadas da cidade.") from exc

        if not resultados:
            raise ValueError(f"Cidade nao encontrada: '{cidade}'.")

        lat = float(resultados[0]["lat"])
        lon = float(resultados[0]["lon"])
        logger.info("Cidade '%s' resolvida para lat=%.4f lon=%.4f", cidade, lat, lon)

        _cache_set(cache_key, (lat, lon))
        return lat, lon

    # ------------------------------------------------------------------
    # Previsao
    # ------------------------------------------------------------------

    def buscar_previsao(self, lat: float, lon: float) -> PrevisaoResponseSchema:
        """Busca previsao para os proximos N dias a partir de lat/lon.

        Implementa cache em memoria com TTL configuravel para nao estourar
        os limites da API gratuita.

        Args:
            lat: Latitude do ponto de interesse.
            lon: Longitude do ponto de interesse.

        Returns:
            PrevisaoResponseSchema com a lista de previsoes diarias.

        Raises:
            Nao lanca excecoes. Em caso de falha da API, retorna previsao
            vazia com lista de dias vazia.
        """
        cache_key = f"previsao:{lat:.4f}:{lon:.4f}"
        cached = _cache_get(cache_key, self._config.cache_ttl_segundos)
        if cached is not None:
            logger.debug("Cache hit para previsao lat=%s lon=%s", lat, lon)
            return cached  # type: ignore[return-value]

        try:
            dados_brutos = self._requisitar_previsao(lat, lon)
            resposta = self._parsear_previsao(lat, lon, dados_brutos)
        except Exception as exc:
            logger.warning(
                "Falha ao buscar previsao (lat=%s, lon=%s): %s", lat, lon, exc
            )
            resposta = PrevisaoResponseSchema(
                lat=lat,
                lon=lon,
                cidade=None,
                dias=[],
                consultado_em=datetime.now(tz=timezone.utc),
                fonte="indisponivel",
            )

        _cache_set(cache_key, resposta)
        return resposta

    def _requisitar_previsao(self, lat: float, lon: float) -> dict:
        """Faz a chamada HTTP a API de previsao.

        Args:
            lat: Latitude.
            lon: Longitude.

        Returns:
            Dicionario JSON retornado pela API.
        """
        url = f"{self._base_url}/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self._api_key,
            "units": "metric",
            "lang": "pt_br",
            "cnt": self._config.previsao_dias * 8,  # API retorna de 3 em 3h
        }
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    def _parsear_previsao(
        self, lat: float, lon: float, dados: dict
    ) -> PrevisaoResponseSchema:
        """Transforma o JSON da API na schema interna agrupando por dia.

        Args:
            lat: Latitude consultada.
            lon: Longitude consultada.
            dados: JSON bruto da API forecast.

        Returns:
            PrevisaoResponseSchema normalizada.
        """
        por_dia: Dict[date, dict] = {}

        for item in dados.get("list", []):
            dt = datetime.fromtimestamp(item["dt"], tz=timezone.utc).date()
            chuva_mm = item.get("rain", {}).get("3h", 0.0)
            vento_kmh = _ms_para_kmh(item["wind"]["speed"])
            temp = item["main"]

            if dt not in por_dia:
                por_dia[dt] = {
                    "temp_min": temp["temp_min"],
                    "temp_max": temp["temp_max"],
                    "precipitacao_mm": chuva_mm,
                    "umidade": temp["humidity"],
                    "vento_kmh": vento_kmh,
                    "descricao": item["weather"][0]["description"],
                    "icone": item["weather"][0]["icon"],
                    "contagem": 1,
                }
            else:
                d = por_dia[dt]
                d["temp_min"] = min(d["temp_min"], temp["temp_min"])
                d["temp_max"] = max(d["temp_max"], temp["temp_max"])
                d["precipitacao_mm"] += chuva_mm
                d["umidade"] = (d["umidade"] * d["contagem"] + temp["humidity"]) / (
                    d["contagem"] + 1
                )
                d["vento_kmh"] = max(d["vento_kmh"], vento_kmh)
                d["contagem"] += 1

        dias = [
            PrevisaoDiariaSchema(
                data=dia,
                temp_min=round(v["temp_min"], 1),
                temp_max=round(v["temp_max"], 1),
                precipitacao_mm=round(v["precipitacao_mm"], 1),
                umidade_relativa_pct=round(v["umidade"], 1),
                velocidade_vento_kmh=round(v["vento_kmh"], 1),
                descricao=v["descricao"],
                icone=v["icone"],
            )
            for dia, v in sorted(por_dia.items())
        ]

        cidade = dados.get("city", {}).get("name")
        return PrevisaoResponseSchema(
            lat=lat,
            lon=lon,
            cidade=cidade,
            dias=dias,
            consultado_em=datetime.now(tz=timezone.utc),
        )

    # ------------------------------------------------------------------
    # Historico
    # ------------------------------------------------------------------

    def buscar_historico(self, lat: float, lon: float) -> PrevisaoResponseSchema:
        """Busca condicoes climaticas dos ultimos N dias para auditoria.

        Utiliza o endpoint One Call API v3 (historical) do OpenWeatherMap.

        Args:
            lat: Latitude do ponto.
            lon: Longitude do ponto.

        Returns:
            PrevisaoResponseSchema com os dias historicos. Lista vazia em
            caso de falha da API.
        """
        cache_key = f"historico:{lat:.4f}:{lon:.4f}"
        cached = _cache_get(cache_key, self._config.cache_ttl_segundos)
        if cached is not None:
            return cached  # type: ignore[return-value]

        dias: list[PrevisaoDiariaSchema] = []
        hoje = date.today()

        for delta in range(1, self._config.historico_dias + 1):
            alvo = hoje - timedelta(days=delta)
            try:
                dia_schema = self._buscar_dia_historico(lat, lon, alvo)
                dias.append(dia_schema)
            except Exception as exc:
                logger.warning(
                    "Falha ao buscar historico para %s (lat=%s, lon=%s): %s",
                    alvo,
                    lat,
                    lon,
                    exc,
                )

        resposta = PrevisaoResponseSchema(
            lat=lat,
            lon=lon,
            dias=sorted(dias, key=lambda d: d.data),
            consultado_em=datetime.now(tz=timezone.utc),
        )
        _cache_set(cache_key, resposta)
        return resposta

    def _buscar_dia_historico(
        self, lat: float, lon: float, dia: date
    ) -> PrevisaoDiariaSchema:
        """Busca dados historicos de um dia especifico via One Call API.

        Args:
            lat: Latitude.
            lon: Longitude.
            dia: Data a consultar.

        Returns:
            PrevisaoDiariaSchema com os dados do dia.
        """
        dt_unix = int(
            datetime(dia.year, dia.month, dia.day, 12, 0, tzinfo=timezone.utc).timestamp()
        )
        url = f"{self._base_url.replace('data/2.5', 'data/3.0')}/onecall/timemachine"
        params = {
            "lat": lat,
            "lon": lon,
            "dt": dt_unix,
            "appid": self._api_key,
            "units": "metric",
            "lang": "pt_br",
        }
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            dados = response.json()

        horas = dados.get("data", [])
        if not horas:
            raise ValueError(f"Sem dados historicos para {dia}")

        temps = [h["temp"] for h in horas]
        chuva = sum(h.get("rain", 0.0) for h in horas)
        umidade = sum(h["humidity"] for h in horas) / len(horas)
        vento = max(_ms_para_kmh(h["wind_speed"]) for h in horas)
        descricao = horas[12 % len(horas)]["weather"][0]["description"]

        return PrevisaoDiariaSchema(
            data=dia,
            temp_min=round(min(temps), 1),
            temp_max=round(max(temps), 1),
            precipitacao_mm=round(chuva, 1),
            umidade_relativa_pct=round(umidade, 1),
            velocidade_vento_kmh=round(vento, 1),
            descricao=descricao,
        )

    # ------------------------------------------------------------------
    # Alertas de janela de aplicacao
    # ------------------------------------------------------------------

    def gerar_alertas_aplicacao(
        self, lat: float, lon: float, tipo_aplicacao: str
    ) -> JanelaAplicacaoResponseSchema:
        """Cruza a recomendacao agronomica com a previsao e gera alertas.

        Args:
            lat: Latitude do talhao.
            lon: Longitude do talhao.
            tipo_aplicacao: Tipo de insumo (ureia | foliar | herbicida).

        Returns:
            JanelaAplicacaoResponseSchema com a decisao e lista de alertas.
        """
        tipo_aplicacao = tipo_aplicacao.lower().strip()
        previsao = self.buscar_previsao(lat, lon)

        hoje = previsao.dias[0] if previsao.dias else None

        alertas: list[AlertaAplicacaoSchema] = []

        if hoje is None:
            return JanelaAplicacaoResponseSchema(
                lat=lat,
                lon=lon,
                tipo_aplicacao=tipo_aplicacao,
                pode_aplicar=False,
                resumo="Clima indisponivel -- consulte o agronomo antes de aplicar",
                alertas=[
                    AlertaAplicacaoSchema(
                        tipo="atencao",
                        parametro="disponibilidade_api",
                        mensagem="Dados climaticos indisponiveis no momento.",
                    )
                ],
                consultado_em=datetime.now(tz=timezone.utc),
            )

        if tipo_aplicacao == "ureia":
            alertas = self._alertas_ureia(hoje)
        elif tipo_aplicacao == "foliar":
            alertas = self._alertas_foliar(hoje)
        elif tipo_aplicacao == "herbicida":
            alertas = self._alertas_herbicida(hoje)
        else:
            logger.warning("Tipo de aplicacao desconhecido: %s", tipo_aplicacao)
            alertas = []

        tem_perigo = any(a.tipo == "perigo" for a in alertas)
        pode_aplicar = not tem_perigo

        resumo = "Pode aplicar -- condicoes favoraveis" if pode_aplicar else (
            "Evitar aplicacao hoje -- condicoes adversas detectadas"
        )

        return JanelaAplicacaoResponseSchema(
            lat=lat,
            lon=lon,
            tipo_aplicacao=tipo_aplicacao,
            pode_aplicar=pode_aplicar,
            resumo=resumo,
            alertas=alertas,
            previsao_proximas_24h=hoje,
            consultado_em=datetime.now(tz=timezone.utc),
        )

    # ------------------------------------------------------------------
    # Logica de alertas por tipo de insumo
    # ------------------------------------------------------------------

    def _alertas_ureia(self, hoje: PrevisaoDiariaSchema) -> list[AlertaAplicacaoSchema]:
        """Gera alertas especificos para aplicacao de Ureia.

        Args:
            hoje: Previsao do dia corrente.

        Returns:
            Lista de AlertaAplicacaoSchema.
        """
        lim = self._config.ureia
        alertas: list[AlertaAplicacaoSchema] = []

        if hoje.precipitacao_mm > lim.precipitacao_max_mm:
            alertas.append(AlertaAplicacaoSchema(
                tipo="perigo",
                parametro="precipitacao",
                mensagem=(
                    f"Chuva prevista de {hoje.precipitacao_mm:.1f} mm supera o limite "
                    f"de {lim.precipitacao_max_mm} mm. Alto risco de volatilizacao do nitrogenio."
                ),
                valor_atual=hoje.precipitacao_mm,
                limite_agronomico=lim.precipitacao_max_mm,
            ))
        elif hoje.precipitacao_mm > lim.precipitacao_prevista_max_mm:
            alertas.append(AlertaAplicacaoSchema(
                tipo="atencao",
                parametro="precipitacao",
                mensagem=(
                    f"Chuva prevista de {hoje.precipitacao_mm:.1f} mm esta acima do ideal "
                    f"({lim.precipitacao_prevista_max_mm} mm). Monitore as condicoes."
                ),
                valor_atual=hoje.precipitacao_mm,
                limite_agronomico=lim.precipitacao_prevista_max_mm,
            ))
        else:
            alertas.append(AlertaAplicacaoSchema(
                tipo="ok",
                parametro="precipitacao",
                mensagem="Precipitacao dentro dos limites para ureia.",
                valor_atual=hoje.precipitacao_mm,
                limite_agronomico=lim.precipitacao_max_mm,
            ))

        if hoje.temp_max > lim.temperatura_max_c:
            alertas.append(AlertaAplicacaoSchema(
                tipo="atencao",
                parametro="temperatura",
                mensagem=(
                    f"Temperatura maxima de {hoje.temp_max:.1f}C supera {lim.temperatura_max_c}C. "
                    "Volatilizacao acelerada -- prefira aplicar ao entardecer."
                ),
                valor_atual=hoje.temp_max,
                limite_agronomico=lim.temperatura_max_c,
            ))

        if hoje.umidade_relativa_pct < lim.umidade_relativa_min_pct:
            alertas.append(AlertaAplicacaoSchema(
                tipo="atencao",
                parametro="umidade_relativa",
                mensagem=(
                    f"Umidade de {hoje.umidade_relativa_pct:.1f}% abaixo do minimo "
                    f"({lim.umidade_relativa_min_pct}%). Volatilizacao elevada."
                ),
                valor_atual=hoje.umidade_relativa_pct,
                limite_agronomico=lim.umidade_relativa_min_pct,
            ))

        return alertas

    def _alertas_foliar(self, hoje: PrevisaoDiariaSchema) -> list[AlertaAplicacaoSchema]:
        """Gera alertas para pulverizacao foliar.

        Args:
            hoje: Previsao do dia corrente.

        Returns:
            Lista de AlertaAplicacaoSchema.
        """
        lim = self._config.foliar
        alertas: list[AlertaAplicacaoSchema] = []

        if hoje.velocidade_vento_kmh > lim.velocidade_vento_max_kmh:
            alertas.append(AlertaAplicacaoSchema(
                tipo="perigo",
                parametro="vento",
                mensagem=(
                    f"Vento de {hoje.velocidade_vento_kmh:.1f} km/h supera o limite "
                    f"de {lim.velocidade_vento_max_kmh} km/h. Risco severo de deriva da calda."
                ),
                valor_atual=hoje.velocidade_vento_kmh,
                limite_agronomico=lim.velocidade_vento_max_kmh,
            ))
        else:
            alertas.append(AlertaAplicacaoSchema(
                tipo="ok",
                parametro="vento",
                mensagem="Vento dentro do limite para pulverizacao foliar.",
                valor_atual=hoje.velocidade_vento_kmh,
                limite_agronomico=lim.velocidade_vento_max_kmh,
            ))

        if hoje.precipitacao_mm > lim.precipitacao_prevista_max_mm:
            alertas.append(AlertaAplicacaoSchema(
                tipo="perigo",
                parametro="precipitacao",
                mensagem=(
                    f"Chuva prevista de {hoje.precipitacao_mm:.1f} mm pode lavar a calda. "
                    f"Limite: {lim.precipitacao_prevista_max_mm} mm."
                ),
                valor_atual=hoje.precipitacao_mm,
                limite_agronomico=lim.precipitacao_prevista_max_mm,
            ))

        if hoje.temp_max > lim.temperatura_max_c:
            alertas.append(AlertaAplicacaoSchema(
                tipo="atencao",
                parametro="temperatura",
                mensagem=(
                    f"Temperatura maxima de {hoje.temp_max:.1f}C supera {lim.temperatura_max_c}C. "
                    "Evaporation da calda pode ser elevada."
                ),
                valor_atual=hoje.temp_max,
                limite_agronomico=lim.temperatura_max_c,
            ))

        if hoje.umidade_relativa_pct < lim.umidade_relativa_min_pct:
            alertas.append(AlertaAplicacaoSchema(
                tipo="atencao",
                parametro="umidade_relativa",
                mensagem=(
                    f"Umidade de {hoje.umidade_relativa_pct:.1f}% abaixo do minimo "
                    f"({lim.umidade_relativa_min_pct}%). Risco de evaporacao prematura."
                ),
                valor_atual=hoje.umidade_relativa_pct,
                limite_agronomico=lim.umidade_relativa_min_pct,
            ))

        return alertas

    def _alertas_herbicida(self, hoje: PrevisaoDiariaSchema) -> list[AlertaAplicacaoSchema]:
        """Gera alertas para aplicacao de herbicidas.

        Args:
            hoje: Previsao do dia corrente.

        Returns:
            Lista de AlertaAplicacaoSchema.
        """
        lim = self._config.herbicida
        alertas: list[AlertaAplicacaoSchema] = []

        if hoje.velocidade_vento_kmh > lim.velocidade_vento_max_kmh:
            alertas.append(AlertaAplicacaoSchema(
                tipo="perigo",
                parametro="vento",
                mensagem=(
                    f"Vento de {hoje.velocidade_vento_kmh:.1f} km/h supera o limite de "
                    f"{lim.velocidade_vento_max_kmh} km/h para herbicidas. Risco de deriva para culturas vizinhas."
                ),
                valor_atual=hoje.velocidade_vento_kmh,
                limite_agronomico=lim.velocidade_vento_max_kmh,
            ))

        if hoje.precipitacao_mm > lim.precipitacao_prevista_max_mm:
            alertas.append(AlertaAplicacaoSchema(
                tipo="perigo",
                parametro="precipitacao",
                mensagem=(
                    f"Chuva prevista de {hoje.precipitacao_mm:.1f} mm pode lixiviar o herbicida. "
                    f"Limite: {lim.precipitacao_prevista_max_mm} mm."
                ),
                valor_atual=hoje.precipitacao_mm,
                limite_agronomico=lim.precipitacao_prevista_max_mm,
            ))

        if hoje.temp_min < lim.temperatura_min_c:
            alertas.append(AlertaAplicacaoSchema(
                tipo="atencao",
                parametro="temperatura_minima",
                mensagem=(
                    f"Temperatura minima de {hoje.temp_min:.1f}C abaixo de {lim.temperatura_min_c}C. "
                    "Eficacia do herbicida pode ser reduzida."
                ),
                valor_atual=hoje.temp_min,
                limite_agronomico=lim.temperatura_min_c,
            ))

        if not alertas:
            alertas.append(AlertaAplicacaoSchema(
                tipo="ok",
                parametro="geral",
                mensagem="Condicoes favoraveis para aplicacao de herbicida.",
            ))

        return alertas