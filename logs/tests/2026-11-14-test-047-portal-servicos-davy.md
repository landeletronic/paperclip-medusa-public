# Teste 047 — Portal de serviços do Davy Jones

## Metadados

| Campo | Valor |
|---|---|
| ID | 2026-11-14-test-047 |
| Data | 2026-11-14 |
| Hora | 17:50 -03:00 |
| Autor | Hermes Agent |
| Tipo | test |
| Status | passou |
| Ambiente | host Davy Jones / rede local privada |

## Casos

| Caso | Esperado | Obtido | Resultado |
|---|---|---|---|
| `GET http://<DAVY_JONES_LAN_IP>/` | redirect HTTPS raiz | 301 para `https://<DAVY_JONES_LAN_IP>/` | passou |
| `GET https://<DAVY_JONES_LAN_IP>/` | portal HTTP 200 | 200, quatro cards | passou |
| `GET /servicos` | redirect para raiz | 301 para `/` | passou |
| Open WebUI | HTTPS 3002 | 200 | passou |
| Grafana | HTTPS 3001 | 302 para login | passou |
| Paperclip | HTTP 3110 | 200 | passou |
| Hermes Dashboard | HTTP 9119 | 302 para login | passou |
| Nginx | configuração válida | `nginx -t` OK, healthy | passou |
| Oráculo completo | zero falhas | `PASS=288 FAIL=0 WARN=0` | passou |

## Evidência

A inspeção no navegador confirmou os destinos:

- `https://<DAVY_JONES_LAN_IP>:3002/`
- `https://<DAVY_JONES_LAN_IP>:3001/`
- `http://<DAVY_JONES_LAN_IP>:3110/`
- `http://<DAVY_JONES_LAN_IP>:9119/`
