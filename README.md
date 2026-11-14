# Paperclip Medusa

> Este repositório é um snapshot público sanitizado. Registros operacionais, planos internos, runbooks e identificadores de infraestrutura foram removidos ou generalizados.

Repositório de documentação, pesquisa e registros operacionais do projeto **Paperclip Medusa**.

> **Regra de ouro:** a raiz contém somente os arquivos essenciais de entrada (`README.md`, `AGENTS.md`, `opencode.json`), governança (`LICENSE`, `NOTICE`, `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`) e configuração oculta de infraestrutura/lint, além de `.github/`. Todo o demais conteúdo vive em uma subpasta organizada por utilidade.

## Sumário

- [Objetivo](#objetivo)
- [Diretriz de IA local](#diretriz-de-ia-local)
- [Estrutura](#estrutura)
- [Registros obrigatórios](#registros-obrigatórios)
- [Convenções de nomenclatura](#convenções-de-nomenclatura)
- [Scripts de automação](#scripts-de-automação)
- [Fluxo Git](#fluxo-git)
- [Estado atual](#estado-atual)
- [Regras para agentes](#regras-para-agentes)

## Objetivo

Centralizar, de forma versionada e auditável:

1. a documentação e a pesquisa do projeto;
2. os ativos visuais (capturas de tela, diagramas e imagens);
3. o histórico de conversas com agentes de IA;
4. os comandos executados, suas saídas e códigos de retorno;
5. as execuções de scripts e pipelines;
6. as tarefas, seus critérios de aceite e evidências;
7. os testes e seus resultados;
8. os inventários periódicos de arquivos e hashes.

## Diretriz de IA local

O Paperclip Medusa deve operar com **100% das ferramentas, agentes e modelos de IA em
infraestrutura local/autogerida**. Paperclip, Hermes, OpenCode, runtimes de inferência,
embeddings e modelos auxiliares não podem depender de APIs de modelos em nuvem.

- O gateway de IA permanece na arquitetura para roteamento, fallback, métricas e controle de
  acesso, mas aponta somente para endpoints locais, como Ollama e llama.cpp.
- O fallback ocorre entre modelos e máquinas locais; indisponibilidade local deve aparecer como
  estado operacional, nunca provocar envio silencioso de prompts a terceiros.
- GitHub, downloads de pacotes/modelos, atualizações e consulta a documentação externa podem
  continuar usando internet: a restrição é sobre processamento de IA e envio de dados de tarefas.
- A decisão completa está em
  [`docs/research/2026-11-11-decisao-ai-100-local.md`](docs/research/2026-11-11-decisao-ai-100-local.md).

## Estrutura

```text
paperclip-medusa/
├── README.md / AGENTS.md / opencode.json
├── LICENSE / NOTICE / CONTRIBUTING.md / CHANGELOG.md / SECURITY.md
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── dependabot.yml
│   └── workflows/{validate,lint,security}.yml
├── docs/          Documentação, planos, pesquisa, runbooks e guias de agentes
├── logs/          Conversas, comandos, execuções, tarefas, testes e inventários
├── scripts/       Automação e validação estrutural
├── src/           Agentes, gateway, Compose, executor, Kubernetes e benchmarks
└── templates/     Modelos dos registros operacionais
```

### Para que serve cada pasta

| Pasta | Utilidade |
|---|---|
| `docs/` | Documentação técnica, convenções, pesquisa e ativos visuais. |
| `docs/agents/` | Integração com OpenCode e Hermes Agent, incluindo a memória estável do projeto. |
| `docs/assets/` | Imagens, diagramas e capturas de tela usados na documentação. |
| `docs/research/` | Estudos, comparativos e material de apoio. |
| `logs/` | Registros operacionais versionados (a memória auditável do projeto). |
| `logs/conversations/` | Transcrições e resumos de cada sessão com agentes de IA. |
| `logs/commands/` | Comandos executados, saídas e códigos de retorno. |
| `logs/executions/` | Execuções de scripts, pipelines e rotinas. |
| `logs/tasks/` | Tarefas, status, critérios de aceite e evidências. |
| `logs/tests/` | Planos de teste, casos, resultados e evidências. |
| `logs/inventories/` | Inventários de arquivos, tamanhos e hashes. |
| `scripts/` | Automação em PowerShell para padronizar os registros. |
| `src/` | Código e infraestrutura: agentes, gateway, Compose, executor, Kubernetes e benchmarks. |
| `templates/` | Modelos reutilizáveis para cada tipo de registro. |
| `.github/workflows/` | Validação estrutural, lint e varredura de segredos no CI. |

### Governança

- [`LICENSE`](LICENSE) e [`NOTICE`](NOTICE): Apache License 2.0 e aviso legal.
- [`CONTRIBUTING.md`](CONTRIBUTING.md): ambiente, fluxo, validações e regras para contribuições.
- [`CHANGELOG.md`](CHANGELOG.md): mudanças relevantes e preparação para releases semânticos.
- [`SECURITY.md`](SECURITY.md): versões suportadas e relato privado de vulnerabilidades.
- [`.github/`](.github/): templates de issues/PR, Dependabot e workflows de qualidade e segurança.

O CI usa versões fixadas e checksums para linters binários. Logs históricos e documentos de pesquisa/planejamento são excluídos do Markdownlint para preservar evidências imutáveis; documentos normativos, READMEs e novos arquivos de governança permanecem cobertos.

### Compatibilidade com agentes de IA

O repositório é compatível com **OpenCode** e **Hermes Agent**:

| Arquivo | Papel |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Fonte única de regras compartilhadas; carregado automaticamente pelos dois aplicativos. |
| [`opencode.json`](opencode.json) | Configuração do OpenCode; carrega instruções adicionais. |
| [`docs/agents/OPENCODE.md`](docs/agents/OPENCODE.md) | Funcionamento, precedência e verificação no OpenCode. |
| [`docs/agents/HERMES.md`](docs/agents/HERMES.md) | Contexto, memória global e verificação no Hermes Agent. |
| [`docs/agents/MEMORY.md`](docs/agents/MEMORY.md) | Memória estável e curada do projeto. |

> A memória global do Hermes (`~/.hermes/memories/MEMORY.md` e `USER.md`) não é versionada. Não crie `.hermes.md` nem `HERMES.md` na raiz: esses nomes têm prioridade sobre `AGENTS.md` no Hermes.

## Registros obrigatórios

Todo trabalho relevante deve gerar um registro em `logs/`:

| Tipo | Pasta | Prefixo | Quando registrar |
|---|---|---|---|
| Conversa | `logs/conversations/` | `session` | No início ou no fim de cada sessão com agente. |
| Comando | `logs/commands/` | `command` | Para todo comando relevante executado no projeto. |
| Execução | `logs/executions/` | `execution` | Para scripts, pipelines e rotinas executadas. |
| Tarefa | `logs/tasks/` | `task` | Ao planejar e ao concluir uma tarefa. |
| Teste | `logs/tests/` | `test` | Para cada validação ou bateria de testes. |
| Inventário | `logs/inventories/` | `inventory` | Em snapshots periódicos ou antes/depois de mudanças grandes. |

### O que cada registro deve conter

- **Conversa:** objetivo, solicitação do usuário, decisões, artefatos gerados, pendências e transcript.
- **Comando:** data/hora, diretório, comando exato, código de saída, saída relevante e efeitos colaterais.
- **Execução:** gatilho, ambiente, passos, duração, status e artefatos produzidos.
- **Tarefa:** status, critérios de aceite, plano, evidências e links para commits/logs.
- **Teste:** objetivo, ambiente, casos, resultado esperado vs. obtido e evidência.
- **Inventário:** caminho, tipo, tamanho, SHA-256 e descrição de cada arquivo relevante.

## Convenções de nomenclatura

```text
YYYY-MM-DD-<prefixo>-<NNN>-<slug>.md
```

- `YYYY-MM-DD`: data do registro.
- `<prefixo>`: `session`, `command`, `execution`, `task`, `test` ou `inventory`.
- `<NNN>`: sequencial com três dígitos (`001`, `002`, ...).
- `<slug>`: descrição curta em minúsculas, sem acentos e separada por hífens.

Exemplos:

```text
logs/conversations/2026-11-09-session-001-bootstrap-repositorio.md
logs/commands/2026-11-09-command-001-bootstrap.md
logs/tests/2026-11-09-test-001-validacao-estrutura.md
```

Regras adicionais:

- Texto em **UTF-8**.
- Uma linha em branco ao final de cada arquivo.
- Nunca registrar segredos, tokens, senhas ou chaves privadas. Mascarar como `<REDACTED>`.
- Evidências grandes (logs extensos) podem ser resumidas, desde que o comando e o resultado sejam preservados.

## Scripts de automação

Os scripts ficam em `scripts/` e devem ser executados a partir da raiz do repositório.

### Criar um registro a partir de um template

```powershell
pwsh -File scripts/New-LogEntry.ps1 -Type conversation -Slug minha-sessao -Title "Minha sessão"
pwsh -File scripts/New-LogEntry.ps1 -Type task -Slug ajuste-x -Title "Ajuste X"
```

Tipos aceitos: `conversation`, `command`, `execution`, `task`, `test`, `inventory`.

### Adicionar uma mensagem à conversa atual

```powershell
pwsh -File scripts/Add-ConversationEntry.ps1 `
  -LogFile logs/conversations/2026-11-09-session-001-bootstrap-repositorio.md `
  -Role user `
  -Message "Solicitação registrada."
```

### Executar e registrar um comando

```powershell
pwsh -File scripts/Record-Command.ps1 `
  -Command "git status --short" `
  -Description "Conferir estado do repositório" `
  -LogFile logs/commands/2026-11-09-command-001-bootstrap.md
```

### Gerar um inventário automático

```powershell
pwsh -File scripts/New-Inventory.ps1 -Slug estado-atual -Title "Inventário do estado atual"
```

### Validar a estrutura antes de commitar

```powershell
pwsh -File scripts/Test-RepositoryStructure.ps1
```

> Em Windows PowerShell 5.1, substitua `pwsh` por `powershell`. Os scripts foram escritos para funcionar nos dois ambientes.

## Fluxo Git

- Branch principal: `main`.
- Branches de trabalho: `feat/`, `fix/`, `docs/`, `chore/`, `test/`.
- Commits seguem [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat: adiciona endpoint de catálogo
fix: corrige cálculo de frete
docs: registra sessão 001
chore: atualiza inventário
test: valida estrutura do repositório
```

- Antes de commitar:

```powershell
pwsh -File scripts/Test-RepositoryStructure.ps1
git status
git diff --staged
```

- O repositório não possui remote configurado. Para publicar:

```powershell
git remote add origin <URL_DO_REPOSITORIO>
git push -u origin main
```

Detalhes em [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md).

## Estado público

Este snapshot contém governança, automação e código reutilizável sem o histórico operacional privado.

## Regras para agentes

1. Ler [`AGENTS.md`](AGENTS.md), este `README.md`, `docs/CONVENTIONS.md` e `docs/GIT_WORKFLOW.md` antes de iniciar.
2. Consultar o guia do aplicativo em uso: [`docs/agents/OPENCODE.md`](docs/agents/OPENCODE.md) ou [`docs/agents/HERMES.md`](docs/agents/HERMES.md).
3. Criar ou atualizar o registro da conversa em `logs/conversations/` ao final de cada sessão.
4. Registrar comandos relevantes em `logs/commands/` com código de saída e saída resumida.
5. Registrar tarefas, testes e inventários nas pastas correspondentes.
6. Manter a raiz limpa: somente arquivos essenciais de entrada, governança e configuração de infraestrutura/lint documentados neste README.
7. Nunca commitar segredos ou dados sensíveis.
8. Executar `scripts/Test-RepositoryStructure.ps1` antes de cada commit.
9. Usar mensagens de commit no padrão Conventional Commits.
10. Preservar o conteúdo original ao mover arquivos; registrar a mudança no inventário.
