# Docker Compose — E1

Esqueleto versionado da Fase 0. Ele declara Paperclip, LiteLLM e dois PostgreSQL independentes,
mas a E1 **não inicia** nenhum serviço.

## Versões fixadas

| Serviço | Imagem |
|---|---|
| Paperclip | `ghcr.io/paperclipai/paperclip:2026.1106.0` |
| LiteLLM | `ghcr.io/berriai/litellm:v1.109.1` |
| PostgreSQL | `postgres:17-alpine` |

## Redes

- `app`: comunicação Paperclip ↔ LiteLLM e saída normal necessária a Git/downloads autorizados;
- `paperclip-database` e `litellm-database`: redes internas independentes, cada uma acessível
  somente pelo respectivo serviço e banco;
- `ollama-access`: rede externa `hermes-architect_backend`, ligada **somente** ao LiteLLM para
  alcançar o Ollama já existente no primary-host.

Paperclip e LiteLLM publicam portas apenas no loopback. Os bancos não publicam portas.

## Variáveis obrigatórias

Copie `.env.example` para `.env` e substitua cada placeholder `replace-with-*`. Gere valores
independentes; não reutilize segredos.

```bash
cp .env.example .env
openssl rand -hex 32
```

| Variável | Uso |
|---|---|
| `PAPERCLIP_DB_PASSWORD` | senha do PostgreSQL exclusivo do Paperclip; use valor URL-safe |
| `BETTER_AUTH_SECRET` | assinatura das sessões humanas do Paperclip |
| `PAPERCLIP_TOOL_ACTION_SIGNING_SECRET` | assinatura de ações de ferramenta sujeitas a aprovação |
| `PAPERCLIP_AGENT_JWT_SECRET` | assinatura dos JWTs curtos entregues aos agentes |
| `LITELLM_DB_PASSWORD` | senha do PostgreSQL exclusivo do LiteLLM; use valor URL-safe |
| `LITELLM_MASTER_KEY` | credencial administrativa do gateway; mantenha o prefixo `sk-` |
| `LITELLM_SALT_KEY` | criptografia das credenciais do LiteLLM; não pode ser regenerada após uso |
| `LITELLM_CONFIG_PATH` | caminho do `config.yaml`; no primary-host usa `/opt/paperclip-medusa/config/gateway.yaml` |

As demais variáveis têm defaults locais documentados em `.env.example`. Não configure
`OPENAI_API_KEY`, `ANTHROPIC_API_KEY` ou qualquer chave de provedor externo.

## Validar sem executar

```bash
docker compose --env-file .env.example -f compose.yaml config --quiet
```

Esse comando somente renderiza e valida o modelo Compose. A inicialização pertence à E2/E3.
