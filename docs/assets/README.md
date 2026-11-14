# Ativos visuais

Esta pasta armazena imagens, diagramas e capturas de tela usados na documentação.

## Organização

| Pasta | Conteúdo |
|---|---|
| `screenshots/` | Capturas de tela do sistema, ferramentas e interfaces. |

## Convenções

- Nomear arquivos com data e descrição: `YYYY-MM-DD-descricao-curta.png`.
- Preferir PNG para capturas de tela e SVG para diagramas vetoriais.
- Evitar imagens com credenciais, tokens ou dados pessoais visíveis.
- Se uma imagem contiver dado sensível, aplicar tarja/desfoque antes de commitar.
- Registrar cada ativo no catálogo da subpasta correspondente.
- Não duplicar arquivos: referencie o ativo existente.

## Uso em Markdown

```markdown
![Descrição](../assets/screenshots/2026-11-09-100035.png)
```

Sempre fornecer texto alternativo descritivo.
