#!/usr/bin/env python3
# =============================================================================
# executor_service.py — interface HTTP AUTENTICADA do executor de containers
# efêmeros (contrato F1.2 §9). É por aqui que integrações nativas (plugin de
# sandbox provider/runner) devem chamar o executor — o container `paperclip`
# NUNCA recebe docker.sock.
#
#   GET  /health          -> {"ok": true, ...}          (sem auth; info mínima)
#   POST /run             -> resultado JSON do run       (Authorization: Bearer <token>)
#
# O body de POST /run é a MESMA spec do executor CLI (image/workspace/command/
# env/limits/timeout/network/user/entrypoint). O serviço delega ao binário do
# executor (que já trata slots de concorrência, remoção garantida e métricas).
#
# Token: gerado no host em $PAPERCLIP_EXECUTOR_SERVICE_TOKEN (600) — fora do git.
# Bind: 127.0.0.1 por padrão (nunca expor à LAN; ver runbook §13).
#
# Uso: python3 executor_service.py
# =============================================================================
import hmac
import json
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

EXECUTOR = os.environ.get("PAPERCLIP_EXECUTOR_BIN", "/usr/local/bin/paperclip-run-executor")
TOKEN_FILE = Path(os.environ.get("PAPERCLIP_EXECUTOR_SERVICE_TOKEN",
                                 "/home/usuario/ci/executor-service.token"))
BIND = os.environ.get("PAPERCLIP_EXECUTOR_SERVICE_BIND", "127.0.0.1")
PORT = int(os.environ.get("PAPERCLIP_EXECUTOR_SERVICE_PORT", "8700"))
MAX_BODY = 256 * 1024


def load_token() -> str:
    try:
        return TOKEN_FILE.read_text().strip()
    except OSError:
        print(f"[executor-service] ERRO: token ilegível em {TOKEN_FILE}", file=sys.stderr)
        sys.exit(2)


class Handler(BaseHTTPRequestHandler):
    server_version = "medusa-executor-service/1.0"

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self) -> bool:
        hdr = self.headers.get("Authorization", "")
        if not hdr.startswith("Bearer "):
            return False
        return hmac.compare_digest(hdr[7:].strip(), load_token())

    def do_GET(self) -> None:  # noqa: N802 (API do http.server)
        if self.path.rstrip("/") in ("", "/health"):
            self._send(200, {"ok": True, "service": "paperclip-run-executor",
                             "version": self.server_version})
        else:
            self._send(404, {"ok": False, "error": "rota não encontrada"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/run":
            self._send(404, {"ok": False, "error": "rota não encontrada"})
            return
        if not self._authorized():
            self._send(401, {"ok": False, "error": "token inválido ou ausente"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY:
                raise ValueError("tamanho de body inválido")
            spec = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError) as e:
            self._send(400, {"ok": False, "error": f"spec inválida: {e}"})
            return
        if not isinstance(spec, dict) or not all(spec.get(k) for k in ("image", "workspace", "command")):
            self._send(400, {"ok": False, "error": "spec sem image/workspace/command"})
            return

        # campos de controle do serviço (não vão à spec do executor)
        allow_roots = spec.pop("allow_roots", []) or []
        allow_unpinned = bool(spec.pop("allow_unpinned", False))
        cmd = [EXECUTOR, "run", "--spec", "-"]
        for root in allow_roots:
            cmd += ["--allow-root", str(root)]
        if allow_unpinned:
            cmd += ["--allow-unpinned"]

        proc = subprocess.run(
            cmd,
            input=json.dumps(spec).encode(),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1800,
        )
        try:
            result = json.loads(proc.stdout)
        except json.JSONDecodeError:
            result = {"ok": False, "error": "executor sem JSON válido",
                      "stderr": proc.stderr.decode(errors="replace")[-500:]}
        result["tool_exit"] = proc.returncode
        self._send(200, result)

    def log_message(self, fmt: str, *args) -> None:  # log mínimo no stderr
        print(f"[executor-service] {self.address_string()} {fmt % args}", file=sys.stderr)


def main() -> None:
    if not TOKEN_FILE.exists() or not TOKEN_FILE.read_text().strip():
        # gera o token se ausente (somente no host, 600 — fora do git)
        import secrets
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(secrets.token_urlsafe(32))
        TOKEN_FILE.chmod(0o600)
        print(f"[executor-service] token gerado em {TOKEN_FILE}", file=sys.stderr)
    server = ThreadingHTTPServer((BIND, PORT), Handler)
    print(f"[executor-service] escutando em {BIND}:{PORT} (executor: {EXECUTOR})", file=sys.stderr)
    server.serve_forever()


if __name__ == "__main__":
    main()
