# Tarefa 048 — Portal de serviços do Davy Jones

## Metadados

| Campo | Valor |
|---|---|
| ID | 2026-11-14-task-048 |
| Data | 2026-11-14 |
| Hora | 17:35 -03:00 |
| Autor | Hermes Agent |
| Tipo | task |
| Status | concluída |
| Relacionados | `2026-11-14-test-047-portal-servicos-davy.md` |

## Objetivo

Criar uma página única, responsiva e acessível para abrir os serviços web do host
`davy-jones-hermes` por ícones clicáveis.

## Critérios de aceite

- [x] Página publicada por HTTPS na raiz da LAN (`https://<DAVY_JONES_LAN_IP>/`).
- [x] HTTP e HTTPS sem caminho abrem o portal.
- [x] Open WebUI preservado em HTTPS na porta 3002.
- [x] Cards com ícones e nomes de Open WebUI, Grafana, Paperclip e Hermes Dashboard.
- [x] Cada card aponta para a aplicação e porta corretas.
- [x] Layout responsivo para desktop e celular.
- [x] Nginx serve o portal sem substituir o Open WebUI.
- [x] Teste de regressão incluído no oráculo.
- [x] Oráculo completo sem falhas.

## Evidências

- URL: `https://<DAVY_JONES_LAN_IP>/`
- Open WebUI: `https://<DAVY_JONES_LAN_IP>:3002/`
- HTML: `nginx/html/servicos/index.html`
- Oráculo: `PASS=288 FAIL=0 WARN=0`.
