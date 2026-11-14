# k8s/ — cluster local da Fase 3 (Kubernetes + KEDA + External Secrets)

Padrão de **escala** da plataforma Medusa (plano da Fase 0 §10; decisão 5: "fila + saturação, com
teto de réplicas"). **PoC local** — o cluster roda via **k3d** (k3s em containers Docker), contido e
reversível, sem tocar em iptables/systemd do host.

| Arquivo | Função |
|---|---|
| `bootstrap.sh` | (re)instala cluster + Vault + ESO + KEDA + workloads (idempotente; token do Vault só no host) |
| `verify.sh` | verificação **somente leitura** (node/API/exposição/ESO/KEDA/teto de réplicas) |
| `namespaces.yaml` | namespaces (`medusa-jobs`, `vault`, `external-secrets`, `keda`) |
| `secretstore-medusa.yaml` | `SecretStore` (Vault in-cluster) |
| `externalsecret-medusa.yaml` | `ExternalSecret` → `Secret medusa-app-secret` (rotação sincronizada) |
| `queue-redis.yaml` | fila local (Redis) |
| `run-worker.yaml` | pool de run-workers (consome a fila) |
| `scaledobject-run-worker.yaml` | KEDA: escala pela fila com **`maxReplicaCount=4` (teto)** |

## Uso (host)

```bash
bash /home/usuario/medusa-k8s/bootstrap.sh     # instalar/(re)criar tudo
bash /home/usuario/medusa-k8s/verify.sh        # verificar (somente leitura)
k3d cluster delete medusa                          # REMOÇÃO COMPLETA sem resíduos
```

- **API do cluster:** apenas `127.0.0.1:6443` (nunca na LAN). Acesso com `kubectl` no host.
- **Token do Vault:** gerado pelo bootstrap em `/home/usuario/ci/vault-root-token` (600) — fora do
  git; valores de teste nunca versionados.
- **Versões pinadas:** k3d `v5.9.0`, kubectl `v1.31.4`, helm `v3.16.4`, charts `vault 0.29.1`,
  `external-secrets 0.10.5`, `keda 2.16.1`, imagens `redis:7.4-alpine`.
- **Limites conhecidos:** Vault em **dev mode** (PoC; sem HA/unseal persistente), single-node,
  fila Redis sem persistência. Operação completa: runbook do Paperclip Medusa **§12**.
