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

Itens ja concluidos e refletidos nas sprints:

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
