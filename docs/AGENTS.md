# AGENTS.md — Constituição de Governança do Agente

**Projeto:** Precision VRT Solo  
**Versão:** 1.0  
**Status:** 🟢 **VIGENTE** — Todo agente DEVE seguir estas regras antes de qualquer alteração

---

## ⛔ REGRA MÃE — INVIOLÁVEL

> **Você NÃO possui autorização para tomar decisões de escopo.**

- **NÃO pode criar funcionalidades** fora do escopo autorizado
- **NÃO pode alterar arquivos não autorizados**
- **NÃO pode escolher uma solução alternativa**
- **NÃO pode "melhorar" outra parte do sistema**
- **NÃO pode corrigir problemas secundários por conta própria**
- **NÃO pode refatorar, renomear, otimizar ou "limpar" código** fora do escopo
- **NÃO pode criar compatibilidade, migrar dados ou alterar arquitetura**

**SE** a correção exigir **QUALQUER** arquivo, componente, rota, serviço, modelo, banco ou configuração **FORA DO ESCOPO EXPLICITAMENTE AUTORIZADO → PARE. NÃO FAÇA A ALTERAÇÃO.**

---

## 🛑 REGRA DE PARADA IMEDIATA

**SE, DURANTE A EXECUÇÃO, FOR IDENTIFICADA QUALQUER NECESSIDADE DE ALTERAR:**

arquivo, função, classe, endpoint, modelo, banco, configuração, template ou componente **FORA DO ESCOPO EXPRESSAMENTE AUTORIZADO:**

```
PARAR IMEDIATAMENTE.
NÃO REALIZAR A ALTERAÇÃO.
NÃO TENTAR CONTORNAR.
NÃO IMPLEMENTAR SOLUÇÃO ALTERNATIVA.
NÃO TOMAR DECISÃO DE ESCOPO.
```

**GERAR RELATÓRIO TÉCNICO CONTENDO:**

1. Problema identificado
2. Arquivo exato
3. Caminho completo
4. Linha ou trecho
5. Dependências afetadas
6. Motivo pelo qual a alteração adicional seria necessária
7. Impacto
8. Risco
9. Possíveis soluções (A, B, ...)
10. Arquivos adicionais que precisariam ser alterados
11. Motivo de cada alteração
12. Recomendação técnica

**AGUARDAR AUTORIZAÇÃO EXPLÍCITA.**

---

## 📋 Documentos de Referência Obrigatórios

Antes de executar QUALQUER tarefa, o agente DEVE ler:

| Documento | Caminho | Propósito |
|-----------|---------|-----------|
| **Master Specification** | `MASTER_SPECIFICATION.md` | Especificação funcional/arquitetural congelada v1.0 |
| **Este arquivo** | `AGENTS.md` | Regras de governança, parada, relatório, Definition of Done |
| **Roadmap Oficial** | `ROADMAP OFICIAL — PRECISION VRT SOLO.md` | Fases de desenvolvimento (se disponível) |

**Não existe exceção.** Se o documento não existe no repo, reportar como dependência faltante.

---

## 📐 Definition of Done (Por Fase/Fix)

Uma tarefa **só é considerada completa** quando **TODOS** os itens abaixo forem satisfeitos:

```
□ Código alterado
□ Teste unitário passando (ou justificado como não aplicável)
□ Teste de integração passando
□ Teste funcional manual validado
□ Teste de regressão (nenhum teste anterior quebrado)
□ Banco validado: schema, FK, integridade, dados críticos
□ Imports validados (sem quebras circulares, sem import faltando)
□ Startup validado (servidor sobe sem erros)
□ Arquivos alterados registrados (baseline anterior → diff → baseline novo)
□ Diff revisado: zero alteração fora do escopo
□ Nenhuma alteração não intencional (nem "while I'm here")
□ Relatório final produzido (arquivos, linhas, o que mudou, por quê)
```

---

## 🏗 Regras de Commit

1. **Cada mudança lógica = um commit**
2. **Mensagem descritiva** em português ou inglês consistente
3. **Nunca commitar:** `*.db`, `.env`, tokens, senhas, `__pycache__/`, `*.pyc`
4. **Formato sugerido:** `[MÓDULO] Descrição clara do que mudou`
   - `[AUTH] Corrigir sessão SQLite obsoleta no nível módulo`
   - `[DOCS] Adicionar especificação mestre v1.0`
   - `[DASHBOARD] Corrigir renderização do topbar`
5. **Baseline antes de refatorações:** registrar hashes/timestamps dos arquivos alterados

---

## 🧪 Validação Obrigatória por Tipo de Alteração

### Alteração de Backend (Python)
```
□ Servidor inicia sem erros (uvicorn / startup)
□ Endpoint respondendo (verificar HTTP status + body)
□ Autenticação preservada (cookies, JWT, tenant isolation)
□ Rollback do banco preservado (não alterar dados existentes sem autorização)
□ Imports verificados (dependências circulares, circular imports)
```

### Alteração de Frontend (HTML/CSS/JS)
```
□ Template renderiza sem erro Jinja2
□ Layout responsivo preservado
□ Dark mode funcionando
□ Sidebar: UPPERCASE, altura consistente
□ Topbar: h-16, conteúdo correto
□ Nenhum emoji na interface
□ Ícones SVG funcionando
□ Sem quebra de JavaScript existente (Alpine.js, theme.js)
```

### Alteração de Banco (Models/Schema)
```
□ Migração reversível planejada (ou justificada)
□ Dados existentes preservados
□ Foreign keys verificadas
□ Backup do estado anterior (hash do .db)
□ Rollback testado
```

### Alteração de Autenticação
```
□ JWT: algoritmo, expiração, payload preservados
□ Cookies: httponly, secure, samesite, path, max_age verificados
□ Refresh token: fluxo completo validado
□ Logout: cookies apagados, blocklist atualizada
□ Multi-tenant: isolamento por tenant_id verificado
```

---

## 🔄 Ciclo de Execução Permitido

```
1. LER master spec + AGENTS.md
         ↓
2. ENTENDER o escopo exato da tarefa
         ↓
3. VERIFICAR quais arquivos estão autorizados
         ↓
4. INVESTIGAR raiz do problema (antes de qualquer fix)
         ↓
5. IMPLEMENTAR somente o autorizado
         ↓
6. VALIDAR: todos os itens da Definition of Done
         ↓
7. REGISTRAR: baseline + diff
         ↓
8. COMMIT: mensagem descritiva
         ↓
9. REPORTAR resultado ao stakeholder
```

**Se em qualquer etapa surgir necessidade fora do escopo → REGRA DE PARADA.**

---

## 📊 Matriz DECIDIDO × NÃO DECIDIDO

| Classificação | O que significa | O que o agente faz |
|---------------|-----------------|---------------------|
| 🟢 **DEFINIDO** | Pode implementar | Executa |
| 🟡 **DEFINIDO, NÃO IMPLEMENTADO** | Requisito aprovado aguardando dev | Executa quando autorizado na fase |
| 🔵 **RECOMENDAÇÃO** | Faz sentido, precisa aprovação | Reporta, **NÃO implementa** |
| 🔴 **NÃO DEFINIDO** | Agente **NÃO pode decidir** | **PARA**, reporta, aguarda |
| ⛔ **BLOQUEADO POR DEPENDÊNCIA** | Requer que outro componente exista primeiro | **NÃO implementa** até desbloqueio |

---

## ⚠️ Padrões de Comportamento Proibidos

| Padrão | Por quê | O que fazer |
|--------|---------|-------------|
| "Quick fix for now, investigate later" | Cria dívida técnica e mascara causa raiz | Investigar antes |
| "Just try changing X and see" | Modifica sem entender causa raiz | Formular hipótese → testar minimamente |
| "While I'm here, let me improve this" | Amplia escopo sem autorização | **NÃO MEXER** fora do escopo |
| "This seems related, I'll fix it too" | Presume relação sem evidência | Reportar e aguardar |
| "I'll skip the test, manually verify" | False positive sem automatização | Criar teste antes do fix |
| "The error is obvious, I'll fix directly" | "Obvio" ≠ causa raiz | Fase 1 do systematic debugging |

---

## 🚫 O QUE NÃO PODE EXISTIR NESTE REPO

| Item | Status |
|------|--------|
| Mock fingindo ser dado real | ❌ PROIBIDO |
| Erro de banco → zero registros (mascarado) | ❌ PROIBIDO |
| Feature inexistente → card fingindo que existe | ❌ PROIBIDO |
| Serviço duplicado | ❌ PROIBIDO |
| Cliente duplicado em módulos diferentes | ❌ PROIBIDO |
| Regra agronômica inventada | ❌ PROIBIDO |
| API inventada para preencher interface | ❌ PROIBIDO |
| Tela criada sem fonte real de dados | ❌ PROIBIDO |
| Empty State confundido com Erro | ❌ PROIBIDO |
| Reautenticação com senha armazenada | ❌ PROIBIDO |

---

## 🎯 Observabilidade Mínima Exigida

Qualquer componente novo deve expor/registar:

```
ERROR
├── endpoint
├── serviço/módulo
├── usuário (se autenticado)
├── timestamp (ISO 8601)
├── operação
├── contexto (request ID, tenant)
└── severidade (DEBUG / INFO / WARNING / ERROR / CRITICAL)
```

---

## 📝 Formato do Relatório Técnico (Ao Parar)

```markdown
## RELATÓRIO TÉCNICO — BLOCO DE ESCOPO

**Data:** YYYY-MM-DD HH:MM
**Tarefa em execução:** [descrição]
**Agente:** Claude Code (Hermes)

### 1. Problema Identificado
[Descrição clara do que foi encontrado]

### 2. Arquivo(s) Afetado(s)
| Arquivo | Caminho | Linha(s) |
|---------|---------|----------|
| auth_service.py | app/services/auth_service.py | 90-140 |

### 3. Dependências
[Listar arquivos/serviços/banco que seriam afetados]

### 4. Por que o Escopo Atual Não É Suficiente
[Explicação técnica]

### 5. Impacto
[O que mudaria se a alteração fosse feita]

### 6. Risco
[Baixo / Médio / Alto + justificativa]

### 7. Soluções Possíveis

#### Solução A (Recomendada)
[Descrição]
- Arquivos: [lista]
- Risco: [avaliação]

#### Solução B (Alternativa)
[Descrição]
- Arquivos: [lista]
- Risco: [avaliação]

### 8. Recomendação Técnica
[Qual solução parece mais adequada e por quê]

### 9. AGUARDANDO AUTORIZAÇÃO
[Sim / Não]
```

---

## 🔄 Checkpoints & Baselines

| Checkpoint | Estado Registrado | Arquivos | Hashes |
|------------|-------------------|----------|--------|
| 13.7.0 | [descrição] | [lista] | [hashes] |
| 13.7.3 | [descrição] | [lista] | [hashes] |
| Próximo | Somente após baseline | [lista] | [hashes] |

**Antes de cada fase:** estado atual registrado  
**Depois de cada fase:** estado posterior + diff exato

---

> **Resumo em uma frase:**  
> *O agente executa o que foi autorizado, para quando encontra algo fora do escopo, reporta com precisão cirúrgica, e aguarda. Nunca decide sozinho.*