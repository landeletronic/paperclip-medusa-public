#!/usr/bin/env bash
# =============================================================================
# bootstrap.sh — (re)instala o cluster Kubernetes local da Fase 3 e o stack de
# escala (Vault + External Secrets + KEDA + fila/run-workers).
#
# Idempotente: cria o cluster se ausente; instala/atualiza os charts; aplica os
# manifests. O token do Vault é GERADO e gravado apenas em
# /home/tlandskron/ci/vault-root-token (600) — nunca versionado.
#
# Uso: bash bootstrap.sh
# Remoção completa: k3d cluster delete medusa (ver runbook §12)
# =============================================================================
set -euo pipefail

CLUSTER=medusa
NS_VAULT=vault
NS_ESO=external-secrets
NS_KEDA=keda
NS_JOBS=medusa-jobs
TOKEN_FILE=/home/tlandskron/ci/vault-root-token
K8S_DIR="$(cd "$(dirname "$0")" && pwd)"

# 1) cluster (idempotente) — API só em loopback; sem traefik/servicelb
if ! k3d cluster list | grep -q "^$CLUSTER "; then
  k3d cluster create "$CLUSTER" \
    --api-port 127.0.0.1:6443 --agents 0 --servers-memory 2g \
    --k3s-arg '--disable=traefik@server:0' \
    --k3s-arg '--disable=servicelb@server:0' \
    --kubeconfig-update-default --kubeconfig-switch-context
fi
kubectl wait --for=condition=Ready node --all --timeout=180s

# 2) namespaces
kubectl apply -f "$K8S_DIR/namespaces.yaml"

# 3) repositórios helm (versões pinadas nos installs)
helm repo add hashicorp https://helm.releases.hashicorp.com >/dev/null 2>&1 || true
helm repo add external-secrets https://charts.external-secrets.io >/dev/null 2>&1 || true
helm repo add kedacore https://kedacore.github.io/charts >/dev/null 2>&1 || true
helm repo update >/dev/null

# 4) token do Vault (apenas no host)
mkdir -p "$(dirname "$TOKEN_FILE")"
if [ ! -s "$TOKEN_FILE" ]; then
  openssl rand -hex 24 > "$TOKEN_FILE"
  chmod 600 "$TOKEN_FILE"
fi
VAULT_TOKEN="$(cat "$TOKEN_FILE")"

# 5) Vault (dev mode — PoC local; ver runbook §12 "limites")
helm upgrade --install vault hashicorp/vault --namespace "$NS_VAULT" \
  --version 0.29.1 \
  --set server.dev.enabled=true \
  --set server.dev.devRootToken="$VAULT_TOKEN" \
  --set server.resources.requests.memory=128Mi \
  --set server.resources.limits.memory=256Mi \
  --wait --timeout 5m

# O chart do Vault usa updateStrategy=OnDelete: o pod precisa ser recriado para
# aplicar o devRootToken (sem isso fica o token antigo e o seed falha com 403).
kubectl -n "$NS_VAULT" delete pod vault-0 --ignore-not-found --wait=true >/dev/null
for _ in $(seq 45); do
  kubectl -n "$NS_VAULT" get pod vault-0 >/dev/null 2>&1 && break
  sleep 2
done
kubectl -n "$NS_VAULT" wait --for=condition=Ready pod/vault-0 --timeout=180s

# 6) External Secrets Operator
helm upgrade --install external-secrets external-secrets/external-secrets --namespace "$NS_ESO" \
  --version 0.10.5 \
  --set installCRDs=true \
  --set resources.requests.memory=96Mi \
  --set resources.limits.memory=192Mi \
  --wait --timeout 5m

# 7) KEDA (autoscaling por fila)
helm upgrade --install keda kedacore/keda --namespace "$NS_KEDA" \
  --version 2.16.1 \
  --set resources.requests.memory=128Mi \
  --set resources.limits.memory=256Mi \
  --wait --timeout 5m

# 8) credencial do Vault no cluster (bootstrap; segredo fora do git)
kubectl -n "$NS_JOBS" create secret generic vault-token \
  --from-literal=token="$VAULT_TOKEN" --dry-run=client -o yaml | kubectl apply -f -

# 9) workloads + External Secrets + KEDA
kubectl apply -f "$K8S_DIR/queue-redis.yaml"
kubectl apply -f "$K8S_DIR/run-worker.yaml"
kubectl apply -f "$K8S_DIR/secretstore-medusa.yaml"
kubectl apply -f "$K8S_DIR/externalsecret-medusa.yaml"
kubectl apply -f "$K8S_DIR/scaledobject-run-worker.yaml"

# 10) semear o Vault (idempotente) — valores de exemplo, não segredos reais
kubectl -n "$NS_VAULT" exec vault-0 -- \
  sh -c "VAULT_TOKEN='$VAULT_TOKEN' vault kv put secret/medusa api-key=valor-inicial-fase3" >/dev/null

echo "bootstrap concluído (cluster=$CLUSTER)"
