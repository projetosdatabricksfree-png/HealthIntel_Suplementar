# Evidencia final - consumo_ans comercial

- Data/hora: 2026-05-15T20:12:00+00:00
- Escopo: `consumo_ans` como produto de dados curados para SQL/BI/dump/CSV/Parquet.
- Fora do escopo comercial: TISS e SIB/SIB historico.
- Evidencia de contagem detalhada: `docs/evidencias/consumo_ans/evidencia_hardgate_com_db.md`.

## Resultado por status

| status | tabelas |
|---|---:|
| disponivel | 12 |
| parcial | 5 |
| vazia_bloqueada | 8 |
| fora_do_escopo | 1 |

## Tabelas disponiveis

| tabela | linhas |
|---|---:|
| `consumo_ans.consumo_produto_plano` | 163661 |
| `consumo_ans.consumo_historico_plano` | 163567 |
| `consumo_ans.consumo_regulatorio_operadora_trimestre` | 161173 |
| `consumo_ans.consumo_igr` | 136908 |
| `consumo_ans.consumo_nip` | 53637 |
| `consumo_ans.consumo_idss` | 13072 |
| `consumo_ans.consumo_taxa_resolutividade_operadora_trimestral` | 26062 |
| `consumo_ans.consumo_prudencial_operadora_trimestral` | 11216 |
| `consumo_ans.consumo_financeiro_operadora_trimestre` | 10978 |
| `consumo_ans.consumo_glosa_operadora_mensal` | 844 |
| `consumo_ans.consumo_tuss_procedimento_vigente` | 64654 |
| `consumo_ans.consumo_regime_especial_operadora_trimestral` | 117 |

## Tabelas parciais

| tabela | motivo |
|---|---|
| `consumo_beneficiarios_operadora_mes` | depende de SIB |
| `consumo_beneficiarios_municipio_mes` | depende de SIB |
| `consumo_oportunidade_municipio` | metricas de beneficiarios dependem de SIB |
| `consumo_operadora_360` | colunas de beneficiarios/score core dependem de SIB |
| `consumo_score_operadora_mes` | componente core depende de SIB |

## Vazias bloqueadas

| tabela | decisao tecnica |
|---|---|
| `consumo_sip_assistencial_operadora` | 0 linhas em validacao real; bloqueada ate carga SIP produzir linhas |
| `consumo_precificacao_plano` | 0 linhas em validacao real; bloqueada ate carga NTRP produzir linhas |
| `consumo_ressarcimento_sus_operadora` | 0 linhas em validacao real; bloqueada ate carga ressarcimento produzir linhas |
| `consumo_rede_assistencial_municipio` | 0 linhas em validacao real; componente CNES bloqueado por fonte DataSUS retornando 404 |
| `consumo_beneficiarios_cobertura_municipio` | 0 linhas em validacao real; cobertura depende de SIB |
| `consumo_plano_servico_opcional` | bloqueada ate confirmar carga real nao vazia |
| `consumo_rede_acreditacao` | bloqueada ate confirmar carga real nao vazia |
| `consumo_regulatorio_complementar_operadora` | bloqueada ate confirmar carga real nao vazia |

## Fora do escopo

| tabela | motivo |
|---|---|
| `consumo_tiss_utilizacao_operadora_mes` | TISS fora do escopo desta sprint |

## Comandos executados

| comando | resultado |
|---|---|
| `python3 -m py_compile ingestao/app/carregar_postgres.py ingestao/app/ingestao_delta_ans.py ingestao/app/ingestao_real.py ingestao/dags/dag_backfill_consumo_ans_36m.py scripts/auditoria/validar_consumo_ans_comercial.py` | sucesso |
| `/opt/healthintel/.venv/bin/dbt parse --profiles-dir . --project-dir .` | sucesso |
| `docker compose -f infra/docker-compose.yml exec -T airflow-scheduler bash -lc /workspace/scripts/airflow_unpause_consumo_ans.sh` | sucesso |
| `docker compose -f infra/docker-compose.yml exec -T airflow-scheduler airflow dags list` | DAGs da sprint despausadas; TISS e SIB pausadas |
| `docker compose -f infra/docker-compose.yml exec -T airflow-scheduler airflow dags trigger dag_backfill_consumo_ans_36m --conf '{"ANS_DELTA_MAX_FILES":"36"}'` | DAG disparada; primeira execucao teve retry por OOM em NTRP VCM |
| `docker compose -f infra/docker-compose.yml exec -T airflow-scheduler airflow dags trigger dag_backfill_consumo_ans_36m --conf '{"ANS_DELTA_MAX_FILES":"36","motivo":"rerun_sem_ntrp_oom"}'` | nova execucao disparada sem NTRP pesado |
| `python3 scripts/auditoria/validar_consumo_ans_comercial.py --evidencia docs/evidencias/consumo_ans/evidencia_hardgate_com_db.md` | sucesso |
| `docker compose -f infra/docker-compose.yml exec -T airflow-scheduler bash -lc "cd /workspace/healthintel_dbt && DBT_PROFILES_DIR=/workspace/healthintel_dbt DBT_LOG_PATH=/tmp/healthintel_dbt_logs DBT_TARGET_PATH=/tmp/healthintel_dbt_target dbt test --select tag:consumo --exclude consumo_tiss_utilizacao_operadora_mes"` | sucesso: PASS=54 WARN=0 ERROR=0 SKIP=0 |

## Backfill 36 meses

Runs iniciados:

- `manual__2026-05-15T20:04:52+00:00`: primeira execucao; NTRP VCM causou exit 137 e a task delta ficou `up_for_retry`.
- `manual__2026-05-15T20:23:35+00:00`: reexecucao sem NTRP pesado.

Estado observado:

| task | estado |
|---|---|
| `registrar_decisoes_fontes_bloqueadas` | success |
| `backfill_cnes_snapshot_atual` | success; registrou bloqueio de fonte DataSUS 404, sem inserir dados fake |
| `backfill_delta_ans_36m_sem_tiss_sem_sib` | running na reexecucao sem NTRP pesado |
| `dbt_build_consumo_ans_sem_tiss_sib` | pendente de upstream |

Decisoes registradas no backfill:

- Portabilidade: fonte mensal por operadora nao localizada no ANS FTP PDA.
- VDA: layout/fonte divergente do dominio VDA financeiro esperado.
- RN623: lista trimestral por operadora nao localizada no ANS FTP PDA.
- CNES: URL configurada `https://cnes.datasus.gov.br/pages/estabelecimentos/geradorDeArquivos.jsp` retornou 404.
- NTRP VCM: parser atual nao e seguro para carga em memoria; primeira execucao foi encerrada com exit 137, entao NTRP permanece bloqueado ate parser streaming.

## Conclusao comercial

O catalogo comercial atual e honesto: nao ha tabela vazia marcada como `disponivel`, TISS nao foi prometido, e SIB ficou parcial/fora do catalogo comercial completo. A entrega comercial liberavel nesta evidencia e composta pelas 12 tabelas `disponivel`. SIP, NTRP, Ressarcimento, CNES e demais vazias permanecem bloqueios tecnicos da sprint ate o backfill ou a correcao de fonte/layout produzir dados reais em `consumo_ans`.
