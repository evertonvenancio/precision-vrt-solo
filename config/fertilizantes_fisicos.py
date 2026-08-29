"""
Configuracao de fertilizantes fisicos para otimizacao de Bulk Blend.

Este modulo contem o catalogo completo de fertilizantes granulados com suas
propriedades fisicas, quimicas e restricoes de compatibilidade.

Typical usage:
    >>> from config.fertilizantes_fisicos import CatalogoFertilizantes
    >>> catalogo = CatalogoFertilizantes()
    >>> ureia = catalogo.get("UREIA")
    >>> logging.info(ureia.composicao)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FertilizanteFisico:
    """Representa um fertilizante granulado com propriedades fisicas e quimicas.

    Attributes:
        codigo: Codigo unico do fertilizante (ex: "UREIA", "MAP").
        nome: Nome comercial completo.
        composicao: Dicionario com percentuais garantidos de nutrientes.
            Chaves padrao: N, P2O5, K2O, CaO, MgO, S, B, Cu, Fe, Mn, Mo, Zn.
        densidade_aparente: Densidade aparente em kg/m3.
        sgn: Size Guide Number - tamanho medio das particulas em mm.
        angulo_repouso: Angulo de repouso em graus.
        custo_kg: Custo por kg em R$.
        inclusao_max_pct: Percentual maximo permitido na mistura (0-100).
        inclusao_min_pct: Percentual minimo permitido na mistura (0-100).
        umidade_pct: Teor de umidade percentual.
        hidroscopicidade: Nivel de absorcao de umidade (baixa/media/alta).
        reatividade: Nivel de reatividade quimica (baixa/media/alta).
    """
    codigo: str
    nome: str
    composicao: Dict[str, float]
    densidade_aparente: float  # kg/m3
    sgn: float  # mm
    angulo_repouso: float  # graus
    custo_kg: float  # R$/kg
    inclusao_max_pct: float = 100.0
    inclusao_min_pct: float = 0.0
    umidade_pct: float = 0.0
    hidroscopicidade: str = "baixa"
    reatividade: str = "baixa"

    def __post_init__(self):
        """Valida consistencia dos dados apos inicializacao."""
        if self.densidade_aparente <= 0:
            raise ValueError(f"Densidade deve ser positiva: {self.densidade_aparente}")
        if self.sgn <= 0:
            raise ValueError(f"SGN deve ser positivo: {self.sgn}")
        if not 0 <= self.inclusao_max_pct <= 100:
            raise ValueError(f"inclusao_max_pct deve estar entre 0 e 100: {self.inclusao_max_pct}")
        if not 0 <= self.inclusao_min_pct <= self.inclusao_max_pct:
            raise ValueError(
                f"inclusao_min_pct ({self.inclusao_min_pct}) deve ser <= "
                f"inclusao_max_pct ({self.inclusao_max_pct})"
            )

    @property
    def custo_ton(self) -> float:
        """Custo por tonelada em R$."""
        return self.custo_kg * 1000.0

    def teor_nutriente(self, nutriente: str) -> float:
        """Retorna o teor percentual de um nutriente especifico."""
        return self.composicao.get(nutriente.upper(), 0.0)


@dataclass(frozen=True)
class Incompatibilidade:
    """Representa uma incompatibilidade entre dois fertilizantes.

    Attributes:
        fertilizante_a: Codigo do primeiro fertilizante.
        fertilizante_b: Codigo do segundo fertilizante.
        severidade: Nivel de severidade ("bloqueante" ou "alerta").
        descricao: Descricao tecnica da incompatibilidade.
        mitigacao: Sugestao de mitigacao (se aplicavel).
    """
    fertilizante_a: str
    fertilizante_b: str
    severidade: str  # "bloqueante" | "alerta"
    descricao: str
    mitigacao: Optional[str] = None

    def __post_init__(self):
        if self.severidade not in ("bloqueante", "alerta"):
            raise ValueError(f"Severidade invalida: {self.severidade}")


# ============================================================
# CATALOGO PADRAO DE FERTILIZANTES
# ============================================================

CATALOGO_PADRAO: Dict[str, FertilizanteFisico] = {
    # --- FONTES DE NITROGENIO ---
    "UREIA": FertilizanteFisico(
        codigo="UREIA",
        nome="Ureia Granulada",
        composicao={"N": 45.0},
        densidade_aparente=750.0,
        sgn=2.5,
        angulo_repouso=32.0,
        custo_kg=3.20,
        inclusao_max_pct=50.0,
        hidroscopicidade="alta",
        reatividade="alta"
    ),
    "SALITRE": FertilizanteFisico(
        codigo="SALITRE",
        nome="Nitrato de Calcio",
        composicao={"N": 15.5, "CaO": 26.0},
        densidade_aparente=1050.0,
        sgn=2.8,
        angulo_repouso=30.0,
        custo_kg=4.50,
        inclusao_max_pct=40.0,
        hidroscopicidade="alta",
        reatividade="media"
    ),
    "MAP": FertilizanteFisico(
        codigo="MAP",
        nome="Fosfato Monoamonico",
        composicao={"N": 11.0, "P2O5": 52.0},
        densidade_aparente=950.0,
        sgn=3.0,
        angulo_repouso=28.0,
        custo_kg=5.80,
        inclusao_max_pct=60.0,
        hidroscopicidade="baixa",
        reatividade="baixa"
    ),
    "DAP": FertilizanteFisico(
        codigo="DAP",
        nome="Fosfato Diamonico",
        composicao={"N": 18.0, "P2O5": 46.0},
        densidade_aparente=900.0,
        sgn=3.2,
        angulo_repouso=29.0,
        custo_kg=5.50,
        inclusao_max_pct=60.0,
        hidroscopicidade="media",
        reatividade="media"
    ),

    # --- FONTES DE FOSFORO ---
    "SS": FertilizanteFisico(
        codigo="SS",
        nome="Superfosfato Simples",
        composicao={"P2O5": 18.0, "S": 12.0, "CaO": 20.0},
        densidade_aparente=1100.0,
        sgn=2.2,
        angulo_repouso=35.0,
        custo_kg=2.80,
        inclusao_max_pct=50.0,
        hidroscopicidade="media",
        reatividade="alta"
    ),
    "TS": FertilizanteFisico(
        codigo="TS",
        nome="Superfosfato Triplo",
        composicao={"P2O5": 41.0, "S": 1.5, "CaO": 14.0},
        densidade_aparente=1000.0,
        sgn=2.5,
        angulo_repouso=33.0,
        custo_kg=4.20,
        inclusao_max_pct=50.0,
        hidroscopicidade="baixa",
        reatividade="baixa"
    ),
    "FOSF_NIT": FertilizanteFisico(
        codigo="FOSF_NIT",
        nome="Fosfato Nitratado",
        composicao={"N": 12.0, "P2O5": 30.0},
        densidade_aparente=980.0,
        sgn=2.8,
        angulo_repouso=31.0,
        custo_kg=4.80,
        inclusao_max_pct=50.0,
        hidroscopicidade="media",
        reatividade="media"
    ),

    # --- FONTES DE POTASSIO ---
    "KCL": FertilizanteFisico(
        codigo="KCL",
        nome="Cloreto de Potassio (MOP)",
        composicao={"K2O": 60.0},
        densidade_aparente=1050.0,
        sgn=2.4,
        angulo_repouso=34.0,
        custo_kg=4.00,
        inclusao_max_pct=60.0,
        hidroscopicidade="baixa",
        reatividade="baixa"
    ),
    "K2SO4": FertilizanteFisico(
        codigo="K2SO4",
        nome="Sulfato de Potassio (SOP)",
        composicao={"K2O": 50.0, "S": 18.0},
        densidade_aparente=1100.0,
        sgn=2.6,
        angulo_repouso=33.0,
        custo_kg=6.50,
        inclusao_max_pct=50.0,
        hidroscopicidade="baixa",
        reatividade="baixa"
    ),

    # --- FONTES DE CALCIO E MAGNESIO ---
    "CAL_DOLO": FertilizanteFisico(
        codigo="CAL_DOLO",
        nome="Calcario Dolomitico",
        composicao={"CaO": 30.0, "MgO": 18.0},
        densidade_aparente=1200.0,
        sgn=1.5,
        angulo_repouso=38.0,
        custo_kg=0.35,
        inclusao_max_pct=80.0,
        hidroscopicidade="baixa",
        reatividade="baixa"
    ),
    "CAL_CALC": FertilizanteFisico(
        codigo="CAL_CALC",
        nome="Calcario Calcitico",
        composicao={"CaO": 50.0},
        densidade_aparente=1300.0,
        sgn=1.4,
        angulo_repouso=40.0,
        custo_kg=0.30,
        inclusao_max_pct=80.0,
        hidroscopicidade="baixa",
        reatividade="baixa"
    ),
    "OXIDO_MG": FertilizanteFisico(
        codigo="OXIDO_MG",
        nome="Oxido de Magnesio",
        composicao={"MgO": 55.0},
        densidade_aparente=800.0,
        sgn=1.8,
        angulo_repouso=36.0,
        custo_kg=3.50,
        inclusao_max_pct=30.0,
        hidroscopicidade="media",
        reatividade="media"
    ),

    # --- FONTES DE ENXOFRE ---
    "SULF_AMON": FertilizanteFisico(
        codigo="SULF_AMON",
        nome="Sulfato de Amonio",
        composicao={"N": 20.0, "S": 24.0},
        densidade_aparente=950.0,
        sgn=2.7,
        angulo_repouso=30.0,
        custo_kg=3.80,
        inclusao_max_pct=40.0,
        hidroscopicidade="media",
        reatividade="media"
    ),
    "S_ELEMENTAL": FertilizanteFisico(
        codigo="S_ELEMENTAL",
        nome="Enxofre Elemental",
        composicao={"S": 90.0},
        densidade_aparente=1800.0,
        sgn=0.3,
        angulo_repouso=45.0,
        custo_kg=2.50,
        inclusao_max_pct=20.0,
        hidroscopicidade="baixa",
        reatividade="baixa"
    ),

    # --- MICRONUTRIENTES ---
    "B_OXIDO": FertilizanteFisico(
        codigo="B_OXIDO",
        nome="Oxido de Boro",
        composicao={"B": 17.0},
        densidade_aparente=1400.0,
        sgn=1.2,
        angulo_repouso=42.0,
        custo_kg=18.00,
        inclusao_max_pct=5.0,
        hidroscopicidade="baixa",
        reatividade="baixa"
    ),
    "CHELATO_ZN": FertilizanteFisico(
        codigo="CHELATO_ZN",
        nome="Chelato de Zinco (EDTA)",
        composicao={"Zn": 15.0},
        densidade_aparente=600.0,
        sgn=0.5,
        angulo_repouso=35.0,
        custo_kg=45.00,
        inclusao_max_pct=5.0,
        hidroscopicidade="media",
        reatividade="media"
    ),
    "SULF_ZN": FertilizanteFisico(
        codigo="SULF_ZN",
        nome="Sulfato de Zinco",
        composicao={"Zn": 22.0, "S": 11.0},
        densidade_aparente=1100.0,
        sgn=1.5,
        angulo_repouso=33.0,
        custo_kg=12.00,
        inclusao_max_pct=5.0,
        hidroscopicidade="media",
        reatividade="media"
    ),
    "SULF_MN": FertilizanteFisico(
        codigo="SULF_MN",
        nome="Sulfato de Manganes",
        composicao={"Mn": 28.0, "S": 14.0},
        densidade_aparente=1150.0,
        sgn=1.4,
        angulo_repouso=34.0,
        custo_kg=10.00,
        inclusao_max_pct=5.0,
        hidroscopicidade="media",
        reatividade="media"
    ),
    "SULF_CU": FertilizanteFisico(
        codigo="SULF_CU",
        nome="Sulfato de Cobre",
        composicao={"Cu": 25.0, "S": 13.0},
        densidade_aparente=1200.0,
        sgn=1.3,
        angulo_repouso=36.0,
        custo_kg=15.00,
        inclusao_max_pct=5.0,
        hidroscopicidade="media",
        reatividade="media"
    ),
    "MOLIBDATO": FertilizanteFisico(
        codigo="MOLIBDATO",
        nome="Molibdato de Amonio",
        composicao={"Mo": 54.0},
        densidade_aparente=1300.0,
        sgn=1.0,
        angulo_repouso=38.0,
        custo_kg=80.00,
        inclusao_max_pct=2.0,
        hidroscopicidade="baixa",
        reatividade="baixa"
    ),
    "FERRO_CHEL": FertilizanteFisico(
        codigo="FERRO_CHEL",
        nome="Chelato de Ferro (EDDHA)",
        composicao={"Fe": 6.0},
        densidade_aparente=550.0,
        sgn=0.4,
        angulo_repouso=35.0,
        custo_kg=55.00,
        inclusao_max_pct=5.0,
        hidroscopicidade="media",
        reatividade="media"
    ),
}


# ============================================================
# INCOMPATIBILIDADES PADRAO
# ============================================================

INCOMPATIBILIDADES_PADRAO: List[Incompatibilidade] = [
    Incompatibilidade(
        fertilizante_a="UREIA",
        fertilizante_b="SS",
        severidade="bloqueante",
        descricao=(
            "Ureia reage com o acido fosforico livre do Superfosfato Simples, "
            "causando degradacao do nitrogenio e aumento de umidade."
        ),
        mitigacao="Usar Superfosfato Triplo (TS) ou adicionar condicionante (ex: talco) antes da mistura."
    ),
    Incompatibilidade(
        fertilizante_a="UREIA",
        fertilizante_b="SALITRE",
        severidade="alerta",
        descricao="Ambos sao altamente higroscopicos. A mistura tende a absorver umidade rapidamente.",
        mitigacao="Reduzir tempo de exposicao ao ar e usar embalagem impermeavel."
    ),
    Incompatibilidade(
        fertilizante_a="KCL",
        fertilizante_b="CAL_DOLO",
        severidade="alerta",
        descricao="Diferenca de densidade muito grande pode causar segregacao durante transporte.",
        mitigacao="Aplicar imediatamente apos mistura ou usar condicionante."
    ),
    Incompatibilidade(
        fertilizante_a="S_ELEMENTAL",
        fertilizante_b="UREIA",
        severidade="alerta",
        descricao="Enxofre elementar fino pode adsorver NH3 volatilizado da ureia.",
        mitigacao="Nao armazenar mistura por mais de 7 dias."
    ),
    Incompatibilidade(
        fertilizante_a="DAP",
        fertilizante_b="CAL_CALC",
        severidade="alerta",
        descricao="Reacao de neutralizacao pode reduzir a disponibilidade de fosforo.",
        mitigacao="Aplicar em ate 48h ou usar TS em vez de DAP."
    ),
]


# ============================================================
# CLASSE CATALOGO
# ============================================================

class CatalogoFertilizantes:
    """Gerencia o catalogo de fertilizantes e suas incompatibilidades.

    Esta classe fornece metodos para consultar fertilizantes, verificar
    compatibilidades e filtrar por tipo de nutriente.

    Args:
        catalogo: Dicionario opcional com fertilizantes. Usa CATALOGO_PADRAO se None.
        incompatibilidades: Lista opcional de incompatibilidades. Usa padrao se None.

    Example:
        >>> catalogo = CatalogoFertilizantes()
        >>> ureia = catalogo.get("UREIA")
        >>> fontes_n = catalogo.por_nutriente("N")
        >>> incompat = catalogo.verificar_incompatibilidade("UREIA", "SS")
    """

    def __init__(
        self,
        catalogo: Optional[Dict[str, FertilizanteFisico]] = None,
        incompatibilidades: Optional[List[Incompatibilidade]] = None
    ):
        self._catalogo = catalogo or CATALOGO_PADRAO.copy()
        self._incompatibilidades = incompatibilidades or INCOMPATIBILIDADES_PADRAO.copy()
        logger.info(
            "Catalogo inicializado com %d fertilizantes e %d incompatibilidades",
            len(self._catalogo), len(self._incompatibilidades)
        )

    def get(self, codigo: str) -> Optional[FertilizanteFisico]:
        """Retorna um fertilizante pelo codigo.

        Args:
            codigo: Codigo do fertilizante (case-insensitive).

        Returns:
            Instancia de FertilizanteFisico ou None se nao encontrado.
        """
        return self._catalogo.get(codigo.upper())

    def listar_todos(self) -> List[FertilizanteFisico]:
        """Retorna lista com todos os fertilizantes do catalogo."""
        return list(self._catalogo.values())

    def listar_codigos(self) -> List[str]:
        """Retorna lista com todos os codigos."""
        return list(self._catalogo.keys())

    def por_nutriente(self, nutriente: str, min_teor: float = 1.0) -> List[FertilizanteFisico]:
        """Filtra fertilizantes que contenham um nutriente especifico.

        Args:
            nutriente: Sigla do nutriente (ex: "N", "P2O5", "K2O").
            min_teor: Teor minimo percentual para inclusao.

        Returns:
            Lista de fertilizantes ordenados por teor decrescente.
        """
        nutriente = nutriente.upper()
        resultado = [
            f for f in self._catalogo.values()
            if f.composicao.get(nutriente, 0.0) >= min_teor
        ]
        resultado.sort(key=lambda x: x.composicao.get(nutriente, 0.0), reverse=True)
        return resultado

    def verificar_incompatibilidade(
        self,
        codigo_a: str,
        codigo_b: str
    ) -> Optional[Incompatibilidade]:
        """Verifica se dois fertilizantes sao incompativeis.

        Args:
            codigo_a: Codigo do primeiro fertilizante.
            codigo_b: Codigo do segundo fertilizante.

        Returns:
            Incompatibilidade encontrada ou None.
        """
        codigo_a = codigo_a.upper()
        codigo_b = codigo_b.upper()
        for inc in self._incompatibilidades:
            if (inc.fertilizante_a == codigo_a and inc.fertilizante_b == codigo_b) or \
               (inc.fertilizante_a == codigo_b and inc.fertilizante_b == codigo_a):
                return inc
        return None

    def listar_incompatibilidades(self, codigo: str) -> List[Incompatibilidade]:
        """Lista todas as incompatibilidades de um fertilizante.

        Args:
            codigo: Codigo do fertilizante.

        Returns:
            Lista de incompatibilidades.
        """
        codigo = codigo.upper()
        return [
            inc for inc in self._incompatibilidades
            if inc.fertilizante_a == codigo or inc.fertilizante_b == codigo
        ]

    def adicionar_fertilizante(self, fertilizante: FertilizanteFisico) -> None:
        """Adiciona um novo fertilizante ao catalogo.

        Args:
            fertilizante: Instancia de FertilizanteFisico.

        Raises:
            ValueError: Se o codigo ja existir no catalogo.
        """
        if fertilizante.codigo.upper() in self._catalogo:
            raise ValueError(f"Fertilizante {fertilizante.codigo} ja existe no catalogo.")
        self._catalogo[fertilizante.codigo.upper()] = fertilizante
        logger.info("Fertilizante %s adicionado ao catalogo.", fertilizante.codigo)

    def adicionar_incompatibilidade(self, inc: Incompatibilidade) -> None:
        """Adiciona uma nova incompatibilidade."""
        self._incompatibilidades.append(inc)
        logger.info(
            "Incompatibilidade %s <-> %s adicionada.",
            inc.fertilizante_a, inc.fertilizante_b
        )


# ============================================================
# CONSTANTES FISICAS
# ============================================================

# Tolerancia maxima de diferenca de SGN para evitar segregacao (%)
TOLERANCIA_SGN_PCT = 15.0

# Tolerancia maxima de diferenca de densidade para evitar segregacao (%)
TOLERANCIA_DENSIDADE_PCT = 20.0

# Angulo de repouso maximo aceitavel para escoamento (graus)
ANGULO_REPOUSO_MAXIMO = 40.0

# Umidade maxima aceitavel na mistura final (%)
UMIDADE_MAXIMA_BLEND = 3.0

# Tolerancia nutricional na otimizacao (%)
TOLERANCIA_NUTRICIONAL_PCT = 5.0


