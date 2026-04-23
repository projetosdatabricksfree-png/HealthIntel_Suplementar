# Sprint 18 — Datasets Complementares

**Status:** Não iniciada
**Objetivo:** mapear e integrar os datasets fora do MVP que têm publicação ANS viável (QUALISS, IEPRS, reajustes coletivos); criar placeholders formais para os que ainda não têm publicação regular; fechar o catálogo de datasets com todos os conjuntos de dados mapeados.
**Critério de saída:** catálogo de datasets completo e atualizado; QUALISS e IEPRS com DDL + layout registry + DAG definidos; reajustes com análise de viabilidade documentada; placeholders formais para datasets futuros.

## Histórias

### HIS-18.1 — QUALISS

- [ ] Avaliar publicação ANS de QUALISS: verificar URL de download, formato (CSV/ZIP), frequência de publicação, estrutura de campos.
- [ ] Se publicação viável:
  - Criar DDL `bruto_ans.qualiss_operadora` em `infra/postgres/init/016_qualiss.sql`. Particionamento por `competencia` (RANGE). Colunas esperadas: `registro_ans`, `competencia`, `indicador_cd`, `indicador_ds`, `resultado_vl`, `meta_vl`, `resultado_normalizado`, `_carregado_em`, `_arquivo_origem`, `_lote_id`, `_hash_arquivo`.
  - Criar layout registry em MongoDB: `bootstrap_layout_registry_qualiss.py` em `scripts/`.
  - Criar DAG `ingestao/dags/dag_ingest_qualiss.py` sob `dag_mestre_mensal`.
  - Criar staging dbt `healthintel_dbt/models/staging/stg_qualiss.sql`.
  - Adicionar entrada em `_sources.yml` com freshness SLO.
- [ ] Se publicação inviável: documentar decisão em `docs/catalogo_datasets.md` com motivo e data de reavaliação.
- [ ] Integrar `qualidade_qualiss` como componente auxiliar do score regulatório em `int_regulatorio_v2_operadora_trimestre.sql` (quando disponível).

### HIS-18.2 — IEPRS (Índice de Desempenho da Atenção Primária)

- [ ] Avaliar publicação ANS de IEPRS: URL, formato, periodicidade, campos disponíveis.
- [ ] Se publicação viável:
  - Criar DDL `bruto_ans.ieprs_operadora` em `infra/postgres/init/017_ieprs.sql`. Colunas esperadas: `registro_ans`, `competencia`, `dimensao`, `indicador`, `resultado`, `peso`, `pontuacao`, `_carregado_em`, `_lote_id`, `_hash_arquivo`.
  - Criar layout registry `scripts/bootstrap_layout_registry_ieprs.py`.
  - Criar DAG `ingestao/dags/dag_ingest_ieprs.py`.
  - Criar staging `stg_ieprs.sql`.
  - Criar intermediate `int_ieprs_normalizado.sql` (normalização 0–100).
  - Integrar como componente no score regulatório com peso parametrizável em `dbt_project.yml`.
- [ ] Se inviável: placeholder formal documentado.

### HIS-18.3 — Reajustes Coletivos

- [ ] Avaliar formato de publicação ANS: reajustes coletivos são publicados via tabela no site ANS ou via PDF. Verificar se há CSV estruturado disponível.
- [ ] Se CSV disponível:
  - DDL `bruto_ans.reajuste_coletivo` em `infra/postgres/init/018_reajuste.sql`. Campos: `registro_ans`, `ano_reajuste`, `indice_aplicado`, `data_vigencia`, `tipo_contrato`, `_carregado_em`, `_lote_id`, `_hash_arquivo`.
  - Layout registry + DAG + staging.
- [ ] Se apenas PDF/HTML: documentar limitação, criar `scripts/parser_reajuste_coletivo.py` como placeholder com instrução de uso manual.
- [ ] Independente do formato: criar `docs/arquitetura/reajuste_coletivo_analise.md` com resultado da análise de viabilidade.

### HIS-18.4 — Valores Comerciais (Placeholder Fase 5)

- [ ] Criar DDL placeholder `bruto_ans.valores_comerciais_plano` em `infra/postgres/init/019_valores_comerciais_placeholder.sql` com comentário `-- Placeholder: sem publicação ANS estruturada. Reavaliação programada para Fase 5.`
- [ ] Criar entrada em `docs/catalogo_datasets.md` com status `placeholder` e motivação.
- [ ] Não criar DAG nem layout registry (dataset não operacional).

### HIS-18.5 — Catálogo de Datasets Completo

- [ ] Atualizar `docs/catalogo_datasets.md` com todos os datasets mapeados, incluindo:

  | Dataset | Schema | Tabela bronze | Status | DAG | Staging dbt | Freshness SLO | Publicação ANS |
  |---------|--------|---------------|--------|-----|-------------|---------------|----------------|
  | CADOP | bruto_ans | cadop | Ativo | dag_ingest_cadop | stg_cadop | 30d warn / 60d error | ANS Open Data |
  | SIB operadora | bruto_ans | sib_beneficiario_operadora | Ativo | dag_mestre_mensal | stg_sib_operadora | 45d warn / 90d error | ANS/SIB |
  | SIB município | bruto_ans | sib_beneficiario_municipio | Ativo | dag_mestre_mensal | stg_sib_municipio | 45d warn / 90d error | ANS/SIB |
  | IGR | bruto_ans | igr_operadora_trimestral | Ativo | dag_trimestral | stg_igr | 95d warn / 120d error | ANS/IGR |
  | NIP | bruto_ans | nip_operadora_trimestral | Ativo | dag_trimestral | stg_nip | 95d warn / 120d error | ANS/NIP |
  | RN 623 | bruto_ans | rn623_lista_operadora | Ativo | dag_trimestral | stg_rn623_lista | 95d warn / 120d error | ANS/RN623 |
  | IDSS | bruto_ans | idss_operadora_anual | Ativo | dag_anual_idss | stg_idss | 365d warn / 400d error | ANS/IDSS |
  | DIOPS | bruto_ans | diops_operadora_trimestral | Ativo | dag_trimestral | stg_diops | 95d warn / 120d error | ANS/DIOPS |
  | FIP | bruto_ans | fip_operadora_trimestral | Ativo | dag_trimestral | stg_fip | 95d warn / 120d error | ANS/FIP |
  | VDA | bruto_ans | vda_operadora_mensal | Ativo | dag_mestre_mensal | stg_vda | 45d warn / 90d error | ANS/VDA |
  | Glosa | bruto_ans | glosa_operadora_mensal | Ativo | dag_mestre_mensal | stg_glosa | 45d warn / 90d error | ANS |
  | Rede Assistencial | bruto_ans | rede_prestador_municipio | Ativo | dag_ingest_rede | stg_rede_assistencial | 60d warn / 120d error | ANS/CNES-Rede |
  | Regime Especial | bruto_ans | regime_especial_operadora | Ativo | dag_trimestral | stg_regime_especial | 95d warn / 120d error | ANS |
  | Prudencial | bruto_ans | prudencial_operadora_trimestral | Ativo | dag_trimestral | stg_prudencial | 95d warn / 120d error | ANS |
  | Portabilidade | bruto_ans | portabilidade_operadora_mensal | Ativo | dag_mestre_mensal | stg_portabilidade | 45d warn / 90d error | ANS |
  | Taxa Resolutividade | bruto_ans | taxa_resolutividade_operadora | Ativo | dag_trimestral | stg_taxa_resolutividade | 95d warn / 120d error | ANS |
  | CNES | bruto_ans | cnes_estabelecimento | Sprint 13 | dag_ingest_cnes | stg_cnes (pendente) | 60d warn / 90d error | DATASUS/CNES |
  | TISS | bruto_ans | tiss_procedimento_trimestral | Sprint 14 | dag_ingest_tiss | stg_tiss (pendente) | 95d warn / 120d error | ANS/TISS |
  | QUALISS | bruto_ans | qualiss_operadora | Sprint 18 | dag_ingest_qualiss | stg_qualiss | A definir | ANS/QUALISS |
  | IEPRS | bruto_ans | ieprs_operadora | Sprint 18 | dag_ingest_ieprs | stg_ieprs | A definir | ANS |
  | Reajustes Coletivos | bruto_ans | reajuste_coletivo | Sprint 18 | Manual/parser | stg_reajuste | Anual | ANS |
  | Valores Comerciais | bruto_ans | valores_comerciais_plano | Placeholder (Fase 5) | — | — | — | Não disponível |

## Entregas esperadas

- [ ] DDL `infra/postgres/init/016_qualiss.sql` (ou análise documentada)
- [ ] DDL `infra/postgres/init/017_ieprs.sql` (ou análise documentada)
- [ ] DDL `infra/postgres/init/018_reajuste.sql` (ou análise documentada)
- [ ] DDL `infra/postgres/init/019_valores_comerciais_placeholder.sql`
- [ ] Scripts de layout registry para datasets viáveis
- [ ] DAGs para datasets viáveis
- [ ] Staging dbt para datasets viáveis
- [ ] `docs/catalogo_datasets.md` completo com todos os 22 datasets
- [ ] `docs/arquitetura/reajuste_coletivo_analise.md`

## Validação esperada

- [ ] `ruff check ingestao scripts`
- [ ] `dbt compile` sem erros com novos staging models
- [ ] `dbt source freshness` sem erros para datasets ativos (incluindo novos)
- [ ] `docs/catalogo_datasets.md` contém entrada para todos os 22 datasets
- [ ] Análise de viabilidade documentada para QUALISS, IEPRS e reajustes
