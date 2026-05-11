# Evidência — Ambiente VPS Pré-Execução (Sprint 42 Fase 2)

**Timestamp:** 2026-05-11T22:31:13Z
**Fase:** 1 — Validação de ambiente

## Containers

| Container | Status |
|---|---|
| healthintel_airflow_scheduler | Up 3 days (healthy) |
| healthintel_airflow_webserver | Up 3 days (healthy) |
| healthintel_api | Up 3 days |
| healthintel_frontend | Up 7 minutes |
| healthintel_grafana | Up 8 hours |
| healthintel_layout_service | Up 3 days |
| healthintel_mongo | Up 3 days (healthy) |
| healthintel_nginx | Up 3 days |
| healthintel_node_exporter | Up 3 days |
| healthintel_postgres | Up 3 days (healthy) |
| healthintel_prometheus | Up 3 days |
| healthintel_redis | Up 3 days (healthy) |

## API Health Check

```
HTTP/1.1 200 OK
Server: nginx
Date: Mon, 11 May 2026 22:31:13 GMT
Content-Type: application/json
Content-Length: 15
```

## Conclusão

✅ 12 containers ativos.
✅ postgres, mongo, redis, airflow-scheduler, airflow-webserver: healthy.
✅ API /saude: HTTP 200.
✅ Ambiente íntegro — prosseguir com DDL e bootstrap.
