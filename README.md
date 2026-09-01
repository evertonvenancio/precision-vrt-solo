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

**Status Atual (01/09/2026):** ✅ **OPERACIONAL** — Aplicação inicia sem erros, 35 roteadores web/API registrados, RBAC funcional, sidebar dinâmica, banco íntegro (30 tabelas).

### Oito Grupos na Sidebar

| Grupo | Conteúdo |
|--------|---------|
| **Dashboard** | Visão centralizada |
| **Comercial** | CRM, Clientes, Orçamentos, Vendas, Agenda, Relatórios |
| **Agronomia** | Prescrição VRT, Compactação, Nematoides, Fertirrigação, Sensoriamento, Monitoramento |
| **Conhecimento** | Culturas, Metodologias, Bibliografia |
| **Biblioteca** | Repositório de documentos |
| **Financeiro** | Financeiro, Patrimônio |
| **Administração** | Cadastros, Usuários, Equipes, Empresas, Produtos, Fornecedores |
| **Configuração** | Centro de comando do sistema |

---

## 🛠 Stack Tecnológico

| Camada | Tecnologia |
|--------|------------|
| **Backend** | FastAPI 0.110+ (Python 3.11+) |
| **ORM** | SQLAlchemy 2.0 (Sessões síncronas por request `SessionLocal()`) |
| **Banco** | SQLite (`precision_vrt.db`) |
| **Auth** | JWT (HS256) em cookies `HttpOnly` + Refresh Token + Blocklist + PBKDF2-SHA256 |
| **RBAC** | Matriz granular em `core/authorization/dependencies.py` (39 módulos, ~157 permissões) |
| **Multi-Tenancy** | `TenantMiddleware` extrai isolamento por tenant no backend |
| **Frontend** | Jinja2 + Tailwind CSS + Alpine.js 3 |
| **Templates** | Layout base com Sidebar colapsável (8 grupos) e Topbar `h-16` fixa |
| **Tema** | Dark/Light mode persistido no `localStorage` |

---

## 📁 Estrutura do Projeto

```
Precision-VRT-Solo/
├── app/
│   ├── app_factory.py          # Factory central FastAPI
│   ├── main.py                 # Entry point uvicorn
│   ├── cli.py                  # CLI do motor VRT
│   ├── templates/              # Layout master base.html, dashboard.html e páginas dos módulos
│   ├── static/                 # CSS/JS compartilhados
│   ├── web/                    # Roteadores web (Server-Side Rendering)
│   ├── api/v1/endpoints/       # Endpoints REST API (JSON)
│   ├── services/               # Serviços de orquestração e negócio
│   ├── db/                     # Engine, SessionLocal, Base
│   └── core/                   # Utilitários, segurança, RBAC, motor VRT
├── models/                     # 48 Modelos SQLAlchemy e Schemas Pydantic
├── docs/                       # Documentação oficial e governança
├── legacy/                     # Módulos legados, backups e scripts utilitários
├── precision_vrt.db            # Banco SQLite ativo (30 tabelas)
├── requirements.txt            # Dependências unificadas
└── README.md                   # Este arquivo
```

---

## 🔐 Autenticação & Autorização

- **Login:** `POST /web/auth/login` → define cookies `access_token`, `refresh_token` e `session_id`
- **Logout:** `POST /web/auth/logout` → revoga tokens na blocklist + limpa cookies
- **Sessão:** Autenticação via `get_token_from_cookie` e RBAC via `Depends(require_permission("modulo:acao"))`
- **RBAC Granular:** ~157 permissões cobrindo 39 módulos no `PERMISSION_MAP`
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

## 📜 Governança do Projeto

Este projeto segue regras estritas descritas na documentação oficial:

- **[MASTER_SPECIFICATION.md](docs/MASTER_SPECIFICATION.md)** — Especificação funcional e arquitetural congelada (v1.0)
- **[AGENTS.md](docs/AGENTS.md)** — Regras de governança do executor técnico
- **[EXECUTOR.md](docs/EXECUTOR.md)** — Contrato operacional e limites
- **[RELATORIO_FINAL.md](docs/RELATORIO_FINAL.md)** — Evidências de integração e métricas reais

---

## 📄 Licença & Propriedade

Proprietário — **NOVAXIS / Precision Platform**  
Uso restrito aos termos do contrato de licenciamento.
