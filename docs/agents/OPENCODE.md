# OpenCode

Guia de compatibilidade do repositório **Paperclip Medusa** com o [OpenCode](https://opencode.ai/docs/).

## 1. Arquivos usados pelo OpenCode

| Arquivo | Função |
|---|---|
| [`../../AGENTS.md`](../../AGENTS.md) | Regras do projeto. Carregado automaticamente a partir da raiz ou de diretórios superiores. |
| [`../../opencode.json`](../../opencode.json) | Configuração do projeto. Declara instruções adicionais no campo `instructions`. |
| [`MEMORY.md`](MEMORY.md) | Memória estável do projeto, carregada como instrução adicional. |
| [`OPENCODE.md`](OPENCODE.md) | Este guia, carregado como instrução adicional. |

O arquivo `opencode.json` atual contém:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": [
    "docs/CONVENTIONS.md",
    "docs/GIT_WORKFLOW.md",
    "docs/agents/MEMORY.md",
    "docs/agents/OPENCODE.md"
  ]
}
```

## 2. Precedência das regras

O OpenCode procura regras nesta ordem:

1. `AGENTS.md` no diretório atual e nos diretórios superiores (a primeira correspondência vence).
2. `~/.config/opencode/AGENTS.md` (regra global do usuário).
3. `~/.claude/CLAUDE.md` (compatibilidade com Claude Code, se habilitada).

O campo `instructions` do `opencode.json` é combinado com o `AGENTS.md`; ele não o substitui.

> **Não crie `CLAUDE.md` na raiz.** O OpenCode só o usaria se `AGENTS.md` não existisse, e manter os dois duplica regras.

## 3. O que o OpenCode não usa

- `MEMORY.md` na raiz não é carregado automaticamente. A memória do projeto usada pelo OpenCode é [`MEMORY.md`](MEMORY.md), referenciada em `opencode.json`.
- `HERMES.md` e `.hermes.md` são específicos do Hermes Agent e não são carregados pelo OpenCode.
- Registros em `logs/` não são carregados automaticamente; o agente deve consultá-los quando a tarefa exigir histórico.

## 4. Fluxo de trabalho no OpenCode

1. Abra a sessão na raiz do repositório para que `AGENTS.md` e `opencode.json` sejam encontrados.
2. Confirme que as instruções foram carregadas pedindo ao agente para resumir as regras.
3. Trabalhe seguindo [`../../AGENTS.md`](../../AGENTS.md), [`../CONVENTIONS.md`](../CONVENTIONS.md) e [`../GIT_WORKFLOW.md`](../GIT_WORKFLOW.md).
4. Registre a sessão em `logs/conversations/` e os demais artefatos nas pastas correspondentes.
5. Execute `powershell -File scripts/Test-RepositoryStructure.ps1` antes de commitar.

## 5. Regras pessoais

- Para regras pessoais válidas em todos os projetos, use `~/.config/opencode/AGENTS.md`.
- Para uma configuração pessoal deste projeto, use `opencode.json` local não versionado ou uma configuração global; não altere as regras compartilhadas sem registrar a decisão.
- O arquivo `AGENTS.override.md` é uma convenção do Hermes Agent; o OpenCode não o carrega automaticamente.

## 6. Verificação

1. Abra uma nova sessão do OpenCode na raiz do repositório.
2. Peça: `Liste as regras que você carregou de AGENTS.md e de opencode.json.`
3. Confira se a resposta menciona:
   - a regra da raiz limpa;
   - os registros obrigatórios em `logs/`;
   - a nomenclatura `YYYY-MM-DD-<prefixo>-<NNN>-<slug>.md`;
   - a proibição de criar `.hermes.md` ou `HERMES.md` na raiz.

Se as regras não forem carregadas:

- confirme que a sessão foi aberta dentro do repositório;
- valide o JSON com `Get-Content opencode.json -Raw | ConvertFrom-Json`;
- reinicie a sessão após alterar `AGENTS.md` ou `opencode.json`;
- verifique se existe um `AGENTS.md` mais próximo na árvore de diretórios.

## 7. Limitações

- O OpenCode não registra sessões automaticamente; o registro em `logs/` é responsabilidade do agente.
- O campo `instructions` não interpreta referências `@arquivo`; use caminhos relativos explícitos, como os já configurados.
- O arquivo `opencode.json` é validado contra <https://opencode.ai/config.json>. Consulte a documentação oficial de [Rules](https://opencode.ai/docs/rules/) e [Config](https://opencode.ai/docs/config/) para campos adicionais.
