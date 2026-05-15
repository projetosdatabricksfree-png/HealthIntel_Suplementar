# Smoke API MVP Comercial - Sprint 43

Data: 2026-05-13 22:38 Europe/Berlin

## Resultado

| Check | Resultado |
| --- | --- |
| API principal `/saude` | OK - `{"status":"ok"}` |
| API principal `/prontidao` | 401 esperado sem token interno; API respondeu com erro estruturado |
| Layout registry `/saude` | OK em validacao anterior da VPS |
| Containers principais | Up; Airflow scheduler/webserver e Postgres healthy |
| Workload em andamento | `dag_ingest_rede_prestadores` e `dag_elt_ans_catalogo` running |

## Observacoes

- Nao foi exposta API key nas evidencias.
- Smoke autenticado dos endpoints comerciais fica pendente ate uso de token valido.
- A API de prontidao exigir token interno e aceitavel para hardening; nao foi tratada como falha de saude publica.

