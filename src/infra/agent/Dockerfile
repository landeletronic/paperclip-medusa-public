# Imagem de runtime da classe exec-run (contrato F1.1 §3) — agente em container.
# Base: runtime oficial do Paperclip (Node 24) pinada por DIGEST; adiciona apenas
# o driver de agente (loop LLM + ferramentas, inferência local via LiteLLM).
FROM ghcr.io/paperclipai/paperclip@sha256:d6584f05cf57a4b26c117eb083725f18c1fe69ddafa7d16c9f8cce83f6fa17da
COPY agent-run.mjs /opt/medusa/agent-run.mjs
LABEL org.opencontainers.image.title="medusa-agent-run" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.description="Agente (LLM + ferramentas) para containers efemeros por run - Fase 4"
