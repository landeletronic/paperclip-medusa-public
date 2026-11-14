# AGENTS.md — regras compartilhadas para agentes

Este arquivo é a fonte única de regras para agentes de IA que trabalham no repositório **Paperclip Medusa**. Ele é carregado automaticamente pelo **OpenCode** e pelo **Hermes Agent** quando a sessão começa na raiz do repositório.

> **Regra de ouro:** a raiz contém somente arquivos essenciais de entrada (`README.md`, `AGENTS.md`, `opencode.json`), governança (`LICENSE`, `NOTICE`, `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`) e configuração oculta de infraestrutura/lint, além de `.github/`. Qualquer outro conteúdo deve viver em uma subpasta organizada por utilidade.

## 1. Leitura obrigatória

Antes de executar qualquer tarefa, leia:

1. `README.md` — visão geral, estrutura e estado atual.
2. `docs/CONVENTIONS.md` — organização, nomenclatura e registros.
3. `docs/GIT_WORKFLOW.md` — branches, commits e publicação.
4. `docs/agents/MEMORY.md` — memória estável do projeto.
5. O guia do aplicativo em uso:
   - **OpenCode:** `docs/agents/OPENCODE.md`
   - **Hermes Agent:** `docs/agents/HERMES.md`

Não presuma o conteúdo desses arquivos: leia-os.

## 2. Estrutura do repositório

| Caminho | Utilidade |
|---|---|
| `docs/` | Documentação técnica, convenções, pesquisa e ativos visuais. |
| `docs/agents/` | Integração com OpenCode e Hermes Agent. |
| `docs/assets/` | Imagens, diagramas e capturas de tela. |
| `docs/research/` | Estudos, comparativos e material de apoio. |
| `logs/` | Registros operacionais versionados (a memória auditável do projeto). |
| `logs/conversations/` | Sessões com agentes de IA. |
| `logs/commands/` | Comandos executados, saídas e códigos de retorno. |
| `logs/executions/` | Execuções de scripts, pipelines e rotinas. |
| `logs/tasks/` | Tarefas, status, critérios de aceite e evidências. |
| `logs/tests/` | Testes, casos e resultados. |
| `logs/inventories/` | Inventários de arquivos e hashes. |
| `scripts/` | Automação em PowerShell. |
| `src/` | Código e infraestrutura da plataforma: agentes, gateway, Compose, executor, Kubernetes e benchmarks. |
| `templates/` | Modelos reutilizáveis de registro. |
| `.github/workflows/` | Validação automatizada no CI. |

## 3. Registros obrigatórios

Todo trabalho relevante gera um registro em `logs/`:

| Tipo | Pasta | Prefixo | Quando registrar |
|---|---|---|---|
| Conversa | `logs/conversations/` | `session` | No início e/ou no fim de cada sessão com agente. |
| Comando | `logs/commands/` | `command` | Para todo comando relevante executado. |
| Execução | `logs/executions/` | `execution` | Para scripts, pipelines e rotinas executadas. |
| Tarefa | `logs/tasks/` | `task` | Ao planejar e ao concluir uma tarefa. |
| Teste | `logs/tests/` | `test` | Para cada validação ou bateria de testes. |
| Inventário | `logs/inventories/` | `inventory` | Em snapshots periódicos ou antes/depois de mudanças grandes. |

Regras:

- Nomenclatura obrigatória: `YYYY-MM-DD-<prefixo>-<NNN>-<slug>.md`.
- O `slug` usa minúsculas, sem acentos e com hífens.
- Um arquivo por sessão/lote/execução; não crie um arquivo por mensagem.
- Use UTF-8 e termine o arquivo com uma linha em branco.
- Nunca registre segredos, tokens, senhas ou chaves. Mascare como `<REDACTED>`.
- Registre comandos com diretório, comando exato, código de saída e saída resumida.
- Registre testes com resultado esperado, resultado obtido e evidência.
- Atualize o status ao concluir: `concluído`, `falhou` ou `cancelado`.
- Não apague registros antigos; eles fazem parte do histórico.

Os modelos ficam em `templates/` e podem ser criados com:

```powershell
powershell -File scripts/New-LogEntry.ps1 -Type task -Slug minha-tarefa -Title "Minha tarefa"
```

## 4. Fluxo de trabalho

1. **Entenda e registre:** identifique o objetivo e crie/atualize a tarefa em `logs/tasks/`.
2. **Inspecione antes de mudar:** leia os arquivos relevantes e verifique `git status`.
3. **Implemente com escopo mínimo:** preserve o conteúdo existente e siga a estrutura do repositório.
4. **Valide:** execute `powershell -File scripts/Test-RepositoryStructure.ps1`.
5. **Registre:** atualize a conversa, os comandos, a execução, os testes e o inventário aplicáveis.
6. **Commit:** use Conventional Commits e uma mudança lógica por commit.

## 5. Git

- Branch principal: `main`.
- Branches de trabalho: `feat/`, `fix/`, `docs/`, `chore/`, `test/`, `refactor/`.
- Mensagens: `<tipo>(<escopo opcional>): <descrição no imperativo>`.
- Antes de commitar:

```powershell
powershell -File scripts/Test-RepositoryStructure.ps1
git status
git diff --staged
```

- Não reescreva histórico publicado sem coordenação.
- O repositório ainda não possui remote configurado; consulte `docs/GIT_WORKFLOW.md` para publicar.

## 6. Segurança

- Nunca versione `.env` reais, credenciais, chaves privadas ou dados pessoais de terceiros.
- Não execute comandos destrutivos sem confirmar o escopo e registrar o risco.
- Se um segredo for commitado por engano, revogue-o, remova-o do histórico e registre o incidente sem repetir o valor.
- Não crie arquivos na raiz fora das exceções documentadas.

## 7. Compatibilidade entre OpenCode e Hermes Agent

- **`AGENTS.md` é o arquivo comum.** Os dois aplicativos o carregam automaticamente a partir da raiz do projeto.
- **`opencode.json`** é a configuração do OpenCode. Ele carrega também `docs/CONVENTIONS.md`, `docs/GIT_WORKFLOW.md`, `docs/agents/MEMORY.md` e `docs/agents/OPENCODE.md`.
- **Não crie `.hermes.md` nem `HERMES.md` na raiz.** O Hermes dá prioridade a esses nomes e deixaria de carregar `AGENTS.md`, quebrando as regras compartilhadas. Se precisar de instruções pessoais, use `AGENTS.override.md` (ignorado pelo Git) ou um perfil separado do Hermes.
- **`MEMORY.md` do Hermes é global**, fica em `~/.hermes/memories/MEMORY.md` (ou no perfil ativo) e é gerenciado pela ferramenta `memory`. Não é um arquivo do repositório.
- **`docs/agents/MEMORY.md` é a memória estável do projeto**, versionada e curada por humanos. Use-a para fatos duradouros, não para histórico de sessão.
- O Hermes também mantém `USER.md` em `~/.hermes/memories/USER.md` para preferências do usuário. Não versione esse arquivo.
- Detalhes operacionais: `docs/agents/OPENCODE.md` e `docs/agents/HERMES.md`.

## 8. Critérios de conclusão

Uma tarefa só termina quando:

- o pedido foi atendido e verificado;
- a estrutura foi validada sem falhas;
- os registros obrigatórios foram criados ou atualizados;
- nenhum segredo foi introduzido;
- o estado final está descrito no commit ou no registro da tarefa.
