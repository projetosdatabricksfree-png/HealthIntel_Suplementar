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
- **`healthintel_dbt/`**: dbt transformation engine. Medallion flow: `bruto_ans` (bronze) → `stg_ans` (silver views) → `int_ans` (ephemeral intermediates) → `nucleo_ans` (gold marts) → `api_ans` (gold API) → `consumo_ans` (client delivery). Fase 5 adds parallel layers: `quality_ans` (DQ models), `mdm_ans` (master data).

**Key flows:**
- **Ingest**: DAG downloads file → validate layout in MongoDB → load `bruto_ans` → record `plataforma.job`.
- **Transform**: dbt staging normalizes, dbt tests validate, dbt marts aggregate, post-hooks create physical indices in `api_ans`.
- **Serve**: FastAPI queries `api_ans` only, logs to `plataforma.log_uso`, caches in Redis.
- **Client delivery**: `consumo_ans` schema serves desnormalized Gold tables directly to client BI tools (Power BI, Metabase, psql). Role `healthintel_cliente_reader` (NOLOGIN) is granted per-client user with no access to internal schemas. Refreshed via `dag_dbt_consumo_refresh.py` / `make consumo-refresh`.

**Data schemas:**
- `bruto_ans`: Raw bronze tables (CADOP, SIB, IGR, NIP, RN623, IDSS, etc.). RANGE partitioned by competência or trimestre.
- `stg_ans`: Staging views. Casting, normalization, `registro_ans` standardization.
- `int_ans`: Ephemeral intermediates (not materialized). Enrich, join, derive metrics.
- `quality_ans`: Fase 5 — Document quality models (`dq_*`). Validates CNPJ-DV, CNES-DV and other regulatory document checks. Tagged `quality`.
- `mdm_ans`: Fase 5 — Public Master Data records. `mdm_operadora_master`, `mdm_estabelecimento_master`, `mdm_prestador_master` plus `xref_*_origem` crosswalks and `*_exception` lists. Tagged `mdm`.
- `nucleo_ans`: Gold mart tables (facts: `fat_*`, dimensions: `dim_*`). Incremental or full refresh per model.
- `api_ans`: Gold API tables. Denormalized, indexed, read-only from FastAPI. Includes `api_premium_*` (Fase 5) — exclusive read surface for premium endpoints.
- `consumo_ans`: Client delivery tables. Desnormalized Gold for direct BI/analyst access. Role `healthintel_cliente_reader`; each client gets individual LOGIN user. No access to internal schemas.
- `consumo_premium_ans` (Fase 5, planned Sprint 31): Premium SQL-direct surface. Role `healthintel_premium_reader`. Cannot grant `healthintel_cliente_reader` access to this schema.
- `bruto_cliente`, `stg_cliente`, `mdm_privado` (Fase 5, planned Sprint 30): Per-tenant private ingestion (contrato/subfatura) — isolated by tenant.
- `plataforma`: Operational metadata (clients, API keys, billing, job logs, dataset versions, `lote_ingestao`). Fase 7 adds: `politica_dataset` (load class/strategy per dataset — 5 classes: `grande_temporal`, `pequena_full_ate_5gb`, `referencia_versionada`, `snapshot_atual`, `historico_sob_demanda`), `retencao_particao_log` (partition retention audit, triggered by default partition inserts), `ingestao_janela_decisao` (per-competência load decision audit: `carregado`/`ignorado_fora_janela`/`rejeitado_historico_sem_flag`). Planned: `cliente_dataset_acesso`, `solicitacao_historico`, `versao_dataset`, `backup_execucao`. SQL functions (Sprint 35): `calcular_janela_carga_anual`, `criar_particao_anual_competencia`, `preparar_particoes_janela_atual`.

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
| **Seed CNES data** | `make demo-data-cnes` |
| **Seed TISS data** | `make demo-data-tiss` |
| **Seed SIB data** | `make demo-data-sib` |
| **Seed CADOP data** | `make demo-data-cadop` |
| **Seed all datasets** | `make seed-dados-completos` |
| **Bootstrap regulatorio layouts** | `make bootstrap-regulatorio-layouts` |
| **Bootstrap rede layouts** | `make bootstrap-rede-layouts` |
| **Bootstrap CNES layouts** | `make bootstrap-cnes-layouts` |
| **Bootstrap TISS layouts** | `make bootstrap-tiss-layouts` |
| **Bootstrap SIB layouts** | `make bootstrap-sib-layouts` |
| **Bootstrap CADOP layouts** | `make bootstrap-cadop-layouts` |
| **Seed ref seeds** | `make dbt-seed-ref` (ref_tuss, ref_rol_procedimento) |
| **Close billing cycle** | `make billing-close REF=YYYYMM` |
| **Refresh consumo layer** | `make consumo-refresh` (runs tag:consumo models + tests) |
| **Smoke test (piloto)** | `make smoke` |
| **Smoke test (rede)** | `make smoke-rede` |
| **Smoke test (CNES)** | `make smoke-cnes` |
| **Smoke test (TISS)** | `make smoke-tiss` |
| **Smoke test (Prata)** | `make smoke-prata` |
| **Smoke test (SIB)** | `make smoke-sib` |
| **Smoke test (CADOP)** | `make smoke-cadop` |
| **Smoke test (consumo)** | `make smoke-consumo` |
| **Smoke test (premium)** | `make smoke-premium` |
| **Smoke test (ingestão real)** | `make smoke-ingestao-real` |
| **Smoke test (restore)** | `make smoke-restore` (Fase 7 — validate restore+PITR) |
| **Smoke test (janela carga SIB)** | `make smoke-janela-carga-sib` (Fase 7 — validate dynamic load window) |
| **Hardgate sem ano hardcoded** | `make hardgate-sem-ano-hardcoded-janelacarga` (asserts no hardcoded year in load window logic) |
| **Load test** | `make load-test` (Locust) |
| **Dev API server** | `make api-dev` (auto-reload on :8000) |
| **Dev layout service** | `make layout-dev` (auto-reload on :8001) |
| **Full CI simulation** | `make ci-local` |
| **Airflow connections** | `make airflow-setup` |
| **Validate all DAGs parse** | `make dag-parse` (lists `DagBag.import_errors`) |
| **Test single DAG** | `make dag-test DAG=dag_name` |
| **Test all DAGs** | `make dag-test-all` |
| **Run real SIB ingestion** | `make dag-run-real-sib UFS=AC COMPETENCIA=YYYYMM` |
| **Run real CADOP ingestion** | `make dag-run-real-cadop COMPETENCIA=YYYYMM` |
| **ELT discover** | `make elt-discover` (catalog ANS datasets) |
| **ELT extract** | `make elt-extract` (download raw ANS files) |
| **ELT load** | `make elt-load` (load to bruto_ans) |
| **ELT full pipeline** | `make elt-all` |
| **ELT status** | `make elt-status` |
| **ELT transform all** | `make elt-transform-all` |
| **ELT validate all** | `make elt-validate-all` |

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
- `app/routers/`: `operadora`, `mercado`, `ranking`, `regulatorio`, `regulatorio_v2`, `financeiro`, `rede`, `cnes`, `tiss`, `meta`, `admin_billing`, `admin_layout`, `bronze`, `prata`, `premium` (Fase 5 — `/v1/premium/*` endpoints reading `api_ans.api_premium_*`).
- `app/schemas/`: Pydantic v2 request/response models per endpoint group.
- `app/services/`: Async query builders (never direct dbt model access, only `api_ans`). Key services: `operadora`, `mercado`, `ranking`, `regulatorio`, `regulatorio_v2`, `financeiro_v2`, `rede`, `cnes`, `tiss`, `bronze`, `prata`, `premium`, `score_v3`, `billing`, `layout_admin`, `meta`, `uso`.
- `app/dependencia.py`: Dependency injection (`validar_chave`, `verificar_plano`, `verificar_camada`). **Phase 3:** `verificar_camada(camada: str)` checks `plataforma.plano.camadas_permitidas[]` — blocks access if plan does not include the requested layer. Camadas válidas: `bronze`, `prata`, `premium`.
- `tests/unit/`: Health checks, auth, schema validation.
- `tests/integration/`: End-to-end endpoint tests against live PostgreSQL.

### Ingestao (`ingestao/`)

- `dags/`: Individual `dag_ingest_{dataset}.py` per dataset (SIB, CADOP, IGR, NIP, RN623, TISS, CNES, DIOPS, FIP, Glosa, VDA, Rede Assistencial, Regime Especial, Portabilidade, Prudencial, Taxa Resolutividade). Also: `dag_mestre_mensal.py` (main monthly orchestrator), `dag_anual_idss.py`, `dag_criar_particao_mensal.py`, `dag_dbt_freshness.py`, `dag_dbt_consumo_refresh.py`, `dag_registrar_versao.py`, `dag_elt_ans_catalogo.py`.
- `app/`: Operators, hooks, utilities (file downloads, layout validation, load jobs).
- `tests/`: DAG parsing, mock operator tests.

### dbt (`healthintel_dbt/`)

- `models/staging/`: Views. Casting, normalizing, one-to-one source mapping.
- `models/intermediate/`: Ephemeral (not materialized). Joins, aggregations, preparation.
- `models/marts/dimensao/`: Dimension tables (dim_operadora_atual, dim_competencia, dim_localidade).
- `models/marts/fato/`: Fact tables (`fat_*`) and Gold BI marts (`mart_*`). Incremental merge with `unique_key` or full refresh. Gold marts (`mart_operadora_360`, `mart_mercado_municipio`, `mart_score_operadora`, `mart_rede_assistencial`, `mart_regulatorio_operadora`, `mart_tiss_procedimento`) live here, schema `nucleo_ans`.
- `models/marts/derivado/`: Reserved directory (currently empty; derived models live in `fato/`).
- `models/api/`: Denormalized API tables. All have `post-hook: criar_indices` macro.
- `models/api/bronze/`: Thin views over `bruto_ans` (11 datasets). Redis cache DISABLED — data mutable until lote closes.
- `models/api/prata/`: Tables from `stg_ans` + `int_ans` (17 models including CNES and TISS). Redis TTL 300s.
- `models/consumo/`: Client delivery tables in `consumo_ans` schema (8 models, `tag: consumo`). Materialized as `table`. No API layer — direct BI access. Refreshed by `dag_dbt_consumo_refresh.py`.
- `models/quality/`: Fase 5 — Document quality validators (`dq_*`). Schema `quality_ans`, `tag: quality`. Includes `dq_cadop_documento`, `dq_cnes_documento`, `dq_operadora_documento`, `dq_prestador_documento`, `audit_operadora_razao_social_divergente_cadop`.
- `models/mdm/`: Fase 5 — Public MDM under `mdm_ans` schema, `tag: mdm`. Subdirs `operadora/`, `prestador/`, `estabelecimento/`. Each has `mdm_<entity>_master` (golden record, hash-deterministic key, status `ATIVO|QUARANTENA|REPROVADO|DESATIVADO`), `mdm_<entity>_exception` and `xref_<entity>_origem`.
- `tests/`: dbt generic tests, singular SQL assertions (assert_*.sql).
- `macros/`: `normalizar_registro_ans`, `competencia_para_data`, `competencia_para_trimestre`, `trimestre_para_competencia`, `calcular_hhi`, `normalizar_0_100`, `versao_metodologia_idss`, `classificar_rating_regulatorio`, `taxa_aprovacao_dataset`, `criar_indices`, `criar_indice_api`, `generate_schema_name`.
- `seeds/ref_*`: Dimension data (ref_uf, ref_municipio_ibge, ref_competencia, ref_modalidade).
- `_sources.yml`: Source declarations with freshness checks (warn after N days).
- `_*.yml`: Documentation (staging, intermediate, dimension, fato, api, exposures).

### Frontend Portal (`frontend/healthintel_frontend_portal/healthintel_frontend/frontend/`)

- React 19 + Vite 7 + TypeScript SPA. Commercial landing + developer portal.
- Auth model: `X-API-Key` header (no email/password). Key stored in `localStorage`.
- Dev server: `npm run dev` (port 5173). Build: `npm run build`. Preview: `npm run preview` (port 4173).
- Vite dev proxy expects backend at `http://localhost:8080`. Override with `VITE_API_BASE_URL` in `.env`.
- Backend CORS must include `http://localhost:5173` when calling API directly.
- Status pages hit `/saude` and `/prontidao`. Playground exercises any router using the user's key.

### Shared Utilities (`shared/`)

- Database utilities, logging (structlog), common schemas.

### Scripts (`scripts/`)

- `bootstrap_layout_registry_*.py`: Initialize MongoDB layout collections.
- `seed_demo_*.py`: Load demo data.
- `smoke_*.py`: End-to-end validation scripts.
- `run_load_test.sh`: Locust perf test.
- `admin/provisionar_cliente_postgres.py`: Provision new client — creates PostgreSQL login role, grants `healthintel_cliente_reader`, configures `consumo_ans` access.
- `elt_*.py`: ANS catalog discovery, raw file extraction, and load scripts (used by `make elt-*`).

---

## Workflow Rules

### Adding an Endpoint

1. Create router in `api/app/routers/{topic}.py`.
2. Define schema in `api/app/schemas/{topic}.py` (Pydantic v2).
3. Query only `api_ans` models via `app/services/{topic}.py`.
4. Use dependency injection: `validar_chave`, `verificar_plano`. For Bronze/Prata endpoints also `verificar_camada('bronze'|'prata')`.
5. Return envelope: `{dados: [...], meta: {competencia_referencia, versao_dataset, total, pagina}}`. Bronze envelope adds `aviso_qualidade`. Prata envelope adds `qualidade: {taxa_aprovacao, registros_quarentena}`.
6. Add test in `api/tests/integration/test_{topic}.py`.

### Adding a dbt Model

1. **Staging (view)**: `models/staging/stg_{source}.sql` — normalize, cast, one-to-one.
2. **Intermediate (ephemeral)**: `models/intermediate/int_{concept}.sql` — join, derive, prepare.
3. **Fact/Dimension (table)**: `models/marts/{dimensao|fato}/{model}.sql`.
   - Set `materialized: table` and `schema: nucleo_ans` (or api_ans for API layer, consumo_ans for client delivery).
   - For incremental: `incremental_merge`, `unique_key: [...]`, reprocess last N competencies.
   - For API: add `post_hook: criar_indices(...)`.
4. **Consumo (table)**: `models/consumo/consumo_{concept}.sql`. Schema `consumo_ans`, tag `consumo`. Readable column names — no internal prefixes.
5. Document in matching `_{tipo}.yml`.
6. Add tests: `tests/assert_*.sql` or `generic_tests` in YAML.
7. Tag with `tag: staging`, `tag: intermediario`, `tag: fato`, `tag: api`, or `tag: consumo`.

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
| **PostgreSQL** | 5432 | — | Schemas: bruto_ans, stg_ans, int_ans, quality_ans, mdm_ans, nucleo_ans, api_ans, consumo_ans, plataforma, alembic. Planejados Fase 5: bruto_cliente, stg_cliente, mdm_privado, consumo_premium_ans |
| **MongoDB** | 27017 (27018 external) | — | DB: healthintel_layout, Collections: layout, layout_versao, etc. |
| **Redis** | 6379 | — | Cache for API key validation (TTL 60s) |

---

## Important Conventions

- **Surrogate keys**: All facts use `operadora_id` (FK to `snap_operadora.id`), not raw `registro_ans`. `snap_operadora` is SCD Type 2 dimension.
- **Competência format**: YYYYMM (e.g., 202504 = May 2025). Use macro `competencia_para_data()` for date conversion.
- **Registro ANS**: Always normalized to exactly 6 digits (with leading zeros). Use macro `normalizar_registro_ans()`.
- **API response**: Always wrap in envelope. Do NOT return raw JSON.
- **Incremental models**: Reprocess last 3–4 competencies per run (ANS often republishes corrections).
- **Partition strategy**: RANGE by competência or trimestre; no LIST or HASH. SIB tables (`bruto_ans.sib_beneficiario_operadora`, `bruto_ans.sib_beneficiario_municipio`) migrated in Sprint 35 to **annual** partitions (`_YYYY` suffix, `FOR VALUES FROM (YYYY01) TO ((YYYY+1)01)`). All other tables remain monthly. Never create monthly SIB partitions.
- **Load window**: Fase 7 enforces dynamic load window via `plataforma.calcular_janela_carga_anual(ANS_ANOS_CARGA_HOT)`. Default `ANS_ANOS_CARGA_HOT=2` (current year + prior year). Helper: `ingestao/app/janela_carga.py` — `obter_janela(dataset_codigo)` returns `JanelaCarga(competencia_minima, competencia_maxima_exclusiva, ano_inicial, ano_final, ano_preparado)`. Competências outside the window are logged to `plataforma.ingestao_janela_decisao` with `acao='ignorado_fora_janela'`, never silently dropped. Hardgate `tests/hardgates/assert_sem_ano_hardcoded_janela.sh` enforces no hardcoded year in production load logic.
- **Freshness**: Entry in `_sources.yml` required for every bronze table.
- **venv isolation**: Each service (`api/`, `healthintel_dbt/`, `ingestao/`) has isolated `.venv` if running outside containers.
- **Layer access control**: `plataforma.plano` has `camadas_permitidas TEXT[]`. Use `verificar_camada('bronze'|'prata')` dependency for Bronze/Prata endpoints. Gold endpoints use existing `verificar_plano`.
- **Rate limit multipliers**: `/v1/bronze` routes consume 3× bucket; `/v1/prata` routes consume 2×; `/v1` (gold) consumes 1×.
- **Bronze cache**: Redis cache DISABLED for Bronze API routes (data is mutable until lote closes).
- **Prata cache**: Redis TTL 300s (5 min) for Prata API routes.
- **Quarantine tables**: Each dataset has a `bruto_ans.*_quarentena` table. Records failing staging validation go there, never into served data. Rejection reason, failed rule and lote preserved.
- **Score v3**: `versao_metodologia = 'v3.0'`. Five components: core(0.25) + regulatorio(0.25) + financeiro(0.20) + rede(0.20) + estrutural(0.10). Fallback to score_v2 with `componente_estimado = true` when a component is missing. Service: `api/app/services/score_v3.py`.

---

## Sprint Structure

**Fase 1 (Sprints 01–12): CONCLUÍDA** — baseline v1.0.0 taggeada.
**Fase 2 (Sprints 13–14): CONCLUÍDA** — CNES + TISS implementados.
**Fase 3 (Sprints 15–20): CONCLUÍDA** — baseline v2.0.0 taggeada.
**Fase 4 (Sprints 21–25): CONCLUÍDA** — v3.0.0 taggeada. Prata completa, ingestão real SIB/CADOP, Gold marts BI, consumo_ans, qualidade v3.
**Fase 5 (Sprints 26–33): CONCLUÍDA (Sprint 33 pendente tag)** — Qualidade documental, MDM público/privado, premium. Tag final prevista `v3.8.0-gov`.
**Fase 6 (Sprints 14–21 do tracking comercial): BACKLOG** — Entrega ao cliente / operação comercial. Aditiva e operacional. Tag final prevista `v4.0.0`.
**Fase 7 (Sprints 34–40): EM ANDAMENTO** — Storage dinâmico, particionamento anual, retenção e backup. Aditiva. Tag final prevista `v4.2.0-dataops`.

### Fase 2 (entregue)
- **Sprint 13**: CNES — bronze, `stg_cnes_estabelecimento`, `fat_cnes_estabelecimento_municipio`, `fat_cnes_rede_gap_municipio`, `api_cnes_municipio`, `api_cnes_rede_gap`. Router/service: `cnes`.
- **Sprint 14**: TISS — bronze, `stg_tiss_procedimento`, `fat_tiss_procedimento_operadora`, `fat_sinistralidade_procedimento`, `api_tiss_operadora_trimestral`, `api_sinistralidade_procedimento`. Router/service: `tiss`.

### Fase 3 (entregue)
- **Sprint 15**: Governança — hash bronze, quarentena semântica, quality gates, freshness SLO, macro `taxa_aprovacao_dataset`.
- **Sprint 16**: Bronze API — 11 modelos em `api/bronze/`, router `bronze`, plano `enterprise_tecnico`, `verificar_camada('bronze')`.
- **Sprint 17**: Prata API — modelos em `api/prata/`, router `prata`, plano `analitico`, `verificar_camada('prata')`, envelope `qualidade.taxa_aprovacao`.
- **Sprint 19**: Score v3 — `fat_score_v3_operadora_mensal`, `api_score_v3_operadora_mensal`, `api_ranking_composto_mensal`, `score_v3.py` service.
- **Sprint 20**: v2.0.0 tag, 5 tiers com `camadas_permitidas`, billing por camada.

### Fase 4 (entregue — v3.0.0)
- **Sprint 21**: Prata completa — CNES/TISS na Prata (17 modelos total), cobertura de testes de integração, `make smoke-prata`.
- **Sprint 22**: Ingestão real — SIB e CADOP com DAGs individuais, `dag_ingest_sib.py` / `dag_ingest_cadop.py`, `make smoke-sib` / `make smoke-cadop`.
- **Sprint 23**: Gold marts BI — `mart_operadora_360`, `mart_mercado_municipio`, `mart_score_operadora`, `mart_rede_assistencial`, `mart_regulatorio_operadora` em `nucleo_ans`.
- **Sprint 24**: consumo_ans — schema `consumo_ans`, 8 modelos desnormalizados, role `healthintel_cliente_reader`, `dag_dbt_consumo_refresh.py`, `make consumo-refresh` / `make smoke-consumo`.
- **Sprint 25**: Qualidade v3 / catálogo — freshness SLO dashboard, catálogo atualizado.

### Fase 5 (em andamento)
- **Sprint 26 (CONCLUÍDA)**: Baseline `v3.0.0` congelado. Documentos: `baseline_hardgate_fase4.md`, `matriz_lacunas_produto.md`, `padrao_nomes_fase5.md`, `governanca_minima_fase5.md`. Sem código.
- **Sprint 27 (CONCLUÍDA)**: Qualidade documental — modelos `dq_*` em `quality_ans`, hardgates de validação documental (CNPJ-DV, etc.) com sinal `warn`.
- **Sprint 28 (CONCLUÍDA)**: Validação determinística CNPJ offline.
- **Sprint 29 (CONCLUÍDA)**: MDM público — `mdm_operadora_master`, `mdm_estabelecimento_master`, `mdm_prestador_master` em `mdm_ans` com `xref_*_origem` e `*_exception`. Tag de release move-se para o final da Fase 5.
- **Sprint 30 (CONCLUÍDA)**: MDM contrato/subfatura — entrada privada por tenant (`bruto_cliente`, `stg_cliente`, `mdm_privado`). Bootstrap `028_fase5_mdm_privado_rls.sql` com RLS por `app.tenant_id`, hashes determinísticos `md5(text)`, 8 modelos `mdm_privado` + 2 staging cliente, 10 testes singulares + 23 testes YAML. Hard gates V1–V10 verdes.
- **Sprint 31 (CONCLUÍDA)**: Produtos premium em SQL direto — `consumo_premium_ans` + `api_ans.api_premium_*`.
- **Sprint 32 (CONCLUÍDA)**: Endpoints `/v1/premium/*`, smoke e hardgate da Fase 5. 9 rotas premium, schemas completos, tenant obrigatório em rotas privadas, smoke 14 cenários, testes de integração 12 cenários, regressão Fase 5.
- **Sprint 33 (backlog)**: Governança documental formal final, release `v3.8.0-gov`.

### Fase 7 (em andamento — v4.2.0-dataops)
- **Sprint 34 (CONCLUÍDA)**: Política dinâmica de carga — `plataforma.politica_dataset` criada via `029_fase7_politica_dataset.sql`; 5 classes de dataset classificadas; doc `docs/arquitetura/politica_carga_dataset.md`.
- **Sprint 35 (implementada localmente)**: Particionamento anual SIB — 3 funções novas (`calcular_janela_carga_anual`, `criar_particao_anual_competencia`, `preparar_particoes_janela_atual`) via `030_fase7_particionamento_anual.sql`; `bruto_ans.sib_beneficiario_operadora` e `sib_beneficiario_municipio` migrados para partições anuais `_YYYY`; `plataforma.retencao_particao_log` para auditoria de default partition; doc `docs/arquitetura/particionamento_anual_postgres.md`.
- **Sprint 36 (implementada localmente)**: Janela dinâmica de ingestão — `ingestao/app/janela_carga.py` com `JanelaCarga` dataclass; `ANS_ANOS_CARGA_HOT=2` via `.env`/Airflow Variable; `plataforma.ingestao_janela_decisao` via `031_fase7_janela_carga.sql`; módulos SIB filtram por janela; hardgate `tests/hardgates/assert_sem_ano_hardcoded_janela.sh`; smoke `make smoke-janela-carga-sib`.
- **Sprint 37 (backlog)**: Última versão vigente TUSS/prestadores.
- **Sprint 38 (backlog)**: Histórico sob demanda por cliente (`dag_historico_sob_demanda.py`).
- **Sprint 39 (backlog)**: Backup pgBackRest — full diário, diferencial 4×/dia, WAL archive, `plataforma.backup_execucao`.
- **Sprint 40 (backlog)**: Restore + PITR + `smoke-restore` + release `v4.2.0-dataops`.

**Regra-mãe da Fase 7**: aditiva e não destrutiva. Nenhum modelo dbt, contrato de API, DAG aprovada, coluna `competencia` ou tabela-mãe `bruto_ans.sib_*` pode ser alterada. Toda lógica nova entra em artefato novo (bootstrap SQL numerado, helper Python novo, documento novo). Nenhum ano hardcoded em lógica produtiva de janela. Histórico completo só pode ser carregado pela DAG da Sprint 38.

**Regra-mãe da Fase 5**: aditiva. Modelos `stg_*`, `int_*`, `fat_*`, `mart_*`, `api_*`, `consumo_*` do baseline `v3.0.0` não podem ser reescritos, renomeados, nem ter semântica alterada. FastAPI premium **nunca** lê `consumo_premium_ans`, `mdm_ans`, `mdm_privado`, `quality_ans`, `bruto_cliente`, `stg_cliente` ou `enrichment` diretamente — só `api_ans.api_premium_*`. Proibido: Serpro, Receita online, BrasilAPI, enrichment, enrich-cnpj, requests externos.

### Fase 6 (backlog — operação comercial)
- Sprints 14–21 (numeração do tracking comercial). Cobre infraestrutura/runtime, API de produção, orquestração e freshness, observabilidade SLA/SLO, segurança LGPD/tenant/billing, onboarding e go-live (`v4.0.0`).
- **Regra-mãe da Fase 6**: aditiva e operacional. Não altera lógica de modelos, não renomeia tabelas, não muda contratos de endpoints existentes.

Sprint docs: `docs/sprints/fase{2,3,4,5,6}/`. HIS-*.* stories por sprint. Runbooks operacionais: `docs/runbooks/` (ingestão real, aprovação de layout, reprocessamento, incidente de pipeline, novo cliente enterprise, versionamento de layout).

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
