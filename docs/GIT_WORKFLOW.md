# Fluxo de trabalho Git

## 1. Identidade local

O repositório usa identidade local (não global) para não interferir em outros projetos:

```powershell
git config user.name "Paperclip Medusa DevOps"
git config user.email "devops@paperclip-medusa.local"
```

Para usar sua identidade pessoal:

```powershell
git config user.name "Seu Nome"
git config user.email "seu.email@exemplo.com"
```

## 2. Branch principal

- Nome: `main`.
- Todo trabalho entra por branch de trabalho e é integrado à `main`.
- Commits diretos na `main` são aceitáveis apenas para bootstrap e correções triviais.

## 3. Branches de trabalho

| Prefixo | Uso |
|---|---|
| `feat/` | Nova funcionalidade. |
| `fix/` | Correção de defeito. |
| `docs/` | Documentação. |
| `chore/` | Manutenção, configuração e infraestrutura. |
| `test/` | Testes e validações. |
| `refactor/` | Refatoração sem mudança de comportamento. |

Exemplo:

```powershell
git switch -c docs/registro-sessao-001
```

## 4. Commits

Padrão: [Conventional Commits](https://www.conventionalcommits.org/).

```text
<tipo>(<escopo opcional>): <descrição no imperativo>
```

Tipos aceitos:

- `feat`
- `fix`
- `docs`
- `chore`
- `test`
- `refactor`
- `perf`
- `build`
- `ci`

Exemplos:

```text
docs: registra sessão 001 de bootstrap
chore: cria estrutura inicial de logs
test: adiciona validação da estrutura do repositório
```

Boas práticas:

- uma mudança lógica por commit;
- mensagem curta no título (até 72 caracteres);
- corpo opcional explicando o porquê;
- referenciar registros de `logs/` quando aplicável.

## 5. Antes de commitar

```powershell
powershell -File scripts/Test-RepositoryStructure.ps1
git status
git diff
git add <arquivos>
git diff --staged
git commit -m "tipo: descrição"
```

## 6. Publicação

O repositório foi criado localmente, sem remote. Para publicar:

```powershell
git remote add origin <URL_DO_REPOSITORIO>
git push -u origin main
```

Para enviar branches de trabalho:

```powershell
git push -u origin <nome-da-branch>
```

## 7. Tags e releases

- Tags semânticas: `vMAJOR.MINOR.PATCH`.
- Criar tag anotada:

```powershell
git tag -a v0.1.0 -m "Bootstrap do repositório"
git push origin v0.1.0
```

## 8. CI

Os workflows executam em `push` e `pull_request` com permissões somente de leitura:

- `.github/workflows/validate.yml`: estrutura da raiz, diretórios/arquivos obrigatórios, JSON de `opencode.json`, precedência do Hermes, nomenclatura dos logs e padrões básicos de segredo;
- `.github/workflows/lint.yml`: Markdownlint, Yamllint, Actionlint, ShellCheck, Hadolint e validações de sintaxe Python, JavaScript e JSON;
- `.github/workflows/security.yml`: Gitleaks no histórico Git, também agendado semanalmente e disponível por execução manual.

Binários baixados no CI têm versão e checksum fixados. As ações de terceiros usam SHA imutável com a versão documentada em comentário. O Dependabot verifica mensalmente atualizações de GitHub Actions.

Antes de abrir um pull request, execute as validações aplicáveis descritas em `CONTRIBUTING.md`.

## 9. Recuperação e segurança

- Não reescrever histórico publicado sem coordenação.
- Não commitar segredos. Em caso de incidente, siga a seção 11 de [`CONVENTIONS.md`](CONVENTIONS.md).
- Use `git fsck` periodicamente para verificar a integridade do repositório.
