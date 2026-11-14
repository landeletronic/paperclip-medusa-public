# Memória estável do projeto

> **Não confundir:** este arquivo é a memória curada do repositório **Paperclip Medusa**. A memória global do Hermes Agent fica em `~/.hermes/memories/MEMORY.md` e é gerenciada pela ferramenta `memory`. Este arquivo é versionado, revisado por humanos e carregado pelo OpenCode via `opencode.json`.

## 1. Identidade do projeto

- Nome: **Paperclip Medusa**.
- Localização: não presumir caminho fixo; descobrir com `git rev-parse --show-toplevel`.
- Branch principal: `main`.
- Repositório Git local, sem remote configurado até o momento.
- Identidade Git local: `Paperclip Medusa DevOps <devops@paperclip-medusa.local>`.
- Inicializado em **2026-11-09**.

### Visão em construção

- Objetivo: empresa de desenvolvimento de software operada por agentes, baseada no `paperclipai/paperclip`.
- Componentes em containers Docker Compose; Kubernetes local com k3d, KEDA e External Secrets já
  implementado para workloads efêmeros.
- Hermes Agent como orquestrador; OpenCode e agentes locais como executores/subagentes.
- **100% das ferramentas, agentes e inferências de IA locais/autogeridas**; nenhuma API de modelo
  em nuvem recebe prompts, contexto, código ou dados de tarefas.
- Gateway local para rotear entre Ollama, llama.cpp e outros endpoints locais, com fallback,
  métricas e controle de acesso.
- Internet continua permitida para Git, downloads, atualizações e documentação; isso não autoriza
  processamento de IA por terceiros.
- Serviço web em HTTPS para monitorar uso e capacidade por máquina/modelo local.
- Linux como sistema operacional.
- Decisões e recomendações: [`../research/2026-11-11-decisoes-arquitetura-paperclip-medusa.md`](../research/2026-11-11-decisoes-arquitetura-paperclip-medusa.md).

## 2. Regras que não mudam sem decisão registrada

1. A raiz contém somente arquivos essenciais de entrada, governança e configuração de infraestrutura/lint documentados; os demais conteúdos vivem em subpastas.
2. Todo conteúdo novo vive em uma subpasta organizada por utilidade.
3. Todo trabalho relevante gera registro em `logs/`.
4. A nomenclatura dos registros é `YYYY-MM-DD-<prefixo>-<NNN>-<slug>.md`.
5. Nenhum segredo é versionado.
6. Arquivos movidos preservam o conteúdo e têm o hash registrado em inventário.
7. Ferramentas e modelos de IA operam localmente; fallback para provedor de IA externo é proibido.

## 3. Estrutura essencial

| Caminho | Papel |
|---|---|
| `AGENTS.md` | Fonte única de regras para OpenCode e Hermes Agent. |
| `opencode.json` | Configuração do OpenCode e instruções adicionais. |
| `docs/agents/` | Guias de integração com OpenCode e Hermes Agent. |
| `docs/CONVENTIONS.md` | Convenções de organização, nomenclatura e registro. |
| `docs/plans/` | Planos de implementação por fase. |
| `docs/GIT_WORKFLOW.md` | Branches, commits, publicação e CI. |
| `logs/` | Memória auditável: conversas, comandos, execuções, tarefas, testes e inventários. |
| `scripts/` | Automação em PowerShell. |
| `templates/` | Modelos de registro. |
| `src/` | Código e infraestrutura: agentes, gateway, Compose, executor, Kubernetes e benchmarks. |

## 4. Decisões de compatibilidade

- `AGENTS.md` é compartilhado pelo OpenCode e pelo Hermes Agent.
- `opencode.json` carrega `docs/CONVENTIONS.md`, `docs/GIT_WORKFLOW.md`, `docs/agents/MEMORY.md` e `docs/agents/OPENCODE.md`.
- `.hermes.md` e `HERMES.md` não devem existir na raiz, pois têm prioridade sobre `AGENTS.md` no Hermes.
- `CLAUDE.md` e `.cursorrules` não são usados, para evitar duplicação de regras.
- `AGENTS.override.md` é permitido apenas como override pessoal e está no `.gitignore`.
- A memória global do Hermes (`MEMORY.md` e `USER.md`) não é versionada.

## 5. Comandos de referência

```powershell
# Validar a estrutura
powershell -File scripts/Test-RepositoryStructure.ps1

# Criar um registro
powershell -File scripts/New-LogEntry.ps1 -Type task -Slug minha-tarefa -Title "Minha tarefa"

# Gerar um inventário
powershell -File scripts/New-Inventory.ps1 -Slug estado-atual -Title "Inventário do estado atual"
```

## 6. Fontes externas de consulta

- [`../research/2026-11-11-fonte-paperclipai-paperclip.md`](../research/2026-11-11-fonte-paperclipai-paperclip.md) — documentação do projeto `paperclipai/paperclip` (<https://github.com/paperclipai/paperclip>), referência para orquestração de agentes, governança, orçamentos, skills e adaptadores. Uso apenas consultivo; não é dependência do projeto.

## 7. Onde procurar o estado atual

- [`../../README.md`](../../README.md) — visão geral e estado atual.
- [`../../logs/README.md`](../../logs/README.md) — índice dos registros.
- `git log --oneline` — histórico de commits.
- [`../../logs/inventories/`](../../logs/inventories/) — snapshots de arquivos e hashes.

### Estado consolidado

- Trilha de Plataforma P0–P4 concluída: PoC, containers por run, painel/capacidade/multiempresa,
  Kubernetes/KEDA/External Secrets e agente em container efêmero.
- Plano padrão do auxiliar local concluído (Fases 0–5): RX 6600 como baseline/Hermes, RX 5500 XT
  com llama.cpp Vulkan/Qwen3 8B, rota `medusa-local-helper`, `Chief of Staff Local` e concorrência
  validada entre as duas GPUs.
- Stack Paperclip/LiteLLM/PostgreSQL operacional no host principal; inferência exclusivamente local.
- Runbook: [`../runbooks/RUNBOOK-operacao-recuperacao.md`](../runbooks/RUNBOOK-operacao-recuperacao.md).
- Estado vivo: [`../plans/2026-11-12-estado-do-projeto.md`](../plans/2026-11-12-estado-do-projeto.md).

## 8. Como atualizar esta memória

- Adicione apenas fatos duradouros, decisões estáveis e referências úteis.
- Não copie histórico de sessão, comandos ou resultados de testes para cá; use `logs/`.
- Não registre segredos, dados pessoais ou informações voláteis (como o commit atual).
- Mantenha o arquivo curto e revise a cada mudança estrutural relevante.
- Registre a alteração em `logs/tasks/` ou no registro da sessão correspondente.
