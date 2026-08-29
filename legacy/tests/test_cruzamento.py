"""
Testes unitários para o módulo de Cruzamento Solo x Planta.

Testa:
- Classificação de fertilidade do solo
- Classificação de desempenho da planta
- Pipeline espacial com GeoJSONs simulados
- Motor de diagnóstico (3 regras + casos especiais)
- Estatísticas e resultados
"""

import pytest

from core.cruzamento_solo_planta import (
    ClassificadorFertilidade,
    ClassificadorPlanta,
    CruzamentoEspacial,
)
from schemas.cruzamento import (
    AlertaDiagnostico,
    ClasseDesempenhPlanta,
    ClasseFertilidade,
    EntradaCruzamento,
    NivelAlerta,
    TipoDiagnostico,
    TipoVariavelPlanta,
)
from services.cruzamento_service import (
    CruzamentoService,
    MotorDiagnostico,
    _calcular_estatisticas,
)


# ===================== FIXTURES: GEOJSONS SIMULADOS =====================

def _make_box(lon_min: float, lat_min: float, lon_max: float, lat_max: float) -> dict:
    """Cria polígono retangular simples como GeoJSON geometry."""
    return {
        "type": "Polygon",
        "coordinates": [[
            [lon_min, lat_min],
            [lon_max, lat_min],
            [lon_max, lat_max],
            [lon_min, lat_max],
            [lon_min, lat_min],
        ]],
    }


@pytest.fixture
def geojson_solo_alta_fertilidade() -> dict:
    """Solo com fertilidade alta: P=25, pH=6.0, V%=70."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": _make_box(-47.5, -23.5, -47.0, -23.0),
                "properties": {
                    "zona_id": 1,
                    "ph": 6.0,
                    "p_mg_dm3": 25.0,
                    "k_mg_dm3": 150.0,
                    "v_percent": 70.0,
                    "mo_percent": 2.5,
                },
            }
        ],
    }


@pytest.fixture
def geojson_solo_baixa_fertilidade() -> dict:
    """Solo com fertilidade baixa: P=5, pH=4.5, V%=30."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": _make_box(-47.5, -23.5, -47.0, -23.0),
                "properties": {
                    "zona_id": 2,
                    "ph": 4.5,
                    "p_mg_dm3": 5.0,
                    "k_mg_dm3": 40.0,
                    "v_percent": 30.0,
                    "mo_percent": 1.0,
                },
            }
        ],
    }


@pytest.fixture
def geojson_solo_multiplas_zonas() -> dict:
    """Solo com 4 zonas de diferentes fertilidades."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": _make_box(-47.5, -23.5, -47.25, -23.25),
                "properties": {
                    "zona_id": 1,
                    "ph": 6.2,
                    "p_mg_dm3": 28.0,
                    "k_mg_dm3": 130.0,
                    "v_percent": 72.0,
                    "mo_percent": 3.0,
                },
            },
            {
                "type": "Feature",
                "geometry": _make_box(-47.25, -23.5, -47.0, -23.25),
                "properties": {
                    "zona_id": 2,
                    "ph": 4.8,
                    "p_mg_dm3": 6.0,
                    "k_mg_dm3": 50.0,
                    "v_percent": 35.0,
                    "mo_percent": 1.2,
                },
            },
            {
                "type": "Feature",
                "geometry": _make_box(-47.5, -23.25, -47.25, -23.0),
                "properties": {
                    "zona_id": 3,
                    "ph": 4.6,
                    "p_mg_dm3": 8.0,
                    "k_mg_dm3": 55.0,
                    "v_percent": 32.0,
                    "mo_percent": 1.5,
                },
            },
            {
                "type": "Feature",
                "geometry": _make_box(-47.25, -23.25, -47.0, -23.0),
                "properties": {
                    "zona_id": 4,
                    "ph": 6.0,
                    "p_mg_dm3": 22.0,
                    "k_mg_dm3": 140.0,
                    "v_percent": 65.0,
                    "mo_percent": 2.8,
                },
            },
        ],
    }


@pytest.fixture
def geojson_planta_ndvi_baixo() -> dict:
    """NDVI baixo: classe Baixo cobrindo toda a área."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": _make_box(-47.6, -23.6, -46.9, -22.9),
                "properties": {"ndvi_classe": "Baixo"},
            }
        ],
    }


@pytest.fixture
def geojson_planta_ndvi_alto() -> dict:
    """NDVI alto: classe Alto cobrindo toda a área."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": _make_box(-47.6, -23.6, -46.9, -22.9),
                "properties": {"ndvi_classe": "Alto"},
            }
        ],
    }


@pytest.fixture
def geojson_planta_ndvi_multiplo() -> dict:
    """NDVI variado por subárea: Alto no norte, Baixo no sul."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": _make_box(-47.6, -23.0, -46.9, -22.9),  # Norte
                "properties": {"ndvi_classe": "Alto"},
            },
            {
                "type": "Feature",
                "geometry": _make_box(-47.6, -23.6, -46.9, -23.0),  # Sul
                "properties": {"ndvi_classe": "Baixo"},
            },
        ],
    }


# ===================== TESTES: CLASSIFICADOR FERTILIDADE =====================

class TestClassificadorFertilidade:
    """Testa classificação de atributos de solo."""

    def test_ph_baixo(self):
        assert ClassificadorFertilidade.classificar_atributo("ph", 4.5) == "baixo"

    def test_ph_medio(self):
        assert ClassificadorFertilidade.classificar_atributo("ph", 5.2) == "medio"

    def test_ph_alto(self):
        assert ClassificadorFertilidade.classificar_atributo("ph", 6.0) == "alto"

    def test_p_baixo(self):
        assert ClassificadorFertilidade.classificar_atributo("p_mg_dm3", 5.0) == "baixo"

    def test_p_medio(self):
        assert ClassificadorFertilidade.classificar_atributo("p_mg_dm3", 15.0) == "medio"

    def test_p_alto(self):
        assert ClassificadorFertilidade.classificar_atributo("p_mg_dm3", 25.0) == "alto"

    def test_v_percent_baixo(self):
        assert ClassificadorFertilidade.classificar_atributo("v_percent", 30.0) == "baixo"

    def test_v_percent_alto(self):
        assert ClassificadorFertilidade.classificar_atributo("v_percent", 70.0) == "alto"

    def test_atributo_desconhecido(self):
        assert ClassificadorFertilidade.classificar_atributo("xyz", 5.0) == "desconhecido"

    def test_fertilidade_alta(self):
        """Solo com P alto, pH ideal e V% alto deve ser 'alta'."""
        atributos = {
            "ph": 6.0,
            "p_mg_dm3": 25.0,
            "k_mg_dm3": 150.0,
            "v_percent": 70.0,
        }
        assert ClassificadorFertilidade.classificar_fertilidade_zona(atributos) == "alta"

    def test_fertilidade_baixa_por_ph(self):
        """pH abaixo de 5.0 deve resultar em fertilidade baixa."""
        atributos = {
            "ph": 4.5,
            "p_mg_dm3": 25.0,
            "v_percent": 70.0,
        }
        assert ClassificadorFertilidade.classificar_fertilidade_zona(atributos) == "baixa"

    def test_fertilidade_baixa_por_p(self):
        """P abaixo de 10 deve resultar em fertilidade baixa."""
        atributos = {
            "ph": 6.0,
            "p_mg_dm3": 5.0,
            "v_percent": 65.0,
        }
        assert ClassificadorFertilidade.classificar_fertilidade_zona(atributos) == "baixa"

    def test_fertilidade_baixa_por_v(self):
        """V% abaixo de 40 deve resultar em fertilidade baixa."""
        atributos = {
            "ph": 6.0,
            "p_mg_dm3": 25.0,
            "v_percent": 35.0,
        }
        assert ClassificadorFertilidade.classificar_fertilidade_zona(atributos) == "baixa"

    def test_fertilidade_media(self):
        """Atributos intermediários devem resultar em fertilidade média."""
        atributos = {
            "ph": 5.8,
            "p_mg_dm3": 15.0,
            "v_percent": 55.0,
        }
        assert ClassificadorFertilidade.classificar_fertilidade_zona(atributos) == "media"

    def test_sem_v_percent(self):
        """Sem V%, deve classificar apenas por P e pH."""
        atributos = {
            "ph": 6.0,
            "p_mg_dm3": 25.0,
        }
        assert ClassificadorFertilidade.classificar_fertilidade_zona(atributos) == "alta"


# ===================== TESTES: CLASSIFICADOR PLANTA =====================

class TestClassificadorPlanta:
    """Testa classificação de NDVI e normalização de classes."""

    def test_ndvi_baixo(self):
        assert ClassificadorPlanta.classificar_ndvi(0.3) == "baixo"

    def test_ndvi_medio(self):
        assert ClassificadorPlanta.classificar_ndvi(0.55) == "medio"

    def test_ndvi_alto(self):
        assert ClassificadorPlanta.classificar_ndvi(0.75) == "alto"

    def test_normalizar_alto_variantes(self):
        for v in ["Alto", "ALTO", "alta", "high", "A", "H"]:
            assert ClassificadorPlanta.normalizar_classe_planta(v) == "alto", f"falhou para '{v}'"

    def test_normalizar_baixo_variantes(self):
        for v in ["Baixo", "BAIXO", "baixa", "low", "L", "B"]:
            assert ClassificadorPlanta.normalizar_classe_planta(v) == "baixo", f"falhou para '{v}'"

    def test_normalizar_medio_variantes(self):
        for v in ["Médio", "MEDIO", "medium", "med", "M"]:
            assert ClassificadorPlanta.normalizar_classe_planta(v) == "medio", f"falhou para '{v}'"

    def test_normalizar_none(self):
        assert ClassificadorPlanta.normalizar_classe_planta(None) is None

    def test_normalizar_invalido(self):
        assert ClassificadorPlanta.normalizar_classe_planta("xyz") is None


# ===================== TESTES: MOTOR DE DIAGNÓSTICO =====================

class TestMotorDiagnostico:
    """Testa as 3 regras principais de diagnóstico."""

    @pytest.fixture
    def motor(self) -> MotorDiagnostico:
        return MotorDiagnostico()

    def test_regra1_limitacao_fisica(self, motor: MotorDiagnostico):
        """Regra 1: Solo ALTA + Planta BAIXO = Limitação Física."""
        alerta = motor.diagnosticar(zona_id=1, fertilidade="alta", planta="baixo")

        assert alerta.tipo_diagnostico == TipoDiagnostico.LIMITACAO_FISICA
        assert alerta.nivel_alerta == NivelAlerta.CRITICO
        assert alerta.modulo_relacionado == "modulo_compactacao"
        assert "compactação" in alerta.mensagem_alerta.lower() or "física" in alerta.mensagem_alerta.lower()
        assert "penetrometria" in alerta.acao_recomendada.lower()

    def test_regra2_limitacao_nutricional(self, motor: MotorDiagnostico):
        """Regra 2: Solo BAIXA + Planta BAIXO = Limitação Nutricional."""
        alerta = motor.diagnosticar(zona_id=2, fertilidade="baixa", planta="baixo")

        assert alerta.tipo_diagnostico == TipoDiagnostico.LIMITACAO_NUTRICIONAL
        assert alerta.nivel_alerta == NivelAlerta.CRITICO
        assert alerta.modulo_relacionado == "modulo_prescricao_vrt"
        assert "nutricional" in alerta.mensagem_alerta.lower()
        assert "VRT" in alerta.acao_recomendada

    def test_regra3_anomalia(self, motor: MotorDiagnostico):
        """Regra 3: Solo BAIXA + Planta ALTO = Anomalia."""
        alerta = motor.diagnosticar(zona_id=3, fertilidade="baixa", planta="alto")

        assert alerta.tipo_diagnostico == TipoDiagnostico.ANOMALIA
        assert alerta.nivel_alerta == NivelAlerta.ATENCAO
        assert "anomalia" in alerta.mensagem_alerta.lower()
        assert "amostragem" in alerta.acao_recomendada.lower()

    def test_eficiencia_adequada(self, motor: MotorDiagnostico):
        """Solo ALTA + Planta ALTO = Eficiência Adequada."""
        alerta = motor.diagnosticar(zona_id=4, fertilidade="alta", planta="alto")

        assert alerta.tipo_diagnostico == TipoDiagnostico.EFICIENCIA_ADEQUADA
        assert alerta.nivel_alerta == NivelAlerta.INFORMATIVO

    def test_inconclusivo_media(self, motor: MotorDiagnostico):
        """Solo MEDIA + Planta MEDIO = Inconclusivo."""
        alerta = motor.diagnosticar(zona_id=5, fertilidade="media", planta="medio")

        assert alerta.tipo_diagnostico == TipoDiagnostico.INCONCLUSIVO

    def test_solo_alta_planta_medio(self, motor: MotorDiagnostico):
        """Solo ALTA + Planta MEDIO = Inconclusivo."""
        alerta = motor.diagnosticar(zona_id=6, fertilidade="alta", planta="medio")
        assert alerta.tipo_diagnostico == TipoDiagnostico.INCONCLUSIVO

    def test_area_ha_preservada(self, motor: MotorDiagnostico):
        """Área deve ser preservada no alerta."""
        alerta = motor.diagnosticar(
            zona_id=7, fertilidade="baixa", planta="baixo", area_ha=12.5
        )
        assert alerta.area_ha == 12.5

    def test_atributos_solo_preservados(self, motor: MotorDiagnostico):
        """Atributos de solo devem ser preservados no alerta."""
        atributos = {"ph": 4.5, "p_mg_dm3": 5.0}
        alerta = motor.diagnosticar(
            zona_id=8, fertilidade="baixa", planta="baixo",
            atributos_solo=atributos
        )
        assert alerta.atributos_solo["ph"] == 4.5
        assert alerta.atributos_solo["p_mg_dm3"] == 5.0

    def test_zona_id_preservado(self, motor: MotorDiagnostico):
        """zona_id deve ser preservado exatamente."""
        alerta = motor.diagnosticar(zona_id="ZONA-XYZ", fertilidade="alta", planta="baixo")
        assert alerta.zona_id == "ZONA-XYZ"


# ===================== TESTES: CRUZAMENTO ESPACIAL =====================

class TestCruzamentoEspacial:
    """Testa o motor de processamento espacial com GeoPandas."""

    @pytest.fixture
    def motor(self) -> CruzamentoEspacial:
        return CruzamentoEspacial()

    def test_carregar_geojson_valido(
        self,
        motor: CruzamentoEspacial,
        geojson_solo_alta_fertilidade: dict,
    ):
        """Deve carregar GeoJSON e retornar GeoDataFrame não vazio."""
        gdf = motor.carregar_geojson(geojson_solo_alta_fertilidade)
        assert len(gdf) == 1
        assert gdf.geometry.is_valid.all()

    def test_carregar_geojson_invalido(self, motor: CruzamentoEspacial):
        """GeoJSON inválido deve lançar ValueError."""
        with pytest.raises(ValueError, match="FeatureCollection"):
            motor.carregar_geojson({"type": "Feature", "geometry": {}})

    def test_carregar_geojson_vazio(self, motor: CruzamentoEspacial):
        """GeoJSON sem features deve lançar ValueError."""
        with pytest.raises(ValueError, match="features"):
            motor.carregar_geojson({"type": "FeatureCollection", "features": []})

    def test_preparar_solo_adiciona_fertilidade(
        self,
        motor: CruzamentoEspacial,
        geojson_solo_alta_fertilidade: dict,
    ):
        """Deve adicionar coluna fertilidade_classe ao GeoDataFrame."""
        gdf_raw = motor.carregar_geojson(geojson_solo_alta_fertilidade)
        gdf_prep = motor.preparar_camada_solo(gdf_raw)

        assert "fertilidade_classe" in gdf_prep.columns
        assert gdf_prep["fertilidade_classe"].iloc[0] == "alta"

    def test_preparar_solo_baixa_fertilidade(
        self,
        motor: CruzamentoEspacial,
        geojson_solo_baixa_fertilidade: dict,
    ):
        """Solo com P=5 e pH=4.5 deve ser classificado como 'baixa'."""
        gdf_raw = motor.carregar_geojson(geojson_solo_baixa_fertilidade)
        gdf_prep = motor.preparar_camada_solo(gdf_raw)

        assert gdf_prep["fertilidade_classe"].iloc[0] == "baixa"

    def test_preparar_planta_ndvi_classe_textual(
        self,
        motor: CruzamentoEspacial,
        geojson_planta_ndvi_baixo: dict,
    ):
        """Deve normalizar classe textual 'Baixo' para 'baixo'."""
        gdf_raw = motor.carregar_geojson(geojson_planta_ndvi_baixo)
        gdf_prep = motor.preparar_camada_planta(gdf_raw, tipo="ndvi")

        assert "planta_classe" in gdf_prep.columns
        assert gdf_prep["planta_classe"].iloc[0] == "baixo"

    def test_overlay_gera_interseccoes(
        self,
        motor: CruzamentoEspacial,
        geojson_solo_alta_fertilidade: dict,
        geojson_planta_ndvi_baixo: dict,
    ):
        """Overlay entre polígonos sobrepostos deve gerar intersecções."""
        gdf_solo = motor.carregar_geojson(geojson_solo_alta_fertilidade)
        gdf_solo = motor.preparar_camada_solo(gdf_solo)

        gdf_planta = motor.carregar_geojson(geojson_planta_ndvi_baixo)
        gdf_planta = motor.preparar_camada_planta(gdf_planta, tipo="ndvi")

        gdf_overlay = motor.executar_overlay(gdf_solo, gdf_planta)

        assert len(gdf_overlay) > 0
        assert "area_intersect_m2" in gdf_overlay.columns
        assert (gdf_overlay["area_intersect_m2"] > 0).all()

    def test_classe_predominante_retorna_dataframe(
        self,
        motor: CruzamentoEspacial,
        geojson_solo_alta_fertilidade: dict,
        geojson_planta_ndvi_baixo: dict,
    ):
        """Deve retornar DataFrame com colunas esperadas."""
        gdf_solo = motor.carregar_geojson(geojson_solo_alta_fertilidade)
        gdf_solo = motor.preparar_camada_solo(gdf_solo)

        gdf_planta = motor.carregar_geojson(geojson_planta_ndvi_baixo)
        gdf_planta = motor.preparar_camada_planta(gdf_planta, tipo="ndvi")

        gdf_overlay = motor.executar_overlay(gdf_solo, gdf_planta)
        df_result = motor.calcular_classe_predominante(gdf_overlay)

        assert not df_result.empty
        assert "fertilidade_classe" in df_result.columns
        assert "planta_classe_predominante" in df_result.columns
        assert "area_total_ha" in df_result.columns


# ===================== TESTES: SERVIÇO COMPLETO =====================

class TestCruzamentoService:
    """Testa o serviço completo de cruzamento."""

    @pytest.fixture
    def service(self) -> CruzamentoService:
        return CruzamentoService()

    def test_entrada_invalida_retorna_erro(
        self,
        service: CruzamentoService,
    ):
        """GeoJSON de tipo inválido deve falhar na validação do schema."""
        with pytest.raises(Exception):
            EntradaCruzamento(
                geojson_solo={"type": "Feature"},  # Inválido
                geojson_planta={"type": "FeatureCollection", "features": []},
            )

    def test_regra1_via_servico_completo(
        self,
        service: CruzamentoService,
        geojson_solo_alta_fertilidade: dict,
        geojson_planta_ndvi_baixo: dict,
    ):
        """Pipeline completo: solo bom + planta ruim deve gerar Regra 1."""
        entrada = EntradaCruzamento(
            geojson_solo=geojson_solo_alta_fertilidade,
            geojson_planta=geojson_planta_ndvi_baixo,
            tipo_variavel_planta=TipoVariavelPlanta.NDVI,
        )

        resultado = service.executar(entrada)

        assert resultado.sucesso is True
        assert len(resultado.alertas) > 0

        alerta = resultado.alertas[0]
        assert alerta.tipo_diagnostico == TipoDiagnostico.LIMITACAO_FISICA
        assert alerta.nivel_alerta == NivelAlerta.CRITICO

    def test_regra2_via_servico_completo(
        self,
        service: CruzamentoService,
        geojson_solo_baixa_fertilidade: dict,
        geojson_planta_ndvi_baixo: dict,
    ):
        """Pipeline completo: solo ruim + planta ruim deve gerar Regra 2."""
        entrada = EntradaCruzamento(
            geojson_solo=geojson_solo_baixa_fertilidade,
            geojson_planta=geojson_planta_ndvi_baixo,
            tipo_variavel_planta=TipoVariavelPlanta.NDVI,
        )

        resultado = service.executar(entrada)

        assert resultado.sucesso is True
        alertas_nutricional = [
            a for a in resultado.alertas
            if a.tipo_diagnostico == TipoDiagnostico.LIMITACAO_NUTRICIONAL
        ]
        assert len(alertas_nutricional) > 0

    def test_regra3_via_servico_completo(
        self,
        service: CruzamentoService,
        geojson_solo_baixa_fertilidade: dict,
        geojson_planta_ndvi_alto: dict,
    ):
        """Pipeline completo: solo ruim + planta boa deve gerar Regra 3 (Anomalia)."""
        entrada = EntradaCruzamento(
            geojson_solo=geojson_solo_baixa_fertilidade,
            geojson_planta=geojson_planta_ndvi_alto,
            tipo_variavel_planta=TipoVariavelPlanta.NDVI,
        )

        resultado = service.executar(entrada)

        assert resultado.sucesso is True
        alertas_anomalia = [
            a for a in resultado.alertas
            if a.tipo_diagnostico == TipoDiagnostico.ANOMALIA
        ]
        assert len(alertas_anomalia) > 0

    def test_resultado_tem_geojson(
        self,
        service: CruzamentoService,
        geojson_solo_alta_fertilidade: dict,
        geojson_planta_ndvi_baixo: dict,
    ):
        """Resultado deve conter GeoJSON da intersecção."""
        entrada = EntradaCruzamento(
            geojson_solo=geojson_solo_alta_fertilidade,
            geojson_planta=geojson_planta_ndvi_baixo,
        )
        resultado = service.executar(entrada)

        assert resultado.geojson_resultado is not None
        assert resultado.geojson_resultado["type"] == "FeatureCollection"

    def test_resultado_tem_estatisticas(
        self,
        service: CruzamentoService,
        geojson_solo_multiplas_zonas: dict,
        geojson_planta_ndvi_multiplo: dict,
    ):
        """Resultado deve conter estatísticas consolidadas."""
        entrada = EntradaCruzamento(
            geojson_solo=geojson_solo_multiplas_zonas,
            geojson_planta=geojson_planta_ndvi_multiplo,
            nome_talhao="Talhão Norte",
            safra="2025/26",
        )
        resultado = service.executar(entrada)

        assert resultado.sucesso is True
        assert resultado.estatisticas is not None
        assert resultado.estatisticas.total_zonas > 0
        assert resultado.estatisticas.area_total_ha > 0

    def test_metadados_preservados(
        self,
        service: CruzamentoService,
        geojson_solo_alta_fertilidade: dict,
        geojson_planta_ndvi_alto: dict,
    ):
        """Nome do talhão e safra devem ser preservados no resultado."""
        entrada = EntradaCruzamento(
            geojson_solo=geojson_solo_alta_fertilidade,
            geojson_planta=geojson_planta_ndvi_alto,
            nome_talhao="Talhão 5",
            safra="2025/26",
        )
        resultado = service.executar(entrada)

        assert resultado.nome_talhao == "Talhão 5"
        assert resultado.safra == "2025/26"

    def test_diagnostico_zona_individual(self, service: CruzamentoService):
        """Diagnóstico individual sem processamento espacial deve funcionar."""
        alerta = service.diagnosticar_zona_individual(
            zona_id="Z01",
            fertilidade="alta",
            planta="baixo",
            area_ha=5.3,
        )
        assert alerta.tipo_diagnostico == TipoDiagnostico.LIMITACAO_FISICA
        assert alerta.area_ha == 5.3

    def test_propriedade_tem_alertas_criticos(
        self,
        geojson_solo_alta_fertilidade: dict,
        geojson_planta_ndvi_baixo: dict,
    ):
        """tem_alertas_criticos deve retornar True quando há alertas críticos."""
        service = CruzamentoService()
        entrada = EntradaCruzamento(
            geojson_solo=geojson_solo_alta_fertilidade,
            geojson_planta=geojson_planta_ndvi_baixo,
        )
        resultado = service.executar(entrada)

        assert resultado.tem_alertas_criticos is True


# ===================== TESTES: ESTATÍSTICAS =====================

class TestEstatisticas:
    """Testa cálculo de estatísticas de cruzamento."""

    def _make_alerta(
        self,
        zona_id: int,
        fertilidade: str,
        planta: str,
        tipo: TipoDiagnostico,
        nivel: NivelAlerta,
        area: float = 5.0,
    ) -> AlertaDiagnostico:
        return AlertaDiagnostico(
            zona_id=zona_id,
            classificacao_solo=ClasseFertilidade(fertilidade),
            classificacao_planta=ClasseDesempenhPlanta(planta),
            tipo_diagnostico=tipo,
            nivel_alerta=nivel,
            mensagem_alerta="Teste",
            acao_recomendada="Ação teste",
            area_ha=area,
        )

    def test_contagem_zonas(self):
        alertas = [
            self._make_alerta(1, "alta", "baixo", TipoDiagnostico.LIMITACAO_FISICA, NivelAlerta.CRITICO, 10.0),
            self._make_alerta(2, "baixa", "baixo", TipoDiagnostico.LIMITACAO_NUTRICIONAL, NivelAlerta.CRITICO, 8.0),
            self._make_alerta(3, "baixa", "alto", TipoDiagnostico.ANOMALIA, NivelAlerta.ATENCAO, 5.0),
        ]
        stats = _calcular_estatisticas(alertas)

        assert stats.total_zonas == 3
        assert stats.area_total_ha == 23.0

    def test_contagem_por_fertilidade(self):
        alertas = [
            self._make_alerta(1, "alta", "baixo", TipoDiagnostico.LIMITACAO_FISICA, NivelAlerta.CRITICO),
            self._make_alerta(2, "baixa", "baixo", TipoDiagnostico.LIMITACAO_NUTRICIONAL, NivelAlerta.CRITICO),
            self._make_alerta(3, "media", "medio", TipoDiagnostico.INCONCLUSIVO, NivelAlerta.ATENCAO),
        ]
        stats = _calcular_estatisticas(alertas)

        assert stats.zonas_fertilidade_alta == 1
        assert stats.zonas_fertilidade_baixa == 1
        assert stats.zonas_fertilidade_media == 1

    def test_area_limitacao_fisica(self):
        alertas = [
            self._make_alerta(1, "alta", "baixo", TipoDiagnostico.LIMITACAO_FISICA, NivelAlerta.CRITICO, 15.0),
            self._make_alerta(2, "alta", "baixo", TipoDiagnostico.LIMITACAO_FISICA, NivelAlerta.CRITICO, 10.0),
            self._make_alerta(3, "baixa", "baixo", TipoDiagnostico.LIMITACAO_NUTRICIONAL, NivelAlerta.CRITICO, 8.0),
        ]
        stats = _calcular_estatisticas(alertas)

        assert stats.area_limitacao_fisica_ha == 25.0
        assert stats.alertas_limitacao_fisica == 2


# ===================== TESTES: SCHEMA ENTRADA =====================

class TestSchemaEntrada:
    """Testa validação do schema de entrada."""

    def test_geojson_invalido_lanca_erro(self):
        with pytest.raises(Exception):
            EntradaCruzamento(
                geojson_solo={"type": "invalid"},
                geojson_planta={"type": "FeatureCollection", "features": [{"type": "Feature"}]},
            )

    def test_geojson_sem_features_lanca_erro(self):
        with pytest.raises(Exception):
            EntradaCruzamento(
                geojson_solo={"type": "FeatureCollection", "features": []},
                geojson_planta={"type": "FeatureCollection", "features": [{"type": "Feature"}]},
            )

    def test_tipo_variavel_default(self):
        entrada = EntradaCruzamento(
            geojson_solo={
                "type": "FeatureCollection",
                "features": [{"type": "Feature", "geometry": _make_box(-47, -23, -46, -22), "properties": {}}],
            },
            geojson_planta={
                "type": "FeatureCollection",
                "features": [{"type": "Feature", "geometry": _make_box(-47, -23, -46, -22), "properties": {}}],
            },
        )
        assert entrada.tipo_variavel_planta == TipoVariavelPlanta.NDVI


# Execução: pytest tests/test_cruzamento.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
