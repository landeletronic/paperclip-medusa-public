# Tarefas

Registro de tarefas planejadas e concluídas.

## Regras

- Nome: `YYYY-MM-DD-task-NNN-<slug>.md`.
- Toda tarefa deve ter status, critérios de aceite e evidências.
- Usar checkboxes para o plano.
- Tarefas concluídas permanecem no histórico.
- Relacionar commits, comandos, testes e inventários.

## Status possíveis

- `backlog`
- `em andamento`
- `bloqueada`
- `concluída`
- `cancelada`

## Como criar

```powershell
powershell -File scripts/New-LogEntry.ps1 -Type task -Slug ajuste-x -Title "Ajuste X"
```

## Índice

| Tarefa | Data | Tema | Status |
|---|---|---|---|
| [`2026-11-09-task-001-bootstrap-repositorio.md`](2026-11-09-task-001-bootstrap-repositorio.md) | 2026-11-09 | Bootstrap e organização do repositório | concluída |
| [`2026-11-09-task-002-compatibilidade-opencode-hermes.md`](2026-11-09-task-002-compatibilidade-opencode-hermes.md) | 2026-11-09 | Compatibilidade OpenCode e Hermes | concluída |
| [`2026-11-09-task-003-conversas-consolidadas.md`](2026-11-09-task-003-conversas-consolidadas.md) | 2026-11-09 | Consolidação das conversas | concluída |
| [`2026-11-11-task-008-execucao-e0-host.md`](2026-11-11-task-008-execucao-e0-host.md) | 2026-11-11 | Executar E0 no Davy Jones | concluída |
| [`2026-11-11-task-009-registrar-ai-local.md`](2026-11-11-task-009-registrar-ai-local.md) | 2026-11-11 | Registrar diretriz de IA 100% local | concluída |
| [`2026-11-12-task-010-esqueleto-e1.md`](2026-11-12-task-010-esqueleto-e1.md) | 2026-11-12 | Esqueleto versionado da E1 | concluída |
| [`2026-11-12-task-011-execucao-e2-gateway.md`](2026-11-12-task-011-execucao-e2-gateway.md) | 2026-11-12 | Banco e gateway locais da E2 | concluída |
| [`2026-11-12-task-012-execucao-e3-paperclip.md`](2026-11-12-task-012-execucao-e3-paperclip.md) | 2026-11-12 | Paperclip e empresa da E3 | concluída |
| [`2026-11-12-task-013-execucao-e4-paperclip.md`](2026-11-12-task-013-execucao-e4-paperclip.md) | 2026-11-12 | Primeira tarefa ponta a ponta da E4 | em andamento |
| [`2026-11-14-task-048-portal-servicos-davy.md`](2026-11-14-task-048-portal-servicos-davy.md) | 2026-11-14 | Portal de serviços do Davy Jones | concluída |

## Backlog

- E3 aguarda autorização explícita para início.
