# Execuções

Registro de execuções de scripts, pipelines e rotinas.

## Regras

- Nome: `YYYY-MM-DD-execution-NNN-<slug>.md`.
- Registrar gatilho, ambiente, entradas, passos, duração, status e artefatos.
- Relacionar comandos, testes e commits.
- Execuções com falha devem incluir a causa raiz e a ação corretiva.

## Como criar

```powershell
powershell -File scripts/New-LogEntry.ps1 -Type execution -Slug deploy-homologacao -Title "Deploy em homologação"
```

## Índice

| Execução | Data | Tema | Status |
|---|---|---|---|
| [`2026-11-09-execution-001-bootstrap-repositorio.md`](2026-11-09-execution-001-bootstrap-repositorio.md) | 2026-11-09 | Bootstrap do repositório | concluído |
| [`2026-11-09-execution-002-compatibilidade-opencode-hermes.md`](2026-11-09-execution-002-compatibilidade-opencode-hermes.md) | 2026-11-09 | Compatibilidade OpenCode e Hermes | concluído |
| [`2026-11-09-execution-003-conversas-consolidadas.md`](2026-11-09-execution-003-conversas-consolidadas.md) | 2026-11-09 | Consolidação das conversas | concluído |
| [`2026-11-11-execution-004-e0-primary-host.md`](2026-11-11-execution-004-e0-primary-host.md) | 2026-11-11 | E0 no host principal | concluído |
| [`2026-11-12-execution-005-esqueleto-e1.md`](2026-11-12-execution-005-esqueleto-e1.md) | 2026-11-12 | Esqueleto versionado da E1 | concluído |
| [`2026-11-12-execution-006-e2-gateway.md`](2026-11-12-execution-006-e2-gateway.md) | 2026-11-12 | Banco e gateway da E2 | concluída |
| [`2026-11-12-execution-007-e3-paperclip.md`](2026-11-12-execution-007-e3-paperclip.md) | 2026-11-12 | Paperclip e empresa da E3 | concluída |
| [`2026-11-12-execution-008-e4-paperclip.md`](2026-11-12-execution-008-e4-paperclip.md) | 2026-11-12 | Primeira tarefa ponta a ponta da E4 | em andamento |
