# Integração com agentes de IA

Documentação da compatibilidade do repositório com **OpenCode** e **Hermes Agent**.

## Fonte única de regras

O arquivo [`../../AGENTS.md`](../../AGENTS.md) é a fonte única de regras compartilhadas. Ele fica na raiz porque os dois aplicativos o carregam automaticamente a partir do diretório de trabalho.

| Arquivo | Papel | Carregado por |
|---|---|---|
| [`../../AGENTS.md`](../../AGENTS.md) | Regras compartilhadas do projeto. | OpenCode e Hermes Agent. |
| [`../../opencode.json`](../../opencode.json) | Configuração do OpenCode; declara instruções adicionais. | OpenCode. |
| [`MEMORY.md`](MEMORY.md) | Memória estável e curada do projeto. | OpenCode (via `opencode.json`); Hermes Agent (sob demanda, por referência no `AGENTS.md`). |
| [`OPENCODE.md`](OPENCODE.md) | Funcionamento, precedência e verificação no OpenCode. | OpenCode (via `opencode.json`). |
| [`HERMES.md`](HERMES.md) | Funcionamento, memória global e verificação no Hermes Agent. | Hermes Agent (sob demanda, por referência no `AGENTS.md`). |

## Como cada aplicativo carrega as regras

### OpenCode

1. Procura `AGENTS.md` no diretório atual e nos diretórios superiores.
2. Carrega `opencode.json` do projeto e aplica o campo `instructions`.
3. Combina as instruções adicionais com o `AGENTS.md`.
4. Usa `~/.config/opencode/AGENTS.md` como regra global apenas se não houver regra local.

### Hermes Agent

1. Procura, na raiz do projeto, `.hermes.md` → `HERMES.md` → `AGENTS.override.md` → `AGENTS.md` → `CLAUDE.md` → `.cursorrules`; o primeiro encontrado vence.
2. Como o repositório usa `AGENTS.md`, o Hermes o carrega automaticamente.
3. Também carrega a memória global `~/.hermes/memories/MEMORY.md` e o perfil `~/.hermes/memories/USER.md` como um snapshot congelado no início da sessão.

> **Atenção:** não crie `.hermes.md` nem `HERMES.md` na raiz. Esses nomes têm prioridade sobre `AGENTS.md` no Hermes e fariam o aplicativo ignorar as regras compartilhadas.

## Verificação rápida

No OpenCode:

```text
Abra uma nova sessão na raiz do repositório e peça:
"Liste as regras que você carregou de AGENTS.md e de opencode.json."
```

No Hermes Agent:

```text
Abra uma nova sessão na raiz do repositório e execute:
/context

Depois peça:
"Liste as regras que você carregou de AGENTS.md."
```

O comando `/context` mostra quais arquivos de contexto foram carregados, truncados ou ignorados.

## Arquivos que não devem existir na raiz

| Arquivo | Motivo |
|---|---|
| `.hermes.md` | Teria prioridade sobre `AGENTS.md` no Hermes e quebraria a fonte única. |
| `HERMES.md` | Mesmo motivo. |
| `CLAUDE.md` | Só seria usado se `AGENTS.md` não existisse; manter os dois duplica regras. |
| `.cursorrules` | Só seria usado se não houvesse `AGENTS.md`; manter os dois duplica regras. |

`AGENTS.override.md` é permitido apenas como override pessoal e está listado no `.gitignore`. Ele não deve ser commitado.

## Relação com os registros operacionais

A compatibilidade não substitui os registros em `logs/`. Toda sessão continua obrigada a registrar conversa, comandos, execuções, tarefas, testes e inventários conforme [`../CONVENTIONS.md`](../CONVENTIONS.md).

## Documentos relacionados

- [`../../README.md`](../../README.md) — visão geral do repositório.
- [`../CONVENTIONS.md`](../CONVENTIONS.md) — convenções de organização e registro.
- [`../GIT_WORKFLOW.md`](../GIT_WORKFLOW.md) — fluxo Git.
- [`MEMORY.md`](MEMORY.md) — memória estável do projeto.
