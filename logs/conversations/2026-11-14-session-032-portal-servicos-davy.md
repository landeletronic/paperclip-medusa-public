# Sessão 032 — Portal de serviços do Davy Jones

## Metadados

| Campo | Valor |
|---|---|
| ID | 2026-11-14-session-032 |
| Data | 2026-11-14 |
| Hora | 17:35 -03:00 |
| Autor | Hermes Agent |
| Tipo | conversation |
| Status | concluído |

## Solicitação

Criar uma página única de acesso aos serviços web do `davy-jones-hermes`, com ícones, nomes e
redirecionamento ao clicar, como Grafana e Open WebUI.

## Decisões

- Publicar na raiz `https://<DAVY_JONES_LAN_IP>/`, reutilizando o HTTPS e a porta 443 existentes.
- Redirecionar `http://<DAVY_JONES_LAN_IP>/` para a mesma raiz HTTPS.
- Mover o acesso externo do Open WebUI para `https://<DAVY_JONES_LAN_IP>:3002/`.
- Exibir apenas aplicações web de usuário: Open WebUI, Grafana, Paperclip e Hermes Dashboard.
- Usar HTML/CSS/JS autocontido, sem dependências externas.
- Usar o hostname atual para formar os links e não fixar o IP em tempo de execução.

## Resultado

Portal publicado na raiz, responsivo e validado. O oráculo final terminou com 288 PASS, 0 FAIL e 0 WARN.

## Artefatos

- `nginx/html/servicos/index.html`
- `nginx/conf.d/owui.conf`
- `docker-compose.yml`
- `tests/verify_stack.sh`
- `docs/runbooks/servicos/nginx.md`
