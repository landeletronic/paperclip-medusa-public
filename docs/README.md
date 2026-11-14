# Documentação

Índice da documentação do projeto **Paperclip Medusa**.

## Conteúdo

| Documento | Descrição |
|---|---|
| [`CONVENTIONS.md`](CONVENTIONS.md) | Convenções de organização, nomenclatura e registro. |
| [`GIT_WORKFLOW.md`](GIT_WORKFLOW.md) | Fluxo de trabalho Git, branches, commits e publicação. |
| [`agents/README.md`](agents/README.md) | Integração com OpenCode e Hermes Agent. |
| [`agents/OPENCODE.md`](agents/OPENCODE.md) | Regras e verificação no OpenCode. |
| [`agents/HERMES.md`](agents/HERMES.md) | Contexto e memória no Hermes Agent. |
| [`agents/MEMORY.md`](agents/MEMORY.md) | Memória estável e curada do projeto. |
| [`assets/README.md`](assets/README.md) | Gestão de imagens, diagramas e capturas de tela. |
| [`assets/screenshots/README.md`](assets/screenshots/README.md) | Catálogo e metadados das capturas de tela. |
| [`research/README.md`](research/README.md) | Índice dos estudos e comparativos. |
| [`plans/README.md`](plans/README.md) | Índice dos planos de implementação. |

## Documentos de pesquisa

- [`research/2026-11-09-comparativo-modelos-free-hermes.md`](research/2026-11-09-comparativo-modelos-free-hermes.md) — estudo histórico de modelos gratuitos; não representa a arquitetura vigente.
- [`research/2026-11-09-limites-modelos-free-hermes.md`](research/2026-11-09-limites-modelos-free-hermes.md) — estudo histórico de cotas externas, substituído pela diretriz local.
- [`research/2026-11-11-decisao-ai-100-local.md`](research/2026-11-11-decisao-ai-100-local.md) — decisão vigente: ferramentas, agentes e modelos de IA somente em infraestrutura local/autogerida.

## Planos

- [`plans/2026-11-11-plano-fase-0-poc.md`](plans/2026-11-11-plano-fase-0-poc.md) — plano da Fase 0: PoC ponta a ponta com LiteLLM, Paperclip e Hermes (concluída, E0–E7).
- [`plans/2026-11-12-estado-do-projeto.md`](plans/2026-11-12-estado-do-projeto.md) — **estado do projeto (documento vivo)**: fases/etapas, concluído, tempo decorrido registrado, pendências/previsões e registro de conclusões.
- [`plans/2026-11-12-plano-fase-1-containers-por-run.md`](plans/2026-11-12-plano-fase-1-containers-por-run.md) — **Fase 1 (concluída)**: containers por run, workspaces persistentes e artefatos (F1.0–F1.6).
- [`plans/2026-11-12-plano-fase-2-painel-capacidade-multiempresa.md`](plans/2026-11-12-plano-fase-2-painel-capacidade-multiempresa.md) — **Fase 2 (concluída)**: painel próprio, capacidade por máquina/modelo e múltiplas empresas (F2.0–F2.4).
- [`plans/2026-11-13-plano-fase-3-kubernetes-keda-external-secrets.md`](plans/2026-11-13-plano-fase-3-kubernetes-keda-external-secrets.md) — **Fase 3 (concluída)**: Kubernetes local, KEDA (fila + teto de réplicas) e External Secrets (F3.0–F3.4).
- [`plans/2026-11-13-plano-fase-4-agente-em-container.md`](plans/2026-11-13-plano-fase-4-agente-em-container.md) — **Fase 4 (concluída)**: agente em container por run, executor-serviço autenticado, workspace sob demanda e observabilidade K8s (F4.0–F4.4; escopo definido por evidência — não constava do roadmap).
- [`plans/2026-11-13-plano-padrao-helper-local.md`](plans/2026-11-13-plano-padrao-helper-local.md) — **PLANO PADRÃO DO PROJETO**: auxiliar local na RX 5500 XT (chief-of-staff), fases 0–5, critérios de aprovação e recomendação final.
- [`plans/2026-11-13-comparacao-plano-padrao-x-estado-atual.md`](plans/2026-11-13-comparacao-plano-padrao-x-estado-atual.md) — comparação do plano padrão com o estado atual (fase a fase, com evidências) e reconciliação da numeração de fases.

## Documentação operacional

Os registros de conversas, comandos, execuções, tarefas, testes e inventários ficam em [`../logs/`](../logs/README.md), separados da documentação conceitual.
