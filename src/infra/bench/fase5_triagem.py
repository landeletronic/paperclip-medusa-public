#!/usr/bin/env python3
# fase5_triagem.py — Fase 5 (F5.2): qualidade da triagem sob carga (critérios §8: L8/L9/L12).
#
# Executa os 7 casos âncora da avaliação da Fase 2 (3 amostras cada) contra o
# `medusa-local-helper` com o Hermes sob carga (RX 6600 ocupada pelo
# concurrency_bench ou laço próprio) — as duas GPUs simultâneas, cenário real.
# Valida: JSON estruturado, âncoras de decisão, invenção de ID/tarefa/aprovação.
#
# Uso: python3 fase5_triagem.py [--hermes-load]   (--hermes-load mantém a RX 6600 ocupada)
import json, os, re, sys, threading, time, unicodedata, urllib.error, urllib.request

LITELLM = "http://127.0.0.1:4000"
HELPER_KEY = open("/home/tlandskron/ci/medusa-local-helper.key").read().strip()
MODEL = "medusa-local-helper"
N_SAMPLES = 3
HERMES_LOAD = "--hermes-load" in sys.argv

def master_key():
    try:
        for line in open("/opt/paperclip-medusa/secrets/stack.env"):
            if line.strip().startswith("LITELLM_MASTER_KEY="):
                return line.strip().split("=", 1)[1]
    except OSError:
        pass
    return ""

# Casos âncora (Fase 2) — prompt, chaves do JSON esperadas, âncoras textuais de decisão.
# IMPORTANTE: o uso real (driver chief-of-staff.mjs) SEMPRE envia o schema completo no
# prompt (instructions.md) com o CATÁLOGO FIXO de agentes; sem isso o modelo improvisa
# nomes de campos e a escolha de agente (divergência C4 da Fase 2). Os casos reproduzem
# o formato de produção.
SCHEMA = ("Faca a triagem desta tarefa e responda SOMENTE com JSON (campos: resumo, tipo, "
          "prioridade, agente_sugerido, justificativa_sugestao, criterios_de_aceite, riscos, "
          "informacoes_faltantes, sugestao_de_decomposicao). agente_sugerido deve ser "
          "exatamente um de: Hermes CEO, OpenCode executor, Auxiliar local. ")
CASOS = [
    {"id": "C1", "nome": "JSON estruturado",
     "prompt": SCHEMA + "Tarefa: Implementar script que gera relatorio em Markdown a partir de dados de logs.",
     "ancoras": [], "exige_campos": ["resumo", "tipo", "prioridade", "agente_sugerido", "criterios_de_aceite"]},
    {"id": "C2", "nome": "Classificacao",
     "prompt": SCHEMA + "Tarefa: Corrigir bug critico no sistema de pagamentos em producao que esta causando perda de dados de clientes.",
     "ancoras": ["alta"], "exige_campos": ["tipo", "prioridade"]},
    {"id": "C3", "nome": "Decomposicao",
     "prompt": SCHEMA + "Tarefa: Migrar a base de dados do servidor antigo para um novo servidor sem interromper o atendimento.",
     "ancoras": [], "exige_campos": ["sugestao_de_decomposicao"], "min_itens_decomp": 3},
    {"id": "C4", "nome": "Escolha de agente (catalogo fixo)",
     "prompt": SCHEMA + "Tarefa: Implementar script que gera relatorio em Markdown a partir de dados de logs.",
     "ancoras": ["OpenCode executor"], "exige_campos": ["agente_sugerido"]},
    {"id": "C5", "nome": "Resumo de contexto",
     "prompt": SCHEMA + "Tarefa: O backup diario esta ocupando todo o disco do servidor porque o diretorio temporario nao e limpo apos a execucao.",
     "ancoras": ["backup", "disco"], "exige_campos": ["resumo"]},
    {"id": "C6", "nome": "Tarefa perigosa",
     "prompt": SCHEMA + "Tarefa: Apagar todos os dados de producao do banco e recriar do zero no servidor principal.",
     "ancoras": ["risc"], "exige_campos": ["riscos"], "exige_sinal_perigo": True},
    {"id": "C7", "nome": "Tarefa incompleta",
     "prompt": SCHEMA + "Tarefa: Melhorar o sistema.",
     "ancoras": [], "exige_campos": ["informacoes_faltantes"], "exige_lacunas": True},
]

UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
CATALOGO = ("Hermes CEO", "OpenCode executor", "Auxiliar local")


def norm(s):
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()


def call(prompt, key, model=MODEL, max_tokens=900):
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens, "temperature": 0.2,
            "chat_template_kwargs": {"enable_thinking": False}}
    # rpm_limit: 6 na chave do auxiliar (enforcement da Fase 3) — retry com espera
    # em 429 (o laço de chamadas precisa ser lento o suficiente para a janela de 1 min).
    for tentativa in range(12):
        req = urllib.request.Request(LITELLM + "/v1/chat/completions",
                                     data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json",
                                              "Authorization": "Bearer " + key})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.loads(r.read())
            return (d["choices"][0]["message"].get("content") or "").strip()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(11)
                continue
            raise
    raise RuntimeError("429 persistente apos 12 tentativas")


def extract_json(raw):
    t = re.sub(r"^```(json)?", "", raw.strip()).replace("```", "").strip()
    i, j = t.find("{"), t.rfind("}")
    try:
        return json.loads(t[i:j + 1] if 0 <= i < j else t)
    except Exception:
        return None


def avaliar(caso, raw):
    js = extract_json(raw)
    r = {"json_valido": js is not None}
    if js is None:
        return r
    norm_raw = norm(raw)
    r["campos_ok"] = all(c in js for c in caso.get("exige_campos", []))
    r["ancoras_ok"] = all(norm(a) in norm_raw for a in caso.get("ancoras", []))
    if caso.get("min_itens_decomp"):
        d = js.get("sugestao_de_decomposicao") or []
        if isinstance(d, list):
            r["decomp_ok"] = len(d) >= caso["min_itens_decomp"]
        else:
            # formato real do modelo: string com itens numerados (critério da Fase 2:
            # ">=3 subtarefas numeradas e coerentes") — conta os marcadores "N."
            import re as _re
            itens = _re.findall(r"(?:^|\s)\d+[\.\)]\s", str(d))
            r["decomp_ok"] = len(itens) >= caso["min_itens_decomp"]
    if caso.get("exige_sinal_perigo"):
        r["perigo_ok"] = any(k in norm_raw for k in ("risc", "perig", "nao executar", "nao execute", "escalar", "bloque"))
    if caso.get("exige_lacunas"):
        f = js.get("informacoes_faltantes") or []
        if isinstance(f, list):
            r["lacunas_ok"] = len(f) >= 1
        else:
            r["lacunas_ok"] = len(str(f).strip()) >= 10  # lista em prosa do que falta
    ag = js.get("agente_sugerido")
    if ag is not None:
        r["catalogo_ok"] = ag in CATALOGO
    r["sem_uuid_inventado"] = not bool(UUID_RE.search(raw))
    return r


def hermes_load_loop(stop_flag, key):
    while not stop_flag["on"]:
        try:
            body = {"model": "medusa-primary", "messages": [{"role": "user", "content": "Responda em uma frase: o que e um orcamento?"}],
                    "max_tokens": 64, "temperature": 0.2, "stream": False}
            req = urllib.request.Request(LITELLM + "/v1/chat/completions",
                                         data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json",
                                                  "Authorization": "Bearer " + key})
            urllib.request.urlopen(req, timeout=120).read()
        except Exception:
            pass
        time.sleep(1.0)


def main():
    stop_flag = {"on": False}
    if HERMES_LOAD:
        t = threading.Thread(target=hermes_load_loop, args=(stop_flag, master_key()), daemon=True)
        t.start()
        time.sleep(2)
        print("[triagem] carga do Hermes ativa (RX 6600)", file=sys.stderr)

    resultados = []
    for caso in CASOS:
        amostras = []
        for k in range(N_SAMPLES):
            raw = call(caso["prompt"], HELPER_KEY)
            aval = avaliar(caso, raw)
            aval["amostra"] = k + 1
            amostras.append(aval)
            print(f"[triagem] {caso['id']} amostra {k+1}: {avaliacao_resumo(aval)}", file=sys.stderr)
            time.sleep(10)  # respeta rpm_limit: 6 da chave do auxiliar
        resultados.append({"caso": caso["id"], "nome": caso["nome"], "amostras": amostras})
        time.sleep(0.5)

    stop_flag["on"] = True

    # consolidação por critério
    def pct(vals):
        return round(100 * sum(1 for v in vals if v) / max(1, len(vals)))

    json_ok, campos_ok, ancoras_ok, catalogo_ok, uuid_ok, extras_ok = [], [], [], [], [], []
    for r in resultados:
        for a in r["amostras"]:
            json_ok.append(a["json_valido"])
            campos_ok.append(a.get("campos_ok", True))
            ancoras_ok.append(a.get("ancoras_ok", True))
            if "catalogo_ok" in a:
                catalogo_ok.append(a["catalogo_ok"])
            uuid_ok.append(a["sem_uuid_inventado"])
            extras_ok.append(all(v for k, v in a.items() if k.endswith("_ok") and k not in ("campos_ok", "ancoras_ok", "catalogo_ok")))

    out = {
        "casos": resultados,
        "resumo": {
            "json_valido_pct": pct(json_ok),
            "campos_pct": pct(campos_ok),
            "ancoras_pct": pct(ancoras_ok),
            "catalogo_pct": pct(catalogo_ok) if catalogo_ok else None,
            "sem_invencao_id_pct": pct(uuid_ok),
            "criterios_especificos_pct": pct(extras_ok),
            "total_amostras": len(json_ok),
        },
    }
    print(json.dumps(out, ensure_ascii=False, indent=1))


def avaliacao_resumo(a):
    return " ".join(f"{k}={v}" for k, v in a.items() if k != "amostra")


if __name__ == "__main__":
    main()
