# Sprints do Projeto

Esta pasta centraliza a execucao operacional das `12` sprints do HealthIntel Suplementar.

Convencoes:

- `[x]` item implementado, testado e validado no repositório;
- `[ ]` item ainda nao implementado ou sem validacao suficiente;
- o status aqui reflete o estado real do codigo, e nao apenas o planejamento do PRD.

## Status consolidado

| Sprint | Status | Arquivo |
| --- | --- | --- |
| 01 | Concluida | `docs/sprints/sprint_01_fundacao_plataforma.md` |
| 02 | Concluida | `docs/sprints/sprint_02_layout_registry_bronze.md` |
| 03 | Concluida | `docs/sprints/sprint_03_camada_canonica_inicial.md` |
| 04 | Concluida | `docs/sprints/sprint_04_score_api_mvp.md` |
| 05 | Concluida | `docs/sprints/sprint_05_metadados_billing_governanca.md` |
| 06 | Concluida | `docs/sprints/sprint_06_hardening_cicd_piloto.md` |
| 07 | Concluida | `docs/sprints/sprint_07_igr_nip_rn623.md` |
| 08 | Planejada | `docs/sprints/sprint_08_score_regulatorio_prudencial.md` |
| 09 | Planejada | `docs/sprints/sprint_09_diops_fip.md` |
| 10 | Planejada | `docs/sprints/sprint_10_vda_glosa_score_v2.md` |
| 11 | Planejada | `docs/sprints/sprint_11_rede_assistencial.md` |
| 12 | Planejada | `docs/sprints/sprint_12_vazios_oportunidade_rollout.md` |

## Regra de marcacao

- marcar `[x]` somente quando a entrega estiver no codigo e com teste ou validacao objetiva;
- nao reabrir tarefa concluida com nova numeracao;
- detalhar novas tarefas sempre dentro da sprint correta;
- preservar compatibilidade com backlog e PRD principal em `docs/healthintel_suplementar_prd_final.md`.

## Observacao de progresso atual

Itens ja concluidos e refletidos nas sprints (01–07):

- scaffold do monorepo e documento mestre;
- infraestrutura local com `Docker Compose`;
- schemas iniciais do PostgreSQL;
- servico real de layout registry com persistencia em `MongoDB`;
- validacao deterministica de layout com aliases manuais;
- pipeline bronze integrado ao layout registry com quarentena e carga em `bruto_ans`;
- modelos dbt iniciais de `staging`, `intermediate`, `snapshot`, `mart` e `api`;
- score v1 parametrizado por seed e camada `api_ans` com indices fisicos;
- API FastAPI conectada ao PostgreSQL com autenticacao, rate limit, cache e `log_uso`.
- billing base com `ciclo_faturamento`, `fatura_consumo`, `historico_plano` e `auditoria_cobranca`;
- endpoints administrativos de billing e script de fechamento mensal com trilha em `plataforma.job`.
- CI com `ruff`, `pytest`, `sqlfluff`, `dbt compile` e validacao de `docker compose config`.
- hardening minimo de runtime com `TrustedHost`, limite de payload, headers de seguranca e `X-Service-Token`.
- smoke fim a fim, baseline de carga e runbooks operacionais da Sprint 06.
- stack regulatoria inicial com `IGR`, `NIP`, `RN 623`, layouts bootstrapados em `MongoDB`, bronze no `PostgreSQL`, `dbt` regulatorio e endpoints basicos.

## Entregas esperadas nas sprints planejadas (08–12)

### Sprint 08 — Score Regulatório, Prudencial e Portabilidade
DDL bronze: `regime_especial_operadora_trimestral`, `prudencial_operadora_trimestral`, `portabilidade_operadora_mensal`, `taxa_resolutividade_operadora_trimestral`. dbt: `stg_regime_especial`, `stg_prudencial`, `stg_portabilidade`, `stg_taxa_resolutividade`, `fat_regime_especial_historico`, `fat_score_regulatorio_operadora_mensal`, `api_score_regulatorio_operadora_mensal`, `api_regime_especial_operadora`. DAGs: `dag_ingest_regime_especial`, `dag_ingest_prudencial`, `dag_ingest_portabilidade`, `dag_ingest_taxa_resolutividade`. Endpoints: `GET /v1/operadoras/{id}/score-regulatorio`, `GET /v1/operadoras/{id}/regime-especial`, `GET /v1/operadoras/{id}/portabilidade`.

### Sprint 09 — DIOPS, FIP e Harmonização Financeira
DDL bronze: `diops_operadora_trimestral`, `fip_operadora_trimestral`. DDL plataforma: `publicacao_financeira`. dbt: `stg_diops`, `stg_fip`, `int_financeiro_operadora_periodo`, `fat_financeiro_operadora_trimestral`. DAGs: `dag_ingest_diops`, `dag_ingest_fip`. Seed: `ref_indicador_financeiro.csv`.

### Sprint 10 — VDA, Glosa e Score v2
DDL bronze: `vda_operadora_mensal`, `glosa_operadora_mensal`. dbt: `stg_vda`, `stg_glosa`, `fat_vda_operadora_mensal`, `fat_glosa_operadora_mensal`, `fat_score_v2_operadora_mensal`, `api_score_v2_operadora_mensal`, `api_financeiro_operadora_mensal`. DAGs: `dag_ingest_vda`, `dag_ingest_glosa`. Endpoints: `GET /v1/operadoras/{id}/financeiro`, `GET /v1/operadoras/{id}/score-v2`. Suite regressao fase 1.

### Sprint 11 — Rede Assistencial
DDL bronze: `rede_prestador_municipio`. dbt: `stg_rede_assistencial`, `int_rede_assistencial_municipio`, `fat_cobertura_rede_municipio`, `fat_densidade_rede_operadora`, `api_rede_assistencial`. DAG: `dag_ingest_rede_assistencial`. Seeds: `ref_populacao_municipio.csv`, `ref_parametro_rede.csv`. Endpoints: `GET /v1/operadoras/{id}/rede`, `GET /v1/rede/municipio/{cd_municipio}`.

### Sprint 12 — Vazios, Oportunidade v2 e Rollout
dbt: `fat_vazio_assistencial_municipio`, `fat_oportunidade_v2_municipio_mensal`, `api_vazio_assistencial`, `api_oportunidade_v2_municipio_mensal`. Endpoints: `GET /v1/mercado/vazio-assistencial`, `GET /v1/rankings/municipio/oportunidade-v2`, `GET /v1/meta/endpoints`. Suite regressao fase 2. Runbooks (4). Catalogos finais. Tag `v1.0.0-baseline`.

## Datasets fora do MVP — Decisao documentada

| Dataset | Decisao |
| --- | --- |
| `taxa_resolutividade` | Sprint 08 — componente do score regulatorio |
| `parto_cesareo` | Sprint 09 — componente qualitativo em `fat_financeiro_operadora_trimestral` |
| `SIP` | Sprint 12 — enriquece `fat_oportunidade_v2`; sem endpoint proprio |
| `valores_comerciais` | Placeholder — macrofase futura (fase 5) |
| `reajustes_coletivos` | Macrofase futura — requer parser PDF/tabela ANS |
| `IEPRS` | Placeholder — sem publicacao ANS regular mapeada |
| `QUALISS` | Macrofase futura (fase 5) — requer camada de rede assistencial completa |
