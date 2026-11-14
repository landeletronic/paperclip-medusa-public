#!/usr/bin/env python3
# paperclip-run-executor — executa um run em container efêmero (Fase 1, F1.2).
#
# Contrato: docs/research/2026-11-12-f1-1-contrato-runtime-workspace-artefatos.md
# (classes de execução, workspace persistente montado em /workspace, artefatos no
# workspace, segredos injetados por run e mascarados, limites, timeout e remoção
# garantida do container).
#
# Princípios de segurança (decisão F1.0):
#   - este executor roda NO HOST (CLI/serviço dedicado), com acesso ao Docker do
#     host; o container `paperclip` NUNCA recebe docker.sock;
#   - só monta o workspace autorizado (raízes permitidas), nunca a raiz do host;
#   - containers efêmeros por run: criados, executados e SEMPRE removidos
#     (sucesso, falha ou timeout);
#   - segredos (env do run) são mascarados nos logs/transcripts retornados.
#
# Saída: JSON no stdout (resultado do run); mensagens humanas no stderr.
# Exit codes: 0 = run ok; 2 = run falhou (exit != 0); 3 = timeout; 4 = spec inválida;
#             5 = erro do Docker/executor; 6 = capacidade esgotada (concorrência).
#
# Uso:
#   executor.py run --spec spec.json [--transcript PATH] [--allow-root DIR ...]
#   executor.py run --spec -            (spec via stdin)
#   executor.py health
#
# Linguagem: Python 3 (somente stdlib). Host-alvo: Ubuntu 26.04 (Docker CLI).

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import secrets as _secrets
import subprocess
import sys
import time
from pathlib import Path

TOOL_NAME = "paperclip-run-executor"
TOOL_VERSION = "0.1.0"

# Tags flutuantes proibidas pelo contrato (pinning obrigatório).
UNPINNED_TAGS = {"latest", "main", "master", "rocm", "stable", "edge", "nightly", ""}

# Raiz padrão de workspaces (volume do Paperclip no host). Estendível por
# --allow-root / EXECUTOR_ALLOWED_ROOTS (separador ':').
DEFAULT_ALLOWED_ROOTS = [
    "/var/lib/docker/volumes/paperclip-medusa_paperclip-data/_data/instances",
]

MOUNT_POINT = "/workspace"
OUTPUT_TAIL_BYTES = 8 * 1024
TRANSCRIPT_MAX_BYTES = 200 * 1024

# --- métricas e capacidade (Fase 2) -----------------------------------------
# Estado persistente dos contadores + publicação no textfile do node-exporter
# (padrão do lab: ci/textfile/*.prom). Concorrência: slots por flock (liberados
# pelo kernel se o processo morrer — crash-safe).
STATE_PATH = Path(os.environ.get("PAPERCLIP_EXECUTOR_STATE",
                                 "/home/tlandskron/ci/paperclip-executor-state.json"))
TEXTFILE_DIR = Path(os.environ.get("PAPERCLIP_TEXTFILE_DIR",
                                   "/home/tlandskron/hermes-architect/ci/textfile"))
MAX_CONCURRENT = max(1, int(os.environ.get("PAPERCLIP_EXECUTOR_MAX_CONCURRENT", "2")))
SLOTS_DIR = STATE_PATH.parent / "paperclip-executor-slots"


def _read_state_nolock() -> dict:
    try:
        raw = STATE_PATH.read_text()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def update_state(**delta) -> dict:
    """Atualiza contadores/últimos valores sob flock e regrava o .prom."""
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "a+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            fh.seek(0)
            raw = fh.read()
            st = json.loads(raw) if raw.strip() else {}
            for k, v in delta.items():
                if k.endswith("_total"):
                    st[k] = int(st.get(k, 0)) + int(v)
                else:
                    st[k] = v
            fh.seek(0)
            fh.truncate()
            fh.write(json.dumps(st))
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)
    write_prom(st)
    return st


def _locked_slots_count() -> int:
    SLOTS_DIR.mkdir(parents=True, exist_ok=True)
    n = 0
    for i in range(MAX_CONCURRENT):
        try:
            fh = open(SLOTS_DIR / f"slot-{i}", "a+")
        except OSError:
            continue
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(fh, fcntl.LOCK_UN)  # está livre
        except OSError:
            n += 1  # ocupado por outro run
        finally:
            fh.close()
    return n


def write_prom(st: dict | None = None) -> None:
    if st is None:
        st = _read_state_nolock()
    active = _locked_slots_count()
    lines = [
        "# HELP paperclip_executor_runs_total Runs executados (aceitos pelo executor)",
        "# TYPE paperclip_executor_runs_total counter",
        f"paperclip_executor_runs_total {int(st.get('runs_total', 0))}",
        "# HELP paperclip_executor_failures_total Runs terminados com falha",
        "# TYPE paperclip_executor_failures_total counter",
        f"paperclip_executor_failures_total {int(st.get('failures_total', 0))}",
        "# HELP paperclip_executor_timeouts_total Runs mortos por timeout",
        "# TYPE paperclip_executor_timeouts_total counter",
        f"paperclip_executor_timeouts_total {int(st.get('timeouts_total', 0))}",
        "# HELP paperclip_executor_rejected_total Runs rejeitados por falta de slot (capacidade)",
        "# TYPE paperclip_executor_rejected_total counter",
        f"paperclip_executor_rejected_total {int(st.get('rejected_total', 0))}",
        "# HELP paperclip_executor_last_duration_ms Duracao do ultimo run (ms)",
        "# TYPE paperclip_executor_last_duration_ms gauge",
        f"paperclip_executor_last_duration_ms {int(st.get('last_duration_ms', 0))}",
        "# HELP paperclip_executor_active_runs Runs em execucao agora",
        "# TYPE paperclip_executor_active_runs gauge",
        f"paperclip_executor_active_runs {active}",
        "# HELP paperclip_executor_max_concurrent Teto de concorrencia do executor",
        "# TYPE paperclip_executor_max_concurrent gauge",
        f"paperclip_executor_max_concurrent {MAX_CONCURRENT}",
        "# HELP paperclip_executor_last_timestamp_seconds Epoch do ultimo run",
        "# TYPE paperclip_executor_last_timestamp_seconds gauge",
        f"paperclip_executor_last_timestamp_seconds {int(st.get('last_timestamp_seconds', 0))}",
    ]
    try:
        TEXTFILE_DIR.mkdir(parents=True, exist_ok=True)
        tmp = TEXTFILE_DIR / f".paperclip_executor.prom.tmp.{os.getpid()}"
        tmp.write_text("\n".join(lines) + "\n")
        tmp.chmod(0o644)
        tmp.replace(TEXTFILE_DIR / "paperclip_executor.prom")
    except OSError as e:
        log(f"aviso: não consegui publicar métricas: {e}")


def acquire_slot():
    """Retorna um handle de slot (flock) ou None se a capacidade estou esgotada."""
    SLOTS_DIR.mkdir(parents=True, exist_ok=True)
    for i in range(MAX_CONCURRENT):
        try:
            fh = open(SLOTS_DIR / f"slot-{i}", "a+")
        except OSError:
            continue
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fh
        except OSError:
            fh.close()
    return None


def release_slot(fh) -> None:
    if fh is None:
        return
    try:
        fcntl.flock(fh, fcntl.LOCK_UN)
    finally:
        fh.close()


def log(msg: str) -> None:
    print(f"[{TOOL_NAME}] {msg}", file=sys.stderr, flush=True)


def die(code: int, msg: str) -> "None":
    log(f"ERRO: {msg}")
    print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False))
    raise SystemExit(code)


def run_cmd(argv: list[str], timeout: int | None = None, input_bytes: bytes | None = None):
    """Executa comando, retornando (rc, stdout_bytes, stderr_bytes)."""
    try:
        p = subprocess.run(
            argv,
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError as e:
        return 127, b"", str(e).encode()
    except subprocess.TimeoutExpired:
        return 124, b"", b"timeout"


def docker_ok() -> tuple[bool, str]:
    rc, out, err = run_cmd(["docker", "info", "--format", "{{.ServerVersion}}"], timeout=15)
    if rc != 0:
        return False, (err or out).decode(errors="replace").strip()
    return True, out.decode(errors="replace").strip()


def resolve_image(image: str, allow_unpinned: bool) -> str:
    """Valida pinning: digest (@sha256:...) ou tag imutável. Recusa flutuantes."""
    if image.startswith("sha256:") or "@sha256:" in image:
        return image
    tag = image.rsplit(":", 1)[1] if ":" in image.rsplit("/", 1)[-1] else ""
    if not allow_unpinned and tag.lower() in UNPINNED_TAGS:
        raise ValueError(
            f"imagem sem pinning (tag '{tag or 'sem tag'}') — use digest (@sha256:...) "
            f"ou tag imutável; --allow-unpinned para exceção explícita"
        )
    return image


def validate_workspace(ws: str, allowed_roots: list[str]) -> Path:
    p = Path(ws).resolve()
    if not p.is_dir():
        raise ValueError(f"workspace não é diretório: {p}")
    for root in allowed_roots:
        r = Path(root).resolve()
        if p == r or r in p.parents:
            return p
    raise ValueError(
        f"workspace fora das raízes permitidas: {p} (permitidas: {allowed_roots})"
    )


def mask_secrets(text: str, secret_values: list[str]) -> str:
    for v in sorted(secret_values, key=len, reverse=True):
        if v and len(v) >= 4:
            text = text.replace(v, "***")
    return text


def main() -> int:
    ap = argparse.ArgumentParser(prog=TOOL_NAME)
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_run = sub.add_parser("run", help="executa um run em container efêmero")
    ap_run.add_argument("--spec", required=True, help="arquivo JSON do run, ou '-' para stdin")
    ap_run.add_argument("--transcript", help="grava transcript completo (mascarado) neste caminho")
    ap_run.add_argument("--allow-root", action="append", default=[], help="raiz adicional permitida (repetível)")
    ap_run.add_argument("--allow-unpinned", action="store_true", help="permite imagem sem digest/tag imutável")
    ap_run.add_argument("--keep-on-error", action="store_true", help="MANTÉM o container se o executor falhar (depuração)")

    sub.add_parser("health", help="verifica Docker disponível")
    sub.add_parser("metrics", help="grava paperclip_executor.prom a partir do estado (sem executar run)")

    args = ap.parse_args()

    if args.cmd == "health":
        ok, info = docker_ok()
        print(json.dumps({"ok": ok, "docker_server": info}, ensure_ascii=False))
        return 0 if ok else 5

    if args.cmd == "metrics":
        st = update_state()
        print(json.dumps({"ok": True, "state": st, "max_concurrent": MAX_CONCURRENT}, ensure_ascii=False))
        return 0

    # ---------------- run ----------------
    raw = sys.stdin.read() if args.spec == "-" else Path(args.spec).read_text()
    try:
        spec = json.loads(raw)
    except json.JSONDecodeError as e:
        die(4, f"spec JSON inválida: {e}")

    for key in ("image", "workspace", "command"):
        if key not in spec:
            die(4, f"spec sem campo obrigatório: {key}")

    image = spec["image"]
    ws_arg = spec["workspace"]
    command = spec["command"]
    if isinstance(command, str):
        command = ["/bin/sh", "-c", command]
    if not isinstance(command, list) or not command:
        die(4, "command deve ser lista não vazia (ou string)")

    env: dict[str, str] = {str(k): str(v) for k, v in (spec.get("env") or {}).items()}
    limits = spec.get("limits") or {}
    timeout_s = int(spec.get("timeout_seconds") or 600)
    network = spec.get("network") or "none"
    user = spec.get("user")
    run_class = spec.get("class") or "generic-run"
    run_id = spec.get("run_id") or f"r{_secrets.token_hex(4)}-{int(time.time())}"
    mount = MOUNT_POINT

    env_roots = [r for r in os.environ.get("EXECUTOR_ALLOWED_ROOTS", "").split(":") if r]
    allowed_roots = DEFAULT_ALLOWED_ROOTS + env_roots + list(args.allow_root)

    try:
        image = resolve_image(image, args.allow_unpinned)
        ws = validate_workspace(ws_arg, allowed_roots)
    except ValueError as e:
        die(4, str(e))

    ok, info = docker_ok()
    if not ok:
        die(5, f"Docker indisponível: {info}")

    cname = re.sub(r"[^a-zA-Z0-9_.-]", "-", f"paperclip-run-{run_id}")[:63]
    secret_values = list(env.values())

    # capacidade: slot de concorrência (flock — liberado pelo kernel se o processo
    # morrer; o .prom é regrava a cada transição de estado).
    slot = acquire_slot()
    if slot is None:
        update_state(rejected_total=1)
        print(json.dumps({"ok": False, "error": f"capacidade esgotada (max_concurrent={MAX_CONCURRENT})",
                          "run_id": run_id}, ensure_ascii=False))
        raise SystemExit(6)

    # cria o container (não inicia ainda): garante ID para auditoria e remoção.
    create = [
        "docker", "create",
        "--name", cname,
        "--label", f"paperclip.run_id={run_id}",
        "--label", f"paperclip.run_class={run_class}",
        "--init",
        "--network", network,
    ]
    if limits.get("cpus"):
        create += ["--cpus", str(limits["cpus"])]
    if limits.get("memory"):
        create += ["--memory", str(limits["memory"])]
    if limits.get("pids"):
        create += ["--pids-limit", str(limits["pids"])]
    if user:
        create += ["--user", str(user)]
    if spec.get("entrypoint"):
        create += ["--entrypoint", str(spec["entrypoint"])]
    for k, v in env.items():
        create += ["--env", f"{k}={v}"]
    create += ["-v", f"{ws}:{mount}:rw", "--workdir", mount]
    create += [image, *command]

    log(f"run_id={run_id} class={run_class} image={image}")
    log(f"workspace={ws} -> {mount} (rw) | network={network} | limits={limits} | timeout={timeout_s}s")

    rc, out, err = run_cmd(create, timeout=120)
    if rc != 0:
        release_slot(slot)
        update_state(runs_total=1, failures_total=1, last_run_id=run_id,
                     last_timestamp_seconds=int(time.time()))
        die(5, f"docker create falhou: {(err or out).decode(errors='replace').strip()}")
    container_id = out.decode().strip()

    started = time.monotonic()
    timed_out = False
    start_rc = 0
    cap_out = b""
    cap_err = b""
    try:
        p = subprocess.run(
            ["docker", "start", "--attach", container_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_s,
        )
        start_rc, cap_out, cap_err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        timed_out = True
        cap_out = e.stdout or b""
        cap_err = e.stderr or b""
    duration_ms = int((time.monotonic() - started) * 1000)

    # coleta estado/límites aplicados antes de remover (auditoria).
    st_rc, st_out, _ = run_cmd(["docker", "inspect", container_id], timeout=30)
    state = {}
    limits_applied = {}
    if st_rc == 0:
        try:
            insp = json.loads(st_out.decode())[0]
            s = insp.get("State", {})
            hc = insp.get("HostConfig", {})
            state = {
                "status": s.get("Status"),
                "exit_code": s.get("ExitCode") if not s.get("Running") else None,
                "oom_killed": s.get("OOMKilled"),
                "error": s.get("Error") or "",
            }
            limits_applied = {
                "nano_cpus": hc.get("NanoCpus"),
                "memory_bytes": hc.get("Memory"),
                "pids_limit": hc.get("PidsLimit"),
                "network_mode": (hc.get("NetworkMode") or ""),
            }
        except Exception:
            pass

    # remove SEMPRE (sucesso, falha, timeout).
    container_removed = False
    if not args.keep_on_error:
        run_cmd(["docker", "rm", "-f", container_id], timeout=60)
        v_rc, _, _ = run_cmd(["docker", "inspect", container_id], timeout=30)
        container_removed = v_rc != 0

    exit_code = state.get("exit_code")
    if timed_out:
        exit_code = None
    elif exit_code is None:
        exit_code = 125 if timed_out else start_rc

    out_txt = mask_secrets(cap_out.decode(errors="replace"), secret_values)
    err_txt = mask_secrets(cap_err.decode(errors="replace"), secret_values)

    transcript_path = None
    if args.transcript:
        tp = Path(args.transcript)
        tp.parent.mkdir(parents=True, exist_ok=True)
        body = (cap_out + b"\n--- stderr ---\n" + cap_err)[:TRANSCRIPT_MAX_BYTES]
        tp.write_text(mask_secrets(body.decode(errors="replace"), secret_values))
        transcript_path = str(tp)

    result = {
        "ok": (exit_code == 0 and not timed_out),
        "run_id": run_id,
        "class": run_class,
        "image": image,
        "container_id": container_id,
        "container_name": cname,
        "container_removed": container_removed,
        "workspace": str(ws),
        "workspace_mount": mount,
        "network": network,
        "limits": limits,
        "limits_applied": limits_applied,
        "timeout_seconds": timeout_s,
        "timed_out": timed_out,
        "duration_ms": duration_ms,
        "exit_code": exit_code,
        "state": state,
        "transcript_path": transcript_path,
        "stdout_tail": out_txt[-OUTPUT_TAIL_BYTES:],
        "stderr_tail": err_txt[-OUTPUT_TAIL_BYTES:],
        "secrets_masked": True,
    }
    # fim do run: libera o slot e publica métricas (contadores/últimos valores).
    release_slot(slot)
    update_state(
        runs_total=1,
        failures_total=(0 if (exit_code == 0 and not timed_out) else 1),
        timeouts_total=(1 if timed_out else 0),
        last_duration_ms=duration_ms,
        last_run_id=run_id,
        last_timestamp_seconds=int(time.time()),
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if timed_out:
        return 3
    return 0 if exit_code == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
