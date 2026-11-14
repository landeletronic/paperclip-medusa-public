#!/usr/bin/env python3
# latency_baseline.py — baseline formal de latência da RX 6600 (plano padrão, Fase 0).
#
# Mede TTFT e tokens/s do modelo primário do Hermes (`qwen3:4b-64k`, q4_0, RX 6600)
# pelos DOIS caminhos de produção: Ollama nativo (/api/generate) e LiteLLM
# (`medusa-primary` → /v1/chat/completions). Streaming real; amostra de VRAM/
# potência/temperatura da GPU durante a carga. Somente leitura.
#
# Uso: python3 latency_baseline.py   (JSON detalhado no stdout; resumo no stderr)
import json, os, statistics, subprocess, time, urllib.request

OLLAMA = "http://127.0.0.1:11434"
LITELLM = "http://127.0.0.1:4000"
MODEL_OLLAMA = "qwen3:4b-64k"
MODEL_LLAMA = "medusa-primary"
N_RUNS = 5
NUM_PREDICT = 64
CARD = "/sys/class/drm/card1/device"  # RX 6600 (0000:01:00.0)

SHORT_PROMPT = "Explique em uma frase o que e um orcamento."
PARA = ("Um orcamento publico lista receitas e despesas previstas, vincula cada gasto a uma fonte "
        "de recurso e permite acompanhar a execucao financeira ao longo do ano. ")
MEDIUM_PROMPT = "Responda em uma frase. Contexto:\n" + PARA * 24  # ~1000 tokens

def gpu_sample():
    def r(p):
        try: return open(p).read().strip()
        except OSError: return None
    hw = CARD + "/hwmon"
    import glob
    p1 = glob.glob(hw + "/hwmon*/power1_average")
    t1 = glob.glob(hw + "/hwmon*/temp1_input")
    return {
        "vram_used_bytes": r(CARD + "/mem_info_vram_used"),
        "power_w": round(int(r(p1[0])) / 1e6, 2) if p1 and r(p1[0]) else None,
        "temp_c": round(int(r(t1[0])) / 1000, 1) if t1 and r(t1[0]) else None,
    }

def post_stream(url, payload, headers):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json", **headers})
    t0 = time.monotonic()
    resp = urllib.request.urlopen(req, timeout=600)
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
        else:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("response") or obj.get("thinking"):
                if ttft is None:
                    ttft = now - t0
                chunks += 1
            if obj.get("eval_count"):
                eval_ct = obj["eval_count"]; eval_ns = obj.get("eval_duration", 0)
    total = time.monotonic() - t0
    return ttft, total, chunks, usage, eval_ct, eval_ns

def bench_ollama(prompt):
    ttft, total, chunks, _u, eval_ct, eval_ns = post_stream(
        OLLAMA + "/api/generate",
        {"model": MODEL_OLLAMA, "prompt": prompt, "stream": True, "think": False,
         "options": {"num_predict": NUM_PREDICT, "temperature": 0.2}}, {})
    tps = round(eval_ct / (eval_ns / 1e9), 2) if eval_ns else None
    return {"ttft_s": ttft, "total_s": round(total, 2), "tokens": eval_ct or chunks, "tok_s": tps}

def bench_llamalm(prompt):
    ttft, total, chunks, usage, _e, _n = post_stream(
        LITELLM + "/v1/chat/completions",
        {"model": MODEL_LLAMA, "messages": [{"role": "user", "content": prompt}],
         "max_tokens": NUM_PREDICT, "temperature": 0.2, "stream": True,
         "stream_options": {"include_usage": True}},
        {"Authorization": "Bearer " + os.environ.get("LITELLM_KEY", "")})
    # tokens: usage se vier; senão, aproximação por chunks
    tokens = (usage or {}).get("completion_tokens") or chunks
    tps = round(tokens / total, 2) if total else None
    return {"ttft_s": ttft, "total_s": round(total, 2), "tokens": tokens, "tok_s": tps}

def summarize(rows):
    def med(vals):
        vals = [v for v in vals if v is not None]
        return round(statistics.median(vals), 3) if vals else None
    ttfts = [r["ttft_s"] for r in rows if r["ttft_s"] is not None]
    return {
        "n": len(rows),
        "ttft_median_s": med(ttfts),
        "ttft_min_s": round(min(ttfts), 3) if ttfts else None,
        "ttft_max_s": round(max(ttfts), 3) if ttfts else None,
        "total_median_s": med([r["total_s"] for r in rows]),
        "tok_s_median": med([r["tok_s"] for r in rows]),
    }

out = {"gpu_idle": gpu_sample(), "configs": {}}
for label, fn in (("ollama_native", bench_ollama), ("litellm_medusa_primary", bench_llamalm)):
    for size, prompt in (("short", SHORT_PROMPT), ("medium_1k", MEDIUM_PROMPT)):
        fn(prompt)  # warm-up (carga do modelo)
        rows = []
        during = None
        for i in range(N_RUNS):
            r = fn(prompt)
            rows.append(r)
            if i == 1:
                during = gpu_sample()
        out["configs"][f"{label}/{size}"] = {"runs": rows, "summary": summarize(rows), "gpu_during": during}
        print(f"[bench] {label}/{size}: {out['configs'][f'{label}/{size}']['summary']}", flush=True)

out["gpu_end"] = gpu_sample()
print(json.dumps(out, ensure_ascii=False, indent=2))
