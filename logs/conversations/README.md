# Conversas

Registro das sessões com agentes de IA.

## Regras

- Uma sessão = um arquivo `YYYY-MM-DD-session-NNN-<slug>.md`.
- Criar o arquivo no início da sessão e atualizá-lo ao longo dela.
- Registrar a solicitação do usuário de forma literal ou fiel.
- Registrar decisões, artefatos, comandos relevantes e pendências.
- Não registrar segredos, tokens ou dados pessoais sensíveis.
- Ao final, preencher hora de término e status (`concluído`, `falhou`, `cancelado`).

## Estrutura mínima

1. Metadados
2. Objetivo
3. Solicitação do usuário
4. Contexto inicial
5. Linha do tempo
6. Decisões
7. Artefatos gerados/alterados
8. Pendências
9. Transcript

## Como criar

```powershell
powershell -File scripts/New-LogEntry.ps1 -Type conversation -Slug minha-sessao -Title "Minha sessão"
```

## Como adicionar uma mensagem

```powershell
powershell -File scripts/Add-ConversationEntry.ps1 `
  -LogFile logs/conversations/2026-11-09-session-001-bootstrap-repositorio.md `
  -Role assistant `
  -Message "Resumo da resposta."
```

## Índice

| Sessão | Data | Tema | Status |
|---|---|---|---|
| [`2026-11-09-session-001-bootstrap-repositorio.md`](2026-11-09-session-001-bootstrap-repositorio.md) | 2026-11-09 | Bootstrap e organização do repositório | concluído |
| [`2026-11-09-session-002-compatibilidade-opencode-hermes.md`](2026-11-09-session-002-compatibilidade-opencode-hermes.md) | 2026-11-09 | Compatibilidade OpenCode e Hermes | concluído |
| [`2026-11-09-session-003-conversas-consolidadas.md`](2026-11-09-session-003-conversas-consolidadas.md) | 2026-11-09 | Consolidação das conversas em um único arquivo | concluído |
| [`2026-11-09-session-004-contexto-e-regras.md`](2026-11-09-session-004-contexto-e-regras.md) | 2026-11-09 | Verificação de contexto e regras | concluído |
| [`2026-11-11-session-005-fonte-paperclip.md`](2026-11-11-session-005-fonte-paperclip.md) | 2026-11-11 | Registro da fonte externa `paperclipai/paperclip` | concluído |
| [`2026-11-11-session-006-decisoes-arquitetura.md`](2026-11-11-session-006-decisoes-arquitetura.md) | 2026-11-11 | Análise das seis decisões de arquitetura | concluído |
| [`2026-11-11-session-007-planejamento-fase-0.md`](2026-11-11-session-007-planejamento-fase-0.md) | 2026-11-11 | Planejamento da Fase 0 | concluído |
| [`2026-11-11-session-008-aprovacao-plano-e-host.md`](2026-11-11-session-008-aprovacao-plano-e-host.md) | 2026-11-11 | Aprovação do plano e definição do host | concluído |
| [`2026-11-11-session-009-decisao-ai-local.md`](2026-11-11-session-009-decisao-ai-local.md) | 2026-11-11 | Decisão de ferramentas e modelos de IA 100% locais | concluído |
| [`2026-11-11-session-010-execucao-e0-primary-host.md`](2026-11-11-session-010-execucao-e0-primary-host.md) | 2026-11-11 | Execução da E0 no host principal | concluído |
| [`2026-11-12-session-011-esqueleto-e1.md`](2026-11-12-session-011-esqueleto-e1.md) | 2026-11-12 | Execução da E1 | concluído |
| [`2026-11-12-session-012-execucao-e2-gateway.md`](2026-11-12-session-012-execucao-e2-gateway.md) | 2026-11-12 | Execução da E2 | concluído |
| [`2026-11-12-session-013-execucao-e3-paperclip.md`](2026-11-12-session-013-execucao-e3-paperclip.md) | 2026-11-12 | Execução da E3 | concluído |
| [`2026-11-12-session-014-execucao-e4-paperclip.md`](2026-11-12-session-014-execucao-e4-paperclip.md) | 2026-11-12 | Execução da E4 | em andamento |
