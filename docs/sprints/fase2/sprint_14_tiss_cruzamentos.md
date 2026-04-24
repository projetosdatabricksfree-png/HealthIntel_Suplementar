# Sprint 14 — D-TISS, TUSS, Rol e Cruzamentos Procedimento × Estabelecimento × Operadora

**Status:** Concluída
**Objetivo:** integrar dados assistenciais TISS (agregados por operadora × grupo TUSS × UF), seeds de referência TUSS e Rol de Procedimentos ANS, e publicar cruzamentos analíticos de sinistralidade por procedimento e gap assistencial CNES × rede.
**Critério de saída:** endpoints de TISS trimestral disponíveis via API, seed TUSS e Rol carregados, cruzamento sinistralidade por grupo de procedimento funcional.

---

## HIS-14.1 — Seeds de referência TUSS e Rol

- [x] Criar `healthintel_dbt/seeds/ref_tuss.csv`: `codigo_tuss`, `descricao`, `grupo`, `subgrupo`, `capitulo`, `vigencia_inicio`, `vigencia_fim`. (~35k códigos, fonte: ANS tabela TUSS vigente).
- [x] Criar `healthintel_dbt/seeds/ref_rol_procedimento.csv`: `codigo_tuss`, `descricao`, `segmento`, `obrigatorio_medico`, `obrigatorio_odonto`, `carencia_dias`, `vigencia_inicio`, `vigencia_fim`. (fonte: RN 465/2021 e atualizações).
- [x] Criar `scripts/gerar_seeds_tuss_rol.py`: script utilitário que gera CSVs com dados sintéticos representativos (grupos principais do TUSS) para uso em CI/CD e dev local.
- [x] Configurar schema `ref_ans` para seeds em `dbt_project.yml`: `+schema: ref_ans`, `+materialized: seed`.
- [x] Documentar seeds em `healthintel_dbt/seeds/_seeds.yml`.

---

## HIS-14.2 — Bronze e ingestão D-TISS

- [x] Definir DDL `bruto_ans.tiss_procedimento_trimestral`: `trimestre`, `registro_ans`, `sg_uf`, `grupo_procedimento`, `grupo_desc`, `subgrupo_procedimento`, `qt_procedimentos`, `qt_beneficiarios_distintos`, `valor_total`, `modalidade`, `tipo_contratacao`, `fonte_publicacao` + metadados padrão. Particionamento RANGE por `trimestre`.
- [x] Criar layout registry TISS em MongoDB (`scripts/bootstrap_layout_registry_tiss.py`): `fonte_dataset`, `layout`, `layout_versao`, aliases para nomes ANS.
- [x] Criar DAG `dag_ingest_tiss`: schedule `0 5 1 2,5,8,11 *` (trimestral, lag ~90d), cadeia padrão de 6 tarefas.
- [x] Adicionar `tiss_procedimento` ao `DATASET_CONFIG` em `ingestao/app/carregar_postgres.py` com função `carregar_tiss_procedimento_bruto()`.
- [x] Atualizar `ingestao/dags/dag_criar_particao_mensal.py`: adicionar bloco PL/pgSQL para partição trimestral de `bruto_ans.tiss_procedimento_trimestral`.
- [x] Adicionar entry em `healthintel_dbt/models/staging/_sources.yml`: `freshness: {warn_after: {count: 120, period: day}, error_after: {count: 180, period: day}}`.

---

## HIS-14.3 — Camada dbt: staging D-TISS

- [x] Criar `healthintel_dbt/models/staging/stg_tiss_procedimento.sql` (view, `stg_ans`):
  - `{{ normalizar_registro_ans('registro_ans') }}` → `registro_ans`.
  - `lpad(grupo_procedimento, 6, '0')` → `grupo_procedimento`.
  - `upper(trim(sg_uf))` → `sg_uf`.
  - `coalesce(qt_procedimentos, 0)` → `qt_procedimentos`.
  - `coalesce(valor_total, 0)` → `valor_total`.
  - Deduplicação via `row_number() over (partition by trimestre, registro_ans, grupo_procedimento, sg_uf order by _carregado_em desc)`.

---

## HIS-14.4 — Intermediates de cruzamento

- [x] Criar `healthintel_dbt/models/intermediate/int_tiss_operadora_trimestre.sql` (ephemeral):
  - Granularidade: `(trimestre, registro_ans, grupo_procedimento)`.
  - Agrega: `qt_procedimentos`, `valor_total`, `valor_medio_por_procedimento`.
  - Calcula: `pct_procedimentos_por_grupo` (dentro do total da operadora no trimestre).
  - Join com `snap_operadora` via `{{ normalizar_registro_ans('registro_ans') }}`.
- [x] Criar `healthintel_dbt/models/intermediate/int_sinistralidade_procedimento.sql` (ephemeral):
  - Cruza `stg_tiss_procedimento` (custo TISS) com staging de DIOPS (receita) por `(trimestre, registro_ans)`.
  - Calcula: `sinistralidade_grupo_pct = valor_tiss / receita_total * 100`.
  - Flag: `flag_sinistralidade_alta` (bool: `sinistralidade_grupo_pct > 80`).
  - Depende de: `stg_tiss_procedimento` + staging DIOPS existente.

---

## HIS-14.5 — Marts

- [x] Criar `healthintel_dbt/models/marts/fato/fat_tiss_procedimento_operadora.sql` (incremental merge, `nucleo_ans`):
  - `unique_key: [trimestre, registro_ans, grupo_procedimento]`.
  - Reprocessa últimos 2 trimestres.
  - Colunas: `qt_procedimentos`, `valor_total`, `valor_medio`, `rank_por_valor` (dentro da operadora), `pct_do_total_operadora`.
- [x] Criar `healthintel_dbt/models/marts/fato/fat_sinistralidade_procedimento.sql` (incremental merge, `nucleo_ans`):
  - `unique_key: [trimestre, registro_ans, grupo_procedimento]`.
  - Colunas: `sinistralidade_grupo_pct`, `desvio_padrao_sinistralidade`, `flag_sinistralidade_alta`, `rank_sinistralidade`.
- [x] Criar `healthintel_dbt/models/marts/fato/fat_cnes_rede_gap_municipio.sql` (incremental merge, `nucleo_ans`):
  - Granularidade: `(competencia, cd_municipio, tipo_unidade)`.
  - Cruza `fat_cnes_estabelecimento_municipio` × `fat_cobertura_rede_municipio`.
  - Colunas: `estabelecimentos_cnes`, `prestadores_credenciados`, `gap_absoluto`, `gap_pct`, `severidade_gap` (nenhum/leve/critico).
- [x] Documentar em `_fatos.yml` (fat_tiss_*, fat_sinistralidade_*, fat_cnes_rede_gap_*).

---

## HIS-14.6 — Camada API dbt

- [x] Criar `healthintel_dbt/models/api/api_tiss_operadora_trimestral.sql` (table, `api_ans`):
  - Desnormalizado com `nm_operadora`, `modalidade_operadora`, `grupo_desc`, ranking.
  - `post-hook: criar_indices(['registro_ans', 'trimestre', 'grupo_procedimento'])`.
- [x] Criar `healthintel_dbt/models/api/api_sinistralidade_procedimento.sql` (table, `api_ans`):
  - Join `fat_sinistralidade_procedimento` + `dim_operadora_atual`.
  - `post-hook: criar_indices(['registro_ans', 'trimestre'])`.
- [x] Criar `healthintel_dbt/models/api/api_cnes_rede_gap.sql` (table, `api_ans`):
  - Desnormalizado para endpoint de vazio avançado.
  - `post-hook: criar_indices(['cd_municipio', 'competencia', 'tipo_unidade'])`.
- [x] Documentar em `_api.yml` (api_tiss_*, api_sinistralidade_*, api_cnes_rede_gap).

---

## HIS-14.7 — FastAPI endpoints TISS

- [x] Criar `api/app/schemas/tiss.py` (Pydantic v2):
  - `TissProcedimentoItem`: `trimestre`, `grupo_procedimento`, `grupo_desc`, `qt_procedimentos`, `valor_total`, `valor_medio`, `pct_do_total`.
  - `SinistralProcedimentoItem`: `trimestre`, `grupo_procedimento`, `sinistralidade_grupo_pct`, `flag_sinistralidade_alta`.
  - `CnesRedeGapItem`: `cd_municipio`, `nm_municipio`, `tipo_unidade`, `estabelecimentos_cnes`, `prestadores_credenciados`, `gap_absoluto`, `severidade_gap`.
  - `TissResponse(dados: list[...], meta: MetaResposta)`.
- [x] Criar `api/app/services/tiss.py`: queries assíncronas exclusivamente em `api_ans`.
- [x] Criar `api/app/routers/tiss.py`:
  - `GET /v1/tiss/{registro_ans}/procedimentos` — procedimentos TISS por operadora e trimestre.
  - `GET /v1/tiss/{registro_ans}/sinistralidade` — sinistralidade por grupo de procedimento.
  - `GET /v1/rede/gap/{cd_municipio}` — gap CNES × rede declarada por município.
  - Auth: `Depends(validar_api_key)`, `Depends(verificar_plano)`.
- [x] Registrar router em `api/app/main.py`.

---

## HIS-14.8 — Testes, seed e smoke

- [x] Criar `scripts/seed_demo_tiss.py`: insere ~40 registros sintéticos em `bruto_ans.tiss_procedimento_trimestral` para trimestre de referência (2025T1), cobrindo ao menos 5 operadoras, 3 grupos TUSS e 3 UFs.
- [x] Adicionar targets no `Makefile`:
  - `bootstrap-tiss-layouts`: executa `bootstrap_layout_registry_tiss.py`.
  - `demo-data-tiss`: executa `seed_demo_tiss.py`.
  - `dbt-seed-ref`: executa `dbt seed --select ref_tuss ref_rol_procedimento`.

---

## Entregas esperadas

- [x] Seeds: `ref_tuss.csv`, `ref_rol_procedimento.csv`.
- [x] Script gerador: `scripts/gerar_seeds_tuss_rol.py`.
- [x] DDL: `bruto_ans.tiss_procedimento_trimestral` (particionado por `trimestre`).
- [x] Layout registry MongoDB: TISS procedimentos.
- [x] DAG: `dag_ingest_tiss` (schedule trimestral).
- [x] Loader Python: `carregar_tiss_procedimento_bruto()`.
- [x] Partição automática: bloco em `dag_criar_particao_mensal.py`.
- [x] Source freshness: entry em `_sources.yml`.
- [x] dbt staging: `stg_tiss_procedimento`.
- [x] dbt intermediates (ephemeral): `int_tiss_operadora_trimestre`, `int_sinistralidade_procedimento`.
- [x] dbt fatos: `fat_tiss_procedimento_operadora`, `fat_sinistralidade_procedimento`, `fat_cnes_rede_gap_municipio`.
- [x] dbt api: `api_tiss_operadora_trimestral`, `api_sinistralidade_procedimento`, `api_cnes_rede_gap`.
- [x] Endpoints: `GET /v1/tiss/{registro_ans}/procedimentos`, `GET /v1/tiss/{registro_ans}/sinistralidade`, `GET /v1/rede/gap/{cd_municipio}`.
- [x] Seed demo: `scripts/seed_demo_tiss.py`.
- [x] Makefile targets: `bootstrap-tiss-layouts`, `demo-data-tiss`, `dbt-seed-ref`.

---

## Validação esperada

- [x] `ruff check api ingestao scripts`
- [x] `pytest -q`
- [x] `dbt seed --select ref_tuss ref_rol_procedimento`
- [x] `dbt build --select +stg_tiss_procedimento+`
- [x] `dbt build --select +fat_tiss_procedimento_operadora+`
- [x] `dbt build --select +api_tiss_operadora_trimestral+`
- [x] Query manual: sinistralidade por grupo TUSS para amostra de 3 operadoras.
- [x] Query manual: gap CNES × rede para municípios capitais.
