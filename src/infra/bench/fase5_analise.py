#!/usr/bin/env python3
# fase5_analise.py — Fase 5 (F5.3): aplica os limiares pré-registrados (L1–L7, L13)
# ao JSON do concurrency_bench.py. Uso: python3 fase5_analise.py <cbench_60min.json>
import json, sys

LIMIARES = {
    "L1_ttft_median_ms_max": 55,
    "L2_ttft_p95_ms_max": 120,
    "L3_tok_s_median_min": 42,
    "L5_vram_rx5500_min_gb": 5.0,   # modelo residente (Q4_K_M ~5 GB+); camada em CPU cairia a VRAM
    "L7_ram_livre_min_mb": 2048,
}

d = json.load(open(sys.argv[1]))
h = d["hermes"]
res = {}

ttft_med_ms = round((h["ttft"]["median"] or 0) * 1000, 1)
ttft_p95_ms = round((h["ttft"]["p95"] or 0) * 1000, 1)
tok_s = h["tok_s"]["median"]

res["L1_ttft_median"] = {"valor_ms": ttft_med_ms, "limiar": 55, "pass": ttft_med_ms <= 55}
res["L2_ttft_p95"] = {"valor_ms": ttft_p95_ms, "limiar": 120, "pass": ttft_p95_ms <= 120}
res["L3_tok_s"] = {"valor": tok_s, "limiar": 42, "pass": tok_s is not None and tok_s >= 42}

hermes_erros = [e for e in d["errors"] if e.get("side") == "hermes"]
helper_erros = [e for e in d["errors"] if e.get("side") == "helper"]
res["L4_erros_hermes"] = {"valor": len(hermes_erros), "limiar": 0, "pass": len(hermes_erros) == 0}

gpu = d.get("gpu") or []
vram_5500 = [g["rx5500"]["vram_used_bytes"] for g in gpu if g.get("rx5500", {}).get("vram_used_bytes")]
vram_min_gb = round(min(int(v) / 1e9 for v in vram_5500), 2) if vram_5500 else None
res["L5_vram_auxiliar"] = {"valor_min_gb": vram_min_gb, "limiar": 5.0,
                           "pass": vram_min_gb is not None and vram_min_gb >= 5.0,
                           "nota": "VRAM >= 5 GB contínua = modelo residente na GPU (camada em CPU reduziria)"}

k = d.get("kernel_hits") or []
res["L6_kernel"] = {"valor": len(k), "limiar": 0, "pass": len(k) == 0, "amostras": k[-5:]}

ram_livre = [15360 - g.get("ram_used_mb", 0) for g in gpu]  # host ~15 GB (free -m)
ram_min = min(ram_livre) if ram_livre else None
res["L7_ram"] = {"valor_livre_mb_estimado": ram_min, "limiar": 2048,
                 "pass": ram_min is not None and ram_min >= 2048}

# L13: estabilidade — janela completa com amostras contínuas dos dois lados
res["L13_estabilidade"] = {
    "janela_min": d.get("window_minutes"),
    "amostras_hermes": h["samples"], "amostras_helper": d["helper"]["samples"],
    "pass": d.get("window_minutes", 0) >= 60 and h["samples"] > 0 and d["helper"]["samples"] > 0,
}

pct = round(100 * sum(1 for v in res.values() if v["pass"]) / len(res), 1)
out = {"resultados": res, "pass_pct": pct,
       "erros_hermes": len(hermes_erros), "erros_helper_429_rate_limit": len(helper_erros),
       "gpu_primeira": gpu[0] if gpu else None, "gpu_ultima": gpu[-1] if gpu else None}
print(json.dumps(out, ensure_ascii=False, indent=1))
print(f"\n=== {pct}% dos limiares passaram ===", file=sys.stderr)
