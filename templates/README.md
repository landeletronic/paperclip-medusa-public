# Templates

Modelos usados por `scripts/New-LogEntry.ps1` para criar registros padronizados.

## Placeholders

| Placeholder | Substituído por |
|---|---|
| `{{ID}}` | Identificador no padrão `YYYY-MM-DD-<prefixo>-<NNN>` |
| `{{DATE}}` | Data (`YYYY-MM-DD`) |
| `{{TIME}}` | Hora local (`HH:mm:ss`) |
| `{{TITLE}}` | Título informado no comando |
| `{{SLUG}}` | Slug informado no comando |
| `{{AUTHOR}}` | Autor (usuário ou agente) |
| `{{WORKSPACE}}` | Caminho da raiz do repositório |
| `{{TYPE}}` | Tipo do registro |

## Arquivos

| Template | Tipo |
|---|---|
| `conversation.md` | Conversa/sessão |
| `command.md` | Comandos |
| `execution.md` | Execução |
| `task.md` | Tarefa |
| `test.md` | Teste |
| `inventory.md` | Inventário |

## Regras

- Manter os placeholders em maiúsculas e entre chaves duplas.
- Não remover seções obrigatórias; adicionar seções específicas quando necessário.
- Texto em UTF-8.
