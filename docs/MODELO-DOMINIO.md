# Precision VRT Solo — Modelo de Domínio
# Documento Contrato entre Interface, Core e Banco de Dados
# Versão: 1.1

## 🎯 Objetivo
Definir as entidades fundamentais do sistema para garantir consistência entre interface, core e banco de dados. Este documento serve como "contrato" para evitar retrabalho ao integrar novos módulos.

> **Fonte de verdade:** Banco SQLite ativo (`precision_vrt.db`) + modelos ORM em `models/`.  
> Banco de auditoria documental: 30 tabelas (29 de aplicação + `sqlite_sequence`).  
> Banco adicional `db/precision.db` (legado/incremental): tabela `empresas`.

---

## 🗄️ Tabelas Reais no Banco Ativo (`precision_vrt.db`)

| # | Tabela | Cols | Domínio |
|---|--------|------|---------|
| 01 | `tenants` | 5 | Multi-tenancy |
| 02 | `usuarios` | 7 | Identidade / RBAC |
| 03 | `funcionarios` | 8 | Pessoas físicas (clientes/equipe) |
| 04 | `clientes` | 14 | CRM |
| 05 | `fazendas` | 6 | Propriedades rurais |
| 06 | `talhoes` | 6 | Subdivisão de fazenda |
| 07 | `orcamentos` | 11 | Comercial |
| 08 | `orcamento_itens` | 6 | Itens do orçamento |
| 09 | `vendas` | 9 | Comercial |
| 10 | `servicos_precos` | 6 | Catálogo |
| 11 | `prescricao` | 8 | Motor VRT |
| 12 | `analises_compactacao` | 15 | Agronomia |
| 13 | `pontos_compactacao` | 9 | Amostragem compactação |
| 14 | `camadas_compactacao` | 7 | Camadas temáticas |
| 15 | `curvas_nutritivas` | 35 | Curvas de resposta |
| 16 | `leituras_extrator` | 24 | Sensoriamento |
| 17 | `pontos_extrator` | 20 | Sensoriamento |
| 18 | `regras_escala_volume` | 4 | Regras |
| 19 | `logs_envio` | 13 | Comunicação |
| 20 | `config_comunicacao` | 17 | Configuração |
| 21 | `artigos_conhecimento` | 9 | Base técnica |
| 22 | `clima_historico_laudo` | 12 | Clima |
| 23 | `ativos_patrimoniais` | 14 | Patrimônio |
| 24 | `titulos_financeiros` | 18 | Financeiro |
| 25 | `config_fiscal` | 11 | Fiscal |
| 26 | `notas_fiscais` | 15 | Fiscal |
| 27 | `config_sistema` | 6 | Configuração geral |
| 28 | `auditoria_eventos` | 14 | Auditoria |
| 29 | `auditoria_filtros` | 6 | Filtros salvos |

---

## 🏗️ Entidades Principais (Camada de Domínio)

### 1. Tenant
```python
@dataclass
class Tenant:
    id: str
    nome: str
    cnpj: Optional[str]
    ativo: bool
    created_at: datetime
```
- Fronteira de segurança multi-tenant.
- Toda entidade de negócio referencia um `tenant_id`.

### 2. Usuário
```python
@dataclass
class Usuario:
    id: str
    tenant_id: str
    nome: str
    email: str
    senha_hash: str
    perfil: str  # "admin", "gerente", "operador", "visualizador"
    ativo: bool
    created_at: datetime
```
- Autenticação via JWT + cookie HttpOnly.
- Hash de senha PBKDF2-SHA256.
- Perfil → conjunto de permissões via `PERMISSION_MAP`.

### 3. Cliente
```python
@dataclass
class Cliente:
    id: str
    tenant_id: str
    nome: str
    cpf_cnpj: str
    email: Optional[str]
    telefone: Optional[str]
    endereco: Optional[str]
    cidade: Optional[str]
    estado: Optional[str]
    cep: Optional[str]
    observacoes: Optional[str]
    ativo: bool
    created_at: datetime
    updated_at: Optional[datetime]
```
- Fonte única para CRM, Financeiro e Operações.
- Pode ter **múltiplas Empresas (CNPJs)** vinculadas.

### 4. Empresa (CNPJ vinculado ao Cliente)
```python
@dataclass
class Empresa:
    id: str
    cliente_id: str
    cnpj: str
    nome_fantasia: str
    razao_social: str
    tenant_id: str
    created_at: datetime
```
- Multi-Empresa por Cliente.
- CRUD implementado em `app/web/empresas.py`.

### 5. Funcionário
```python
@dataclass
class Funcionario:
    id: str
    tenant_id: str
    nome: str
    cargo: str
    cpf: Optional[str]
    salario_base: Optional[float]
    comissao_percentual: Optional[float]
    ativo: bool
    created_at: datetime
```

### 6. Fazenda / Propriedade
```python
@dataclass
class Fazenda:
    id: str
    cliente_id: str
    tenant_id: str
    nome: str
    area_total: float
    localizacao: Optional[str]
```

### 7. Talhão
```python
@dataclass
class Talhao:
    id: str
    fazenda_id: str
    nome: str
    area: float
    coordenadas: Optional[str]
```

### 8. Orçamento
```python
@dataclass
class Orcamento:
    id: str
    tenant_id: str
    cliente_id: str
    vendedor_id: Optional[str]
    validade: datetime
    status: str
    valor_total: float
    condicoes: Optional[str]
    observacoes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
```
- Conectado a `orcamento_itens` (N itens).
- Pode virar `venda` ao ser aprovado.

### 9. Venda
```python
@dataclass
class Venda:
    id: str
    tenant_id: str
    cliente_id: str
    orcamento_id: Optional[str]
    valor_total: float
    status: str
    data_venda: datetime
    observacoes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
```

### 10. Prescrição VRT
```python
@dataclass
class Prescricao:
    id: str
    tenant_id: str
    cliente_id: Optional[str]
    talhao_id: Optional[str]
    safra: Optional[str]
    metodologia: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
```
- Núcleo do motor agronômico.
- Snapshot do contexto no momento da geração.

### 11. Análise de Compactação
```python
@dataclass
class AnaliseCompactacao:
    id: str
    tenant_id: str
    cliente_id: Optional[str]
    talhao_id: Optional[str]
    profundidade: float
    densidade: float
    resistencia: float
    umidade: float
    data_coleta: datetime
    responsavel: Optional[str]
    metodologia: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    observacoes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
```

### 12. Pontos / Camadas de Compactação
- `pontos_compactacao` — pontos amostrais georreferenciados.
- `camadas_compactacao` — camadas temáticas derivadas.

### 13. Curvas Nutritivas
- `curvas_nutritivas` — 35 colunas; tabelas de resposta por cultura × nutriente.

### 14. Leituras / Pontos do Extrator
- `leituras_extrator` (24 colunas) e `pontos_extrator` (20 colunas).
- Dados de campo coletados por sensores/extrator.

### 15. Base Técnica (Conhecimento)
- `artigos_conhecimento` — repositório de culturas, metodologias, bibliografia.

### 16. Patrimônio
```python
@dataclass
class AtivoPatrimonial:
    id: str
    tenant_id: str
    nome: str
    categoria: str
    identificacao: str
    data_aquisicao: datetime
    valor_aquisicao: float
    valor_atual: Optional[float]
    responsavel: Optional[str]
    localizacao: Optional[str]
    estado: str
    ultima_manutencao: Optional[datetime]
    proxima_manutencao: Optional[datetime]
    observacoes: Optional[str]
```

### 17. Financeiro / Títulos
- `titulos_financeiros` — 18 colunas: receitas, despesas, comissões, salários, controle de inadimplência.

### 18. Fiscal
- `config_fiscal` + `notas_fiscais` — preparo para integração contábil.

### 19. Configuração do Sistema
```python
@dataclass
class ConfigSistema:
    id: int
    tenant_id: str
    chave: str
    valor: str
    updated_at: datetime
```

### 20. Comunicação
- `config_comunicacao` + `logs_envio` — canais de envio e logs de execução.

### 21. Auditoria
```python
@dataclass
class AuditoriaEvento:
    id: str
    tenant_id: str
    usuario_id: Optional[str]
    modulo: str
    acao: str
    entidade: str
    entidade_id: Optional[str]
    dados_antes: Optional[str]   # JSON
    dados_depois: Optional[str]  # JSON
    ip: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime
    justificativa: Optional[str]
```
- `auditoria_filtros` — filtros salvos pelo usuário.

### 22. Clima / Histórico para Laudo
- `clima_historico_laudo` — 12 colunas; insumo para laudos técnicos.

### 23. Regras de Escala / Volume
- `regras_escala_volume` — parametrização de cálculo de volume/escala.

---

## 🎯 Enumerações (status e tipos)

| Enum | Valores |
|------|---------|
| `SafraStatus` | `planejada`, `em_andamento`, `concluida` |
| `PrescricaoStatus` | `rascunho`, `validada`, `aprovada`, `aplicada` |
| `TipoCamada` | `indice_espectral`, `mapa_produtividade`, `mapa_compactacao`, `mapa_umidade`, `mapa_condutividade`, `mapa_altitude`, `mapa_declividade`, `mapa_relevo`, `mapa_drone`, `mapa_sensor`, `mapa_laboratorio`, `outro` |
| `TipoIndice` | `NDVI`, `NDRE`, `GNDVI`, `EVI`, `SAVI`, `MSAVI`, `OSAVI`, `VARI`, `ARVI`, `CCCI`, `SIPI`, `MCARI`, `MTVI2`, `CI_Green`, `CI_Red_Ege`, `LAI`, `FAPAR`, `Fractional_Cover`, `Biomassa`, `Clorofila`, `Estresse_Hidrico`, `Temperatura` |
| `TipoExportacao` | `caderno_tecnico`, `cartao_cabine`, `maquina` |

---

## 🎯 Relacionamentos entre Entidades

```
Tenant ──┬──> Usuario (tenant_id)
         ├──> Cliente (tenant_id)
         ├──> Fazenda (tenant_id)
         ├──> Orcamento (tenant_id)
         ├──> Venda (tenant_id)
         ├──> Prescricao (tenant_id)
         ├──> AtivoPatrimonial (tenant_id)
         ├──> TituloFinanceiro (tenant_id)
         └──> AuditoriaEvento (tenant_id)

Cliente ──┬──> Empresa (cliente_id)  [MULTI-CNPJ]
          ├──> Fazenda (cliente_id)
          ├──> Orcamento (cliente_id)
          ├──> Venda (cliente_id)
          └──> Prescricao (cliente_id)

Fazenda ──> Talhao (fazenda_id)

Orcamento ──> OrcamentoItem (orcamento_id)
Orcamento ──> Venda (orcamento_id)   [quando aprovado]

Prescricao ──┬──> AnaliseCompactacao (cliente_id/talhao_id)
             ├──> PontosCompactacao (cliente_id/talhao_id)
             └──> CamadasCompactacao (cliente_id/talhao_id)

LeituraExtrator ──> PontoExtrator (ponto_id)
CurvaNutritiva (referência por cultura × nutriente)

ConfigComunicacao ──> LogEnvio (config_id)
ConfigFiscal ──> NotaFiscal (config_id)
ConfigSistema (chave/valor por tenant)

AuditoriaEvento (transversal — qualquer entidade pode gerar evento)
AuditoriaFiltro (salvo por usuário para consultas)
```

---

## 🎯 Regras de Negócio

### 1. Regra de Tenant (Multi-tenancy)
- **Toda entidade de negócio DEVE ter `tenant_id`.**
- Filtros de consulta DEVEM sempre incluir `tenant_id`.
- Não existe leitura ou escrita cross-tenant.

### 2. Regra de Cliente como Fonte Única
- **Cliente único** = fonte de verdade para todos os módulos.
- Um cliente pode ter **múltiplas Empresas (CNPJs)** e **múltiplas Fazendas**.

### 3. Regra de Safras
- Sempre que o domínio agrícola exigir, referenciar `safra` como string (`"2024"`, `"2024-2025"`).
- Permitir combinação de múltiplas safras (não assumir anos específicos).

### 4. Regra de Camadas Temáticas
- Usar abstração comum (`camadas_compactacao`) em vez de tipos específicos.
- O motor não deve conhecer tipos específicos (NDVI, NDRE etc.) — extensão por novos tipos em `TipoCamada`.

### 5. Regra de Auditoria
- Toda mutação relevante DEVE gerar evento em `auditoria_eventos`.
- Histórico imutável: correção gera novo evento, não sobrescreve.

### 6. Regra de Configuração como Source of Truth
- Parâmetros técnicos (metodologias, faixas, regras) ficam em `config_sistema`, `config_fiscal`, `config_comunicacao`.
- Não há valores hardcoded em código de negócio.

### 7. Empty State ≠ Erro
| Cenário | Resposta |
|---------|----------|
| Consulta OK + 0 resultados | EMPTY STATE LEGÍTIMO |
| Consulta falhou | ERRO (não mascarar com `[]` ou `0`) |
| Permissão negada | 403 |
| Não autenticado | 401 |

---

## 🎯 Contratos entre Camadas

### Interface ↔ Core
- Interface envia DTOs simples, Core orquestra serviços.
- Interface nunca manipula diretamente entidades do Core.

### Core ↔ Banco de Dados
- Core usa entidades do Modelo de Domínio.
- Banco armazena entidades do Modelo de Domínio.
- Core isola a lógica de negócio do acesso a dados.

### Core ↔ Config
- Core lê de `config_sistema` (chave/valor por tenant).
- Configuração é injetada, não hardcoded.

### Auth ↔ Request
- Identidade extraída do cookie HttpOnly via `app/web/auth_dependencies.py`.
- `require_permission_web(permissao)` valida RBAC e injeta contexto.

---

## 🎯 Versionamento

**Versão:** 1.1  
**Data da última atualização:** 2026-09-01  
**Mudanças nesta versão:**
- Inclusão de `tenants`, `empresas`, `auditoria_eventos`, `auditoria_filtros`
- Mapeamento tabular direto com `precision_vrt.db` (29 tabelas de aplicação)
- Tabela adicional `empresas` em `db/precision.db` (banco incremental)
- Contratos de Auth via cookie HttpOnly
