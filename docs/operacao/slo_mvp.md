# SLO MVP

## Escopo

SLOs dos endpoints centrais da API pública do HealthIntel Suplementar.

## Metas

| Endpoint | SLO | Observacao |
| --- | --- | --- |
| `GET /v1/operadoras` | p95 `<= 200 ms` | com cache aquecido |
| `GET /v1/operadoras/{registro_ans}` | p95 `<= 200 ms` | leitura em `api_ans` |
| `GET /v1/operadoras/{registro_ans}/score` | p95 `<= 220 ms` | leitura em `api_ans` |
| `GET /v1/meta/*` | p95 `<= 150 ms` | consultas leves de metadados |

## Disponibilidade

- Disponibilidade mensal mínima: `99,5%` por endpoint.
- Janela de erro 5xx: `<= 1%` por 15 minutos.

## Regras operacionais

- Queda de dependência critica retorna `503` em `/saude` e `/prontidao`.
- Limite por plano é reforcado no middleware de autenticacao e rate limit.
- Eventos de atraso, quarentena ou reprocessamento devem aparecer em `GET /v1/meta/pipeline`.
