# Inventários

Snapshots do estado do repositório.

## Regras

- Nome: `YYYY-MM-DD-inventory-NNN-<slug>.md`.
- Incluir caminho, tipo, tamanho, SHA-256 e descrição.
- Gerar antes e depois de mudanças relevantes.
- Não editar inventários antigos; gerar um novo com sequencial novo.
- Inventários não substituem backup; são evidências de estado.

## Como gerar automaticamente

```powershell
powershell -File scripts/New-Inventory.ps1 -Slug estado-atual -Title "Inventário do estado atual"
```

## Índice

| Inventário | Data | Escopo | Status |
|---|---|---|---|
| [`2026-11-09-inventory-001-estado-inicial.md`](2026-11-09-inventory-001-estado-inicial.md) | 2026-11-09 | Estado anterior à reorganização | concluído |
| [`2026-11-09-inventory-002-estado-final.md`](2026-11-09-inventory-002-estado-final.md) | 2026-11-09 | Estado após o bootstrap | concluído |
| [`2026-11-09-inventory-003-pos-compatibilidade-agentes.md`](2026-11-09-inventory-003-pos-compatibilidade-agentes.md) | 2026-11-09 | Estado após a compatibilidade com agentes | concluído |
| [`2026-11-09-inventory-004-pos-conversas-consolidadas.md`](2026-11-09-inventory-004-pos-conversas-consolidadas.md) | 2026-11-09 | Estado após a consolidação das conversas | concluído |
