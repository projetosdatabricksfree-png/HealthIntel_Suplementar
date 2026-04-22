# Sprint 07 — IGR, NIP e RN 623

**Status:** Concluida
**Objetivo:** iniciar a fase regulatoria com ingestao e padronizacao das bases regulatórias prioritarias.
**Criterio de saida:** datasets regulatorios principais ficam disponiveis em bronze, staging e API basica.

## Historias

### HIS-07.1 — Ingerir IGR

- [x] Mapear fonte oficial e contrato de coleta do IGR.
- [x] Implementar layout registry para IGR.
- [x] Carregar IGR em `bruto_ans`.

### HIS-07.2 — Ingerir NIP

- [x] Mapear publicacao oficial de NIP.
- [x] Implementar parsing e carga em bronze.
- [x] Criar staging regulatorio para NIP.

### HIS-07.3 — Ingerir listas da RN 623

- [x] Mapear as listas trimestrais de excelencia e reducao.
- [x] Registrar versao de publicacao por trimestre.
- [x] Carregar listas em schema core.

### HIS-07.4 — Preparar historico regulatorio

- [x] Versionar mudancas metodologicas por dataset.
- [x] Garantir compatibilidade de layout entre publicacoes.
- [x] Registrar lineage e origem de cada arquivo regulatorio.

## Entregas implementadas

- [x] DDL regulatoria com `bruto_ans.igr_operadora_trimestral`, `bruto_ans.nip_operadora_trimestral`, `bruto_ans.rn623_lista_operadora_trimestral` e `plataforma.publicacao_regulatoria`.
- [x] Layout registry regulatorio com bootstrap em `scripts/bootstrap_layout_registry_regulatorio.py`.
- [x] Seed demo regulatorio com publicacao versionada em `scripts/seed_demo_regulatorio.py`.
- [x] Camada dbt `stg_igr`, `stg_nip`, `stg_rn623_lista`, `int_regulatorio_operadora_trimestre`, `fat_monitoramento_regulatorio_trimestral`, `api_regulatorio_operadora_trimestral` e `api_rn623_lista_trimestral`.
- [x] Endpoints `GET /v1/operadoras/{registro_ans}/regulatorio` e `GET /v1/regulatorio/rn623`.
- [x] Dags `dag_ingest_igr`, `dag_ingest_nip` e `dag_ingest_rn623`.

## Validacao executada

- [x] `ruff check api ingestao scripts`
- [x] `pytest -q`
- [x] `dbt build`
- [x] `python scripts/bootstrap_layout_registry_regulatorio.py`
- [x] `python scripts/seed_demo_regulatorio.py`
- [x] `python scripts/smoke_piloto.py`

### HIS-07.5 — Ingerir IDSS e modelar fato de reclamacao

- [x] Criar DDL `bruto_ans.idss` com colunas: `registro_ans`, `ano_base`, `idss_total`, `idqs`, `idga`, `idsm`, `idgr`, `faixa_idss`, `_carregado_em`, `_arquivo_origem`, `_lote_id` — tabela anual sem particao (PRD secao 6.2).
- [x] Implementar `stg_idss.sql` (view, `stg_ans`): cast NUMERIC em todos os campos de nota, normalizacao de `registro_ans` via macro `normalizar_registro_ans`, determinacao de versao metodologica via macro `versao_metodologia_idss` (PRD secao 6.3 e 7.1).
- [x] Implementar `fat_idss_operadora.sql` (incremental merge, `nucleo_ans`). `unique_key: [operadora_id, ano_base]`. Inclui componentes `idqs`, `idga`, `idsm`, `idgr` normalizados e campo `versao_metodologia` (PRD secao 7.1).
- [x] Implementar `fat_reclamacao_operadora.sql` (incremental merge, `nucleo_ans`). `unique_key: [operadora_id, competencia_id]`. Derivado de `stg_nip` ou fonte ANS separada; campos: `n_reclamacao_total`, `n_reclamacao_resolvida`, `taxa_resolucao`, `indice_reclamacao_por_beneficiario` (PRD secao 7.1).
- [x] Implementar `dag_anual_idss` (trigger manual apos publicacao ANS) com sub-tarefas: `dag_ingest_idss` → `dag_dbt_staging_idss` (`dbt run --select stg_idss`) → `dag_dbt_fat_idss` (`dbt run --select fat_idss_operadora`) → `dag_dbt_recalculo_score` (`dbt run --select fat_score_operadora_mensal+ --full-refresh`) (PRD secao 8.1).
- [x] Adicionar entries de freshness em `_fontes.yml` para as fontes regulatorias: `bruto_ans.igr` (`warn_after: {count: 120, period: day}`), `bruto_ans.nip` (`warn_after: {count: 90, period: day}`), `bruto_ans.rn623_lista_operadora_trimestral` (`warn_after: {count: 120, period: day}`).
- [x] Criar teste dbt `assert_idss_entre_0_e_1.sql` (valida que `idss_total`, `idqs`, `idga`, `idsm`, `idgr` estao no intervalo [0, 1]) (PRD secao 7.1).
