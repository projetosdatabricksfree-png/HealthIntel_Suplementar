# HealthIntel Suplementar

Plataforma de engenharia de dados e API SaaS/DaaS para consumo de dados publicos da ANS com arquitetura medalhao, governanca de layout manual em MongoDB e exposicao via FastAPI.

## Estado atual do repositorio

- `docs/healthintel_suplementar_prd_final.md`: documento mestre do produto, arquitetura e backlog executavel.
- `api/`: scaffold da API publica e endpoints administrativos.
- `mongo_layout_service/`: scaffold do servico de governanca de layouts.
- `ingestao/`: base para DAGs Airflow e scripts de ingestao.
- `healthintel_dbt/`: projeto dbt para staging, intermediate, marts e camada `api_ans`.
- `infra/`: bootstrap local com Docker Compose, PostgreSQL, MongoDB, Redis, Airflow e Nginx.
- `mcp_server/`: legado orientado a Databricks/MCP, preservado fora da trilha principal do bootstrap atual.

## Como subir o scaffold local

1. Copie `.env.exemplo` para `.env` ou `.env.local` para definir as variaveis locais da stack.
2. Se houver conflito de porta local, ajuste `*_EXTERNAL_PORT` no arquivo de ambiente antes do `make up`.
3. Rode `make up`.
4. A API ficara disponivel em `http://localhost:8080`.
5. O servico de layout ficara disponivel em `http://localhost:8081`.
6. O Airflow ficara disponivel em `http://localhost:8088`.
7. Para evitar falha de bootstrap do Airflow, mantenha `AIRFLOW_FERNET_KEY` com um valor base64 valido; o template ja vem com uma chave local funcional.
8. Para preparar layouts regulatorios no MongoDB, rode `python scripts/bootstrap_layout_registry_regulatorio.py`.
9. Para popular dados locais de demonstracao, rode `make demo-data`.
10. Para publicar os modelos dbt ate a Sprint 07, rode `docker compose -f infra/docker-compose.yml run --rm --entrypoint sh dbt -lc "dbt deps && dbt build"`.
11. Para fechar billing local do ciclo, rode `make billing-close REF=2026-04`.
12. Para validar o pipeline local da Sprint 06/07, rode `make ci-local`.
13. Para smoke fim a fim, rode `python scripts/smoke_piloto.py`.
14. Para carga Locust local, rode `bash scripts/run_load_test.sh`.

## Credenciais locais de desenvolvimento

- Header: `X-API-Key`
- Valor local bootstrap: `hi_local_dev_2026_api_key`
- Valor administrativo local: `hi_local_admin_2026_api_key`

Essas chaves existem apenas para o ambiente local de desenvolvimento e sao armazenadas em hash em `plataforma.chave_api`.

## Endpoints principais

- `GET /saude`
- `GET /v1/operadoras`
- `GET /v1/operadoras/{registro_ans}`
- `GET /v1/operadoras/{registro_ans}/score`
- `GET /v1/operadoras/{registro_ans}/regulatorio`
- `GET /v1/regulatorio/rn623`
- `GET /v1/meta/dataset`
- `GET /v1/meta/versao`
- `GET /v1/meta/pipeline`
- `GET /admin/billing/resumo`
- `POST /admin/billing/fechar-ciclo`
- `POST /admin/billing/upgrade`
- `GET /admin/layouts`
- `POST /admin/layouts`
- `GET /prontidao`

## Objetivo desta entrega

Esta entrega nao implementa a plataforma completa. Ela cria a base do monorepo, os contratos iniciais e o PRD final para iniciar as 12 sprints sem reabrir decisoes estruturais.

## Operacao da Sprint 06

- `docs/runbooks/`: runbooks de subida, aprovacao de layout e reprocessamento.
- `docs/operacao/slo_sla.md`: metas operacionais e SLA por plano.
- `docs/operacao/baseline_capacidade.md`: baseline de carga e envelope por plano.
- `docs/operacao/piloto_controlado.md`: checklist de readiness do piloto.
