# Sprint 08 — Score Regulatório, Prudencial e Portabilidade

**Status:** Planejada
**Objetivo:** consolidar fatos regulatórios completos (regime especial, prudencial, portabilidade, taxa de resolutividade) e publicar o primeiro score regulatório composto.
**Critério de saída:** API e marts regulatórios expõem risco regulatório rastreável; operadoras em regime especial têm score truncado em 39,99 e rating D/E validado por teste automatizado.

## Histórias

### HIS-08.1 — Ingerir regime especial e taxa de resolutividade

- [ ] Mapear publicação ANS de regime especial (direção fiscal e técnica): URL, periodicidade, formato CSV/XLS, encoding.
- [ ] Criar layout registry para regime especial em MongoDB (`fonte_dataset`, `layout`, `layout_versao`).
- [ ] Definir DDL `bruto_ans.regime_especial_operadora_trimestral` com colunas: `registro_ans`, `trimestre`, `tipo_regime` (direcao_fiscal|direcao_tecnica|liquidacao|cancelamento), `data_inicio`, `data_fim`, `_carregado_em`, `_arquivo_origem`, `_lote_id`. Particionamento RANGE por `trimestre`.
- [ ] Implementar DAG `dag_ingest_regime_especial` sob `dag_trimestral`.
- [ ] Mapear publicação de taxa de resolutividade ANS (periodicidade, colunas, fonte).
- [ ] Definir DDL `bruto_ans.taxa_resolutividade_operadora_trimestral` com colunas: `registro_ans`, `trimestre`, `taxa_resolutividade`, `n_reclamacao_resolvida`, `n_reclamacao_total`, `_carregado_em`, `_arquivo_origem`, `_lote_id`. Particionamento RANGE por `trimestre`.
- [ ] Implementar DAG `dag_ingest_taxa_resolutividade` sob `dag_trimestral`.
- [ ] Criar `stg_regime_especial.sql` (view) com cast de tipos, normalização de `registro_ans` via macro `normalizar_registro_ans`, derivação de `ativo` (bool: `data_fim IS NULL OR data_fim > current_date`).
- [ ] Criar `stg_taxa_resolutividade.sql` (view) com cast NUMERIC, normalização de trimestre via macro `competencia_para_data`, join com `ref_modalidade`.

### HIS-08.2 — Ingerir prudencial e portabilidade

- [ ] Mapear publicação ANS de dados prudenciais: margem de solvência, capital mínimo, índice de liquidez — URL, periodicidade, colunas.
- [ ] Criar layout registry prudencial em MongoDB.
- [ ] Definir DDL `bruto_ans.prudencial_operadora_trimestral` com colunas: `registro_ans`, `trimestre`, `margem_solvencia`, `capital_minimo_requerido`, `capital_disponivel`, `indice_liquidez`, `situacao_prudencial`, `_carregado_em`, `_arquivo_origem`, `_lote_id`. Particionamento RANGE por `trimestre`.
- [ ] Implementar DAG `dag_ingest_prudencial` sob `dag_trimestral` (conforme hierarquia PRD seção 8.1).
- [ ] Mapear publicação ANS de portabilidade: movimentação de beneficiários por operadora/mês.
- [ ] Criar layout registry portabilidade em MongoDB.
- [ ] Definir DDL `bruto_ans.portabilidade_operadora_mensal` com colunas: `registro_ans`, `competencia`, `modalidade`, `tipo_contratacao`, `qt_portabilidade_entrada`, `qt_portabilidade_saida`, `_carregado_em`, `_arquivo_origem`, `_lote_id`. Particionamento RANGE por `competencia`.
- [ ] Implementar DAG `dag_ingest_portabilidade` sob `dag_mestre_mensal`.
- [ ] Criar `stg_prudencial.sql` (view): cast NUMERIC, normalização de `registro_ans`, flag `situacao_inadequada` (bool).
- [ ] Criar `stg_portabilidade.sql` (view): cast de tipos, normalização de `competencia` via macro `competencia_para_data`.

### HIS-08.3 — Modelar fatos regulatórios e score regulatório composto

- [ ] Criar `fat_regime_especial_historico.sql` (incremental merge, `nucleo_ans`). `unique_key: [operadora_id, trimestre_inicio]`. Colunas: `operadora_id` (FK snap_operadora), `trimestre_inicio`, `trimestre_fim`, `tipo_regime`, `ativo`, `duracao_trimestres`. Reprocessa últimas 4 competências.
- [ ] Criar intermediate `int_regulatorio_v2_operadora_trimestre.sql` (ephemeral) unificando IGR + NIP + RN 623 + regime especial + prudencial + taxa_resolutividade por operadora/trimestre com normalização 0–100 via macro `normalizar_0_100`.
- [ ] Criar `fat_score_regulatorio_operadora_mensal.sql` (table full refresh mensal, `nucleo_ans`). Pesos configuráveis via `var('score_regulatorio_pesos')` em `dbt_project.yml`:
  - `igr_peso: 0.30`
  - `nip_peso: 0.25`
  - `rn623_peso: 0.15`
  - `prudencial_peso: 0.20`
  - `taxa_resolutividade_peso: 0.10`
- [ ] Implementar regra de truncamento: operadoras com `regime_especial_ativo = true` têm `score_regulatorio` truncado em `39.99` e `rating` forçado para `D` ou `E` conforme PRD seção 10.
- [ ] Criar teste `tests/assert_score_regulatorio_entre_0_e_100.sql`.
- [ ] Criar teste `tests/assert_regime_especial_truncado_39.sql` validando que nenhuma operadora em regime ativo tem score > 39.99.

### HIS-08.4 — Expor serviços regulatórios e atualizar metadados

- [ ] Criar `api_score_regulatorio_operadora_mensal.sql` (table, `api_ans`) com macro `criar_indices(['operadora_id', 'competencia', 'score_regulatorio'])`.
- [ ] Criar `api_regime_especial_operadora.sql` (table, `api_ans`) com índice em `operadora_id` e `ativo`.
- [ ] Criar router `api/app/routers/regulatorio_v2.py` com endpoints:
  - `GET /v1/operadoras/{registro_ans}/score-regulatorio` — retorna histórico de score regulatório por competência com componentes.
  - `GET /v1/operadoras/{registro_ans}/regime-especial` — retorna histórico de regime especial com períodos e tipo.
  - `GET /v1/operadoras/{registro_ans}/portabilidade` — retorna movimentação de portabilidade mensal.
- [ ] Criar schemas Pydantic v2: `ScoreRegulatorioResponse`, `RegimeEspecialResponse`, `PortabilidadeResponse`.
- [ ] Registrar `plataforma.versao_dataset` para `regime_especial`, `prudencial`, `portabilidade`, `taxa_resolutividade`.
- [ ] Atualizar `models/api/_exposicao.yml` com novos exposures.
- [ ] Criar `scripts/bootstrap_layout_registry_regulatorio_v2.py` para novos datasets.
- [ ] Adicionar testes de contrato: validar schema de resposta de cada endpoint via `pytest` com httpx.

## Entregas esperadas

- [ ] DDL: `bruto_ans.regime_especial_operadora_trimestral`, `bruto_ans.prudencial_operadora_trimestral`, `bruto_ans.portabilidade_operadora_mensal`, `bruto_ans.taxa_resolutividade_operadora_trimestral`.
- [ ] Layout registry MongoDB: 4 novos datasets com `fonte_dataset`, `layout`, `layout_versao`.
- [ ] dbt staging: `stg_regime_especial`, `stg_prudencial`, `stg_portabilidade`, `stg_taxa_resolutividade`.
- [ ] dbt intermediate (ephemeral): `int_regulatorio_v2_operadora_trimestre`.
- [ ] dbt fatos: `fat_regime_especial_historico`, `fat_score_regulatorio_operadora_mensal`.
- [ ] dbt api: `api_score_regulatorio_operadora_mensal`, `api_regime_especial_operadora`.
- [ ] DAGs: `dag_ingest_regime_especial`, `dag_ingest_prudencial`, `dag_ingest_portabilidade`, `dag_ingest_taxa_resolutividade`.
- [ ] Endpoints: `GET /v1/operadoras/{registro_ans}/score-regulatorio`, `GET /v1/operadoras/{registro_ans}/regime-especial`, `GET /v1/operadoras/{registro_ans}/portabilidade`.
- [ ] Testes dbt: `assert_score_regulatorio_entre_0_e_100.sql`, `assert_regime_especial_truncado_39.sql`.
- [ ] `dbt_project.yml` com var `score_regulatorio_pesos`.
- [ ] Script: `scripts/bootstrap_layout_registry_regulatorio_v2.py`.

## Validação esperada

- [ ] `ruff check api ingestao scripts`
- [ ] `pytest -q`
- [ ] `dbt build --select tag:regulatorio_v2`
- [ ] `python scripts/bootstrap_layout_registry_regulatorio_v2.py`
- [ ] `python scripts/smoke_regulatorio_v2.py` (valida endpoints + truncamento regime especial)
