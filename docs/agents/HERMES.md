# Hermes Agent

Guia de compatibilidade do repositório **Paperclip Medusa** com o **Hermes Agent**.

## 1. Como o Hermes carrega o contexto do projeto

Na raiz do projeto, o Hermes procura os arquivos de contexto nesta ordem e usa **apenas o primeiro encontrado**:

1. `.hermes.md`
2. `HERMES.md`
3. `AGENTS.override.md`
4. `AGENTS.md`
5. `CLAUDE.md`
6. `.cursorrules`

Como o repositório usa [`../../AGENTS.md`](../../AGENTS.md), esse é o arquivo carregado automaticamente.

> **Atenção:** não crie `.hermes.md` nem `HERMES.md` na raiz. Eles têm prioridade sobre `AGENTS.md` e fariam o Hermes ignorar as regras compartilhadas com o OpenCode.

O Hermes também carrega:

- `SOUL.md` — personalidade global, lida apenas de `HERMES_HOME` (normalmente `~/.hermes/SOUL.md`);
- `AGENTS.md` de subdiretórios — descobertos progressivamente quando o agente acessa arquivos daquelas pastas;
- a memória global `MEMORY.md` e o perfil `USER.md`, descritos abaixo.

## 2. Memória global do Hermes

O Hermes mantém dois arquivos globais, fora do repositório:

| Arquivo | Conteúdo | Limite |
|---|---|---|
| `~/.hermes/memories/MEMORY.md` | Notas do agente: ambiente, convenções, ferramentas e aprendizados. | 2.200 caracteres |
| `~/.hermes/memories/USER.md` | Perfil do usuário: identidade, preferências e estilo de comunicação. | 1.375 caracteres |

Regras importantes:

- Os arquivos ficam em `~/.hermes/memories/` ou em `~/.hermes/profiles/<perfil>/memories/` quando um perfil é usado.
- O conteúdo é injetado no system prompt como um **snapshot congelado** no início da sessão. Alterações feitas durante a sessão só aparecem na próxima sessão.
- O agente grava usando a ferramenta `memory`, com `target: "memory"` ou `target: "user"`.
- A memória não compacta automaticamente: quando o limite é atingido, a ferramenta retorna erro e o agente precisa consolidar ou remover entradas.
- Não aponte dois processos do Hermes para o mesmo `HERMES_HOME`; use perfis separados.

### O que guardar na memória global

- fatos do ambiente que valem para vários projetos;
- preferências permanentes do usuário;
- aprendizados sobre ferramentas e fluxos que se repetem.

### O que não guardar na memória global

- regras específicas deste repositório — elas pertencem a [`../../AGENTS.md`](../../AGENTS.md);
- histórico de sessão, comandos e decisões — eles pertencem a `logs/`;
- segredos, tokens ou dados pessoais de terceiros.

A memória estável deste projeto fica em [`MEMORY.md`](MEMORY.md), versionada no repositório. Ela não substitui a memória global do Hermes.

## 3. Comandos úteis

| Comando | Função |
|---|---|
| `/context` | Mostra o que foi carregado no contexto, incluindo `AGENTS.md`, `SOUL.md` e memória. |
| `/context all` | Inclui o custo de habilidades e ferramentas. |
| `/memory` | Revisa gravações pendentes quando a aprovação de escrita está ativa. |
| `/memory pending` | Lista gravações pendentes. |
| `/memory approve all` | Aprova todas as gravações pendentes. |
| `/new` | Inicia uma nova sessão e recarrega o snapshot de memória e contexto. |
| `/compress` | Compacta o histórico para reduzir o consumo de tokens. |

Use `/new` em limites naturais de trabalho: fim de tarefa, mudança de assunto ou início de um novo dia. É nesse momento que a memória atualizada passa a valer.

## 4. Entradas sugeridas para a memória global

Se quiser que o Hermes lembre de fatos deste projeto em qualquer sessão, peça para ele salvar entradas curtas como:

```text
O repositório Paperclip Medusa deve ser aberto pela raiz do clone (descubra-a com
`git rev-parse --show-toplevel`) e usa `AGENTS.md` como fonte única de regras.
Os registros operacionais do Paperclip Medusa ficam em logs/ e seguem YYYY-MM-DD-<prefixo>-<NNN>-<slug>.md.
A raiz do Paperclip Medusa permite somente arquivos essenciais de entrada, governança e configuração documentados.
O guia do Hermes no Paperclip Medusa é docs/agents/HERMES.md.
```

Não copie esse bloco automaticamente: peça ao agente para usar a ferramenta `memory` e confirme com `/memory` ou abrindo o arquivo.

## 5. Fluxo de trabalho no Hermes

1. Abra a sessão na raiz do repositório para que `AGENTS.md` seja encontrado.
2. Execute `/context` e confirme que `AGENTS.md` aparece como carregado.
3. Trabalhe seguindo [`../../AGENTS.md`](../../AGENTS.md), [`../CONVENTIONS.md`](../CONVENTIONS.md) e [`../GIT_WORKFLOW.md`](../GIT_WORKFLOW.md).
4. Registre a sessão em `logs/conversations/` e os demais artefatos nas pastas correspondentes.
5. Execute `powershell -File scripts/Test-RepositoryStructure.ps1` antes de commitar.
6. Ao concluir, use `/new` para que a próxima sessão leia o estado atualizado.

## 6. Overrides pessoais

- `AGENTS.override.md` é um override pessoal por diretório, normalmente ignorado pelo Git. Ele tem prioridade sobre `AGENTS.md`, mas não deve ser commitado.
- Para isolamento completo, use um perfil do Hermes com `HERMES_HOME` próprio.
- Não edite `AGENTS.md` para incluir preferências pessoais; mantenha as regras compartilhadas no repositório.

## 7. Verificação e solução de problemas

Se o Hermes não estiver seguindo as regras:

1. Confirme que a sessão foi aberta na raiz retornada por `git rev-parse --show-toplevel`.
2. Execute `/context` e verifique se `AGENTS.md` foi carregado, truncado ou bloqueado.
3. Verifique se existe `.hermes.md`, `HERMES.md` ou `AGENTS.override.md` na raiz; qualquer um deles tem prioridade.
4. Confirme que a memória está habilitada na configuração do Hermes.
5. Inicie uma nova sessão com `/new` após alterar arquivos de contexto.
6. Consulte a documentação oficial de [Context Files](https://hermes-agent.ai/docs/user-guide/features/context-files) e [Persistent Memory](https://hermes-agent.ai/docs/user-guide/features/memory).

## 8. Limitações

- O Hermes não registra sessões automaticamente no repositório; o registro em `logs/` é responsabilidade do agente.
- A memória global tem limite de caracteres e não é versionada.
- O snapshot de memória e contexto é congelado no início da sessão; mudanças exigem uma nova sessão ou o comando de atualização de prompts, quando disponível.
