# Sprint 25 — Qualidade, Catálogo e v3.0.0

**Status:** Pendente
**Objetivo:** expandir contratos de qualidade para todos os modelos finais; criar catálogo de dados para clientes; executar suite de regressão Fase 4; congelar baseline `v3.0.0`.
**Critério de saída:** `dbt test` zero falhas em toda a stack (hard gate); catálogo publicado com grão e métricas documentados; `testes/regressao/test_endpoints_fase4.py` zero falhas (hard gate); `make smoke-prata` e `make smoke-consumo` zero falhas (hard gates); `dbt docs generate` sem `description` vazia nos modelos finais; tag `v3.0.0` criada.

## Histórias

### HIS-25.1 — Expansão dos Testes dbt para toda a Stack

- [ ] Auditar todos os modelos staging (`stg_*`) em `_staging.yml`: garantir `not_null` em `registro_ans` e `competencia`; `accepted_values` em campos de domínio (modalidade, uf, situacao).
- [ ] Auditar todos os intermediate (`int_*`) em `_intermediate.yml`: garantir `not_null` em chaves de join; ausência de duplicatas pós-dedup onde esperado.
- [ ] Adicionar testes faltantes em marts existentes (`fat_*`) em `_fato.yml`:
  - `unique` em `unique_key` de cada fato incremental
  - `not_null` em todas as chaves e métricas críticas
  - `dbt_utils.expression_is_true` para invariantes: `qt_beneficiarios >= 0`, `market_share_pct between 0 and 100`, `taxa_aprovacao between 0 and 1`
- [ ] Garantir cobertura completa em `_marts_gold.yml` (Sprint 23) e `_consumo.yml` (Sprint 24) — todos os testes aplicáveis presentes.

### HIS-25.2 — Testes Singulares Adicionais

- [ ] `healthintel_dbt/tests/assert_mart_operadora_360_sem_orfaos.sql`:
  - Todo `registro_ans` em `mart_operadora_360` deve existir em `dim_operadora_atual`
- [ ] `healthintel_dbt/tests/assert_consumo_score_faixa_valida.sql`:
  - `consumo_score_operadora_mes.score_total between 0 and 100` sem exceções
- [ ] `healthintel_dbt/tests/assert_consumo_beneficiarios_nao_negativos.sql`:
  - `consumo_beneficiarios_operadora_mes.qt_beneficiarios >= 0` para todos os registros
- [ ] `healthintel_dbt/tests/assert_staging_registro_ans_6_digitos.sql`:
  - `length(registro_ans) = 6` em todos os modelos staging — consolidar ou confirmar cobertura do assert existente
- [x] `healthintel_dbt/tests/assert_lote_ingestao_sem_duplicata.sql`:
  - `plataforma.lote_ingestao` não deve ter dois registros `sucesso` para o mesmo `hash_arquivo`

### HIS-25.3 — Catálogo de Dados para Clientes

- [x] Criar pasta `docs/catalogo_dados/`.
- [x] Criar `docs/catalogo_dados/README.md`:
  - Título: **Catálogo de Dados para Clientes — HealthIntel Suplementar**
  - Índice de todos os datasets por camada disponível ao cliente (Bronze API, Prata API, Gold Marts via FastAPI, consumo_ans via PostgreSQL direto)
  - Legenda de colunas (chave primária, chave de negócio, métrica, dimensão)
  - Cadência de atualização por camada
  - Instruções de acesso: como conectar ao `consumo_ans` com `healthintel_cliente_reader`
- [x] Criar uma página por mart Gold e modelo de consumo (6 marts + 8 modelos consumo = 14 arquivos `{modelo}.md`), cada um contendo:
  - Propósito e casos de uso do cliente
  - Grão (ex: "uma linha por operadora por mês")
  - Chaves primárias e chaves de negócio
  - Tabela de colunas: nome | tipo | descrição | origem | unidade
  - Métricas disponíveis com definição de negócio
  - Exemplo de query SQL analítica típica
- [x] Criar `docs/catalogo_dados/glossario.md`: termos-chave do domínio (registro_ans, competencia, IDSS, IGR, sinistralidade, taxa de quarentena, etc.)

### HIS-25.4 — Exposures e dbt Docs

- [ ] Completar `healthintel_dbt/models/exposures.yml`:
  - Exposure `api_ans_prod`: tipo `application`, dependências de todos os modelos `api_ans.*`
  - Exposure `consumo_ans_clientes`: tipo `application`, dependências de todos os modelos `consumo_ans.*`
  - Exposure `airflow_ingestao`: tipo `application`, dependências de todos os `bruto_ans` sources
- [ ] Executar `dbt docs generate` — verificar que todos os modelos têm `description` preenchida (hard gate).
- [ ] Salvar artefatos: `docs/dbt_docs_v3.0.0/` com `manifest.json`, `catalog.json`, `index.html`.
- [x] Criar `docs/arquitetura/lineage_fase4.md`: diagrama textual (ou Mermaid) do lineage completo Bronze → consumo_ans.

### HIS-25.5 — Documentação Column-Level na Staging

- [ ] Para os seguintes modelos staging com maior consumo, adicionar `columns` completo em `_staging.yml`:
  - `stg_cadop`: `registro_ans`, `razao_social`, `cnpj`, `modalidade`, `uf_sede`, `situacao`, `competencia`
  - `stg_sib_operadora`: `registro_ans`, `competencia`, `qt_beneficiarios`, `modalidade`
  - `stg_sib_municipio`: `registro_ans`, `competencia`, `cd_municipio`, `qt_beneficiarios`
  - `stg_diops`: `registro_ans`, `trimestre`, `receita_total`, `sinistralidade_pct`
  - `stg_tiss_procedimento`: `registro_ans`, `trimestre`, `cd_procedimento_tuss`, `qt_procedimentos`, `vl_total`

### HIS-25.6 — Suite de Regressão Fase 4

- [ ] Criar `testes/regressao/test_endpoints_fase4.py` cobrindo:
  - Prata completa: todos os 17 endpoints `/v1/prata/*` com plano `analitico` (incluindo CNES e TISS prata)
  - Bloqueio prata: HTTP 403 para plano `piloto` em `/v1/prata/*`
  - `aviso_qualidade` presente no envelope quando `taxa_aprovacao < 0.95`
  - Bronze API: regressão dos 11 endpoints `/v1/bronze/*` com plano `enterprise_tecnico`
  - Ouro API: regressão dos endpoints principais (`/v1/operadoras`, `/v1/rankings/composto`, `/v1/operadoras/{id}/score-v3`)
  - Lote ingestão: `plataforma.lote_ingestao` tem registros SIB e CADOP com status `sucesso`
  - consumo_ans: queries diretas nos 8 modelos com role `healthintel_cliente_reader`; PERMISSION DENIED confirmado nas 5 camadas internas
- [x] Executar `pytest testes/regressao/test_endpoints_fase4.py -v` — zero falhas (hard gate obrigatório para aceite da sprint).

### HIS-25.7 — Baseline v3.0.0

- [ ] Atualizar `docs/CHANGELOG.md` com entrada `v3.0.0`:
  - Sprints 21–25 da Fase 4
  - Novos endpoints prata (CNES, TISS prata + aviso_qualidade)
  - Novos DAGs (dag_ingest_sib, dag_ingest_cadop, dag_dbt_consumo_refresh)
  - Tabela `plataforma.lote_ingestao`
  - 6 marts Gold (`mart_operadora_360`, `mart_mercado_municipio`, `mart_regulatorio_operadora`, `mart_rede_assistencial`, `mart_score_operadora`, `mart_tiss_procedimento`)
  - Schema `consumo_ans` com 8 data products; role `healthintel_cliente_reader`
  - Catálogo de dados para clientes publicado
  - 3 dimensões adicionais (`dim_modalidade`, `dim_segmentacao`, `dim_tipo_contratacao`)
- [ ] Atualizar `docs/sprints/README.md` e `docs/sprints/fase4/README.md` (não marcar nenhuma sprint como Concluída antes da aprovação formal).
- [ ] Atualizar `CLAUDE.md`: adicionar `consumo_ans` na seção de schemas; `Sprint Structure` com Fase 4; comandos `make consumo-refresh`, `make smoke-prata`, `make smoke-consumo`, `make bootstrap-sib-layouts`, `make bootstrap-cadop-layouts`; role `healthintel_cliente_reader`.
- [ ] Criar tag git `v3.0.0` após todos os critérios de saída passarem.

## Entregas esperadas

- [ ] `_staging.yml` com column-level docs nos 5 modelos principais
- [ ] `_fato.yml`, `_marts_gold.yml`, `_consumo.yml` com testes completos
- [ ] Testes singulares `assert_mart_*.sql`, `assert_consumo_*.sql`, `assert_lote_ingestao_sem_duplicata.sql`
- [x] `docs/catalogo_dados/README.md` + 14 páginas de modelos + `glossario.md`
- [x] `docs/arquitetura/lineage_fase4.md`
- [ ] `healthintel_dbt/models/exposures.yml` completo
- [ ] `docs/dbt_docs_v3.0.0/` com artefatos gerados
- [x] `testes/regressao/test_endpoints_fase4.py`
- [ ] `docs/CHANGELOG.md` atualizado com entrada `v3.0.0`
- [ ] `CLAUDE.md` atualizado
- [ ] Tag git `v3.0.0`

## Validação esperada (hard gates)

- [x] `ruff check api ingestao scripts`
- [x] `dbt compile` — zero erros em toda a stack
- [x] `dbt test` — zero falhas em toda a stack
- [x] `pytest testes/regressao/test_endpoints_fase4.py -v` — zero falhas
- [x] `make smoke-prata` — zero falhas
- [x] `make smoke-consumo` — zero falhas
- [ ] `dbt docs generate` sem `description` vazia nos modelos finais
- [x] `docs/catalogo_dados/` contém README + 14 páginas de modelo + glossário
- [ ] Tag `v3.0.0` criada e apontando para commit pós-regressão aprovada
