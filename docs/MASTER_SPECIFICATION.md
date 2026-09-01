# Precision VRT Solo — Master Specification (v1.0)

**Data:** 2026-08-28  
**Autor:** Consolidado a partir da especificação mestre do stakeholder  
**Status:** 🟢 **CONGELADO** — Não alterar sem autorização explícita  
**Repositório:** `evertonvenancio/precision-vrt-solo`

---

> **Regra Mãe:**  
> **O executor técnico executa. Não decide escopo.**  
> Se precisar decidir, **para e pergunta**.  
> Qualquer alteração fora dos arquivos explicitamente autorizados → **PARAR IMEDIATAMENTE**, gerar relatório técnico, aguardar autorização.

---

## 1. Visão Geral do Produto

O **Precision VRT Solo** é uma **plataforma operacional de agricultura de precisão**, não um CRUD administrativo com mapas.

### Camadas Arquiteturais

```
┌──────────────────────────────────────────────┐
│           PRECISION VRT SOLO                 │
├──────────────────────────────────────────────┤
│  1. RELACIONAMENTO COMERCIAL (CRM)           │
│     Clientes · Orçamentos · Vendas · Agenda  │
│                                              │
│  2. OPERAÇÃO AGRONÔMICA                      │
│     Prescrição VRT · Compactação · Nematoides│
│     Fertirrigação · Sensoriamento · Monitor. │
│                                              │
│  3. CONHECIMENTO TÉCNICO (BASE TÉCNICA)      │
│     Culturas · Metodologias · Bibliografia   │
│                                              │
│  4. ADMINISTRAÇÃO                            │
│     Financeiro · Patrimônio · Cadastros      │
│     Usuários · Equipes · Empresas · Produtos │
│     Fornecedores · Configurações             │
└──────────────────────────────────────────────┘
```

### Fluxo Central (Ciclo Fechado de Evidência)

```
DADO → DIAGNÓSTICO → DECISÃO → RECOMENDAÇÃO → PRESCRIÇÃO 
   → EXECUÇÃO → RESULTADO → HISTÓRICO → PRÓXIMA DECISÃO
```

---

## 2. Hierarquia da Marca

```
NOVAXIS (empresa desenvolvedora)
   ↓
Precision Platform (plataforma tecnológica)
   ↓
Precision SR Solo (nome em documento "Layout Oficial")
   ↓
Precision VRT Solo (nome da evolução atual — **oficial neste repo**)
```

> **Regra:** Tratar nomenclatura como consolidada. Não renomear sem autorização.

---

## 3. Arquitetura Visual Global

### 3.1 Sidebar
- Coluna estrutural permanente
- Estados: **expandido** (260px) / **recolhido** (64px)
- Ícones **SVG** (proibido emojis)
- Organização em 8 grupos (conforme árvore abaixo)
- **Dinâmico**: construído a partir de `permissões + módulos habilitados + configuração + contexto`
- Módulo sem acesso → **não aparece** (não apenas esconder conteúdo)

### 3.2 Topbar (`h-16` fixa)
- Altura **exatamente igual à área do logo do Sidebar** (`h-16`)
- Conteúdo: Bem-vindo + dia + data + hora + clima + cidade + controles (tema + usuário)
- Não compete com conteúdo; parece produto acabado

### 3.3 Estrutura de Navegação (Sidebar)

```
DASHBOARD

COMERCIAL
 ├── Orçamentos
 ├── Vendas
 ├── Agenda
 └── Relatórios

AGRONOMIA
 ├── Recomendação
 ├── Prescrição VRT
 ├── Compactação
 ├── Nematoides
 ├── Fertirrigação
 ├── Sensoriamento
 └── Monitoramento

CONHECIMENTO
 ├── Culturas
 ├── Metodologias
 └── Bibliografia

BIBLIOTECA
 └── (Estrutura de arquivos/documentos)

FINANCEIRO
 ├── Financeiro
 └── Patrimônio

ADMINISTRAÇÃO
 ├── Clientes
 ├── Usuários
 ├── Equipes
 ├── Empresas
 ├── Produtos
 └── Fornecedores

CONFIGURAÇÃO
 └── (Centro de Comando)
```

---

## 4. Dashboard Modular (Requisito Crítico 🔴)

### 4.1 Cards — Componentes Modulares Configuráveis
Cada card **deve** possuir:
- identificação, título, ícone, fonte de dados, permissão necessária
- rota de destino (clicável → abre módulo relacionado)
- tamanho (Pequeno / Médio / Grande), posição, ordem, visibilidade
- configuração persistida por **usuário + tenant**

### 4.2 Interações
| Ação | Comportamento |
|------|---------------|
| Clique | Navega para o módulo de destino |
| Clique + Segurar | Entra em modo de movimentação (drag) |
| Arrastar | Muda posição (persistir) |
| Redimensionar | Pequeno ↔ Médio ↔ Grande (persistir) |

### 4.3 Dashboard por Perfil + Tenant
```
Tenant (padrão da empresa)
   ↓
Personalização do usuário
```

---

## 5. Módulos Detalhados

### 5.1 CRM & Comercial (Ciclo Completo)
```
LEAD → OPORTUNIDADE → CONTATO → ORÇAMENTO 
   → NEGOCIAÇÃO → VENDA → EXECUÇÃO → ACOMPANHAMENTO → RENOVAÇÃO
```
- **Cliente único** = fonte de verdade para todos os módulos
- Orçamento conectado a: cliente, vendedor, serviços, produtos, preços, descontos, validade, condições, aprovação, auditoria, venda
- Venda preserva origem (Orçamento → Aprovação → Venda → Financeiro)

### 5.2 Prescrição VRT (Motor Central 🔴)
**Não é tela isolada — é processo integrado.**

```
CLIENTE → ÁREA/TALHÃO → HISTÓRICO → DADOS DE CAMPO 
   → SENSORIAMENTO → ÍNDICES ESPECTRAIS → DIAGNÓSTICO 
   → METODOLOGIA → RECOMENDAÇÃO → PRESCRIÇÃO VRT 
   → GRADE/ZONAS/TAXAS → ARQUIVO → EXECUÇÃO 
   → MONITORAMENTO → RESULTADO → NOVO HISTÓRICO
```

#### Grade Amostral (Diferencial 🔴)
- **Não é malha fixa** — nasce dos dados
- Considera: histórico, índices espectrais, variabilidade espacial, zonas, produtividade, mapas, análises anteriores, pontos já coletados, critérios da metodologia
- **Rastreabilidade ponto → coleta → resultado → recomendação → prescrição**

### 5.3 Compactação
- Recebe inteligência espacial da Prescrição
- Entrada: área, histórico, dados espaciais, manejo, amostragem, variabilidade
- Saída: pontos de amostragem, zonas, diagnóstico, classificação, recomendação, prescrição

### 5.4 Nematoides
- Conectado ao histórico espacial
- Histórico → índices espectrais → variabilidade → zonas suspeitas → grade amostral inteligente → coleta → laboratório → mapa diagnóstico → recomendação → prescrição

### 5.5 Fertirrigação / Sensoriamento / Monitoramento
- Seguem mesma arquitetura: **Dados → Contexto → Cultura → Parâmetros → Cálculo → Recomendação → Resultado**
- Sensoriamento = **fonte de dados** para inteligência agronômica
- Monitoramento = **acompanhamento contínuo** (histórico, evolução, comparação, alertas)

### 5.6 Base Técnica (Repositório de Conhecimento)
| Pilar | Conteúdo |
|-------|----------|
| **Culturas** | Ficha técnica: nome, identificação, características, parâmetros, metodologias relacionadas, referências, histórico |
| **Metodologias** | Nome, versão, descrição, objetivo, aplicação, parâmetros, procedimento, critérios, fonte, data, status (**versionamento obrigatório**) |
| **Bibliografia** | Título, autor, ano, editora/fonte, tipo, link/identificador, observações, metodologias relacionadas, culturas relacionadas |

> **Regra:** Resultado técnico não aparece sem rastrear fonte quando metodologia exigir referência.

### 5.7 Financeiro (Operacional, não Contábil)
- Recebe de Venda → Receita → Contas → Fluxo
- Visão empresarial: faturamento, recebimentos, despesas, comissões, salários/base, serviços, inadimplência
- Visão por funcionário: salário base, comissão, bonificações, descontos, total
- **Exporta relatórios "mastigados" para contabilidade** (não substitui contador)

### 5.8 Patrimônio
- Ativo, categoria, identificação, aquisição, valor, responsável, localização, estado, manutenção, movimentação, baixa, histórico
- Exemplo: Drone X — aquisição, responsável, localização, última/próxima manutenção, estado, histórico

### 5.9 Cadastros (Fundação — Fonte Única)
```
CLIENTE ÚNICO → CRM, Financeiro, Operações, Relatórios, Histórico
```
Entidades: Clientes, Usuários, Equipes, Empresas, Produtos, Fornecedores, Serviços

### 5.10 Agenda (Contextualizada)
- Relaciona compromissos com: cliente, propriedade, área, consultor, serviço, visita, amostragem, operação, acompanhamento
- Exemplo: `João → Fazenda X → coleta nematoides → Talhão 04 → 14h`

### 5.11 Relatórios (Transversal)
- Consultam **dados reais** + filtros → visualização → exportação (CSV/XLSX/PDF)
- Respeitam permissões do usuário
- Categorias: Comercial, Agronômico, Operacional, Financeiro, Auditoria

### 5.12 Laudos & Documentos (Motor de Documentos)
- Templates configuráveis: capa, logotipo, identidade, responsável técnico, cliente, propriedade, talhão, data, metodologia, mapas, tabelas, gráficos, recomendações, bibliografia, observações, assinatura, rodapé, numeração, versão, anexos
- **Cada recomendação carrega sua fonte bibliográfica no laudo**

---

## 6. Configurações — Centro de Comando Administrativo

Não é "trocar senha". Controla o **padrão oficial da operação**:

| Domínio | Itens |
|---------|-------|
| **Sistema** | identidade visual, empresa, unidades, parâmetros gerais, templates, numeração, padrões |
| **Comercial** | regras de orçamento, validade, descontos, aprovação, comissão, condições |
| **Agricultura** | metodologias, referências, parâmetros, faixas, interpretações, regras de recomendação, culturas, nutrientes, critérios de compactação/nematoides/fertirrigação |
| **Prescrição** | parâmetros, metodologias, critérios, fontes, regras de cálculo |
| **Documentos** | modelos, capa, cabeçalho, rodapé, assinatura, responsável técnico, identidade visual |
| **Acessos** | usuários, perfis, permissões, módulos, ações |
| **Auditoria** | eventos, retenção, consultas, filtros, histórico |
| **Dashboard** | cards, disposição, tamanho, visibilidade, prioridade, ordem |

### Versionamento de Configurações (Crítico 🔴)
- Metodologia A v1.0 → v1.1: prescrição antiga **permanece vinculada à v1.0**
- Protege: histórico, auditoria, reprodução do cálculo, responsabilidade técnica, rastreabilidade

---

## 7. Autenticação & Autorização (Separação Estrita)

| Camada | Pergunta | Exemplos |
|--------|----------|----------|
| **Autenticação** | "Quem é você?" | usuário, senha, sessão, JWT, refresh token, recuperação, MFA |
| **Autorização (RBAC Granular)** | "O que pode fazer?" | visualizar/criar/editar/excluir por módulo, ação, registro |

### Modelo de Permissões (por Módulo + Ação)
```yaml
CRM:         [visualizar, criar, editar, excluir]
ORÇAMENTOS:  [visualizar, criar, editar, cancelar, aplicar_desconto]
PRESCRIÇÃO:  [visualizar, criar, editar, aprovar, alterar_metodologia]
FINANCEIRO:  [visualizar, lançar, editar, exportar, administrar]
CONFIGURAÇÕES: [visualizar, alterar, administrar]
```

> **Regra:** Interface = representação visual das permissões reais.  
> Esconder botão no frontend ≠ segurança. **API também deve bloquear.**

### Multiempresa / Multi-tenant (Desde a Base 🔴)
- `tenant` = fronteira de segurança (não apenas campo cadastral)
- **Usuário Tenant A ❌ nunca consulta/altera/exporta Tenant B** (garantido no backend)
- Isolamento: clientes, propriedades, áreas, amostras, grades, análises, prescrições, recomendações, orçamentos, vendas, agenda, relatórios, documentos, auditorias, configurações, usuários, equipes, fornecedores, produtos, patrimônio, financeiro

---

## 8. Auditoria Transversal & Imutável 🔴

### Princípio
> **Auditoria não é página isolada — é mecanismo transversal.**  
> Registra: `quem → fez o quê → quando → onde → antes → depois → por quê → com qual autorização`

### Eventos que Geram Auditoria (Lista Mínima)
- Alteração de configuração / metodologia / parâmetro / preço
- Desconto excepcional / alteração de recomendação / prescrição
- Exclusão / restauração / aprovação / rejeição
- Mudança de permissão / alteração de usuário / acesso
- Operações financeiras sensíveis / emissão de documentos
- Exceções operacionais

### Padrão: Exceção + Justificativa + Senha → Auditoria
```
PADRÃO → EXCEÇÃO → JUSTIFICATIVA → AUTENTICAÇÃO → ALTERAÇÃO → AUDITORIA
```
- Senha **nunca armazenada** no evento (apenas registro de reautenticação válida)
- Histórico imutável: correção gera novo evento, não sobrescreve

### Empty State ≠ Erro (Regra Arquitetural Permanente)
| Cenário | Resposta |
|---------|----------|
| Consulta OK + 0 resultados | **EMPTY STATE LEGÍTIMO** |
| Consulta falhou | **ERRO** (não mascarar com `[]` ou `0`) |
| Dado inválido | **VALIDAÇÃO** |
| Permissão negada | **403** |
| Não autenticado | **401** |

---

## 9. Requisitos Estruturais Críticos (Não Implícitos)

| Requisito | Prioridade |
|-----------|------------|
| SaaS Multi-tenant desde a base | 🔴 |
| RBAC + Permissões modulares | 🔴 |
| Configuração como "Source of Truth" | 🔴 |
| Versionamento de configurações (metodologias, prescrições) | 🔴 |
| Auditoria imutável + contexto completo | 🔴 |
| Snapshot da prescrição (contexto congelado no momento da geração) | 🔴 |
| Prescrição como núcleo do motor agronômico | 🔴 |
| Grade amostral orientada por dados históricos/espectrais | 🔴 |
| Laudo como produto final configurável + motor de documentos | 🔴 |
| Dashboard modular (cards clicáveis, arrastáveis, redimensionáveis, persistidos) | 🔴 |
| Dashboard por usuário + tenant | 🔴 |
| Sidebar dinâmico (construído a partir de permissões) | 🔴 |
| Financeiro operacional (não contábil) | 🟠 |
| Patrimônio (definir antes de implementar) | 🟡 |
| Integrações: camada própria (não chamada direta no módulo) | 🟠 |
| APIs índices espectrais = CORE (não "futuro") | 🔴 |
| Segurança de sessão (expiração, refresh, revogação, MFA) | 🟠 |
| Rate limiting, validação payload, proteção uploads | 🟠 |
| LGPD / Governança de dados | 🟠 |
| Feature flags por tenant | 🟢 (preparar arquitetura) |
| Planos SaaS (arquitetura preparada) | 🟢 (preparar arquitetura) |
| Observabilidade mínima (erro, endpoint, usuário, timestamp, operação) | 🟠 |
| Backup / Disaster Recovery (RPO/RTO definidos) | 🟡 |
| Matriz de rastreabilidade por requisito (ID, status, teste, auditoria) | 🔴 |

---

## 10. Governança de Alterações (Constituição do Projeto)

### Regra de Ouro
> **Nenhum executor técnico pode ampliar o escopo por conta própria.**  
> Se uma alteração exigir: outro arquivo, outro módulo, alteração de banco, API, arquitetura, contrato, migração, alteração de dados, mudança de regra → **PARAR.**

### Relatório Obrigatório ao Parar
1. Problema identificado
2. Arquivo exato (caminho completo)
3. Linha / símbolo / classe / função
4. Dependências afetadas
5. Por que o escopo atual não é suficiente
6. Impacto
7. Risco
8. Soluções possíveis (A, B, ...)
9. Arquivos que seriam alterados
10. Dados que seriam afetados
11. Recomendação técnica
12. **Aguardar autorização explícita**

---

## 11. Definition of Done (Por Fase)

Uma fase **só termina** quando **TODOS** forem satisfeitos:
- [ ] Código alterado
- [ ] Teste unitário
- [ ] Teste de integração
- [ ] Teste funcional
- [ ] Teste de regressão
- [ ] Banco validado (schema, FK, integridade, dados críticos)
- [ ] Imports validados
- [ ] Startup validado
- [ ] Arquivos alterados registrados (baseline + diff)
- [ ] Diff revisado
- [ ] **Zero alteração fora do escopo**
- [ ] Relatório final produzido

---

## 12. Roadmap de Execução (Ordem Proposta)

1. **Arquitetura de Acesso** — Usuário → Perfil → Permissões → Módulos → Ações
2. **Configurações** — Tudo que é padrão oficial
3. **Auditoria** — Mecanismo transversal imutável
4. **Entidades Centrais** — Empresa → Usuário → Cliente → Propriedade → Talhão → Safra
5. **Dados Espaciais** — Geometria → Mapas → Pontos → Zonas
6. **Motor Agronômico** — Sensoriamento → Histórico → Amostragem → Laboratório → Interpretação
7. **Prescrição** — Recomendação → Prescrição → Aplicação
8. **Módulos Técnicos** — Compactação → Nematoides → Fertirrigação → Demais
9. **CRM** — Clientes → Oportunidades → Orçamento → Venda → Agenda
10. **Financeiro Operacional** — Receitas → Despesas → Comissões → Relatórios
11. **Documentos** — Laudos → PDFs → Anexos → Bibliografia
12. **Dashboard Modular** — Cards → Layout → Drag → Resize → Config → Permissões
13. **Fiscal/Integradores** — Notas → Boletos → APIs
14. **Regressão Operacional** — Tudo funcionando junto

---

## 13. Matriz DECIDIDO × NÃO DECIDIDO (Viva)

| Classificação | Significado | Ação do Executor |
|---------------|-------------|----------------|
| 🟢 **DEFINIDO** | Pode implementar | Executar |
| 🟡 **DEFINIDO, NÃO IMPLEMENTADO** | Requisito aprovado aguardando dev | Aguardar autorização de fase |
| 🔵 **RECOMENDAÇÃO** | Faz sentido, precisa aprovação | Reportar, não implementar |
| 🔴 **NÃO DEFINIDO** | Executor **não pode decidir** | Parar, reportar, aguardar |
| ⛔ **BLOQUEADO POR DEPENDÊNCIA** | Ex: Laudo depende de Prescrição final | Não implementar até desbloquear |

---

## 14. Checkpoints / Baselines

| Checkpoint | Descrição |
|------------|-----------|
| **13.7** | Sistema validado |
| **13.7.3** | Somente leitura / auditoria |
| **Próximo** | Alteração autorizada (somente após baseline registrado) |

**Antes de mexer:** estado atual registrado (hashes, schema, dados)  
**Depois:** estado posterior registrado + diff exato

---

## 15. Observabilidade Mínima

Separar em canais:
- **Log Operacional** — "Sistema fez X"
- **Log de Segurança** — "Usuário tentou Y"
- **Auditoria de Negócio** — "Usuário alterou Z"
- **Erro Técnico** — "Banco/API apresentou erro"

---

## 16. Princípio Final

> **O Precision VRT Solo não é um CRM com mapa.**  
> Núcleo = **Motor Agronômico + Dados Espaciais + Prescrição + Rastreabilidade**  
> CRM, Financeiro, Agenda, Patrimônio = camadas administrativas de suporte.

> **Nenhuma funcionalidade visual é "implementada" porque "a tela existe".**  
> Três estados: **DESENHADO → IMPLEMENTADO → VALIDADO (dados reais + comportamento esperado)**

---

---

**FIM DA ESPECIFICAÇÃO MESTRE v1.0**
