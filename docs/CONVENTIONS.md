# Convenções do repositório

Este documento define as regras de organização, nomenclatura e registro do projeto **Paperclip Medusa**.

## 1. Princípios

1. **Raiz limpa:** somente arquivos essenciais de entrada, governança e configuração de infraestrutura/lint documentados; demais conteúdos ficam em subpastas por utilidade.
2. **Uma utilidade, uma pasta:** cada arquivo pertence ao diretório que representa sua função.
3. **Rastreabilidade:** toda ação relevante gera um registro versionado em `logs/`.
4. **Reprodutibilidade:** comandos e execuções devem ser registrados de forma que possam ser repetidos.
5. **Segurança:** nenhum segredo é versionado.
6. **Preservação:** ao mover arquivos, o conteúdo original é mantido e a mudança é registrada.

## 2. Estrutura de diretórios

```text
docs/                  Documentação conceitual e técnica
  agents/              Integração com OpenCode e Hermes Agent
  assets/              Imagens, diagramas e capturas
  research/            Estudos e comparativos
  plans/               Planos de implementação por fase
logs/                  Registros operacionais
  conversations/       Sessões com agentes de IA
  commands/            Comandos executados
  executions/          Execuções de scripts e pipelines
  tasks/               Tarefas e critérios de aceite
  tests/               Testes e resultados
  inventories/         Inventários de arquivos e hashes
scripts/               Automação em PowerShell
src/                   Código-fonte da aplicação
templates/             Modelos de registro
```

## 3. Nomenclatura de registros

Formato obrigatório:

```text
YYYY-MM-DD-<prefixo>-<NNN>-<slug>.md
```

| Tipo | Prefixo | Pasta |
|---|---|---|
| Conversa | `session` | `logs/conversations/` |
| Comando | `command` | `logs/commands/` |
| Execução | `execution` | `logs/executions/` |
| Tarefa | `task` | `logs/tasks/` |
| Teste | `test` | `logs/tests/` |
| Inventário | `inventory` | `logs/inventories/` |

Regras do `slug`:

- minúsculas;
- sem acentos;
- palavras separadas por hífen;
- curto e descritivo (2 a 6 palavras).

Exemplo: `2026-11-09-session-001-bootstrap-repositorio.md`.

## 4. Metadados mínimos

Todo registro deve começar com uma seção de metadados contendo, no mínimo:

| Campo | Obrigatório | Descrição |
|---|---|---|
| ID | Sim | Identificador único do registro. |
| Data | Sim | Data no formato `YYYY-MM-DD`. |
| Hora | Sim | Hora local com fuso, quando aplicável. |
| Autor | Sim | Pessoa ou agente responsável. |
| Tipo | Sim | `conversation`, `command`, `execution`, `task`, `test` ou `inventory`. |
| Status | Recomendado | `em andamento`, `concluído`, `falhou`, `cancelado`. |
| Relacionados | Recomendado | Links para outros registros, commits ou issues. |

## 5. Registro de conversas

- Uma conversa = um arquivo em `logs/conversations/`.
- O arquivo deve conter:
  - objetivo da sessão;
  - solicitação do usuário (preferencialmente literal);
  - contexto inicial;
  - linha do tempo das ações;
  - decisões tomadas;
  - artefatos gerados ou alterados;
  - pendências;
  - transcript ou resumo fiel das mensagens.
- Conversas longas podem ser resumidas, mas decisões e comandos devem permanecer explícitos.
- Atualizar o mesmo arquivo ao longo da sessão; não criar um arquivo por mensagem.

## 6. Registro de comandos

- Agrupar comandos relacionados em um único arquivo por sessão/lote.
- Para cada comando, registrar:
  - data/hora;
  - diretório de trabalho;
  - comando exato;
  - código de saída;
  - saída relevante (resumida, se muito extensa);
  - efeitos colaterais.
- Comandos destrutivos devem ser destacados com aviso.
- Usar `scripts/Record-Command.ps1` para captura automática.

## 7. Registro de execuções

Uma execução representa a rodada de um script, pipeline ou rotina. Deve conter:

- gatilho (manual, agendado, CI, evento);
- ambiente (SO, versões, branch, commit);
- entradas;
- passos executados;
- duração;
- status final;
- artefatos produzidos;
- logs relacionados.

## 8. Registro de tarefas

- Toda tarefa deve ter status e critérios de aceite verificáveis.
- Usar checkboxes para o plano de execução.
- Anexar evidências: links para commits, testes e comandos.
- Tarefas concluídas não devem ser apagadas; servem de histórico.

## 9. Registro de testes

- Cada bateria de testes gera um arquivo em `logs/tests/`.
- Incluir:
  - objetivo;
  - ambiente;
  - casos de teste com resultado esperado e obtido;
  - evidência (comando, saída ou link);
  - conclusão (`passou`, `falhou`, `parcial`).
- Testes automatizados devem apontar para o script ou workflow correspondente.

## 10. Inventários

- Inventários são snapshots do estado do repositório.
- Gerar antes e depois de reorganizações relevantes.
- Incluir caminho, tipo, tamanho, SHA-256 e descrição.
- Usar `scripts/New-Inventory.ps1` para geração automática.

## 11. Segredos e dados sensíveis

Nunca versionar:

- senhas, tokens, chaves de API, chaves privadas;
- arquivos `.env` reais;
- dados pessoais de terceiros;
- capturas de tela com credenciais visíveis.

Se um segredo for commitado acidentalmente:

1. revogar o segredo imediatamente;
2. remover do histórico com ferramenta apropriada;
3. registrar o incidente em `logs/` (sem repetir o segredo);
4. comunicar os responsáveis.

## 12. Qualidade e revisão

Antes de cada commit:

```powershell
powershell -File scripts/Test-RepositoryStructure.ps1
git status
git diff --staged
```

Critérios de aceite do repositório:

- raiz contém apenas os arquivos essenciais de entrada, governança e configuração permitidos;
- diretórios obrigatórios existem;
- registros seguem o padrão de nomenclatura;
- nenhum segredo detectável;
- links relativos da documentação resolvem.

## 13. Retenção

- Registros são permanentes por padrão.
- Não remover histórico sem justificativa registrada.
- Inventários antigos podem ser mantidos para comparação.
