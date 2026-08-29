# Precision VRT Solo

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-orange.svg)](https://www.sqlalchemy.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey.svg)](https://www.sqlite.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4+-38B2AC.svg)](https://tailwindcss.com/)
[![Alpine.js](https://img.shields.io/badge/Alpine.js-3.13+-8BC0D0.svg)](https://alpinejs.dev/)
[![Status](https://img.shields.io/badge/Status-Operacional-brightgreen.svg)](#)

> **Plataforma operacional de agricultura de precisão** — Motor agronômico + Dados espaciais + Prescrição VRT + Rastreabilidade completa.

---

## 📋 Visão Rápida

O **Precision VRT Solo** é uma plataforma SaaS multi-tenant para gestão integrada do ciclo agronômico-comercial:

```
┌─────────────────────────────────────────────────────────────┐
│  CADASTRO → CLIENTE → PROPRIEDADE/TALHÃO → OPORTUNIDADE    │
│       ↓                                                        │
│  ORÇAMENTO → VENDA → AGENDA → OPERAÇÃO AGRONÔMICA           │
│       ↓                                                        │
│  PROCESSAMENTO → RESULTADO → RELATÓRIO → FINANCEIRO          │
│       ↓                                                        │
│  HISTÓRICO (ciclo fechado de evidência)                      │
└─────────────────────────────────────────────────────────────┘
```

**Status Atual (29/08/2026):** ✅ **OPERACIONAL** — Aplicação inicia sem erros, 28 roteadores web/API registrados, RBAC funcional, sidebar dinâmica, banco íntegro (33 tabelas).

### Quatro Camadas Principais

| Camada | Módulos |
|--------|---------|
| **Relacionamento Comercial** | CRM, Clientes, Orçamentos, Vendas, Agenda, Relatórios |
| **Operação Agronômica** | Prescrição VRT, Compactação, Nematoides, Fertirrigação, Sensoriamento, Monitoramento |
| **Conhecimento Técnico** | Culturas, Metodologias, Bibliografia |
| **Administração** | Financeiro, Patrimônio, Cadastros, Usuários, Equipes, Empresas, Produtos, Fornecedores, Configurações |

---

## 🛠 Stack Tecnológico

| Camada | Tecnologia |
|--------|------------|
| **Backend** | FastAPI 0.110+ (Python 3.11+) |
| **ORM** | SQLAlchemy 2.0 (Sessões síncronas por request `SessionLocal()`) |
| **Banco** | SQLite (`precision_vrt.db`) |
| **Auth** | JWT (HS256) em cookies `HttpOnly` + Refresh Token + Blocklist + PBKDF2-SHA256 |
| **RBAC** | Matriz granular em `core/authorization/dependencies.py` (34 módulos, 157 permissões) |
| **Multi-Tenancy** | `TenantMiddleware` extrai isolamento por tenant no backend |
| **Frontend** | Jinja2 + Tailwind CSS + Alpine.js 3 |
| **Templates** | Layout base com Sidebar colapsável e Topbar `h-16` fixa |
| **Tema** | Dark/Light mode persistido no `localStorage` |

---

## 📁 Estrutura do Projeto

```
Precision-VRT-Solo/
├── app/
│   ├── app_factory.py          # Factory central FastAPI (registro de 21+ routers)
│   ├── main.py                 # Entry point uvicorn
│   ├── cli.py                  # CLI do motor VRT
│   ├── templates/              # Layout master base.html, dashboard.html e páginas dos módulos
│   ├── static/                 # CSS/JS compartilhados (components.css, theme.js)
│   ├── web/                    # 25+ Roteadores web (Server-Side Rendering)
│   ├── api/v1/endpoints/       # Endpoints REST API (JSON)
│   ├── services/               # 25+ Serviços de orquestração e negócio
│   ├── db/                     # Engine, SessionLocal, Base
│   └── core/                   # Utilitários, segurança, RBAC, motor VRT
├── models/                     # 28 Modelos SQLAlchemy e Schemas Pydantic
├── docs/                       # Documentação oficial e governança do projeto
│   ├── MASTER_SPECIFICATION.md # Especificação Mestre v1.0 CONGELADA
│   ├── AGENTS.md               # Regras de governança do agente
│   ├── EXECUTOR.md             # Contrato operacional
│   ├── modelo_domínio.md       # Modelo de domínio Interface/Core/DB
│   ├── CHANGELOG.md            # Histórico de alterações
│   └── RELATORIO_FINAL.md      # Relatório técnico de integração
├── legacy/                     # Módulos legados, backups e scripts utilitários
├── precision_vrt.db            # Banco SQLite local
├── requirements.txt            # Dependências unificadas do projeto
└── README.md                   # Este arquivo
```

---

## 🔐 Autenticação & Autorização

- **Login:** `POST /web/auth/login` → define cookies `access_token`, `refresh_token` e `session_id`
- **Logout:** `POST /web/auth/logout` → revoga tokens na blocklist + limpa cookies
- **Sessão:** Autenticação via `get_token_from_cookie` e RBAC via `Depends(require_permission("modulo:acao"))`
- **RBAC Granular:** 157 permissões cobrindo 34 módulos no `PERMISSION_MAP`
- **Multi-Tenant:** Isolamento rigoroso garantido via `TenantMiddleware` e consultas no banco por `tenant_id`

---

## ⚙️ Configuração & Execução

### Pré-requisitos
- Python 3.11+
- Install dependências: `pip install -r requirements.txt`

### Variáveis de Ambiente (`.env`)
```env
SECRET_KEY=precision_vrt_solo_secret_key_2024
DATABASE_URL=sqlite:///./precision_vrt.db
DEBUG=true
```

### Subir o Servidor
```bash
# Desenvolvimento
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Ou via módulo Python
python -m app.main
```

### Acessar
- **Login:** `http://localhost:8000/web/auth/login`
- **Dashboard:** `http://localhost:8000/web/dashboard`
- **API Docs:** `http://localhost:8000/docs`

---

## 🧪 Testes & Validação

```bash
# Testes de integração e rotas
pytest

# Validação do startup da aplicação
python -c "from app.app_factory import create_app; create_app()"
```

---

## 📜 Governança do Projeto

Este projeto segue regras estritas descritas na documentação oficial:

- **[MASTER_SPECIFICATION.md](docs/MASTER_SPECIFICATION.md)** — Especificação funcional e arquitetural congelada (v1.0)
- **[AGENTS.md](docs/AGENTS.md)** — Regras de governança do agente, regra de parada imediata e Definition of Done
- **[EXECUTOR.md](docs/EXECUTOR.md)** — Contrato operacional e limites do executor técnico
- **[RELATORIO_FINAL.md](docs/RELATORIO_FINAL.md)** — Evidências de integração e métricas do sistema

---

## 🗂 Matriz de Status dos Módulos

| Módulo | Status | Observação |
|--------|--------|------------|
| Auth (Login/Logout/JWT/Cookies) | 🟢 Implementado | PBKDF2-SHA256, cookies HttpOnly, refresh token e blocklist |
| Dashboard Modular | 🟢 Implementado | 28 variáveis de contexto, estatísticas reais do banco |
| Clientes (CRUD) | 🟢 Implementado | Entidade única centralizada (`models/cliente_sql.py`) |
| Prescrição VRT (Motor) | 🟢 Implementado | Krigagem, zoneamento K-Means e recomendação NPK (`core/prescricao_vrt/`) |
| Compactação & Nematoides | 🟢 Implementado | Services, modelos ORM e rotas web operacionais |
| Vendas & Títulos Financeiros | 🟢 Implementado | Venda à vista/prazo, parcelamento, saldo residual e baixa de títulos |
| Orçamentos | 🟢 Implementado | Rotas web, ORM e emissão de propostas |
| Configurações & Auditoria | 🟢 Implementado | Configuração do sistema e registro imutável de eventos no banco |
| Base Técnica & Cadastros | 🟢 Implementado | Culturas, Metodologias versionadas e Bibliografia |
| Multi-tenant & RBAC | 🟢 Implementado | Matriz de 157 permissões cobrindo 34 módulos |

---

## 📄 Licença & Propriedade

Proprietário — **NOVAXIS / Precision Platform**  
Uso restrito aos termos do contrato de licenciamento.
