# Código-fonte

Diretório de código e infraestrutura da aplicação **Paperclip Medusa**.

## Estado

- A trilha de plataforma e o plano padrão do auxiliar local foram concluídos.
- O diretório contém a stack Compose, gateway local, agentes, executor efêmero, manifests Kubernetes,
  staging Vulkan e ferramentas de benchmark.
- A inferência permanece 100% local, com Paperclip, LiteLLM, Ollama/llama.cpp e bancos operacionais
  no host host principal.

## Organização

```text
src/
├── agents/             Instruções dos agentes CEO e executor
├── gateway/            Configuração e capacidade do LiteLLM
└── infra/
    ├── agent/          Runtime de agentes e Chief of Staff Local
    ├── bench/          Benchmarks de latência, triagem e concorrência
    ├── compose/        Stack Docker Compose
    ├── executor/       Executor efêmero e serviço autenticado
    ├── helper-staging/ Staging Vulkan do auxiliar local
    ├── host/           Preparação conservadora do host
    └── k8s/            k3d, KEDA, External Secrets e workloads
```

## Componentes

- [`infra/compose/`](infra/compose/README.md) — stack Compose do Paperclip, LiteLLM e bancos.
- [`infra/executor/`](infra/executor/README.md) — execução isolada por container e API autenticada.
- [`infra/agent/`](infra/agent/) — agente efêmero e `Chief of Staff Local`.
- [`infra/helper-staging/`](infra/helper-staging/README.md) — build/staging Vulkan na RX 5500 XT.
- [`infra/k8s/`](infra/k8s/README.md) — cluster k3d, KEDA, External Secrets e fila Redis.
- [`infra/bench/`](infra/bench/) — medições de latência, qualidade, falha e concorrência.
- [`infra/host/`](infra/host/README.md) — preparação e operação do host principal.
- [`gateway/`](gateway/README.md) — modelos, capacidade e fallback exclusivamente locais.
- [`agents/ceo/`](agents/ceo/README.md) e [`agents/opencode-dev/`](agents/opencode-dev/README.md) — instruções dos agentes.

## Regras

- Cada aplicação deve ter seu próprio README com instruções de execução.
- Dependências e artefatos de build não são versionados (ver `.gitignore`).
- Testes automatizados devem ser executados pelo CI e registrados em `logs/tests/`.
- Segredos ficam em variáveis de ambiente ou cofre, nunca no código.
