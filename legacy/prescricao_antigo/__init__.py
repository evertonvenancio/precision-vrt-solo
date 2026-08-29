"""
Precision VRT Solo — Módulo de Prescrição Agronômica

Calcula recomendacoes de fertilizantes e corretivos por zona de manejo
com base em metodologias tecnicas brasileiras consolidadas:
  • IAC — Boletim Tecnico 100 (van Raij et al., 1996)
  • CFSEMG — Comissao de Fertilidade do Solo do Estado de Minas Gerais
  • Embrapa — Manuais regionais de adubacao e calagem
  • CONAMA 357/2005 — Guardrail ambiental para fosforo

Suporta:
  • Macronutrientes: N, P2O5, K2O, Ca, Mg, S
  • Micronutrientes: B, Cu, Fe, Mn, Zn
  • Corretivos: calagem, gessagem
  • Qualquer cultura e metodologia cadastrada em CONFIG
  • Qualquer quantidade de zonas geradas pelo Zoneador
  • Multiplas safras
  • Mapas auxiliares (NDVI, produtividade, compactacao, umidade, CE)
  • Analises laboratoriais padronizadas

Guardrail ambiental: P > 40 mg/dm3 bloqueia P2O5 (CONAMA 357/2005).

NOVO: Interface CamadaTematica e Motor Composto para arquitetura extensível.
"""

from .configuracao import ConfigPrescricao
from .contratos import (
    NotasTecnicas,
    PrescricaoZona,
    ResumoPrescricao,
    ResultadoCorretivo,
    ResultadoNutriente,
    ResultadoPrescricao,
    StatusNutriente,
    TipoCorretivo,
)
from .motor import MotorPrescricao
from .validacao import (
    calcular_custo_nutriente,
    calcular_dose_corrigida,
    calcular_exportacao,
    classificar_status_nutriente,
    get_parametros_metodo,
)

# Importar interfaces de tipos - COMENTADO PARA DESBLOQUEAR INICIALIZAÇÃO
# As classes serão implementadas posteriormente
# from ..tipos.camada_tematica import (
#     CamadaTematicaInterface,
#     CamadaTematicaBase,
#     IndiceEspectral,
#     MapaProdutividade,
#     MapaCompactacao,
#     MapaUmidade,
#     MapaLaboratorio,
#     FabricaCamadasTematicas,
#     CombinadorCamadas,
#     TipoCamada,
#     TipoIndice
# )

__all__ = [
    # Motor principal (legado para compatibilidade)
    "MotorPrescricao",
    
    # Configuracao
    "ConfigPrescricao",
    
    # Contratos / Modelos
    "ResultadoNutriente",
    "ResultadoCorretivo",
    "PrescricaoZona",
    "ResumoPrescricao",
    "NotasTecnicas",
    "ResultadoPrescricao",
    "StatusNutriente",
    "TipoCorretivo",
    
    # Funcoes auxiliares
    "calcular_exportacao",
    "get_parametros_metodo",
    "classificar_status_nutriente",
    "calcular_dose_corrigida",
    "calcular_custo_nutriente",
]
