# Sprint 09 — DIOPS, FIP e Harmonização Financeira

**Status:** Concluída
**Objetivo:** iniciar a fase financeira com ingestão e padronização dos datasets econômico-financeiros, publicar fato financeiro trimestral harmonizado e versionar publicações financeiras.
**Critério de saída:** fatos financeiros básicos (solvência, liquidez, resultado, sinistralidade) disponíveis em marts e preparados para composição do score v2 na Sprint 10.

## Histórias

### HIS-09.1 — Ingerir DIOPS

- [x] Mapear formato vigente do DIOPS: URL no portal ANS/dados.gov.br, periodicidade (trimestral + anual), colunas publicadas (demonstração de resultado, balanço patrimonial, DFC), encoding.
- [x] Criar layout registry financeiro DIOPS em MongoDB (`fonte_dataset`, `layout`, `layout_versao`).
- [x] Definir DDL `bruto_ans.diops_operadora_trimestral` com colunas: `registro_ans`, `trimestre`, `cnpj`, `ativo_total`, `passivo_total`, `patrimonio_liquido`, `receita_total`, `despesa_total`, `resultado_periodo`, `provisao_tecnica`, `margem_solvencia_calculada`, `_carregado_em`, `_arquivo_origem`, `_lote_id`. Particionamento RANGE por `trimestre`.
- [x] Criar `stg_diops.sql` (view, `stg_ans`): cast NUMERIC em todos os campos monetários, normalização de `registro_ans` via macro `normalizar_registro_ans`, derivação de `resultado_operacional = receita_total - despesa_total`.
- [x] Implementar DAG `dag_ingest_diops` sob extensão de `dag_trimestral`. Periodicidade: trimestral com run anual de reprocessamento completo.
- [x] Adicionar `stg_diops` ao `_fontes.yml` com freshness `warn_after: {count: 120, period: day}`.

### HIS-09.2 — Ingerir FIP

- [x] Mapear arquivos e periodicidade do FIP (Formulário de Informações Periódicas): URL portal ANS, granularidade temporal, colunas.
- [x] Criar layout registry FIP em MongoDB.
- [x] Definir DDL `bruto_ans.fip_operadora_trimestral` com colunas: `registro_ans`, `trimestre`, `modalidade`, `tipo_contratacao`, `sinistro_total`, `contraprestacao_total`, `sinistralidade_bruta`, `ressarcimento_sus`, `evento_indenizavel`, `_carregado_em`, `_arquivo_origem`, `_lote_id`. Particionamento RANGE por `trimestre`.
- [x] Criar `stg_fip.sql` (view, `stg_ans`): cast NUMERIC, normalização de `registro_ans`, cálculo de `sinistralidade_liquida = sinistro_total - ressarcimento_sus`.
- [x] Implementar DAG `dag_ingest_fip` sob `dag_trimestral`.
- [x] Adicionar `stg_fip` ao `_fontes.yml` com freshness `warn_after: {count: 120, period: day}`.

### HIS-09.3 — Harmonizar fatos financeiros

- [x] Criar tabela `plataforma.publicacao_financeira` via Alembic (análogo a `plataforma.publicacao_regulatoria`): `id` (serial PK), `dataset` (text), `trimestre` (text), `data_publicacao_ans` (date), `data_carga` (timestamptz), `versao_arquivo` (text), `hash_sha256` (text), `observacao` (text).
- [x] Criar intermediate `int_financeiro_operadora_periodo.sql` (ephemeral): join DIOPS × FIP por operadora/trimestre, cálculo de: `indice_sinistralidade`, `margem_liquida`, `cobertura_provisao` (provisao_tecnica / (sinistro_total/4)), `resultado_normalizado` via macro `normalizar_0_100`.
- [x] Criar `fat_financeiro_operadora_trimestral.sql` (incremental merge, `nucleo_ans`). `unique_key: [operadora_id, trimestre]`. Inclui métricas DIOPS + FIP harmonizadas. Reprocessa últimas 4 competências trimestrais.
- [x] Criar seed `ref_indicador_financeiro.csv` com campos: `indicador`, `formula`, `sentido` (maior_melhor|menor_melhor), `intervalo_minimo`, `intervalo_maximo`.
- [x] Incorporar `parto_cesareo_pct` como coluna qualitativa opcional em `fat_financeiro_operadora_trimestral` quando disponível via IDSS/seed.

### HIS-09.4 — Validar a fundação financeira

- [x] Criar teste `tests/assert_indicadores_financeiros_nao_negativos.sql` (`sinistro_total`, `contraprestacao_total`, `provisao_tecnica` ≥ 0).
- [x] Criar teste `tests/assert_sinistralidade_entre_0_e_2.sql` (`sinistralidade_bruta` entre 0 e 2 — valores acima de 1 são normais em crise mas acima de 2 indicam erro de carga).
- [x] Criar `scripts/smoke_financeiro.py`: executa `dbt build --select tag:financeiro`, valida row count em `fat_financeiro_operadora_trimestral` com cobertura de pelo menos 8 trimestres.
- [x] Validar reprocessamento histórico: `dbt build --select fat_financeiro_operadora_trimestral --full-refresh` e confirmar cobertura ≥ 8 trimestres por query de contagem.

## Entregas esperadas

- [x] DDL: `bruto_ans.diops_operadora_trimestral`, `bruto_ans.fip_operadora_trimestral`, `plataforma.publicacao_financeira`.
- [x] Layout registry MongoDB: DIOPS e FIP com `fonte_dataset`, `layout`, `layout_versao`.
- [x] dbt staging: `stg_diops`, `stg_fip`.
- [x] dbt intermediate (ephemeral): `int_financeiro_operadora_periodo`.
- [x] dbt fato: `fat_financeiro_operadora_trimestral`.
- [x] dbt seed: `ref_indicador_financeiro.csv`.
- [x] DAGs: `dag_ingest_diops`, `dag_ingest_fip`.
- [x] Testes dbt: `assert_indicadores_financeiros_nao_negativos.sql`, `assert_sinistralidade_entre_0_e_2.sql`.
- [x] Script: `scripts/smoke_financeiro.py`.
- [x] `_fontes.yml` atualizado com entries de freshness para DIOPS e FIP.

## Validação esperada

- [x] `ruff check api ingestao scripts`
- [x] `pytest -q`
- [x] `dbt build --select tag:financeiro`
- [x] `python scripts/smoke_financeiro.py`
- [x] Reprocessamento histórico: `dbt build --select fat_financeiro_operadora_trimestral --full-refresh` com cobertura ≥ 8 trimestres validada por query de contagem.
