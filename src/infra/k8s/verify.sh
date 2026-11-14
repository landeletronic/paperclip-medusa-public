#!/usr/bin/env bash
# =============================================================================
# verify.sh — verificação SOMENTE LEITURA do cluster K8s local da Fase 3.
#
# Checa: node Ready, API só em loopback (sem exposição à LAN), ausência de
# NodePort/LoadBalancer, saúde de Vault/ESO/KEDA, sincronia do ExternalSecret
# e respeito ao teto de réplicas do pool run-worker.
#
# Uso: bash verify.sh   (exit 0 = tudo ok; SOMENTE LEITURA — não altera nada)
# =============================================================================
set -uo pipefail

pass=0; fail=0
ck() {
  if bash -c "$2" >/dev/null 2>&1; then
    echo "PASS  $1"; pass=$((pass+1))
  else
    echo "FAIL  $1"; fail=$((fail+1))
  fi
}

ck "cluster responde (kubectl)" "kubectl get nodes >/dev/null"
ck "node k3d-medusa-server-0 Ready" "kubectl get node k3d-medusa-server-0 -o jsonpath='{.status.conditions[?(@.type==\"Ready\")].status}' | grep -qx True"
ck "API do cluster só em loopback (127.0.0.1:6443)" "ss -ltn | grep -q '127.0.0.1:6443'"
ck "API do cluster NÃO exposta à LAN" "! ss -ltn | grep -E '(^| )([0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+|\\*|0\\.0\\.0\\.0):6443 ' | grep -vq '127.0.0.1:6443'"
ck "sem serviço NodePort/LoadBalancer" "! kubectl get svc -A -o jsonpath='{range .items[*]}{.spec.type}{\"\\n\"}{end}' | grep -qE 'NodePort|LoadBalancer'"
ck "Vault em execução" "kubectl -n vault get pod vault-0 -o jsonpath='{.status.phase}' | grep -qx Running"
ck "External Secrets Operator pronto" "kubectl -n external-secrets get deploy external-secrets -o jsonpath='{.status.readyReplicas}' | grep -qE '^[1-9]'"
ck "KEDA operator pronto" "kubectl -n keda get deploy keda-operator -o jsonpath='{.status.readyReplicas}' | grep -qE '^[1-9]'"
ck "ExternalSecret pronto (sincronizado)" "kubectl -n medusa-jobs get externalsecret medusa-app-credentials -o jsonpath='{.status.conditions[?(@.type==\"Ready\")].status}' | grep -qx True"
ck "Secret materializado via ESO" "kubectl -n medusa-jobs get secret medusa-app-secret -o jsonpath='{.data.api-key}' | grep -q ."
ck "fila redis-queue em execução" "kubectl -n medusa-jobs get deploy redis-queue -o jsonpath='{.status.readyReplicas}' | grep -qE '^[1-9]'"
ck "run-worker dentro do teto de réplicas (<=4)" "test \"\$(kubectl -n medusa-jobs get deploy run-worker -o jsonpath='{.spec.replicas}' 2>/dev/null || echo 0)\" -le 4"
ck "ScaledObject registrado (maxReplicaCount=4)" "kubectl -n medusa-jobs get scaledobject run-worker-scaler -o jsonpath='{.spec.maxReplicaCount}' | grep -qx 4"

echo "== RESUMO: PASS=$pass FAIL=$fail =="
[ "$fail" -eq 0 ]
