# Registro de comandos 031 — Portal de serviços do Davy Jones

## Metadados

| Campo | Valor |
|---|---|
| ID | 2026-11-14-command-031 |
| Data | 2026-11-14 |
| Início | 17:35 -03:00 |
| Autor | Hermes Agent |
| Tipo | command |
| Status | concluído |
| Workspace | repositório de infraestrutura do host |

## Objetivo

Implementar, publicar e validar o portal web dos serviços do host.

## Comandos relevantes

Os comandos abaixo são reproduções sanitizadas: os valores reais de host e diretório foram
substituídos por variáveis para não publicar identificadores internos.

| # | Comando | Exit | Resultado |
|---|---|---|---|
| 1 | `bash tests/verify_stack.sh` (antes) | 0 | 283 PASS |
| 2 | `bash -n tests/verify_stack.sh` | 0 | sintaxe válida |
| 3 | `ssh "$TARGET_HOST" "cd '$REMOTE_PROJECT_DIR' && docker compose config -q"` | 0 | Compose válido |
| 4 | `ssh "$TARGET_HOST" "cd '$REMOTE_PROJECT_DIR' && docker compose up -d nginx"` | 0 | nginx recriado e healthy |
| 5 | `ssh "$TARGET_HOST" 'docker exec nginx nginx -t'` | 0 | configuração válida |
| 6 | `curl -ksS -o /dev/null -w '%{http_code} %{redirect_url}\n' "https://$DAVY_JONES_LAN_IP/"` | 0 | portal respondeu 200 |
| 7 | `ssh "$TARGET_HOST" "cd '$REMOTE_PROJECT_DIR' && bash tests/verify_stack.sh"` | 0 | 288 PASS, 0 FAIL, 0 WARN |

## Efeitos colaterais

- Nginx foi recriado para aplicar o bind-mount somente leitura do portal.
- Open WebUI, Grafana, Paperclip e Hermes Dashboard permaneceram acessíveis.
- Nenhum segredo foi lido ou registrado.
