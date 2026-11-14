# Registros operacionais

Esta pasta é a memória auditável do projeto. Todo trabalho relevante gera um registro versionado aqui.

## Tipos de registro

| Pasta | Prefixo | Conteúdo |
|---|---|---|
| [`conversations/`](conversations/README.md) | `session` | Sessões com agentes de IA, decisões e transcript. |
| [`commands/`](commands/README.md) | `command` | Comandos executados, saídas e códigos de retorno. |
| [`executions/`](executions/README.md) | `execution` | Execuções de scripts, pipelines e rotinas. |
| [`tasks/`](tasks/README.md) | `task` | Tarefas, critérios de aceite e evidências. |
| [`tests/`](tests/README.md) | `test` | Testes, casos e resultados. |
| [`inventories/`](inventories/README.md) | `inventory` | Inventários de arquivos e hashes. |

## Nomenclatura

```text
YYYY-MM-DD-<prefixo>-<NNN>-<slug>.md
```

Exemplo: `2026-11-14-task-043-versionar-backlog-commits-logicos.md`.

## Regras

1. Um registro por sessão/lote/execução, não um por linha de comando.
2. Registrar data, hora, autor, status e links relacionados.
3. Nunca incluir segredos; mascarar como `<REDACTED>`.
4. Atualizar o status ao concluir (`concluído`, `falhou`, `cancelado`).
5. Não apagar registros antigos; eles fazem parte do histórico.
6. Usar os templates de `templates/` e os scripts de `scripts/`.

## Como consultar o histórico

Os arquivos em cada pasta são o índice canônico. Este README não mantém uma lista manual exaustiva,
pois ela ficava desatualizada a cada sessão.

```bash
# Todos os registros, em ordem cronológica
find logs -type f -name '*.md' ! -name README.md | sort

# Registro mais recente de cada tipo
for d in conversations commands executions tasks tests inventories; do
  find "logs/$d" -maxdepth 1 -type f -name '*.md' ! -name README.md | sort | tail -1
done

# Quantidade por tipo
for d in conversations commands executions tasks tests inventories; do
  printf '%-14s %s\n' "$d" "$(find "logs/$d" -maxdepth 1 -type f -name '*.md' ! -name README.md | wc -l)"
done
```

## Estado consolidado

- Estado vivo das fases: [`../docs/plans/2026-11-12-estado-do-projeto.md`](../docs/plans/2026-11-12-estado-do-projeto.md).
- Runbook operacional: [`../docs/runbooks/RUNBOOK-operacao-recuperacao.md`](../docs/runbooks/RUNBOOK-operacao-recuperacao.md).
- Inventários: [`inventories/`](inventories/README.md).
- Histórico Git: `git log --oneline --decorate`.
