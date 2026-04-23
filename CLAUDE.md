# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Persona: CAVEMAN (Token Compression)

This repository uses the **Caveman** persona to maximize token efficiency and focus.

- **Style**: Silent Action / Caveman (Token Compression).
- **Rules**:
  - **Do not explain or respond in text unless absolutely necessary for a question.**
  - **Prioritize creating files, objects, and running commands directly.**
  - No greetings, no conversational filler, no apologies.
  - No summaries of actions; the file changes speak for themselves.
  - Omit repetitive explanations.
  - Just the task. Just the code.

---

## Architecture Overview

**HealthIntel Suplementar** is a medallion-architecture data platform for ANS (Brazilian health regulator) data analysis. Four-service monorepo design:

- **`api/`**: FastAPI service exposing data via REST. Reads PostgreSQL `api_ans` schema exclusively (never `nucleo_ans`). X-API-Key auth + Redis caching (TTL 60s). Response envelope: `{dados: [...], meta: {...}}`.
- **`mongo_layout_service/`**: MongoDB governance service. Stores file layout metadata, versioning, and bootstrap registries. Token-based auth.
- **`ingestao/`**: Airflow DAGs + Python scripts. Download ANS datasets, validate structure via MongoDB layouts, load to PostgreSQL `bruto_ans` (Bronze).
- **`healthintel_dbt/`**: dbt transformation engine. Medallion flow: `bruto_ans` (bronze) → `stg_ans` (silver views) → `int_ans` (ephemeral intermediates) → `nucleo_ans` (gold marts) → `api_ans` (gold API).

**Key flows:**
- **Ingest**: DAG downloads file → validate layout in MongoDB → load `bruto_ans` → record `plataforma.job`.
- **Transform**: dbt staging normalizes, dbt tests validate, dbt marts aggregate, post-hooks create physical indices in `api_ans`.
- **Serve**: FastAPI queries `api_ans` only, logs to `plataforma.log_uso`, caches in Redis.

**Data schemas:**
- `bruto_ans`: Raw bronze tables (CADOP, SIB, IGR, NIP, RN623, IDSS, etc.). RANGE partitioned by competência or trimestre.
- `stg_ans`: Staging views. Casting, normalization, `registro_ans` standardization.
- `int_ans`: Ephemeral intermediates (not materialized). Enrich, join, derive metrics.
- `nucleo_ans`: Gold mart tables (facts: `fat_*`, dimensions: `dim_*`). Incremental or full refresh per model.
- `api_ans`: Gold API tables. Denormalized, indexed, read-only from FastAPI.
- `plataforma`: Operational metadata (clients, API keys, billing, job logs, dataset versions).

---

## Development Commands

| Task | Command |
|------|---------|
| **Start services** | `make up` |
| **Stop services** | `make down` |
| **View logs** | `make logs` |
| **Service status** | `make ps` |
| **Python linting** | `make lint` (Ruff) |
| **SQL linting** | `make sql-lint` (SQLFluff) |
| **Run all tests** | `make test` (pytest) |
| **Run single test** | `pytest api/tests/unit/test_saude.py -v` |
| **dbt deps** | `make dbt-deps` |
| **dbt compile** | `make dbt-compile` |
| **dbt build** | `make dbt-build` |
| **dbt test** | `make dbt-test` |
| **dbt seed** | `make dbt-seed` |
| **Seed demo data** | `make demo-data` (core + regulatorio + idss) |
| **Seed rede data** | `make demo-data-rede` |
| **Bootstrap regulatorio layouts** | `make bootstrap-regulatorio-layouts` |
| **Bootstrap rede layouts** | `make bootstrap-rede-layouts` |
| **Close billing cycle** | `make billing-close REF=YYYYMM` |
| **Smoke test (piloto)** | `make smoke` |
| **Smoke test (rede)** | `make smoke-rede` |
| **Load test** | `make load-test` (Locust) |
| **Dev API server** | `make api-dev` (auto-reload on :8000) |
| **Dev layout service** | `make layout-dev` (auto-reload on :8001) |
| **Full CI simulation** | `make ci-local` |

---

## Key Files and Patterns

### Configuration & Environment

- `.env`: Service credentials (PostgreSQL, MongoDB, Redis, API tokens). Checked into git but contains default values safe for local dev.
- `pyproject.toml`: Python dependencies (pinned), pytest config, ruff config.
- `.pre-commit-config.yaml`: Git hooks (Ruff, SQLFluff, YAML/JSON checks).
- `infra/docker-compose.yml`: PostgreSQL 16, MongoDB 7, Redis 7, Airflow, Nginx.

### API Service (`api/`)

- `app/main.py`: FastAPI entrypoint. Health check, CORS, auth middleware.
- `app/core/`: Database pools, Redis client, config loading.
- `app/middleware/`: `autenticacao.py` (X-API-Key validation + Redis cache), `rate_limit.py` (SlowAPI), `hardening.py` (security headers), `log_requisicao.py` (request timing).
- `app/routers/`: `operadora`, `mercado`, `ranking`, `regulatorio`, `regulatorio_v2`, `financeiro`, `financeiro_v2`, `rede`, `meta`, `admin_billing`, `admin_layout`.
- `app/schemas/`: Pydantic v2 request/response models per endpoint group.
- `app/services/`: Async query builders (never direct dbt model access, only `api_ans`).
- `app/dependencia.py`: Dependency injection (validar_chave, verificar_plano).
- `tests/unit/`: Health checks, auth, schema validation.
- `tests/integration/`: End-to-end endpoint tests against live PostgreSQL.

### Ingestao (`ingestao/`)

- `dags/`: Airflow DAGs (dag_mestre_mensal, dag_trimestral, dag_anual_idss, etc.). Sub-DAG pattern for orchestration.
- `app/`: Operators, hooks, utilities (file downloads, layout validation, load jobs).
- `tests/`: DAG parsing, mock operator tests.

### dbt (`healthintel_dbt/`)

- `models/staging/`: Views. Casting, normalizing, one-to-one source mapping.
- `models/intermediate/`: Ephemeral (not materialized). Joins, aggregations, preparation.
- `models/marts/dimensao/`: Dimension tables (dim_operadora_atual, dim_competencia, dim_localidade).
- `models/marts/fato/`: Fact tables. Incremental merge with `unique_key` or full refresh.
- `models/marts/derivado/`: Derived score/index tables computed from facts (score, ranking, oportunidade).
- `models/api/`: Denormalized API tables. All have `post-hook: criar_indices` macro.
- `tests/`: dbt generic tests, singular SQL assertions (assert_*.sql).
- `macros/`: `normalizar_registro_ans`, `competencia_para_data`, `competencia_para_trimestre`, `trimestre_para_competencia`, `calcular_hhi`, `normalizar_0_100`, `versao_metodologia_idss`, `classificar_rating_regulatorio`, `criar_indices`, `criar_indice_api`, `generate_schema_name`.
- `seeds/ref_*`: Dimension data (ref_uf, ref_municipio_ibge, ref_competencia, ref_modalidade).
- `_sources.yml`: Source declarations with freshness checks (warn after N days).
- `_*.yml`: Documentation (staging, intermediate, dimension, fato, api, exposures).

### Shared Utilities (`shared/`)

- Database utilities, logging (structlog), common schemas.

### Scripts (`scripts/`)

- `bootstrap_layout_registry_*.py`: Initialize MongoDB layout collections.
- `seed_demo_*.py`: Load demo data.
- `smoke_*.py`: End-to-end validation scripts.
- `run_load_test.sh`: Locust perf test.

---

## Workflow Rules

### Adding an Endpoint

1. Create router in `api/app/routers/{topic}.py`.
2. Define schema in `api/app/schemas/{topic}.py` (Pydantic v2).
3. Query only `api_ans` models via `app/services/{topic}.py`.
4. Use dependency injection: `validar_chave`, `verificar_plano`.
5. Return envelope: `{dados: [...], meta: {competencia_referencia, versao_dataset, total, pagina}}`.
6. Add test in `api/tests/integration/test_{topic}.py`.

### Adding a dbt Model

1. **Staging (view)**: `models/staging/stg_{source}.sql` — normalize, cast, one-to-one.
2. **Intermediate (ephemeral)**: `models/intermediate/int_{concept}.sql` — join, derive, prepare.
3. **Fact/Dimension/Derived (table)**: `models/marts/{dimensao|fato|derivado}/{model}.sql`.
   - Set `materialized: table` and `schema: nucleo_ans` (or api_ans for API layer).
   - For incremental: `incremental_merge`, `unique_key: [...]`, reprocess last N competencies.
   - For API: add `post_hook: criar_indices(...)`.
4. Document in matching `_{tipo}.yml`.
5. Add tests: `tests/assert_*.sql` or `generic_tests` in YAML.
6. Tag with `tag: staging`, `tag: intermediario`, `tag: fato`, `tag: derivado`, or `tag: api`.

### Adding a DAG

1. Create `ingestao/dags/dag_{dataset}.py` (Airflow 2.9+, astronomer-cosmos).
2. Use sub-task pattern under dag_mestre_mensal or dag_trimestral.
3. Implement load operator: validate layout, insert/upsert to `bruto_ans`.
4. Record job metadata in `plataforma.job` (status, timestamps, dataset name).
5. Add freshness entry in `healthintel_dbt/models/staging/_sources.yml`.

### Testing

Test paths (from `pyproject.toml`): `api/tests/`, `ingestao/tests/`, `testes/`.

- **Unit**: `pytest api/tests/unit/` (API) or `pytest testes/unit/` (layout service).
- **Integration**: `pytest api/tests/integration/` — endpoints vs. live DB.
- **Regression**: `pytest testes/regressao/` — cross-phase endpoint regression suite.
- **Ingestao**: `pytest ingestao/tests/` — DAG parsing, mock operator tests.
- **dbt**: `dbt test` — generic tests + singular SQL assertions.
- **Smoke**: `make smoke` (piloto) or `make smoke-rede` — end-to-end validation.
- **Load**: `make load-test` — Locust perf baseline (`testes/load/locustfile.py`).

---

## Service Dependencies

| Service | Port | Depends | Notes |
|---------|------|---------|-------|
| **API** | 8000 | PostgreSQL, Redis, MongoDB (layout lookup) | Reads only `api_ans` |
| **Layout Service** | 8001 | MongoDB | Token-gated, no auth header |
| **Airflow** | 8088 | PostgreSQL, MongoDB (layout validation) | DAGs load from `ingestao/dags/` |
| **PostgreSQL** | 5432 | — | Schemas: bruto_ans, stg_ans, int_ans, nucleo_ans, api_ans, plataforma, alembic |
| **MongoDB** | 27017 (27018 external) | — | DB: healthintel_layout, Collections: layout, layout_versao, etc. |
| **Redis** | 6379 | — | Cache for API key validation (TTL 60s) |

---

## Important Conventions

- **Surrogate keys**: All facts use `operadora_id` (FK to `snap_operadora.id`), not raw `registro_ans`. `snap_operadora` is SCD Type 2 dimension.
- **Competência format**: YYYYMM (e.g., 202504 = May 2025). Use macro `competencia_para_data()` for date conversion.
- **Registro ANS**: Always normalized to exactly 6 digits (with leading zeros). Use macro `normalizar_registro_ans()`.
- **API response**: Always wrap in envelope. Do NOT return raw JSON.
- **Incremental models**: Reprocess last 3–4 competencies per run (ANS often republishes corrections).
- **Partition strategy**: RANGE by competência (monthly) or trimestre (quarterly); no LIST or HASH.
- **Freshness**: Entry in `_sources.yml` required for every bronze table.
- **venv isolation**: Each service (`api/`, `healthintel_dbt/`, `ingestao/`) has isolated `.venv` if running outside containers.

---

## Sprint Structure

Sprints 01–07 complete (MVP + regulatory base). Sprints 08–12 in progress:

- **Sprint 08**: Score regulatório, regime especial, prudencial, portabilidade.
- **Sprint 09**: DIOPS, FIP, harmonização financeira.
- **Sprint 10**: VDA, glosa, score v2.
- **Sprint 11**: Rede assistencial.
- **Sprint 12**: Vazios assistenciais, oportunidade v2, rollout enterprise.

Each sprint has: HIS-*.* stories, "Entregas esperadas" checklist, "Validação esperada" checklist.

---

## Debugging & Troubleshooting

- **dbt incremental merge fails**: Check `unique_key` uniqueness in last N competencies. Run `dbt build --full-refresh` to reset.
- **API latency spike**: Check Redis connection pool (`core/redis_client.py`), PostgreSQL slow query log, query plan via `EXPLAIN ANALYZE`.
- **Layout validation fails**: Verify CSV encoding, field count, and layout version in MongoDB (`mongo_layout_service` logs).
- **DAG timeout**: Check Airflow logs, worker resources, upstream dataset freshness.
- **Test failures in CI**: Run `make ci-local` locally first; check dbt compile errors, SQLFluff violations, pytest assertions.

---

## Useful SQL Queries

```sql
-- Check dataset freshness
SELECT dataset, MAX(_carregado_em) as ultima_carga FROM plataforma.job WHERE status = 'sucesso' GROUP BY dataset ORDER BY ultima_carga DESC;

-- List incompatible operadoras (regime especial)
SELECT registro_ans, COUNT(*) FROM fat_regime_especial_historico WHERE ativo = true GROUP BY registro_ans;

-- API query distribution
SELECT endpoint, COUNT(*) FROM plataforma.log_uso WHERE DATE(_criado_em) = CURRENT_DATE GROUP BY endpoint ORDER BY COUNT DESC;
```
