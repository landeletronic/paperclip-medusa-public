# executor/ — mecanismo de execução por container efêmero (Fase 1)

`executor.py` é o **executor dedicado de escopo mínimo** previsto no contrato
[`../../../docs/research/2026-11-12-f1-1-contrato-runtime-workspace-artefatos.md`](../../../docs/research/2026-11-12-f1-1-contrato-runtime-workspace-artefatos.md)
e na decisão F1.0: cria **um container efêmero por run**, monta o workspace persistente em
`/workspace`, injeta segredos por run, aplica limites/timeout e **remove o container sempre**
(sucesso, falha ou timeout).

> **Regra de segurança:** este executor roda **no host** (CLI; futuramente serviço dedicado) com
> acesso ao Docker do host. O container `paperclip` **nunca** recebe `docker.sock` — o Paperclip
> delega a criação de containers a este mecanismo (integração na F1.3).

## Uso

```bash
# Instalação canônica no host (executado como usuário comum do grupo docker — ex.: tlandskron):
#   sudo install -m 755 -o root -g root src/infra/executor/executor.py /usr/local/bin/paperclip-run-executor
/usr/local/bin/paperclip-run-executor health          # Docker disponível?
/usr/local/bin/paperclip-run-executor run --spec spec.json        # executa um run
/usr/local/bin/paperclip-run-executor run --spec - < spec.json    # spec via stdin
/usr/local/bin/paperclip-run-executor run --spec spec.json --transcript /caminho/run.log
```

> **Menor privilégio:** o executor roda como **usuário comum do grupo `docker`** (não `root`); a
> cópia em `/opt/paperclip-medusa/executor/` (referência/documentação do deploy) não é a operacional.
> O `user` do spec (`uid:gid` do dono do workspace) mantém os artefatos com o dono correto.

- Saída: **JSON no stdout** (resultado: exit code, duração, limites aplicados, transcript,
  tails mascarados, `container_removed`); mensagens humanas no stderr.
- Exit codes do tool: `0` run ok · `2` run falhou · `3` timeout · `4` spec inválida · `5` erro Docker ·
  `6` capacidade esgotada (concorrência).
- **Métricas (Fase 2):** cada run atualiza `paperclip_executor.prom` (textfile do node-exporter):
  `paperclip_executor_{runs,failures,timeouts,rejected}_total`, `_last_duration_ms`, `_active_runs`,
  `_max_concurrent`, `_last_timestamp_seconds`; `metrics` regrava o `.prom` sem executar run.
  Estado: `PAPERCLIP_EXECUTOR_STATE` (default `~/ci/paperclip-executor-state.json`); textfile:
  `PAPERCLIP_TEXTFILE_DIR` (default `~/hermes-architect/ci/textfile`).
- **Capacidade:** `PAPERCLIP_EXECUTOR_MAX_CONCURRENT` (default `2`) — teto de runs simultâneos, slots
  por `flock` (crash-safe); acima do teto o run é **rejeitado** (exit 6, métrica `rejected_total`).

## Spec (JSON)

| Campo | Obrigatório | Descrição |
|---|---|---|
| `image` | sim | imagem **pinada** (digest `@sha256:...` ou tag imutável); flutuantes são recusadas (`--allow-unpinned` para exceção) |
| `workspace` | sim | caminho do workspace no host (deve estar dentro das raízes permitidas); montado rw em `/workspace` |
| `command` | sim | lista de comando (ou string = `sh -c`) |
| `env` | não | variáveis/segredos por run (valores **mascarados** em logs/transcripts) |
| `limits` | não | `cpus`, `memory` (ex.: `256m`), `pids` |
| `timeout_seconds` | não | prazo do run (default 600); estouro = container removido, `timed_out: true` |
| `network` | não | modo de rede (default `none`; integração F1.3 usa rede interna do Compose) |
| `user` | não | usuário dentro do container (ex.: `1000:1000`) |
| `entrypoint` | não | sobrescreve o entrypoint da imagem (necessário em imagens de runtime com entrypoint de servidor — ex.: `"/bin/sh"` com `command: ["-c", …]`) |
| `class` | não | classe de execução (`exec-run`/`ceo-run`/`generic-run`) |
| `run_id` | não | identificador (gerado se ausente) — usado em labels do container para auditoria |

Ver [`spec.example.json`](spec.example.json).

## Raízes permitidas de workspace

Por padrão: `/var/lib/docker/volumes/paperclip-medusa_paperclip-data/_data/instances`
(workspaces do Paperclip no volume). Estenda com `--allow-root DIR` (repetível) ou
`EXECUTOR_ALLOWED_ROOTS` (separador `:`). Caminhos fora disso são **recusados**.

## Garantias (cláusulas do contrato atendidas)

1. Container criado por run e **sempre removido** (`docker rm -f` + verificação), mesmo em
   falha/timeout.
2. Só monta o workspace autorizado em `/workspace` (rw) — nunca raiz do host, `docker.sock` ou
   `~/.ssh`.
3. Artefatos gravados no workspace sobrevivem ao container (fs do container é descartado).
4. Segredos (`env`) injetados por run e **mascarados** em `stdout_tail`/`stderr_tail`/transcript.
5. Limites (`--cpus`, `--memory`, `--pids-limit`) aplicados e reportados em `limits_applied`.
6. Auditoria: labels `paperclip.run_id`/`paperclip.run_class`, `container_id`, estado
   (`exit_code`, `oom_killed`), duração.
7. 100% local: sem rede externa por padrão (`network: none`).

## Integração (F1.3)

A integração com o Paperclip (environments/execution-workspaces/leases/anexação de artefatos)
chama este mecanismo — por plugin de sandbox provider (caminho nativo, SDK de plugin do produto)
ou pelo adaptador — sempre **sem** expor o socket do Docker ao container `paperclip`.
