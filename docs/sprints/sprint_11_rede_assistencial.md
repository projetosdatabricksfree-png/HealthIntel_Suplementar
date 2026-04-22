# Sprint 11 — Rede Assistencial

**Status:** Planejada
**Objetivo:** construir a camada de inteligência de cobertura e rede assistencial por município/UF/operadora; publicar endpoints de rede com granularidade geográfica.
**Critério de saída:** dados de rede assistencial harmonizados com integridade geográfica validada e disponíveis via API com cobertura por município e UF.

## Histórias

### HIS-11.1 — Ingerir rede assistencial

- [ ] Mapear fonte oficial: Painel Rede Credenciada ANS (dados.ans.gov.br — diretório Rede_Assistencial), periodicidade (mensal/trimestral), formato (CSV ZIP), encoding.
- [ ] Identificar granularidade do arquivo: prestador × operadora × município × segmento × especialidade.
- [ ] Criar layout registry rede assistencial em MongoDB (`fonte_dataset`, `layout`, `layout_versao`).
- [ ] Definir DDL `bruto_ans.rede_prestador_municipio`: `registro_ans`, `competencia`, `cd_municipio` (IBGE 6d), `nm_municipio`, `sg_uf`, `segmento` (medico|odonto), `tipo_prestador`, `qt_prestador`, `qt_especialidade_disponivel`, `_carregado_em`, `_arquivo_origem`, `_lote_id`. Particionamento RANGE por `competencia`.
- [ ] Criar `stg_rede_assistencial.sql` (view, `stg_ans`): cast de tipos, normalização de `cd_municipio` (6 dígitos com lpad), join com `ref_municipio_ibge` para validação, flag `municipio_valido` (bool).
- [ ] Implementar DAG `dag_ingest_rede_assistencial` sob `dag_mestre_mensal`.
- [ ] Adicionar entry em `_fontes.yml`: freshness `warn_after: {count: 60, period: day}`.

### HIS-11.2 — Harmonizar cobertura geográfica

- [ ] Criar intermediate `int_rede_assistencial_municipio.sql` (ephemeral): agrega prestadores e especialidades por operadora × município × competência; join com `dim_localidade` para enriquecer com região e UF; calcula `qt_prestador_por_10k_beneficiarios` cruzando com `fat_beneficiario_localidade`.
- [ ] Estender `dim_localidade.sql` com coluna `pop_estimada_ibge` (populaçao estimada IBGE) via seed para cálculo de densidade de rede per capita.
- [ ] Criar seed `ref_populacao_municipio.csv` com campos: `cd_municipio`, `nm_municipio`, `sg_uf`, `pop_estimada`, `ano_referencia` (fonte IBGE Estimativas).
- [ ] Criar seed `ref_parametro_rede.csv` com limiares de cobertura mínima por segmento e porte de município (pequeno/médio/grande definidos por faixa de pop_estimada).
- [ ] Criar `fat_cobertura_rede_municipio.sql` (incremental merge, `nucleo_ans`). `unique_key: [operadora_id, cd_municipio, competencia_id]`. Colunas: métricas de cobertura, `tem_cobertura` (bool: `qt_prestador > 0`), `cobertura_minima_atendida` (bool: `qt_prestador_por_10k >= limiar` do seed).

### HIS-11.3 — Publicar fatos de rede

- [ ] Criar `fat_densidade_rede_operadora.sql` (table full refresh, `nucleo_ans`): agrega `fat_cobertura_rede_municipio` por operadora/competência; calcula `qt_municipio_coberto`, `qt_uf_coberto`, `pct_municipios_cobertos` (sobre total de UFs onde opera), `score_rede` (0–100, normalizado via macro `normalizar_0_100`).
- [ ] Criar `api_rede_assistencial.sql` (api_ans, table + post-hook índices em `operadora_id`, `cd_municipio`, `competencia`): desnormalizado por operadora/município/competência com campos para os dois endpoints.
- [ ] Criar router `api/app/routers/rede.py` com endpoints:
  - `GET /v1/operadoras/{registro_ans}/rede` — retorna cobertura de rede por UF e mês da operadora.
  - `GET /v1/rede/municipio/{cd_municipio}` — retorna operadoras com cobertura no município e densidade de rede.
- [ ] Criar schemas Pydantic v2: `RedeOperadoraResponse`, `RedeMunicipioResponse`.
- [ ] Registrar `plataforma.versao_dataset` para `rede_assistencial`.
- [ ] Atualizar `models/api/_exposicao.yml` com exposures de rede.

### HIS-11.4 — Validar qualidade de rede

- [ ] Criar teste `tests/assert_cobertura_uf_completa.sql`: para cada operadora ativa com beneficiários em UF X, deve existir pelo menos 1 registro de rede para essa UF no mês (severity: warn — não falha build, registra alerta).
- [ ] Criar teste `tests/assert_municipio_ibge_valido.sql`: `cd_municipio` em `stg_rede_assistencial` deve existir em `ref_municipio_ibge` (severity: error).
- [ ] Criar teste `tests/assert_rede_sem_operadora_fantasma.sql`: todo `registro_ans` em `bruto_ans.rede_prestador_municipio` deve existir em `dim_operadora_atual` (severity: warn).
- [ ] Criar alerta de atraso em `dag_ingest_rede_assistencial`: se `max(_carregado_em)` de `bruto_ans.rede_prestador_municipio` for > 75 dias, disparar alerta via Airflow EmailOperator.
- [ ] Criar `scripts/smoke_rede.py`: valida endpoints `/v1/operadoras/{id}/rede` e `/v1/rede/municipio/{cd_municipio}` com operadora e município de referência.

## Entregas esperadas

- [ ] DDL: `bruto_ans.rede_prestador_municipio`.
- [ ] Seeds: `ref_populacao_municipio.csv`, `ref_parametro_rede.csv`.
- [ ] Layout registry MongoDB: rede assistencial.
- [ ] dbt staging: `stg_rede_assistencial`.
- [ ] dbt intermediate (ephemeral): `int_rede_assistencial_municipio`.
- [ ] dbt fatos: `fat_cobertura_rede_municipio`, `fat_densidade_rede_operadora`.
- [ ] dbt api: `api_rede_assistencial`.
- [ ] DAG: `dag_ingest_rede_assistencial`.
- [ ] Endpoints: `GET /v1/operadoras/{registro_ans}/rede`, `GET /v1/rede/municipio/{cd_municipio}`.
- [ ] Testes dbt: `assert_cobertura_uf_completa.sql`, `assert_municipio_ibge_valido.sql`, `assert_rede_sem_operadora_fantasma.sql`.
- [ ] Script: `scripts/smoke_rede.py`.
- [ ] `dim_localidade.sql` estendida com `pop_estimada_ibge`.

## Validação esperada

- [ ] `ruff check api ingestao scripts`
- [ ] `pytest -q`
- [ ] `dbt build --select tag:rede`
- [ ] `python scripts/smoke_rede.py`
- [ ] Verificação geográfica manual: query validando cobertura de municípios por UF para amostra de 3 operadoras.
