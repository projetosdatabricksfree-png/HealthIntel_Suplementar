# Sprint 10 — VDA, Glosa e Score v2

**Status:** Planejada
**Objetivo:** ampliar a camada financeira com VDA e glosa mensais, calcular o score composto v2 (core + regulatório + financeiro) e publicar endpoints financeiros e de score v2.
**Critério de saída:** plataforma passa a oferecer inteligência financeira profunda por operadora; score v2 versionado disponível na API; regressão sobre endpoints existentes aprovada sem falhas.

## Histórias

### HIS-10.1 — Ingerir VDA

- [ ] Mapear origem oficial do VDA (Valor Devido à ANS): URL portal ANS, periodicidade mensal, colunas (`registro_ans`, `competencia`, `valor_devido`, `situacao_cobranca`), encoding.
- [ ] Criar layout registry VDA em MongoDB.
- [ ] Definir DDL `bruto_ans.vda_operadora_mensal`: `registro_ans`, `competencia`, `valor_devido`, `valor_pago`, `saldo_devedor`, `situacao_cobranca` (adimplente|inadimplente|parcelado), `data_vencimento`, `_carregado_em`, `_arquivo_origem`, `_lote_id`. Particionamento RANGE por `competencia`.
- [ ] Criar `stg_vda.sql` (view, `stg_ans`): cast NUMERIC, normalização de `registro_ans` via macro `normalizar_registro_ans`, derivação de `inadimplente` (bool: `saldo_devedor > 0`).
- [ ] Criar `fat_vda_operadora_mensal.sql` (incremental merge, `nucleo_ans`). `unique_key: [operadora_id, competencia_id]`. Inclui `inadimplente`, `saldo_devedor`, `meses_inadimplente_consecutivos`.
- [ ] Implementar DAG `dag_ingest_vda` sob `dag_mestre_mensal`.
- [ ] Adicionar `stg_vda` ao `_fontes.yml` com freshness `warn_after: {count: 45, period: day}`.

### HIS-10.2 — Ingerir glosa

- [ ] Mapear dataset de glosa ANS: origem (auditoria/ressarcimento SUS), periodicidade, granularidade (operadora × mês × tipo_glosa), colunas.
- [ ] Criar layout registry glosa em MongoDB.
- [ ] Definir DDL `bruto_ans.glosa_operadora_mensal`: `registro_ans`, `competencia`, `tipo_glosa`, `qt_glosa`, `valor_glosa`, `valor_faturado`, `_carregado_em`, `_arquivo_origem`, `_lote_id`. Particionamento RANGE por `competencia`.
- [ ] Criar `stg_glosa.sql` (view, `stg_ans`): cast NUMERIC, normalização de `registro_ans`, derivação de `taxa_glosa_calculada = valor_glosa / NULLIF(valor_faturado, 0)`.
- [ ] Criar `fat_glosa_operadora_mensal.sql` (incremental merge, `nucleo_ans`). `unique_key: [operadora_id, competencia_id, tipo_glosa]`.
- [ ] Implementar DAG `dag_ingest_glosa` sob `dag_mestre_mensal`.

### HIS-10.3 — Calcular score v2

- [ ] Criar intermediate `int_score_v2_componentes.sql` (ephemeral): consolida por operadora/competência os scores normalizados: `score_core` (fat_score_operadora_mensal), `score_regulatorio` (fat_score_regulatorio_operadora_mensal), `score_financeiro_trimestral` (fat_financeiro_operadora_trimestral — interpolado para mensal via lag/last_value), `penalizacao_vda` (−5 pts se inadimplente no mês), `penalizacao_glosa` (−3 pts se `taxa_glosa_calculada` > limiar configurável via var).
- [ ] Criar `fat_score_v2_operadora_mensal.sql` (table full refresh mensal, `nucleo_ans`). Pesos v2 configuráveis via `var('score_v2_pesos')` em `dbt_project.yml`:
  - `score_core_peso: 0.40`
  - `score_regulatorio_peso: 0.30`
  - `score_financeiro_peso: 0.20`
  - `penalizacoes_peso: 0.10`
- [ ] Versionar pesos: campo `versao_metodologia = 'v2.0'` em cada registro. Futuras mudanças incrementam versão sem reescrever histórico.
- [ ] Manter truncamento em 39,99 para regime especial ativo (herdado do score regulatório — validado por join com `fat_regime_especial_historico`).
- [ ] Criar `api_score_v2_operadora_mensal.sql` (api_ans, table + post-hook índices em `operadora_id`, `competencia`, `score_v2`).
- [ ] Criar `api_financeiro_operadora_mensal.sql` (api_ans, table + post-hook índices em `operadora_id`, `competencia`): agrega VDA + glosa mensais desnormalizados.
- [ ] Criar testes `tests/assert_score_v2_entre_0_e_100.sql` e `tests/assert_score_v2_regime_especial_truncado.sql`.

### HIS-10.4 — Atualizar a API e executar regressão

- [ ] Criar router `api/app/routers/financeiro.py` com endpoints:
  - `GET /v1/operadoras/{registro_ans}/financeiro` — séries temporais de indicadores DIOPS/FIP/VDA/glosa.
  - `GET /v1/operadoras/{registro_ans}/score-v2` — histórico de score v2 mensal com sub-scores por componente.
- [ ] Criar schemas Pydantic v2: `FinanceiroResponse`, `ScoreV2Response` com campo `componentes` (dict de sub-scores) e `versao_metodologia`.
- [ ] Atualizar `models/api/_exposicao.yml` com exposures para financeiro e score v2.
- [ ] Registrar `plataforma.versao_dataset` para `vda`, `glosa`, `score_v2`.
- [ ] Criar `testes/regressao/test_endpoints_fase1.py` cobrindo todos os endpoints das sprints 04, 07 e 08: `/v1/operadoras`, `/v1/operadoras/{id}`, `/v1/operadoras/{id}/score`, `/v1/mercado/municipio`, `/v1/rankings/operadora/score`, `/v1/operadoras/{id}/regulatorio`, `/v1/regulatorio/rn623`, `/v1/operadoras/{id}/score-regulatorio`, `/v1/operadoras/{id}/regime-especial`, `/v1/operadoras/{id}/portabilidade`.
- [ ] Executar suite de regressão: `pytest testes/regressao/` — zero falhas como critério de saída obrigatório.

## Entregas esperadas

- [ ] DDL: `bruto_ans.vda_operadora_mensal`, `bruto_ans.glosa_operadora_mensal`.
- [ ] Layout registry MongoDB: VDA e glosa.
- [ ] dbt staging: `stg_vda`, `stg_glosa`.
- [ ] dbt fatos: `fat_vda_operadora_mensal`, `fat_glosa_operadora_mensal`, `fat_score_v2_operadora_mensal`.
- [ ] dbt api: `api_score_v2_operadora_mensal`, `api_financeiro_operadora_mensal`.
- [ ] DAGs: `dag_ingest_vda`, `dag_ingest_glosa`.
- [ ] Endpoints: `GET /v1/operadoras/{registro_ans}/financeiro`, `GET /v1/operadoras/{registro_ans}/score-v2`.
- [ ] Testes dbt: `assert_score_v2_entre_0_e_100.sql`, `assert_score_v2_regime_especial_truncado.sql`.
- [ ] Suite regressão: `testes/regressao/test_endpoints_fase1.py`.
- [ ] `dbt_project.yml` com var `score_v2_pesos`.

## Validação esperada

- [ ] `ruff check api ingestao scripts`
- [ ] `pytest -q`
- [ ] `pytest testes/regressao/ -v` — zero regressões (hard gate)
- [ ] `dbt build --select tag:financeiro_v2 tag:score_v2`
- [ ] Verificação de latência: p95 de `GET /v1/operadoras/{id}/score-v2` < 200ms com Redis warm.
