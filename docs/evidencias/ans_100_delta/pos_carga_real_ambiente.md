# Evidência — Ambiente VPS Pós-Carga Real

**Timestamp:** 2026-05-13T11:28:52Z

**Commit:** 072c13c


## docker compose ps
```
NAME                            IMAGE                             COMMAND                  SERVICE                CREATED         STATUS                PORTS
healthintel_airflow_scheduler   apache/airflow:2.9.1-python3.12   "/usr/bin/dumb-init …"   airflow-scheduler      4 days ago      Up 4 days (healthy)   8080/tcp
healthintel_airflow_webserver   apache/airflow:2.9.1-python3.12   "/usr/bin/dumb-init …"   airflow-webserver      4 days ago      Up 4 days (healthy)   0.0.0.0:8088->8080/tcp, [::]:8088->8080/tcp
healthintel_api                 python:3.12-slim                  "bash -lc 'pip insta…"   api                    4 days ago      Up 4 days

healthintel_frontend            infra-frontend                    "/docker-entrypoint.…"   frontend               5 minutes ago   Up 5 minutes          0.0.0.0:5173->80/tcp, [::]:5173->80/tcp
healthintel_grafana             grafana/grafana:11.1.0            "/run.sh"                grafana                45 hours ago    Up 45 hours           127.0.0.1:3001->3000/tcp
healthintel_layout_service      python:3.12-slim                  "bash -lc 'pip insta…"   mongo_layout_service   4 days ago      Up 4 days

healthintel_mongo               mongo:7                           "docker-entrypoint.s…"   mongo                  4 days ago      Up 4 days (healthy)   0.0.0.0:27018->27017/tcp, [::]:27018->27017/tcp
healthintel_nginx               nginx:1.26-alpine                 "/docker-entrypoint.…"   nginx                  4 days ago      Up 4 days             80/tcp, 0.0.0.0:8080-8081->8080-8081/tcp, :::8080-8081->8080-8081/tcp
healthintel_node_exporter       prom/node-exporter:v1.8.1         "/bin/node_exporter …"   node-exporter          4 days ago      Up 4 days             127.0.0.1:9100->9100/tcp
healthintel_postgres            postgres:16                       "docker-entrypoint.s…"   postgres               4 days ago      Up 4 days (healthy)   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp
healthintel_prometheus          prom/prometheus:v2.53.0           "/bin/prometheus --c…"   prometheus             4 days ago      Up 4 days             127.0.0.1:9090->9090/tcp
healthintel_redis               redis:7                           "docker-entrypoint.s…"   redis                  4 days ago      Up 4 days (healthy)   0.0.0.0:6379->6379/tcp, :::6379->6379/tcp
```

## /saude (interno VPS)
```
HTTP/1.1 200 OK
Server: nginx
Date: Wed, 13 May 2026 11:29:02 GMT
Content-Type: application/json
Content-Length: 15
Connection: keep-alive
x-request-id: b428900be2f8fc8826e9c8665e915743
x-content-type-options: nosniff
x-frame-options: DENY
referrer-policy: strict-origin-when-cross-origin
permissions-policy: geolocation=(), microphone=(), camera=()
x-process-time: 0.0040
x-cache: miss
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
Strict-Transport-Security: max-age=31536000; includeSubDomains

{"status":"ok"}```

## /ready (interno VPS)
```
HTTP/1.1 404 Not Found
Server: nginx
Date: Wed, 13 May 2026 11:29:07 GMT
Content-Type: application/json
Content-Length: 22
Connection: keep-alive
x-request-id: 11209799a565bc12c926f21442015edd
x-content-type-options: nosniff
x-frame-options: DENY
referrer-policy: strict-origin-when-cross-origin
permissions-policy: geolocation=(), microphone=(), camera=()
x-process-time: 0.0030
x-cache: miss
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
Strict-Transport-Security: max-age=31536000; includeSubDomains

{"detail":"Not Found"}```

## Frontend (externo)
```
HTTP/2 200

accept-ranges: bytes
alt-svc: h3=":443"; ma=2592000
content-type: text/html
date: Wed, 13 May 2026 11:29:08 GMT
```
