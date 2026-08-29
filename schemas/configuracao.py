"""
Schemas Pydantic do módulo Configurações — Precision VRT Solo.

Responsabilidade: validação e serialização de dados do model ConfigSistema.
Zero lógica de negócio. Zero acesso ao banco.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# =========================================================================
# GRUPO: EMPRESA
# =========================================================================

class EmpresaBase(BaseModel):
    """Dados da empresa proprietária do sistema."""
    nome_empresa: Optional[str] = Field(default=None, max_length=255)
    slogan: Optional[str] = Field(default=None, max_length=255)
    nome_fantasia: Optional[str] = Field(default=None, max_length=255)
    cnpj: Optional[str] = Field(default=None, max_length=14)
    responsavel_tecnico: Optional[str] = Field(default=None, max_length=255)
    crea: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)
    telefone: Optional[str] = Field(default=None, max_length=20)


# =========================================================================
# GRUPO: SISTEMA
# =========================================================================

class SistemaBase(BaseModel):
    """Dados de identificação e comportamento do software."""
    nome_software: Optional[str] = Field(default="Precision VRT Solo", max_length=100)
    versao: Optional[str] = Field(default=None, max_length=20)
    idioma: Optional[str] = Field(default="pt-BR", max_length=10)
    tema: Optional[str] = Field(default="auto", max_length=10)


# =========================================================================
# GRUPO: LOCALIZAÇÃO
# =========================================================================

class LocalizacaoBase(BaseModel):
    """Localização padrão para novos cadastros."""
    cidade_padrao: Optional[str] = Field(default=None, max_length=100)
    estado_padrao: Optional[str] = Field(default=None, max_length=2)


# =========================================================================
# GRUPO: AUDITORIA
# =========================================================================

class AuditoriaBase(BaseModel):
    """Controles de auditoria e rastreabilidade."""
    auditoria_ativa: bool = Field(default=True)


# =========================================================================
# GRUPO: METODOLOGIA (herdado da versão anterior)
# =========================================================================

class MetodologiaBase(BaseModel):
    """Metodologia agronômica padrão do sistema."""
    metodologia_padrao_id: Optional[str] = Field(default="IAC_Graos", max_length=100)


# =========================================================================
# SCHEMAS COMPLETOS
# =========================================================================

class ConfiguracaoSistemaBase(BaseModel):
    """Schema base com todos os campos do model ConfigSistema.

    Usado como fundação para Create, Update e Response.
    """
    model_config = ConfigDict(extra="forbid")

    tenant_id: UUID

    empresa: EmpresaBase = Field(default_factory=EmpresaBase)
    sistema: SistemaBase = Field(default_factory=SistemaBase)
    localizacao: LocalizacaoBase = Field(default_factory=LocalizacaoBase)
    auditoria: AuditoriaBase = Field(default_factory=AuditoriaBase)
    metodologia: MetodologiaBase = Field(default_factory=MetodologiaBase)


class ConfiguracaoSistemaCreate(ConfiguracaoSistemaBase):
    """Schema para criação de uma nova configuração de sistema.

    Herda todos os campos de ConfiguracaoSistemaBase.
    O campo id é gerado automaticamente pelo banco.
    """
    pass


class ConfiguracaoSistemaUpdate(BaseModel):
    """Schema para atualização parcial de configuração de sistema.

    Todos os campos são opcionais — permite PATCH sem enviar dados
    de grupos que não serão alterados.
    """
    model_config = ConfigDict(extra="forbid")

    empresa: Optional[EmpresaBase] = None
    sistema: Optional[SistemaBase] = None
    localizacao: Optional[LocalizacaoBase] = None
    auditoria: Optional[AuditoriaBase] = None
    metodologia: Optional[MetodologiaBase] = None


class ConfiguracaoSistemaResponse(BaseModel):
    """Schema de resposta para leitura de configuração de sistema.

    Inclui campos de controle (id, timestamps, ativo) além dos dados.
    Configurado para trabalhar com SQLAlchemy via from_attributes.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    empresa: EmpresaBase
    sistema: SistemaBase
    localizacao: LocalizacaoBase
    auditoria: AuditoriaBase
    metodologia: MetodologiaBase
