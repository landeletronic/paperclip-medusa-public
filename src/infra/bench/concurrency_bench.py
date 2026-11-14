#!/usr/bin/env python3
# concurrency_bench.py — Fase 5 do plano padrão: concorrência RX 6600 (Hermes) + RX 5500 (auxiliar).
#
# Executa as DUAS cargas simultaneamente por uma janela configurável:
#  - Hermes: `medusa-primary` (qwen3:4b-64k) via LiteLLM, prompt curto (64 tok), 1 chamada/INTERVALO_HERMES.
#  - Auxiliar: `medusa-local-helper` (Qwen3 8B na RX 5500) via LiteLLM, prompt de triagem JSON,
#    laço sequencial (concorrência 1 por design).
# Amostra VRAM/potência/temperatura das duas GPUs + RAM a cada SAMPLE_S. Streaming real;
# TTFT = primeiro token. Somente leitura (nenhuma alteração de config).
#
# Uso: python3 concurrency_bench.py [MINUTOS]   (padrão 60)
# Saída: JSON final no stdout (progresso no stderr).
import json, os, statistics, subprocess, sys, threading, time, urllib.request

LITELLM = "http://127.0.0.1:4000"
MODEL_HERMES = "medusa-primary"
MODEL_HELPER = "medusa-local-helper"
MINUTES = int(sys.argv[1]) if len(sys.argv) > 1 else 60
NUM_PREDICT = 64
INTERVALO_HERMES = 3.0
SAMPLE_S = 30
CARDS = {"rx6600": "/sys/class/drm/card1/device", "rx5500": "/sys/class/drm/card2/device"}
HELPER_KEY_FILE = "/home/tlandskron/ci/medusa-local-helper.key"
HELPER_KEY = open(HELPER_KEY_FILE).read().strip() if os.path.exists(HELPER_KEY_FILE) else ""


def _master_key():
    # Lê a master key do stack.env sem imprimi-la (env LITELLM_KEY tem precedência).
    if os.environ.get("LITELLM_KEY"):
        return os.environ["LITELLM_KEY"]
    try:
        for line in open("/opt/paperclip-medusa/secrets/stack.env"):
            line = line.strip()
            if line.startswith("LITELLM_MASTER_KEY="):
                return line.split("=", 1)[1]
    except OSError:
        pass
    return ""


LITELLM_KEY = _master_key()

HERMES_PROMPT = "Explique em uma frase o que e um orcamento."
TRIAGEM_PROMPT = (
    "Faca a triagem desta tarefa e responda SOMENTE com JSON (campos: resumo, tipo, prioridade, "
    "agente_sugerido, justificativa_sugestao, criterios_de_aceite, riscos, informacoes_faltantes, "
    "sugestao_de_decomposicao). Tarefa: Implementar script que gera relatorio em Markdown a partir "
    "de dados de logs."
)

results = {"hermes": [], "helper": [], "gpu": [], "errors": [], "stop": False}


def gpu_sample():
    def r(p):
        try:
            return open(p).read().strip()
        except OSError:
            return None

    import glob

    out = {}
    for name, card in CARDS.items():
        p1 = glob.glob(card + "/hwmon/hwmon*/power1_average")
        t1 = glob.glob(card + "/hwmon/hwmon*/temp1_input")
        out[name] = {
            "vram_used_bytes": r(card + "/mem_info_vram_used"),
            "power_w": round(int(r(p1[0])) / 1e6, 2) if p1 and r(p1[0]) else None,
            "temp_c": round(int(r(t1[0])) / 1000, 1) if t1 and r(t1[0]) else None,
        }
    out["ram_used_mb"] = int(subprocess.run(
        ["free", "-m"], capture_output=True, text=True).stdout.splitlines()[1].split()[2])
    return out


def post_stream(url, payload, headers):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json", **headers})
    t0 = time.monotonic()
    resp = urllib.request.urlopen(req, timeout=300)
    ttft = None
    chunks = 0
    usage = None
    eval_ct = eval_ns = 0
    for raw in resp:
        now = time.monotonic()
        line = raw.decode(errors="ignore").strip()
        if not line:
            continue
        if line.startswith("data:"):
            line = line[5:].strip()
            if line == "[DONE]":
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("usage"):
                usage = obj["usage"]
            choices = obj.get("choices") or []
            if choices and (choices[0].get("delta") or choices[0].get("message")):
                delta = choices[0].get("delta") or choices[0].get("message") or {}
                if delta.get("content") or delta.get("reasoning_content"):
                    if ttft is None:
                        ttft = now - t0
                    chunks += 1
    total = time.monotonic() - t0
    return ttft, total, chunks, usage


def call_hermes_once():
    ttft, total, chunks, usage = post_stream(
        LITELLM + "/v1/chat/completions",
        {"model": MODEL_HERMES, "messages": [{"role": "user", "content": HERMES_PROMPT}],
         "max_tokens": NUM_PREDICT, "temperature": 0.2, "stream": True,
         "stream_options": {"include_usage": True}},
        {"Authorization": "Bearer " + LITELLM_KEY})
    tokens = (usage or {}).get("completion_tokens") or chunks
    return {"t": time.time(), "ttft_s": ttft, "total_s": round(total, 2),
            "tokens": tokens, "tok_s": round(tokens / total, 2) if total else None}


def call_helper_once():
    ttft, total, chunks, usage = post_stream(
        LITELLM + "/v1/chat/completions",
        {"model": MODEL_HELPER, "messages": [{"role": "user", "content": TRIAGEM_PROMPT}],
         "max_tokens": 900, "temperature": 0.2, "stream": True,
         "stream_options": {"include_usage": True}, "chat_template_kwargs": {"enable_thinking": False}},
        {"Authorization": "Bearer " + HELPER_KEY})
    tokens = (usage or {}).get("completion_tokens") or chunks
    return {"t": time.time(), "ttft_s": ttft, "total_s": round(total, 2), "tokens": tokens}


def hermes_loop():
    while not results["stop"]:
        try:
            results["hermes"].append(call_hermes_once())
        except Exception as e:
            results["errors"].append({"side": "hermes", "t": time.time(), "err": str(e)[:150]})
        time.sleep(INTERVALO_HERMES)


def helper_loop():
    while not results["stop"]:
        try:
            results["helper"].append(call_helper_once())
        except Exception as e:
            results["errors"].append({"side": "helper", "t": time.time(), "err": str(e)[:150]})


def sampler_loop(end_ts):
    while time.time() < end_ts and not results["stop"]:
        try:
            results["gpu"].append({"t": time.time(), **gpu_sample()})
        except Exception as e:
            results["errors"].append({"side": "sampler", "t": time.time(), "err": str(e)[:150]})
        time.sleep(SAMPLE_S)


def kernel_scan():
    out = subprocess.run(["journalctl", "-k", "--since", "-70min", "--no-pager"],
                         capture_output=True, text=True).stdout.lower()
    hits = [l for l in out.splitlines()
            if any(k in l for k in ("amdgpu", "vulkan", "page fault", "reset", "ring timeout", "gpu fault"))]
    return hits[-20:]


def summarize(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    if not vals:
        return None
    vals_sorted = sorted(vals)
    p95 = vals_sorted[int(len(vals_sorted) * 0.95) - 1] if len(vals_sorted) > 1 else vals_sorted[0]
    return {"n": len(vals), "median": round(statistics.median(vals), 4),
            "min": round(min(vals), 4), "max": round(max(vals), 4), "p95": round(p95, 4)}


def main():
    end_ts = time.time() + MINUTES * 60
    threads = [
        threading.Thread(target=hermes_loop, daemon=True),
        threading.Thread(target=helper_loop, daemon=True),
        threading.Thread(target=sampler_loop, args=(end_ts,), daemon=True),
    ]
    for t in threads:
        t.start()
    print(f"[bench] janela de {MINUTES} min iniciada; amostragem a cada {SAMPLE_S}s", file=sys.stderr, flush=True)
    while time.time() < end_ts:
        time.sleep(20)
        n_h, n_a = len(results["hermes"]), len(results["helper"])
        print(f"[bench] restam {int((end_ts - time.time()) / 60)}min | hermes={n_h} helper={n_a} erros={len(results['errors'])}", file=sys.stderr, flush=True)
    results["stop"] = True
    time.sleep(5)

    hermes = results["hermes"]
    helper = results["helper"]
    gpu = results["gpu"]
    out = {
        "window_minutes": MINUTES,
        "hermes": {"ttft": summarize(hermes, "ttft_s"), "tok_s": summarize(hermes, "tok_s"),
                   "total_s": summarize(hermes, "total_s"), "samples": len(hermes)},
        "helper": {"ttft": summarize(helper, "ttft_s"), "total_s": summarize(helper, "total_s"),
                   "samples": len(helper)},
        "gpu": gpu,
        "errors": results["errors"],
        "kernel_hits": kernel_scan(),
    }
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
