# Comandos

Registro dos comandos executados no projeto.

## Regras

- Agrupar comandos relacionados em um único arquivo por sessão/lote.
- Nome: `YYYY-MM-DD-command-NNN-<slug>.md`.
- Para cada comando, registrar:
  - hora;
  - diretório de trabalho;
  - comando exato;
  - código de saída;
  - saída relevante;
  - efeitos colaterais.
- Destacar comandos destrutivos ou irreversíveis.
- Nunca registrar segredos.

## Como criar

```powershell
powershell -File scripts/New-LogEntry.ps1 -Type command -Slug bootstrap -Title "Bootstrap"
```

## Como executar e registrar automaticamente

```powershell
powershell -File scripts/Record-Command.ps1 `
  -Command "git status --short" `
  -Description "Conferir estado do repositório" `
  -LogFile logs/commands/2026-11-09-command-001-bootstrap.md
```

## Índice

| Registro | Data | Tema | Status |
|---|---|---|---|
| [`2026-11-09-command-001-bootstrap.md`](2026-11-09-command-001-bootstrap.md) | 2026-11-09 | Bootstrap do repositório | concluído |
| [`2026-11-09-command-002-compatibilidade-opencode-hermes.md`](2026-11-09-command-002-compatibilidade-opencode-hermes.md) | 2026-11-09 | Compatibilidade OpenCode e Hermes | concluído |
| [`2026-11-09-command-003-conversas-consolidadas.md`](2026-11-09-command-003-conversas-consolidadas.md) | 2026-11-09 | Consolidação das conversas | concluído |
| [`2026-11-11-command-007-execucao-e0-primary-host.md`](2026-11-11-command-007-execucao-e0-primary-host.md) | 2026-11-11 | Execução da E0 no host principal | concluído |
| [`2026-11-12-command-008-esqueleto-e1.md`](2026-11-12-command-008-esqueleto-e1.md) | 2026-11-12 | Esqueleto e validação da E1 | concluído |
| [`2026-11-12-command-009-execucao-e2-gateway.md`](2026-11-12-command-009-execucao-e2-gateway.md) | 2026-11-12 | Implantação e aceite da E2 | concluído |
| [`2026-11-12-command-010-execucao-e3-paperclip.md`](2026-11-12-command-010-execucao-e3-paperclip.md) | 2026-11-12 | Implantação e aceite da E3 | concluído |
| [`2026-11-12-command-011-execucao-e4-paperclip.md`](2026-11-12-command-011-execucao-e4-paperclip.md) | 2026-11-12 | Implantação e aceite da E4 | em andamento |
