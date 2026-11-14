# Gateway local — LiteLLM

`config.yaml` expõe dois nomes OpenAI-compatible e roteia exclusivamente para modelos servidos
pelo Ollama local:

- `medusa-primary` → `qwen3:4b-64k`;
- `medusa-fallback` → `qwen3:8b-chat-16k`.

O fallback é somente local. Não há configuração, chave ou fallback para OpenAI, Anthropic,
OpenRouter, Google, Groq ou outro serviço externo de inferência.

Os endpoints vêm de `OLLAMA_PRIMARY_BASE_URL` e `OLLAMA_FALLBACK_BASE_URL`. Na PoC ambos apontam
para `http://ollama:11434`, acessível apenas ao container LiteLLM pela rede externa controlada.
A E2 provou health, inferência primária e fallback local; o gateway está ativo somente em loopback.
