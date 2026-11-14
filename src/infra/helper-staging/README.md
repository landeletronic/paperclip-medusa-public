# helper-staging/ — staging isolado do auxiliar local (plano padrão, Fase 1)

Executa o **llama.cpp (backend VULKAN)** em container com acesso **exclusivo** à
**RX 5500 XT** (`/dev/dri/renderD129`, PCI `0000:03:00.0`) — porta só em **loopback**,
sem volumes/bancos de produção. Modelo inicial: **Qwen3 4B Q4_K_M** (8K e 16K de contexto).

## Componentes

| Item | Onde | Nota |
|---|---|---|
| `Dockerfile` | este diretório | build do `llama-server` com `GGML_VULKAN=ON`, **commit pinado** (`llama.cpp.commit` na label) |
| Imagem | `medusa-llama-vulkan:<sha>` | runtime Ubuntu 24.04 + Mesa/RADV |
| Modelos | `/home/usuario/medusa-helper-staging/models/` | GGUF com **SHA-256 registrado** (`models/SHA256SUMS`) |
| Serviço | container `medusa-helper-staging` | `127.0.0.1:8085` → `:8080` (somente loopback) |

## Subir (exclusividade da RX 5500)

```bash
docker run -d --name medusa-helper-staging \
  --device /dev/dri/renderD129:/dev/dri/renderD129 \
  -p 127.0.0.1:8085:8080 \
  -v /home/usuario/medusa-helper-staging/models:/models:ro \
  medusa-llama-vulkan:<sha> \
  llama-server -m /models/<modelo>.gguf -c 16384 -ngl 999 -mg 0 --host 0.0.0.0 --port 8080
```

- **Só `renderD129` é passado** (RX 5500): o Mesa dentro do container enxerga uma única GPU —
  exclusividade por device passthrough (reforçada por `-mg 0`).
- `-ngl 999` = todas as camadas na GPU (gate: `offloaded N/N layers to GPU` no log).
- Trocar `-c 8192` / `-c 16384` para os testes de contexto do plano.

## Verificar (gate da Fase 1)

```bash
docker logs medusa-helper-staging 2>&1 | grep -i 'offloaded'   # N/N na GPU, 0 no CPU
curl http://127.0.0.1:8085/health
curl http://127.0.0.1:8085/v1/chat/completions -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"responda: ok"}],"max_tokens":8}'
journalctl -k --since '-30 min' | grep -iE 'amdgpu.*(fault|reset|timeout)'   # esperado: vazio
```

## Limites (do plano padrão)

- porta só loopback/tailnet restrita; **nenhum volume ou banco de produção**;
- `qwen3:4b` primeiro (8K/16K); avaliação do 8B é a Fase 2; integração (LiteLLM/Paperclip) é Fase 3/4.
