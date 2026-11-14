# Política de segurança

## Versões suportadas

O projeto ainda não publica releases versionadas. Apenas o estado mais recente da branch `main` é
mantido. Esta política será atualizada quando houver tags e releases suportados.

## Como reportar uma vulnerabilidade

Não abra uma issue pública com segredos, credenciais, dados pessoais, detalhes de exploração ou
informações que permitam reproduzir um ataque antes da correção.

Enquanto o repositório não tiver remote público:

1. contate o mantenedor por um canal privado previamente acordado;
2. informe componente, impacto, pré-condições e passos mínimos de reprodução;
3. remova ou masque tokens, chaves e dados pessoais;
4. aguarde confirmação antes de divulgar publicamente.

Após publicação no GitHub, use **Security → Report a vulnerability** para criar um advisory privado.

## Expectativa de resposta

- Confirmação inicial: até 5 dias úteis.
- Triagem e severidade: até 10 dias úteis.
- Prazo de correção: depende do impacto e da disponibilidade de mitigação.

Esses prazos são metas operacionais, não um SLA contratual.

## Escopo prioritário

- exposição acidental de serviços, bancos ou APIs fora de loopback/tailnet;
- vazamento de segredos ou chaves virtuais;
- quebra do isolamento entre empresas, runs, workspaces ou containers;
- execução não autorizada pelo executor ou pelos agentes;
- fallback de inferência para provedores externos;
- comprometimento da cadeia de CI, imagens ou dependências.
