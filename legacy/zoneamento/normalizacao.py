# MIGRADO para core/zoneamento/ em 2026-08-04

Este arquivo foi movido de core/zoneamento/ para legacy/zoneamento/ durante a
reestruturação do módulo Zoneamento na ETAPA Z2.

Motivo da migração:
- A implementação original usava pandas em vez de numpy puro
- Dependia de classes que não existiam nos novos contratos
- Era incompatível com a nova arquitetura modular solicitada

A nova implementação está em:
- core/zoneamento/normalizacao.py (reescrito do zero)
- core/zoneamento/utils/matriz.py (funções auxiliares)

Para referência, a implementação original continha:
- normalizar_dados() com StandardScaler, MinMaxScaler, RobustScaler
- preparar_dados() com preenchimento de nulos
- Dependências de pandas e sklearn.preprocessing

Versão original:
- Autor: Hermes Agent
- Data de criação: Não registrada (implementado durante sessão de desenvolvimento)
- Linhas: 74

"""Precision VRT Solo — Normalização do Módulo de Zoneamento (LEGACY)

Implementação original movida para referência durante reestruturação Z2.
"""
