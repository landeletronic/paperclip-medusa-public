# Scripts

Automação em PowerShell para padronizar a criação e a validação dos registros.

## Requisitos

- Windows PowerShell 5.1 ou PowerShell 7+.
- Executar a partir da raiz do repositório (os scripts calculam a raiz a partir de `$PSScriptRoot`).

## Scripts disponíveis

### `New-LogEntry.ps1`

Cria um registro a partir do template correspondente, com sequencial automático.

```powershell
powershell -File scripts/New-LogEntry.ps1 -Type conversation -Slug minha-sessao -Title "Minha sessão"
powershell -File scripts/New-LogEntry.ps1 -Type task -Slug ajuste-x -Title "Ajuste X"
```

Parâmetros:

| Parâmetro | Obrigatório | Descrição |
|---|---|---|
| `-Type` | Sim | `conversation`, `command`, `execution`, `task`, `test` ou `inventory`. |
| `-Slug` | Sim | Slug curto, sem acentos. |
| `-Title` | Não | Título legível; padrão derivado do slug. |
| `-Date` | Não | Data `YYYY-MM-DD`; padrão hoje. |
| `-Author` | Não | Autor; padrão `git config user.name`. |
| `-Workspace` | Não | Caminho da raiz; padrão detectado. |

### `Add-ConversationEntry.ps1`

Acrescenta uma mensagem a um arquivo de conversa existente.

```powershell
powershell -File scripts/Add-ConversationEntry.ps1 `
  -LogFile logs/conversations/2026-11-09-session-001-bootstrap-repositorio.md `
  -Role assistant `
  -Message "Resumo da resposta."
```

`-Role` aceita `user`, `assistant`, `system` ou `tool`.

### `Record-Command.ps1`

Executa um comando, captura saída/exit code e anexa o resultado a um log de comandos. Se `-LogFile` for omitido, cria um novo registro automaticamente.

```powershell
powershell -File scripts/Record-Command.ps1 `
  -Command "git status --short" `
  -Description "Conferir estado do repositório" `
  -LogFile logs/commands/2026-11-09-command-001-bootstrap.md
```

> **Atenção:** a saída do comando é gravada integralmente (até 20.000 caracteres). Não execute comandos que imprimam segredos.

### `New-Inventory.ps1`

Gera um inventário automático com caminho, tipo, tamanho e SHA-256 de todos os arquivos, excluindo `.git` e artefatos de build.

```powershell
powershell -File scripts/New-Inventory.ps1 -Slug estado-atual -Title "Inventário do estado atual"
```

### `Test-RepositoryStructure.ps1`

Valida a estrutura do repositório e retorna código de saída 1 se houver falha.

```powershell
powershell -File scripts/Test-RepositoryStructure.ps1
```

Validações:

- T1: raiz contém apenas arquivos essenciais de entrada, governança e infraestrutura permitidos.
- T2: diretórios obrigatórios existem.
- T3: arquivos obrigatórios existem.
- T4: registros em `logs/` seguem o padrão de nomenclatura.
- T5: repositório Git inicializado.
- T6: nenhum segredo de alta confiança detectado.
- T7: nenhum arquivo `.env` real versionado.

## Convenções dos scripts

- Texto em ASCII para compatibilidade com Windows PowerShell 5.1.
- `$ErrorActionPreference = 'Stop'` para falhar rápido.
- Escrita em UTF-8 sem BOM.
- Nenhum script apaga arquivos automaticamente.
