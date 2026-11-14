#!/usr/bin/env python3
# fase5_falha.py — Fase 5 (F5.2): falha da RX 5500 não interrompe Hermes nem Paperclip (L10).
#
# 1. Mede o Hermes (medusa-primary) em repouso de carga.
# 2. Para o container `medusa-helper` (RX 5500) e mede o Hermes durante a falha —
#    o LiteLLM deve cair no fallback sancionado `medusa-hermes-direct` (ollama/qwen3:4b-64k).
# 3. Verifica que a API do Paperclip continua respondendo durante a falha.
# 4. Reinicia o helper e confirma a volta do auxiliar.
# 5. Verifica L11: o helper NÃO tem porta publicada (inacessível fora da rede interna).
#
# Uso: python3 fase5_falha.py   (somente leitura + parada/reinício controlados do helper)
import json, statistics, subprocess, time, urllib.request

LITELLM = "http://127.0.0.1:4000"
PAPERCLIP = "http://127.0.0.1:3100"
MODEL = "medusa-primary"
HELPER_KEY = open("/home/usuario/ci/medusa-local-helper.key").read().strip()


def master_key():
    try:
        for line in open("/opt/paperclip-medusa/secrets/stack.env"):
            if line.strip().startswith("LITELLM_MASTER_KEY="):
                return line.strip().split("=", 1)[1]
    except OSError:
        pass
    return ""


KEY = master_key()


def chamada(modelo, key, prompt="Responda em uma frase: o que e um orcamento?"):
    t0 = time.monotonic()
    body = {"model": modelo, "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 64, "temperature": 0.2}
    req = urllib.request.Request(LITELLM + "/v1/chat/completions",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json",
                                          "Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.loads(r.read())
    total = time.monotonic() - t0
    modelo_real = d.get("model", "?")
    return {"lat_s": round(total, 2), "modelo_resposta": modelo_real}


def medir(n=4, modelo=MODEL, key=None):
    rows = []
    for _ in range(n):
        try:
            rows.append(chamada(modelo, key or KEY))
        except Exception as e:
            rows.append({"erro": str(e)[:120]})
        time.sleep(0.5)
    return rows


def paperclip_alive():
    try:
        with urllib.request.urlopen(PAPERCLIP + "/api/health", timeout=10) as r:
            return r.status
    except Exception as e:
        return f"erro: {str(e)[:80]}"


def helper_ports():
    out = subprocess.run(["docker", "port", "medusa-helper"], capture_output=True, text=True).stdout.strip()
    return out or "(nenhuma porta publicada)"


out = {}

# 0) baseline rápido do Hermes
out["hermes_antes"] = medir(4)

# 1) para o helper (RX 5500)
subprocess.run(["docker", "stop", "medusa-helper"], capture_output=True, text=True)
time.sleep(3)

# 2) Hermes durante a falha — esperado: segue operando normalmente
out["hermes_durante_falha"] = medir(4)

# 2b) auxiliar durante a falha — esperado: fallback sancionado para o Hermes
# (medusa-local-helper → medusa-hermes-direct → ollama/qwen3:4b-64k; Fase 3)
out["auxiliar_durante_falha"] = medir(3, modelo="medusa-local-helper", key=HELPER_KEY)

# 3) Paperclip vivo durante a falha
out["paperclip_durante_falha"] = paperclip_alive()

# 4) reinicia o helper e confirma a volta
subprocess.run(["docker", "start", "medusa-helper"], capture_output=True, text=True)
volta_ok = False
for _ in range(30):
    time.sleep(4)
    try:
        r = chamada("medusa-local-helper", HELPER_KEY, "Diga apenas: ok")
        if r["lat_s"]:
            volta_ok = True
            out["helper_volta"] = r
            break
    except Exception:
        pass
out["helper_volta_ok"] = volta_ok

# 5) L11 — exposição
out["helper_portas"] = helper_ports()

print(json.dumps(out, ensure_ascii=False, indent=1))
