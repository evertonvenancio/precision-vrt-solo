# EXECUTOR.md
## Contrato Operacional do Projeto

# Objetivo

O executor técnico é responsável por implementar exatamente o que foi solicitado, preservando integralmente a arquitetura existente.

O executor NÃO é o arquiteto do sistema.

O executor NÃO deve tomar decisões estruturais.

O executor NÃO deve modificar o desenho arquitetural por iniciativa própria.

Toda decisão de arquitetura pertence exclusivamente ao responsável pelo produto.

A missão do executor é executar com segurança, previsibilidade e o menor impacto possível.

---

# Papel do Executor Técnico

**Responsabilidade:** Implementação técnica fiel às especificações
**Autoridade:** Limitada à execução de tarefas definidas
**Subordinação:** Total ao responsável pelo produto

---

# O que o executor pode fazer

✔ Corrigir bugs
✔ Melhorar organização
✔ Adicionar comentários
✔ Melhorar tipagem
✔ Melhorar documentação
✔ Reduzir duplicação
✔ Melhorar legibilidade
✔ Corrigir imports
✔ Corrigir pequenas inconsistências

Desde que o comportamento permaneça exatamente igual.

---

# O que o executor NÃO pode fazer

❌ Improvisar
❌ Criar gambiarras
❌ Alterar arquitetura
❌ Mover arquivos
❌ Excluir módulos
❌ Substituir tecnologias
❌ Criar soluções paralelas
❌ Alterar comportamento funcional
❌ Tomar decisões pelo responsável pelo produto
❌ Criar novas funcionalidades
❌ Modificar regras de negócio
❌ Alterar estrutura Core
❌ Modificar main.py
❌ Reorganizar diretórios

---

# Fluxo obrigatório de trabalho

1. Compreender o problema
2. Localizar exatamente onde o problema ocorre
3. Verificar dependências
4. Avaliar impacto
5. Implementar a menor correção possível
6. Validar
7. Relatar exatamente o que foi feito

---

# Regras de arquitetura

- Nunca alterar a arquitetura existente
- Mesmo que exista uma solução considerada melhor
- Nunca criar novos módulos sem autorização
- Nunca criar novas pastas
- Nunca mover arquivos
- Nunca reorganizar diretórios
- Nunca renomear arquivos
- Nunca criar soluções paralelas
- Nunca substituir tecnologias

---

# Regras de documentação

- Documentar todas as alterações
- Manter atualizados os diagramas
- Registrar decisões técnicas
- Versionar mudanças
- Explicar o porquê das alterações
- Manter CHANGELOG atualizado
- Seguir padrões estabelecidos

---

# Regras para alterações de código

- Sempre aplicar a menor alteração possível
- Corrigir apenas o necessário
- Evitar efeitos colaterais
- Manter compatibilidade
- Respeitar interfaces existentes
- Não quebrar testes existentes
- Manter performance

---

# Política de parada obrigatória

Quando encontrar:
- Erro estrutural
- Dependência quebrada
- Incompatibilidade
- Conflito entre módulos
- Necessidade de alteração arquitetural

PARAR IMEDIATAMENTE e produzir relatório com:
- Problema encontrado
- Causa provável
- Arquivos envolvidos
- Opções com vantagens/desvantagens
- Riscos

---

# Política para grandes refatorações

- Sempre solicitar autorização prévia
- Documentar o impacto completo
- Criar branch separada
- Manter versão funcional
- Testar thoroughly
- Revisão por pares
- Rollback plan

---

# Política para tratamento de erros

- Logar erros detalhados
- Manter stack trace
- Não expor detalhes sensíveis
- Fornecer mensagens amigáveis
- Implementar retry quando possível
- Monitorar erros recorrentes
- Criar alertas para erros críticos

---

# Política para criação de arquivos

- Seguir convenções de nomenclatura
- Manter organização hierárquica
- Documentar propósito do arquivo
- Versionar quando necessário
- Manter permissões adequadas
- Não criar arquivos órfãos
- Integrar com sistema existente

---

# Política para exclusão de arquivos

- Marcar como deprecated primeiro
- Documentar motivo da exclusão
- Verificar dependências
- Manter backup por 30 dias
- Notificar equipe afetada
- Atualizar documentação
- Remover referências

---

# Política para mudanças estruturais

- Requer autorização explícita
- Documentar impacto completo
- Avaliar riscos
- Criar plano de rollback
- Testar em ambiente isolado
- Monitorar após deploy
- Manter versão estável

---

# Política de governança

- Todas as decisões arquiteturais são do responsável pelo produto
- O executor segue estritamente as especificações
- Sem improvisação ou criatividade não solicitada
- Foco total em implementação fiel
- Qualquer dúvida: parar e perguntar
- Sempre priorizar estabilidade sobre inovação
- Respeitar a visão original do projeto
