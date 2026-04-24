# Sprint 19 — Score v3 e Índice Composto

**Status:** Concluída
**Objetivo:** criar o score composto final (v3) agregando todas as dimensões disponíveis: core (SIB), regulatório (IGR/NIP/RN623/prudencial/QUALISS/IEPRS), financeiro (DIOPS/FIP/VDA/glosa), rede (cobertura/vazios), e estrutural (CNES/TISS quando disponíveis); criar ranking composto definitivo.
**Critério de saída:** `fat_score_v3_operadora_mensal` materializado e testado; endpoint `/v1/operadoras/{id}/score-v3` respondendo; ranking composto operacional; `versao_metodologia = 'v3.0'` registrada.

## Histórias

### HIS-19.1 — Definição de Pesos Score v3

- [x] Documentar pesos finais em `healthintel_dbt/dbt_project.yml` como variável `score_v3_pesos`:
  ```yaml
  score_v3_pesos:
    core: 0.25          # crescimento + presença (SIB)
    regulatorio: 0.25   # IGR + NIP + RN623 + prudencial + QUALISS + IEPRS
    financeiro: 0.20    # DIOPS + FIP + VDA + glosa
    rede: 0.20          # cobertura + vazios (CNES/TISS quando disponíveis)
    estrutural: 0.10    # CNES estabelecimentos (quando Sprint 13 concluída)
  ```
- [x] Definir fallback quando componente não disponível: `coalesce(componente, score_v2_normalizado)` com flag `componente_estimado = true`.
- [x] Documentar regra de fallback em `docs/arquitetura/score_v3_metodologia.md`.

### HIS-19.2 — Intermediate Score v3

- [x] Criar `healthintel_dbt/models/intermediate/int_score_v3_componentes.sql` (ephemeral).
- [x] Juntar:
  - `int_score_insumo` (componente core/crescimento)
  - `int_regulatorio_v2_operadora_trimestre` (componente regulatório)
  - `int_financeiro_operadora_periodo` (componente financeiro)
  - `int_rede_assistencial_municipio` agregado por operadora (componente rede)
  - `int_cnes_operadora` quando Sprint 13 concluída (componente estrutural; placeholder nulo até lá)
- [x] Normalizar cada componente para escala 0–100 com macro `normalizar_0_100`.
- [x] Calcular `score_v3_final = SUM(componente_i * peso_i)` por operadora e competência.
- [x] Flag `score_completo` (bool): true quando todos os 5 componentes disponíveis sem fallback.

### HIS-19.3 — Fact Score v3

- [x] Criar `healthintel_dbt/models/marts/fato/fat_score_v3_operadora_mensal.sql` (incremental merge).
  - `unique_key: [operadora_id, competencia_id]`
  - Colunas: `operadora_id`, `competencia_id`, `score_v3_final`, `score_core`, `score_regulatorio`, `score_financeiro`, `score_rede`, `score_estrutural`, `score_completo`, `versao_metodologia`
  - Reprocessar últimas 4 competências.
- [x] Tag `tag: fato_v3`.
- [x] Adicionar entrada em `healthintel_dbt/models/marts/fato/_fato.yml`.
- [x] Testes genéricos: `not_null`, `unique` em `(operadora_id, competencia_id)`.
- [x] Testes singulares:
  - `tests/assert_score_v3_range.sql` — `score_v3_final BETWEEN 0 AND 100`
  - `tests/assert_score_v3_componentes_range.sql` — todos os sub-scores 0–100
  - `tests/assert_score_v3_versao.sql` — `versao_metodologia = 'v3.0'` para todos os registros

### HIS-19.4 — API Score v3

- [x] Criar `healthintel_dbt/models/api/api_score_v3_operadora_mensal.sql` (api_ans, table + post-hook índices em `operadora_id`, `competencia`, `score_v3_final DESC`).
- [x] Criar serviço `api/app/services/score_v3.py` com funções:
  - `buscar_score_v3_operadora(registro_ans: str, competencia: str | None) -> list`
  - `buscar_historico_score_v3(registro_ans: str, periodos: int) -> list`
- [x] Adicionar endpoints em router existente `api/app/routers/operadora.py`:
  - `GET /v1/operadoras/{registro_ans}/score-v3`
  - `GET /v1/operadoras/{registro_ans}/score-v3/historico`
- [x] Schema Pydantic em `api/app/schemas/score_v3.py`: `ScoreV3Response`, `ScoreV3ComponentesResponse`.
- [x] Envelope: `{dados: [{score_v3_final, score_core, score_regulatorio, score_financeiro, score_rede, score_estrutural, score_completo, versao_metodologia}], meta: {...}}`.

### HIS-19.5 — Ranking Composto

- [x] Criar `healthintel_dbt/models/marts/fato/fat_ranking_composto_mensal.sql` (full refresh).
  - Colunas: `operadora_id`, `competencia_id`, `score_v3_final`, `posicao_geral`, `posicao_por_modalidade`, `variacao_posicao_3m`
  - Calcular `posicao_geral` via `RANK() OVER (PARTITION BY competencia_id ORDER BY score_v3_final DESC)`.
- [x] Criar `healthintel_dbt/models/api/api_ranking_composto_mensal.sql` (api_ans, table).
- [x] Adicionar endpoint em `api/app/routers/ranking.py`:
  - `GET /v1/rankings/composto` com filtros `competencia`, `modalidade`, `uf`, `limite`.
- [x] Schema Pydantic: `RankingCompostoResponse`.

### HIS-19.6 — Registro de Versão de Metodologia

- [x] Inserir `versao_metodologia = 'v3.0'` em `plataforma.versao_dataset` para `score_v3`.
- [x] Documentar pesos, componentes, fallback e data de vigência em `docs/CHANGELOG.md`.
- [x] Criar `docs/arquitetura/score_v3_metodologia.md` com:
  - Fórmula completa
  - Pesos por componente
  - Fontes de dados de cada componente
  - Regras de fallback
  - Comparação com v1 e v2

## Entregas esperadas

- [x] `healthintel_dbt/models/intermediate/int_score_v3_componentes.sql`
- [x] `healthintel_dbt/models/marts/fato/fat_score_v3_operadora_mensal.sql`
- [x] `healthintel_dbt/models/marts/fato/fat_ranking_composto_mensal.sql`
- [x] `healthintel_dbt/models/api/api_score_v3_operadora_mensal.sql`
- [x] `healthintel_dbt/models/api/api_ranking_composto_mensal.sql`
- [x] `api/app/services/score_v3.py`
- [x] `api/app/schemas/score_v3.py`
- [x] Endpoints `/v1/operadoras/{id}/score-v3` e `/v1/rankings/composto`
- [x] Testes singulares `assert_score_v3_*.sql`
- [x] `docs/arquitetura/score_v3_metodologia.md`

## Validação esperada

- [x] `ruff check api`
- [x] `dbt build --select tag:fato_v3` sem falhas
- [x] `dbt test --select fat_score_v3_operadora_mensal` — zero falhas
- [x] `pytest api/tests/integration/test_score_v3.py -v`
- [x] `score_v3_final BETWEEN 0 AND 100` para todos os registros (teste singular)
- [x] `versao_metodologia = 'v3.0'` presente em todos os registros
- [x] Ranking composto com posições únicas por competência (sem empate não tratado)
