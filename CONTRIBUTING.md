# Contribuindo com o Paperclip Medusa

Obrigado por contribuir. O projeto combina documentação auditável, infraestrutura local e agentes de
IA. Mudanças devem ser pequenas, reproduzíveis e não podem enviar prompts, código ou dados de tarefas
para provedores externos de IA.

## Antes de começar

1. Leia `AGENTS.md`, `README.md`, `docs/CONVENTIONS.md` e `docs/GIT_WORKFLOW.md`.
2. Abra uma issue para mudanças relevantes, incidentes ou decisões arquiteturais.
3. Crie uma branch com prefixo `feat/`, `fix/`, `docs/`, `chore/`, `test/` ou `refactor/`.
4. Nunca inclua segredos, `.env` reais, dados pessoais ou saídas com credenciais.

## Ambiente

Ferramentas recomendadas:

- Git;
- PowerShell 7 (`pwsh`) para os scripts do repositório;
- Python 3.9+;
- Node.js 22+;
- ShellCheck;
- Docker/Compose quando a mudança afetar a stack;
- Gitleaks para varredura de segredos.

## Fluxo de contribuição

1. Registre a tarefa em `logs/tasks/`.
2. Inspecione o estado com `git status` e leia os arquivos afetados.
3. Implemente apenas o escopo necessário.
4. Adicione ou atualize testes e registros operacionais.
5. Execute as validações locais.
6. Use Conventional Commits.
7. Abra um pull request preenchendo o template e relacionando a issue/tarefa.

## Validações locais

```bash
# Estrutura (PowerShell)
pwsh -File scripts/Test-RepositoryStructure.ps1

# Markdown e YAML
npx --yes markdownlint-cli2@0.24.1 '**/*.md'
python3 -m yamllint -c .yamllint.yml .

# Python, JavaScript e shell
python3 -m py_compile src/infra/executor/*.py src/infra/bench/*.py
find src -type f -name '*.mjs' -exec node --check {} \;
find src scripts -type f -name '*.sh' -exec shellcheck {} +

# Segredos — requer Gitleaks 8.30.1
gitleaks git --redact --verbose --config .gitleaks.toml
```

Quando Docker estiver disponível:

```bash
docker compose --env-file src/infra/compose/.env.example \
  -f src/infra/compose/compose.yaml config
```

## Commits

Formato:

```text
<tipo>(<escopo opcional>): <descrição no imperativo>
```

Uma mudança lógica por commit. Não faça squash, rebase ou force-push em histórico compartilhado sem
coordenação.

## Pull requests

O PR deve:

- explicar problema, solução e riscos;
- listar testes executados e limitações;
- atualizar documentação e `logs/`;
- manter inferência de IA 100% local;
- passar estrutura, lint e Gitleaks;
- não conter mudanças alheias ao escopo.

## Licença das contribuições

Ao enviar uma contribuição, você concorda que ela seja disponibilizada sob a Apache License 2.0,
conforme `LICENSE`.
