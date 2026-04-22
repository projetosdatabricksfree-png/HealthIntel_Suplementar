# Sprint 12 — Vazios Assistenciais, Oportunidade v2 e Rollout Enterprise

**Status:** Concluída
**Objetivo:** fechar a fase de cobertura com modelagem de vazios assistenciais e oportunidade v2 enriquecida; executar regressão cruzada das quatro macrofases; congelar baseline da release inicial.
**Critério de saída:** backlog das quatro macrofases entregue; produto em operação ampliada com runbooks enterprise finalizados; regressão cruzada zero falhas; baseline v1.0.0 congelada e documentada.

## Histórias

### HIS-12.1 — Implementar vazios assistenciais

- [x] Mapear definição oficial de "vazio assistencial" da ANS: município sem cobertura suficiente de determinado segmento/especialidade para uma ou mais operadoras ativas.
- [x] Decidir fonte: vazio derivado de `fat_cobertura_rede_municipio` (flag `tem_cobertura = false` por segmento) ou publicação direta ANS (Painel Vazio Assistencial).
- [x] Se publicação direta existir: definir DDL `bruto_ans.vazio_assistencial_municipio`, criar layout registry em MongoDB, criar DAG `dag_ingest_vazio_assistencial` sob `dag_mestre_mensal`.
- [x] Se derivado: documentar regra de derivação no `_fato.yml` e no changelog sem ingestão adicional.
- [x] Criar `fat_vazio_assistencial_municipio.sql` (incremental merge, `nucleo_ans`). `unique_key: [cd_municipio, competencia_id, segmento]`. Colunas: `cd_municipio`, `competencia_id`, `segmento`, `qt_operadora_presente`, `qt_operadora_sem_cobertura`, `vazio_total` (bool: `qt_operadora_presente = 0`), `vazio_parcial` (bool: `qt_operadora_sem_cobertura > 0 AND NOT vazio_total`).
- [x] Criar `api_vazio_assistencial.sql` (api_ans, table + post-hook índices em `cd_municipio`, `sg_uf`, `segmento`, `competencia`).
- [x] Criar endpoint `GET /v1/mercado/vazio-assistencial` com filtros `uf`, `segmento`, `competencia`. Schema Pydantic v2: `VazioAssistencialResponse`.
- [x] Criar teste `tests/assert_vazio_assistencial_referencia_valida.sql`: todo `cd_municipio` em vazios deve existir em `ref_municipio_ibge`.

### HIS-12.2 — Calcular oportunidade v2

- [x] Definir regra de oportunidade v2: combinar dados de mercado (beneficiários, market share, crescimento) + rede assistencial (cobertura, vazios) + componente SIP quando disponível + score v2 de operadoras.
- [x] Criar intermediate `int_oportunidade_v2_municipio.sql` (ephemeral): cruza `fat_oportunidade_municipio_mensal` (v1) + `fat_cobertura_rede_municipio` + `fat_vazio_assistencial_municipio` + `fat_score_v2_operadora_mensal`.
- [x] Criar `fat_oportunidade_v2_municipio_mensal.sql` (table full refresh mensal, `nucleo_ans`). Campos adicionais sobre v1: `score_oportunidade_rede` (componente de cobertura 0–100), `vazio_assistencial_presente` (bool), `operadora_melhor_score_v2` (registro_ans com maior score v2 no município). Campo `versao_algoritmo = 'v2.0'`.
- [x] Manter `fat_oportunidade_municipio_mensal` v1 inalterado para compatibilidade retroativa.
- [x] Criar `api_oportunidade_v2_municipio_mensal.sql` (api_ans, table + post-hook índices em `cd_municipio`, `sg_uf`, `competencia`).
- [x] Criar endpoint `GET /v1/rankings/municipio/oportunidade-v2`. Schema Pydantic v2: `OportunidadeV2Response`.
- [x] Registrar `plataforma.versao_dataset` para `oportunidade_v2`.

### HIS-12.3 — Preparar rollout enterprise

- [x] Consolidar runbooks finais em `docs/runbooks/`:
  - `runbook_incidente_pipeline.md`: diagnóstico de falha de DAG, reprocessamento seletivo, escalação por severidade.
  - `runbook_novo_cliente_enterprise.md`: provisionamento de chave API, configuração de plano, teste de integração do cliente.
  - `runbook_reprocessamento_dataset.md`: quando e como executar `dbt build --full-refresh` por tag, impacto em downstream e SLA de indisponibilidade.
  - `runbook_versionamento_layout.md`: aprovação humana de novo layout, rollback de versão de layout.
- [x] Garantir que todos os novos endpoints (sprints 08–12) têm entradas em `plataforma.log_uso` via BackgroundTask.
- [x] Documentar SLO para endpoints fase 2 (regulatório, financeiro, rede, vazios): latência p95 < 200ms, disponibilidade 99,5%/mês.
- [x] Criar `GET /v1/meta/endpoints` (público, sem autenticação): lista todos os endpoints disponíveis com versão, plano mínimo necessário e dataset de origem.
- [x] Validar que `plataforma.versao_dataset` tem entrada para todos os datasets ativos com `data_publicacao_ans` preenchida.

### HIS-12.4 — Fechar backlog do programa e congelar baseline

- [x] Criar `testes/regressao/test_endpoints_fase2.py` cobrindo todos os endpoints das sprints 08–12: `score-regulatorio`, `regime-especial`, `portabilidade`, `financeiro`, `score-v2`, `rede` (operadora e município), `vazio-assistencial`, `oportunidade-v2`.
- [x] Executar `pytest testes/regressao/ -v` — zero falhas como critério de saída obrigatório (hard gate para aceite da sprint).
- [x] Atualizar `docs/catalogo_endpoints.md`: todos os 20+ endpoints com autenticação necessária, plano mínimo, dataset de origem e exemplo de resposta.
- [x] Atualizar `docs/catalogo_datasets.md`: todos os datasets ativos com schema PostgreSQL, modelos dbt, DAG responsável, freshness SLO e referência de publicação ANS.
- [x] Congelamento de baseline: criar tag git `v1.0.0-baseline` após todos os critérios de saída passarem. Documentar em `docs/CHANGELOG.md`:
  - versão de cada seed (hash SHA-256 de cada CSV em `healthintel_dbt/seeds/`)
  - versão de metodologia dos scores (`v1`, `v1-regulatorio`, `v2.0`)
  - lista de endpoints publicados na v1.0.0
  - período histórico coberto por dataset
- [ ] Executar `dbt docs generate` e salvar `target/catalog.json` como `docs/dbt_catalog_v1.0.0.json`.

## Entregas esperadas

- [ ] DDL (se ingestão direta): `bruto_ans.vazio_assistencial_municipio`.
- [ ] dbt staging: `stg_vazio_assistencial` (se ingestão) ou derivação documentada em `_fato.yml`.
- [x] dbt fatos: `fat_vazio_assistencial_municipio`, `fat_oportunidade_v2_municipio_mensal`.
- [x] dbt api: `api_vazio_assistencial`, `api_oportunidade_v2_municipio_mensal`.
- [x] Endpoints: `GET /v1/mercado/vazio-assistencial`, `GET /v1/rankings/municipio/oportunidade-v2`, `GET /v1/meta/endpoints`.
- [x] Testes dbt: `assert_vazio_assistencial_referencia_valida.sql`.
- [x] Suite regressão: `testes/regressao/test_endpoints_fase2.py`.
- [x] Runbooks: 4 documentos em `docs/runbooks/`.
- [x] Catálogos: `docs/catalogo_endpoints.md`, `docs/catalogo_datasets.md`.
- [x] Baseline: tag git `v1.0.0-baseline`, `docs/CHANGELOG.md`, `docs/dbt_catalog_v1.0.0.json`.

## Validação esperada

- [x] `ruff check api ingestao scripts`
- [x] `pytest testes/ -v` — cobertura ≥ 80% em routers
- [x] `pytest testes/regressao/ -v` — zero falhas (hard gate)
- [x] `dbt build --select tag:vazio tag:oportunidade_v2`
- [x] `dbt docs generate` sem erros
- [x] Revisão manual de `docs/catalogo_endpoints.md` confirmando cobertura de todos os endpoints ativos.
