# Sprint 13 — CNES Estabelecimentos

**Status:** Em andamento
**Objetivo:** integrar o Cadastro Nacional de Estabelecimentos de Saúde (DATASUS) à plataforma, criando a camada analítica de estabelecimentos por município, e publicar endpoints de CNES com granularidade geográfica.
**Critério de saída:** dados de estabelecimentos CNES disponíveis via API com totais por município e tipo de unidade; cruzamento com rede credenciada habilitado via intermediate.

---

## HIS-13.1 — Bronze e ingestão CNES

- [x] Mapear fonte: DATASUS CNES (ftp.datasus.gov.br/cnes/ ou dados.gov.br), periodicidade mensal, formato CSV, encoding UTF-8.
- [x] Definir DDL `bruto_ans.cnes_estabelecimento`: `competencia`, `cnes` (7d), `cnpj`, `razao_social`, `nome_fantasia`, `sg_uf`, `cd_municipio`, `nm_municipio`, `tipo_unidade`, `tipo_unidade_desc`, `esfera_administrativa`, `vinculo_sus`, `leitos_existentes`, `leitos_sus`, `latitude`, `longitude`, `situacao`, `fonte_publicacao` + metadados padrão. Particionamento RANGE por `competencia`.
- [x] Criar layout registry CNES em MongoDB (`scripts/bootstrap_layout_registry_cnes.py`): `fonte_dataset`, `layout`, `layout_versao`, aliases para nomes DATASUS (CO_CNES, SG_UF, etc.).
- [x] Criar DAG `dag_ingest_cnes`: schedule `0 5 15 * *`, cadeia `inicio → mapear_publicacao → validar_layout → carregar_bruto → registrar_versao → fim`.
- [x] Adicionar `cnes_estabelecimento` ao `DATASET_CONFIG` em `ingestao/app/carregar_postgres.py` com função `carregar_cnes_bruto()`.
- [ ] Atualizar `ingestao/dags/dag_criar_particao_mensal.py`: adicionar bloco PL/pgSQL para criação de partição mensal de `bruto_ans.cnes_estabelecimento`.
- [ ] Adicionar entry em `healthintel_dbt/models/staging/_sources.yml`: `freshness: {warn_after: {count: 45, period: day}, error_after: {count: 90, period: day}}`.

---

## HIS-13.2 — Camada dbt: staging e intermediates

- [ ] Criar `healthintel_dbt/models/staging/stg_cnes_estabelecimento.sql` (view, `stg_ans`):
  - `lpad(cnes, 7, '0')` → `cnes`
  - `lpad(cd_municipio, 6, '0')` → `cd_municipio`
  - `upper(trim(sg_uf))` → `sg_uf`
  - `upper(trim(tipo_unidade))` → `tipo_unidade`
  - `coalesce(vinculo_sus, false)` → `vinculo_sus`
  - `coalesce(leitos_existentes, 0)` → `leitos_existentes`
  - `coalesce(leitos_sus, 0)` → `leitos_sus`
  - Deduplicação via `row_number() over (partition by competencia, cnes order by _carregado_em desc)`.
- [ ] Criar `healthintel_dbt/models/intermediate/int_cnes_municipio_resumo.sql` (ephemeral):
  - Granularidade: `(competencia, cd_municipio, tipo_unidade)`.
  - Agrega: `total_estabelecimentos`, `total_leitos`, `total_leitos_sus`, `pct_leitos_sus`.
  - Join com `dim_localidade` para enriquecer com `nm_municipio`, `sg_uf`, `regiao`.
- [ ] Criar `healthintel_dbt/models/intermediate/int_cnes_x_rede_municipio.sql` (ephemeral):
  - Cruza `int_cnes_municipio_resumo` com `fat_cobertura_rede_municipio` por `(competencia, cd_municipio)`.
  - Calcula: `gap_estabelecimentos_vs_rede = total_estabelecimentos_cnes - qt_prestador_rede`, `flag_gap_critico` (bool).

---

## HIS-13.3 — Camada dbt: marts e API

- [ ] Criar `healthintel_dbt/models/marts/fato/fat_cnes_estabelecimento_municipio.sql` (incremental merge, `nucleo_ans`):
  - `unique_key: [competencia, cd_municipio, tipo_unidade]`.
  - Colunas: `total_estabelecimentos`, `total_leitos`, `total_leitos_sus`, `pct_leitos_sus`, `pct_vinculo_sus`, enriquecimento geográfico.
  - Reprocessa últimas 3 competências.
- [ ] Criar `healthintel_dbt/models/api/api_cnes_municipio.sql` (table, `api_ans`):
  - Desnormalizado com `nm_municipio`, `nm_uf`, `regiao`, `tipo_unidade_desc`.
  - `post-hook: criar_indices(['cd_municipio', 'sg_uf', 'competencia', 'tipo_unidade'])`.
- [ ] Documentar em `healthintel_dbt/models/marts/fato/_fatos.yml` e `healthintel_dbt/models/api/_api.yml`.
- [ ] Tag: `tag: fato` em fat, `tag: api` em api_cnes_municipio.

---

## HIS-13.4 — FastAPI endpoints CNES

- [ ] Criar `api/app/schemas/cnes.py` (Pydantic v2):
  - `CnesMunicipioItem`: `cd_municipio`, `nm_municipio`, `sg_uf`, `tipo_unidade`, `tipo_unidade_desc`, `total_estabelecimentos`, `total_leitos`, `total_leitos_sus`, `pct_leitos_sus`.
  - `CnesUfItem`: `sg_uf`, `tipo_unidade`, `total_estabelecimentos`, `total_leitos`.
  - `CnesResponse(dados: list[...], meta: MetaResposta)`.
- [ ] Criar `api/app/services/cnes.py`: queries assíncronas em `api_ans.api_cnes_municipio`. Apenas `api_ans`.
- [ ] Criar `api/app/routers/cnes.py`:
  - `GET /v1/cnes/municipio/{cd_municipio}` — estabelecimentos por município e competência.
  - `GET /v1/cnes/uf/{sg_uf}` — totais por UF e tipo de unidade.
  - Auth: `Depends(validar_api_key)`, `Depends(verificar_plano)`.
  - Resposta: envelope `{dados: [...], meta: {...}}`.
- [ ] Registrar router em `api/app/main.py`: `app.include_router(cnes.router)`.

---

## HIS-13.5 — Testes, seed e smoke

- [ ] Criar `scripts/seed_demo_cnes.py`: insere ~50 registros sintéticos em `bruto_ans.cnes_estabelecimento` para competência de referência (202501), cobrindo ao menos 5 municípios e 4 tipos de unidade.
- [ ] Criar `scripts/smoke_cnes.py`: valida endpoints `GET /v1/cnes/municipio/{cd_municipio}` e `GET /v1/cnes/uf/{sg_uf}` com dados de referência.
- [ ] Adicionar targets no `Makefile`:
  - `bootstrap-cnes-layouts`: executa `bootstrap_layout_registry_cnes.py`.
  - `demo-data-cnes`: executa `seed_demo_cnes.py`.
  - `smoke-cnes`: executa `smoke_cnes.py`.

---

## Entregas esperadas

- [x] DDL: `bruto_ans.cnes_estabelecimento` (particionado por `competencia`).
- [x] Layout registry MongoDB: CNES estabelecimentos.
- [x] DAG: `dag_ingest_cnes` (schedule mensal dia 15).
- [x] Loader Python: `carregar_cnes_bruto()` em `carregar_postgres.py`.
- [ ] Partição automática: bloco em `dag_criar_particao_mensal.py`.
- [ ] Source freshness: entry em `_sources.yml`.
- [ ] dbt staging: `stg_cnes_estabelecimento`.
- [ ] dbt intermediates (ephemeral): `int_cnes_municipio_resumo`, `int_cnes_x_rede_municipio`.
- [ ] dbt fato: `fat_cnes_estabelecimento_municipio`.
- [ ] dbt api: `api_cnes_municipio`.
- [ ] Endpoints: `GET /v1/cnes/municipio/{cd_municipio}`, `GET /v1/cnes/uf/{sg_uf}`.
- [ ] Seed demo: `scripts/seed_demo_cnes.py`.
- [ ] Smoke test: `scripts/smoke_cnes.py`.
- [ ] Makefile targets: `bootstrap-cnes-layouts`, `demo-data-cnes`, `smoke-cnes`.

---

## Validação esperada

- [ ] `ruff check api ingestao scripts`
- [ ] `pytest -q`
- [ ] `dbt build --select +tag:api,api_cnes_municipio`
- [ ] `make smoke-cnes`
- [ ] Query manual: total de estabelecimentos por tipo de unidade para um município de referência.
