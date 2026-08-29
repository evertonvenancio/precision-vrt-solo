
"""
Precision VRT Solo - Configuração do Motor

Configurações para o motor de prescrição VRT.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ConfigPrescricao:
    """Configuração do motor de prescrição VRT."""
    
    # Limites de aplicação
    limite_n_max: float = 300.0
    limite_p_max: float = 150.0
    limite_k_max: float = 200.0
    limite_ca_max: float = 2000.0
    limite_mg_max: float = 200.0
    limite_s_max: float = 100.0
    
    # Limites micro
    limite_b_max: float = 2.0
    limite_cu_max: float = 5.0
    limite_fe_max: float = 50.0
    limite_mn_max: float = 20.0
    limite_mo_max: float = 5.0
    limite_zn_max: float = 10.0
    
    # Configurações de cálculo
    custo_n: float = 2.50
    custo_p: float = 3.00
    custo_k: float = 1.80
    custo_ca: float = 0.50
    custo_mg: float = 0.60
    custo_s: float = 1.20
    
    # Limites de aplicação em kg/ha
    LIMITES_MICRO = {
        'B': 2.0,
        'Cu': 5.0,
        'Fe': 50.0,
        'Mn': 20.0,
        'Mo': 5.0,
        'Zn': 10.0
    }
    
    def __post_init__(self):
        """Valida configurações após inicialização."""
        if self.limite_n_max <= 0:
            raise ValueError("Limite de N deve ser positivo")
        if self.limite_p_max <= 0:
            raise ValueError("Limite de P deve ser positivo")
        if self.limite_k_max <= 0:
            raise ValueError("Limite de K deve ser positivo")
    
    def get_custo_nutriente(self, nutriente: str) -> float:
        """Retorna o custo por unidade do nutriente."""
        custos = {
            'N': self.custo_n,
            'P': self.custo_p,
            'K': self.custo_k,
            'Ca': self.custo_ca,
            'Mg': self.custo_mg,
            'S': self.custo_s
        }
        return custos.get(nutriente, 0.0)
    
    def get_limite_nutriente(self, nutriente: str) -> float:
        """Retorna o limite de aplicação do nutriente."""
        limites = {
            'N': self.limite_n_max,
            'P': self.limite_p_max,
            'K': self.limite_k_max,
            'Ca': self.limite_ca_max,
            'Mg': self.limite_mg_max,
            'S': self.limite_s_max
        }
        return limites.get(nutriente, 0.0)

# Instância global de configuração
INSTANCIA_CONFIG = ConfigPrescricao()

__all__ = [
    'ConfigPrescricao',
    'INSTANCIA_CONFIG'
]
