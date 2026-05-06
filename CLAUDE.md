# CLAUDE.md

## Skills Obrigatórios

- → **token-economy** (`skills/token-economy/SKILL.md`) — gestão de tokens, seleção de modelo, uso de `/compact`, `/clear`, Plan Mode. **Aplicar automaticamente em toda sessão.**

### Skills temáticos HealthIntel (acionar quando o trabalho tocar a área)

- **healthintel-daas-governance** — qualquer mudança que afete identidade/posicionamento DaaS ou escopo do produto.
- **healthintel-ans-ingestion-bronze** — mexer em `ingestao/`, `bruto_ans`, layouts, DAGs ou fontes ANS.
- **healthintel-dbt-medallion-modeling** — modelos dbt, schemas (`stg_*` → `int_*` → `nucleo_ans` → `api_ans` → `consumo_ans`), tags e exposição.
- **healthintel-api-serving** — mudanças em `api/` (routers, schemas, services, deps, envelope `{dados, meta}`).
- **healthintel-data-quality-contracts** — testes dbt, contratos de tabela, `quality_ans`, validações regulatórias.
- **healthintel-observability-billing-ops** — `plataforma.log_uso`, `plataforma.job`, billing, alertas, métricas de uso.
- **healthintel-commercial-protection-security** — paginação, rate limit, auth, autorização por plano/camada, antiextração.
- **healthintel-sprint-release-hardgates** — fechar sprint, taggar release, hardgates, baseline imutável, `[x]` só após evidência.

## Architecture Overview

**HealthIntel Suplementar** — plataforma medallion de dados ANS (regulador brasileiro). Cinco componentes:

- **`api/`**: FastAPI. Lê exclusivamente `api_ans`. X-API-Key + Redis (auth cache 60s; prata 300s). Envelope: `{dados: [...], meta: {...}}`.
- **`mongo_layout_service/`**: Governança MongoDB. Metadados de layout, versionamento. Auth por token.
- **`ingestao/`**: Airflow DAGs. Download ANS → validação layout → `bruto_ans` → `plataforma.job`.
- **`healthintel_dbt/`**: dbt. Fluxo: `bruto_ans` → `stg_ans` → `int_ans` → `nucleo_ans` → `api_ans` → `consumo_ans`. Camadas paralelas: `quality_ans`, `mdm_ans`.
- **`frontend/healthintel_frontend_fase9/`**: Site público + portal cliente (Vite + React 19 + TS, react-router-dom, recharts). Consome a API via `api_ans` apenas — nunca expõe schemas internos.

**Schemas PostgreSQL:**
- `bruto_ans`: Bronze. RANGE partition por competência/trimestre. SIB: partições anuais `_YYYY` (nunca mensais).
- `stg_ans` / `int_ans`: Staging views / Ephemeral intermediates (não materializados).
- `nucleo_ans`: Gold marts (`fat_*`, `dim_*`). `api_ans`: Gold API (indexado, read-only). `consumo_ans`: Entrega cliente BI.
- `quality_ans`: `dq_*` (CNPJ-DV, CNES-DV). `mdm_ans`: MDM público (`mdm_*_master`, `xref_*_origem`).
- `consumo_premium_ans`: SQL-direto premium. `bruto_cliente` / `stg_cliente` / `mdm_privado`: ingestion privada por tenant.
- `plataforma`: Metadados operacionais — `politica_dataset`, `ingestao_janela_decisao`, `retencao_particao_log`, `job`, `log_uso`.

---

## Development Commands

| Tarefa | Comando |
|--------|---------|
| Serviços | `make up / down / logs / ps` · `make up-hml / down-hml` |
| Lint / CI | `make lint` · `make sql-lint` · `make ci-local` |
| Testes | `make test` · `pytest <path> -v` · `make dbt-test` |
| dbt | `make dbt-build` · `make dbt-compile` · `make dbt-seed` · `make dbt-seed-ref` |
| dbt seletivo | `make dbt-build-core` / `dbt-test-core` (Fase 9) · `make dbt-build-premium` / `dbt-test-premium` |
| Seeds / Bootstrap | `make demo-data` · `make seed-dados-completos` · `make bootstrap-*-layouts` |
| Smoke tests | `make smoke[-rede|-cnes|-tiss|-prata|-sib|-cadop|-consumo|-premium|-core|-ingestao-real]` |
| Smoke Fase 7 | `make smoke-janela-carga-sib` · `make smoke-versao-vigente-tuss` · `make smoke-historico-sob-demanda` · `make smoke-pgbackrest` · `make hardgate-sem-ano-hardcoded-janelacarga` |
| Ingestão real | `make dag-run-real-sib UFS=AC COMPETENCIA=YYYYMM` · `make dag-run-real-cadop COMPETENCIA=YYYYMM` |
| Billing / Consumo | `make billing-close REF=YYYYMM` · `make consumo-refresh` |
| Capacidade / Disco | `make capacidade-snapshot` · `make capacidade-monitor` · `make capacidade-relatorio` · `make monitor-disco` |
| Carga ANS VPS | `make carga-ans-padrao-vps[-dry-run|-incluir-pendentes]` · `make monitor-full2a-sem-tiss[-once]` |
| ELT | `make elt-discover / elt-extract / elt-load / elt-all / elt-status` · `make elt-transform-all / elt-validate-all` |
| Dev backend | `make api-dev` (:8000) · `make layout-dev` (:8001) · `make load-test` · `make dag-parse` |
| Dev frontend (Fase 9) | `cd frontend/healthintel_frontend_fase9 && npm install && npm run dev` (:5173) · `npm run build` · `npm run lint` |

---

## Workflow Rules

**Endpoint:** router `api/app/routers/` → schema `app/schemas/` (Pydantic v2) → service `app/services/` (só `api_ans`) → deps `validar_chave` + `verificar_plano` [+ `verificar_camada('bronze'|'prata')`] → envelope `{dados, meta}` → teste integration.

**dbt model:** staging view (`stg_`) → intermediate ephemeral (`int_`) → mart table (`nucleo_ans`) → api table (`api_ans`, `post_hook: criar_indices`) → consumo table (`consumo_ans`, tag `consumo`) → doc em `_{tipo}.yml` → testes `assert_*.sql`.

**DAG:** `ingestao/dags/dag_{dataset}.py` → validar layout MongoDB → upsert `bruto_ans` → registrar `plataforma.job` → freshness em `_sources.yml`.

**Testes:** `pytest api/tests/unit/` · `pytest api/tests/integration/` · `pytest testes/regressao/` · `make smoke` · `make load-test`

---

## Service Dependencies

| Serviço | Porta | Notas |
|---------|-------|-------|
| API | 8000 | Lê só `api_ans`; auth cache 60s |
| Layout Service | 8001 | MongoDB, token-gated |
| Airflow | 8088 | DAGs em `ingestao/dags/` |
| Frontend Fase 9 | 5173 | Vite dev server (`npm run dev`); build Nginx via `Dockerfile` |
| PostgreSQL | 5432 | Todos os schemas acima |
| MongoDB | 27017 | `healthintel_layout` |
| Redis | 6379 | Auth cache 60s + prata TTL 300s |

---

## Important Conventions

- **Surrogate keys**: `operadora_id` (FK `snap_operadora.id`, SCD Type 2). Nunca `registro_ans` cru em fatos.
- **Competência**: YYYYMM. Macro `competencia_para_data()`. Registro ANS: 6 dígitos com zeros — `normalizar_registro_ans()`.
- **API**: sempre envelope. Bronze: sem Redis cache (dado mutável até lote fechar). Prata: TTL 300s. Rate limit: bronze 3×, prata 2×, gold 1×.
- **Incremental**: reprocessar últimas 3–4 competências. Freshness entry obrigatória em `_sources.yml`.
- **Partições SIB**: anuais `_YYYY` (`FOR VALUES FROM (YYYY01) TO ((YYYY+1)01)`). Nunca criar partição mensal SIB.
- **Janela carga (Fase 7)**: `calcular_janela_carga_anual(ANS_ANOS_CARGA_HOT=2)`. Fora da janela → `ingestao_janela_decisao` com `acao='ignorado_fora_janela'`. Nunca descartar silenciosamente. Nenhum ano hardcoded em lógica produtiva.
- **Score v3**: `versao_metodologia='v3.0'`. Componentes: core(0.25) + regulatorio(0.25) + financeiro(0.20) + rede(0.20) + estrutural(0.10).
- **Quarentena**: `bruto_ans.*_quarentena` para registros inválidos — nunca entram em dados servidos.
- **Layer access**: `plataforma.plano.camadas_permitidas[]`. Dep `verificar_camada` para bronze/prata; `verificar_plano` para gold.
- **FastAPI premium**: lê somente `api_ans.api_premium_*`. Proibido: Serpro, BrasilAPI, enrich-cnpj, requests externos.

---

## Sprint Status

| Fase | Status | Tag |
|------|--------|-----|
| Fases 1–4 (Sprints 01–25) | CONCLUÍDA | `v3.0.0` |
| Fase 5 (Sprints 26–32 concluídos, Sprint 33 backlog) | CONCLUÍDA* | `v3.8.0-gov` pendente |
| Fase 6 (operação comercial, backlog) | BACKLOG | `v4.0.0` |
| Fase 7 (Sprints 34–36 implementados, 37–40 backlog) | EM ANDAMENTO | `v4.2.0-dataops` |
| Fase 9 (Sprints 1–7: MVP comercial Core ANS) | EM ANDAMENTO | `v5.0.0-core-mvp` |

**Regras ativas (todas aditivas — não alterar artefatos de fase anterior):**
- **Fase 5**: `stg_*`, `int_*`, `fat_*`, `mart_*`, `api_*`, `consumo_*` do baseline v3.0.0 são imutáveis.
- **Fase 7**: nenhum modelo dbt, API, DAG aprovada, coluna `competencia` ou `bruto_ans.sib_*` pode ser alterado. Novos artefatos entram via bootstrap SQL numerado ou helper Python novo.
- **Fase 6**: não altera modelos, tabelas ou contratos de endpoints existentes.
- **Fase 9**: produto HealthIntel Core ANS. Tag `core_ans` no dbt. Novos endpoints adicionam; não alteram contratos existentes. Comandos: `make dbt-build-core`, `make smoke-core`, `make monitor-disco`.

Fase 7 backlog: Sprint 37 (TUSS) · Sprint 38 (histórico sob demanda) · Sprint 39 (pgBackRest) · Sprint 40 (restore PITR).
Fase 9 backlog: Sprint 5 (antiextração avançada) · Sprint 6 completo (backup R2) · Sprint 7 (landing page, Postman collection).

Docs: `docs/sprints/fase{2,3,4,5,6,7,9}/` · Runbooks: `docs/runbooks/` · Comercial: `docs/comercial/`

---

## Debugging

- **dbt incremental**: verificar unicidade `unique_key`; `dbt build --full-refresh` para reset.
- **API latency**: checar Redis pool (`core/redis_client.py`), slow query log, `EXPLAIN ANALYZE`.
- **Layout validation**: encoding CSV, field count, versão no MongoDB (`mongo_layout_service` logs).
- **CI failures**: `make ci-local`; checar dbt compile, SQLFluff, pytest assertions.

## Useful SQL

```sql
-- Freshness datasets
SELECT dataset, MAX(_carregado_em) FROM plataforma.job WHERE status='sucesso' GROUP BY dataset ORDER BY 2 DESC;
-- Distribuição API hoje
SELECT endpoint, COUNT(*) FROM plataforma.log_uso WHERE DATE(_criado_em)=CURRENT_DATE GROUP BY endpoint ORDER BY 2 DESC;
```
