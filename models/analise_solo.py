"""
Precision VRT Solo — Modelo Análise Solo

Representa apenas resultados laboratoriais.
Nunca calcular, nunca interpretar.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseModel
from .amostra_solo import AmostraSolo

class AnaliseSolo(BaseModel):
    """
    Modelo de dados de análise de solo.
    Contém apenas atributos básicos dos resultados laboratoriais.
    """
    
    amostra_id: str  # Relacionamento com AmostraSolo
    laboratorio: Optional[str] = None
    data_analise: Optional[datetime] = None
    ph_cacl2: Optional[float] = None
    ph_h2o: Optional[float] = None
    mo: Optional[float] = None  # Matéria Orgânica %
    p_mehlich1: Optional[float] = None  # mg/dm³
    k_mehlich1: Optional[float] = None  # mg/dm³
    ca_mehlich1: Optional[float] = None  # cmolc/dm³
    mg_mehlich1: Optional[float] = None  # cmolc/dm³
    al_mehlich1: Optional[float] = None  # cmolc/dm³
    h_mehlich1: Optional[float] = None  # cmolc/dm³
    v_mehlich1: Optional[float] = None  # %
    t_mehlich1: Optional[float] = None  # cmolc/dm³
    s_mehlich1: Optional[float] = None  # cmolc/dm³
    b_mehlich1: Optional[float] = None  # %
    bs_mehlich1: Optional[float] = None  # %
    saturacao_base: Optional[float] = None  # %
    saturacao_aluminio: Optional[float] = None  # %
    argila: Optional[float] = None  # %
    silte: Optional[float] = None  # %
    areia: Optional[float] = None  # %
    textura_classe: Optional[str] = None
    resultados_complementares: Optional[Dict[str, Any]] = None
    observacoes: Optional[str] = None
    
    def __init__(self, amostra_id: str, **kwargs):
        super().__init__(**kwargs)
        self.amostra_id = amostra_id