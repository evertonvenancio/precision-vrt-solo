# CHANGELOG.md
## Changelog do Precision VRT Solo

> **Fonte de verdade:** Histórico do Git (`git log`).  
> Cada entrada abaixo corresponde a um commit real do repositório.

---

## [Não versionado] — 2026-09-01
### Documentação
- `[DOCS]` Atualizar AGENTS.md para linguagem neutra do executor (`676e7f0`)

---

## [1.1.0] — 2026-08-31
### Novas Funcionalidades
- **Multi-Empresa por Cliente** — CRUD completo de CNPJs vinculados a um cliente (`9c75216`, `01b6e60`)
  - `models/empresa.py` — modelo ORM
  - `app/services/empresa_service.py` — service
  - `app/web/empresas.py` — rotas web
  - `app/templates/empresas_lista.html` + `empresas_form.html`
  - Botão "Empresas" na listagem de clientes (`clientes.html`)

### Mudanças
- **Reorganização da sidebar** em 8 grupos lógicos: DASHBOARD, COMERCIAL, AGRONOMIA, CONHECIMENTO, BIBLIOTECA, FINANCEIRO, ADMINISTRAÇÃO, CONFIGURAÇÃO (`9860707`)
  - Removido menu "Empresas" redundante do sidebar
  - Submenu "Conhecimento" dividido em Culturas, Metodologias e Bibliografia
  - Submenu "Biblioteca" isolado de "Conhecimento"

### Correções
- Templates de base técnica (Culturas / Metodologias / Bibliografia) e rotas corrigidas (`9860707`)

---

## [1.0.1] — 2026-08-29
### Mudanças
- Migração completa para autenticação via cookie HttpOnly em 28 rotas web (`a4eeba3`)
- Criação de `app/web/auth_dependencies.py` com `require_permission_web`
- Substituição de `HTTPBearer` por `get_token_from_cookie` em todos os roteadores

### Documentação
- Atualização do README e RELATORIO_FINAL com status operacional (`b9936bc`)

### Correções
- Duplicação de paths em 15 roteadores web corrigida; 7 roteadores faltantes criados (`435af6c`)
- TypeError em `base.html` (`group.items` → `group["items"]`) (`ad48176`)
- Caminho do banco (`DB_PATH`) em `core/seguranca/seguranca.py` corrigido (`ad48176`)
- `__table_args__ = {"extend_existing": True}` em `Orcamento` (`ad48176`)
- Acesso a `ConfigSistema` via SQL direto no `DashboardService` (`ad48176`)
- Criação de `template_config.py` para compartilhar `Jinja2Templates` com globals RBAC (`23e0ec2`)

### Refatorações
- Implementação de routers web faltantes (fertirrigação, sensoriamento, monitoramento) (`879919e`)
- Correção de rotas de conhecimento e equipe (`879919e`)
- Eliminação de stubs de rotas remanescentes em `Financeiro` (`058bcff`)

---

## [1.0.0] — 2026-08-28/29
### Novas Funcionalidades
- Integração completa: RBAC, Vendas, Orçamentos e Motor VRT v1.0 (`6de0f14`)
- Estrutura inicial do projeto Precision VRT Solo (`f5f94d9`)

---

## Formato

Cada entrada contém:
- **Versão** — SemVer
- **Data** — ISO 8601 (YYYY-MM-DD)
- **Commit** — Hash curto
- **Mudanças** — Descritas em PT-BR
