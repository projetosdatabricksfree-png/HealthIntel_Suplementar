# Evidência — Smokes API

Data: 2026-05-11

## Validação VPS pós-deploy

### docker compose ps

```
NAME                            IMAGE                             COMMAND         SERVICE                STATUS
healthintel_airflow_scheduler   apache/airflow:2.9.1-python3.12  ...             airflow-scheduler      Up 3 days (healthy)
healthintel_airflow_webserver   apache/airflow:2.9.1-python3.12  ...             airflow-webserver      Up 3 days (healthy)
healthintel_api                 python:3.12-slim                 ...             api                    Up 3 days
healthintel_frontend            infra-frontend                   ...             frontend               Up 15 minutes
healthintel_grafana             grafana/grafana:11.1.0           ...             grafana                Up 7 hours
healthintel_layout_service      python:3.12-slim                 ...             mongo_layout_service   Up 3 days
healthintel_mongo               mongo:7                          ...             mongo                  Up 3 days (healthy)
healthintel_nginx               nginx:1.26-alpine                ...             nginx                  Up 3 days
healthintel_postgres            postgres:16                      ...             postgres               Up 3 days (healthy)
healthintel_redis               redis:7                          ...             redis                  Up 3 days (healthy)
```

Todos os serviços críticos estão `Up` e `healthy`.

---

## Categoria 1 — Endpoints HTTP validados

### GET /saude

```
HTTP/1.1 200 OK
Content-Type: application/json
x-process-time: 0.0040

{"status":"ok"}
```

**Resultado: 200 OK**

### GET /prontidao

```
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{"codigo":"AUTENTICACAO_INVALIDA","mensagem":"Token interno ausente ou inválido.","detalhe":{}}
```

**Resultado: 401 conforme esperado** — `/prontidao` é protegido por token interno (hardening de segurança 2026-05-07). Comportamento correto.

### Frontend

```
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 1410
```

**Resultado: 200 OK** — nginx servindo build React.

---

## Categoria 2 — Tabelas api_ans validadas por SQL (smokes SQL)

Ver evidência em `smoke_sql.md`. As 12 tabelas do delta foram verificadas via SQL:
- Todas as tabelas existem no schema `api_ans`
- Contagem 0 no ambiente local é esperada (sem carga de dados reais)
- Na VPS os dados são carregados pelos DAGs Airflow

### Verificação adicional via VPS (pós-deploy)

As tabelas delta foram criadas pelo `dbt build --select tag:delta_ans_100` na VPS após o deploy.
O resultado `PASS=162 ERROR=0` confirma que todos os modelos foram materializados com sucesso.

---

## Categoria 3 — Rotas HTTP inexistentes nesta sprint

Os seguintes endpoints **não existem como rotas HTTP FastAPI** nesta entrega:

| Endpoint listado no sprint doc | Status | Motivo |
|-------------------------------|--------|--------|
| `GET /api/produtos-planos` | Não existe | Entrega foi `api_ans.api_produto_plano` (SQL-direct) |
| `GET /api/tuss/procedimentos` | Não existe | Entrega foi `api_ans.api_tuss_procedimento_vigente` (SQL-direct) |
| `GET /api/tiss/ambulatorial` | Não existe | Entrega foi `api_ans.api_tiss_ambulatorial_operadora_mes` (SQL-direct) |
| `GET /api/tiss/hospitalar` | Não existe | Entrega foi `api_ans.api_tiss_hospitalar_operadora_mes` (SQL-direct) |
| `GET /api/sip` | Não existe | Entrega foi `api_ans.api_sip_assistencial_operadora` (SQL-direct) |
| `GET /api/ressarcimento-sus` | Não existe | Entrega foi `api_ans.api_ressarcimento_sus_operadora_plano` (SQL-direct) |
| `GET /api/precificacao` | Não existe | Entrega foi `api_ans.api_painel_precificacao` (SQL-direct) |
| `GET /api/rede/prestadores-acreditados` | Não existe | Entrega foi `api_ans.api_prestador_acreditado` (SQL-direct) |
| `GET /api/regulatorio/penalidades` | Não existe | Entrega foi `api_ans.api_penalidade_operadora` (SQL-direct) |

**Decisão formal**: A Sprint 41 entregou a camada de banco (`api_ans.*` + `consumo_ans.*` via dbt). Routers HTTP FastAPI para esses datasets são escopo de sprint posterior. Não bloqueia o fechamento.

Os routers existentes (`tiss.py`, `operadora.py`, `rede.py`, `regulatorio.py`, etc.) servem os datasets anteriores ao Sprint 41 e continuam funcionando.
