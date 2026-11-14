# Testes

Registro de testes e validações.

## Regras

- Nome: `YYYY-MM-DD-test-NNN-<slug>.md`.
- Registrar objetivo, ambiente, casos, resultado esperado vs. obtido e evidência.
- Status final: `passou`, `falhou` ou `parcial`.
- Testes automatizados devem apontar para o script ou workflow correspondente.
- Anexar saídas relevantes sem segredos.

## Como criar

```powershell
powershell -File scripts/New-LogEntry.ps1 -Type test -Slug validacao-estrutura -Title "Validação da estrutura"
```

## Índice

| Teste | Data | Tema | Resultado |
|---|---|---|---|
| [`2026-11-09-test-001-validacao-estrutura.md`](2026-11-09-test-001-validacao-estrutura.md) | 2026-11-09 | Validação da estrutura do repositório | passou |
| [`2026-11-09-test-002-compatibilidade-opencode-hermes.md`](2026-11-09-test-002-compatibilidade-opencode-hermes.md) | 2026-11-09 | Validação da compatibilidade OpenCode e Hermes | passou |
| [`2026-11-09-test-003-conversas-consolidadas.md`](2026-11-09-test-003-conversas-consolidadas.md) | 2026-11-09 | Validação da consolidação das conversas | passou |
| [`2026-11-11-test-009-validacao-ai-local.md`](2026-11-11-test-009-validacao-ai-local.md) | 2026-11-11 | Validação da decisão de IA 100% local | passou |
| [`2026-11-11-test-010-aceite-e0-davy.md`](2026-11-11-test-010-aceite-e0-davy.md) | 2026-11-11 | Aceite da E0 no Davy Jones | passou |
| [`2026-11-12-test-011-aceite-e1.md`](2026-11-12-test-011-aceite-e1.md) | 2026-11-12 | Aceite do esqueleto da E1 | passou |
| [`2026-11-12-test-012-aceite-e2-gateway.md`](2026-11-12-test-012-aceite-e2-gateway.md) | 2026-11-12 | Aceite do banco e gateway da E2 | passou |
| [`2026-11-12-test-013-aceite-e3-paperclip.md`](2026-11-12-test-013-aceite-e3-paperclip.md) | 2026-11-12 | Aceite do Paperclip e empresa da E3 | passou |
| [`2026-11-12-test-014-aceite-e4-paperclip.md`](2026-11-12-test-014-aceite-e4-paperclip.md) | 2026-11-12 | Aceite da primeira tarefa ponta a ponta da E4 | em andamento |
| [`2026-11-14-test-047-portal-servicos-davy.md`](2026-11-14-test-047-portal-servicos-davy.md) | 2026-11-14 | Portal de serviços do Davy Jones | passou |
