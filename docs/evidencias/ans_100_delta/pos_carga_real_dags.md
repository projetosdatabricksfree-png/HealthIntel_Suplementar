# Evidência — DAGs Delta ANS

**Timestamp:** 2026-05-13T11:28:52Z

**Commit:** 072c13c


## Lista DAGs delta
```
dag_ingest_beneficiarios_cobertura     | /opt/airflow/dags/dag_ingest_beneficiarios_cobertura.py     | airflow | False

dag_ingest_depara_sip_tuss             | /opt/airflow/dags/dag_ingest_depara_sip_tuss.py             | airflow | True

dag_ingest_precificacao_ntrp           | /opt/airflow/dags/dag_ingest_precificacao_ntrp.py           | airflow | False

dag_ingest_produto_plano               | /opt/airflow/dags/dag_ingest_produto_plano.py               | airflow | False

dag_ingest_rede_assistencial           | /opt/airflow/dags/dag_ingest_rede_assistencial.py           | airflow | True

dag_ingest_rede_prestadores            | /opt/airflow/dags/dag_ingest_rede_prestadores.py            | airflow | False

dag_ingest_regulatorios_complementares | /opt/airflow/dags/dag_ingest_regulatorios_complementares.py | airflow | False

dag_ingest_ressarcimento_sus           | /opt/airflow/dags/dag_ingest_ressarcimento_sus.py           | airflow | False

dag_ingest_sip_delta                   | /opt/airflow/dags/dag_ingest_sip_delta.py                   | airflow | False

dag_ingest_tiss                        | /opt/airflow/dags/dag_ingest_tiss.py                        | airflow | True

dag_ingest_tiss_subfamilias            | /opt/airflow/dags/dag_ingest_tiss_subfamilias.py            | airflow | False

dag_ingest_tuss                        | /opt/airflow/dags/dag_ingest_tuss.py                        | airflow | True

dag_ingest_tuss_oficial                | /opt/airflow/dags/dag_ingest_tuss_oficial.py                | airflow | False

```

## Últimas execuções: dag_ingest_produto_plano
```
dag_id                   | run_id                               | state   | execution_date            | start_date                       | end_date

=========================+======================================+=========+===========================+==================================+=================================
dag_ingest_produto_plano | manual__2026-05-13T11:24:27+00:00    | success | 2026-05-13T11:24:27+00:00 | 2026-05-13T11:24:28.220952+00:00 | 2026-05-13T11:25:32.167318+00:00
dag_ingest_produto_plano | manual__2026-05-13T11:13:57+00:00    | failed  | 2026-05-13T11:13:57+00:00 | 2026-05-13T11:13:57.423963+00:00 | 2026-05-13T11:15:40.192477+00:00
dag_ingest_produto_plano | manual__2026-05-13T11:05:45+00:00    | failed  | 2026-05-13T11:05:45+00:00 | 2026-05-13T11:05:45.977797+00:00 | 2026-05-13T11:06:06.488407+00:00
dag_ingest_produto_plano | manual__2026-05-13T10:54:41+00:00    | failed  | 2026-05-13T10:54:41+00:00 | 2026-05-13T10:54:42.988788+00:00 | 2026-05-13T10:56:10.968643+00:00
dag_ingest_produto_plano | manual__2026-05-12T00:32:37+00:00    | failed  | 2026-05-12T00:32:37+00:00 | 2026-05-12T00:32:38.371522+00:00 | 2026-05-12T00:32:46.349324+00:00
dag_ingest_produto_plano | manual__2026-05-11T23:10:01+00:00    | failed  | 2026-05-11T23:10:01+00:00 | 2026-05-11T23:10:02.579134+00:00 | 2026-05-11T23:10:09.628651+00:00
dag_ingest_produto_plano | manual__2026-05-11T22:39:28+00:00    | failed  | 2026-05-11T22:39:28+00:00 | 2026-05-11T22:45:49.851384+00:00 | 2026-05-11T22:46:12.690549+00:00
dag_ingest_produto_plano | scheduled__2026-04-01T00:00:00+00:00 | failed  | 2026-04-01T00:00:00+00:00 | 2026-05-11T22:45:49.846120+00:00 | 2026-05-11T22:46:12.671396+00:00


```

## Últimas execuções: dag_ingest_tuss_oficial
```
dag_id                  | run_id                            | state   | execution_date            | start_date                       | end_date

========================+===================================+=========+===========================+==================================+=================================
dag_ingest_tuss_oficial | manual__2026-05-13T10:54:35+00:00 | success | 2026-05-13T10:54:35+00:00 | 2026-05-13T10:54:36.178498+00:00 | 2026-05-13T10:55:35.530746+00:00
dag_ingest_tuss_oficial | manual__2026-05-12T00:32:27+00:00 | success | 2026-05-12T00:32:27+00:00 | 2026-05-12T00:32:28.832682+00:00 | 2026-05-12T00:33:18.544991+00:00
dag_ingest_tuss_oficial | manual__2026-05-11T23:09:54+00:00 | failed  | 2026-05-11T23:09:54+00:00 | 2026-05-11T23:09:54.798720+00:00 | 2026-05-11T23:09:59.469641+00:00
dag_ingest_tuss_oficial | manual__2026-05-11T22:56:39+00:00 | success | 2026-05-11T22:56:39+00:00 | 2026-05-11T22:56:40.271971+00:00 | 2026-05-11T22:57:24.190583+00:00
dag_ingest_tuss_oficial | manual__2026-05-11T22:39:11+00:00 | failed  | 2026-05-11T22:39:11+00:00 | 2026-05-11T22:45:41.272328+00:00 | 2026-05-11T22:45:58.222922+00:00


```

## Últimas execuções: dag_ingest_tiss_subfamilias
```
dag_id                      | run_id                               | state  | execution_date            | start_date                       | end_date

============================+======================================+========+===========================+==================================+=================================
dag_ingest_tiss_subfamilias | manual__2026-05-12T00:32:48+00:00    | failed | 2026-05-12T00:32:48+00:00 | 2026-05-12T00:32:49.041358+00:00 | 2026-05-12T00:33:14.696414+00:00
dag_ingest_tiss_subfamilias | manual__2026-05-11T23:10:11+00:00    | failed | 2026-05-11T23:10:11+00:00 | 2026-05-11T23:10:11.399446+00:00 | 2026-05-11T23:10:16.544484+00:00
dag_ingest_tiss_subfamilias | manual__2026-05-11T22:40:49+00:00    | failed | 2026-05-11T22:40:49+00:00 | 2026-05-11T22:46:15.228261+00:00 | 2026-05-11T22:46:42.263640+00:00
dag_ingest_tiss_subfamilias | scheduled__2026-04-01T00:00:00+00:00 | failed | 2026-04-01T00:00:00+00:00 | 2026-05-11T22:46:15.222972+00:00 | 2026-05-11T22:46:43.043832+00:00


```

## Últimas execuções: dag_ingest_sip_delta
```
dag_id               | run_id                               | state   | execution_date            | start_date                       | end_date

=====================+======================================+=========+===========================+==================================+=================================
dag_ingest_sip_delta | manual__2026-05-13T10:54:52+00:00    | success | 2026-05-13T10:54:52+00:00 | 2026-05-13T10:54:53.044566+00:00 | 2026-05-13T10:55:34.310260+00:00
dag_ingest_sip_delta | manual__2026-05-12T00:32:58+00:00    | failed  | 2026-05-12T00:32:58+00:00 | 2026-05-12T00:32:59.635835+00:00 | 2026-05-12T00:33:11.324299+00:00
dag_ingest_sip_delta | manual__2026-05-11T23:10:20+00:00    | failed  | 2026-05-11T23:10:20+00:00 | 2026-05-11T23:10:21.700335+00:00 | 2026-05-11T23:10:26.954512+00:00
dag_ingest_sip_delta | manual__2026-05-11T22:40:58+00:00    | failed  | 2026-05-11T22:40:58+00:00 | 2026-05-11T22:46:24.051681+00:00 | 2026-05-11T22:46:31.301445+00:00
dag_ingest_sip_delta | scheduled__2026-04-01T00:00:00+00:00 | failed  | 2026-04-01T00:00:00+00:00 | 2026-05-11T22:46:24.051362+00:00 | 2026-05-11T22:46:31.313451+00:00


```

## Últimas execuções: dag_ingest_ressarcimento_sus
```
dag_id                       | run_id                               | state  | execution_date            | start_date                       | end_date

=============================+======================================+========+===========================+==================================+=================================
dag_ingest_ressarcimento_sus | manual__2026-05-12T00:33:10+00:00    | failed | 2026-05-12T00:33:10+00:00 | 2026-05-12T00:33:11.165928+00:00 | 2026-05-12T00:33:21.556374+00:00
dag_ingest_ressarcimento_sus | manual__2026-05-11T23:10:28+00:00    | failed | 2026-05-11T23:10:28+00:00 | 2026-05-11T23:10:28.617507+00:00 | 2026-05-11T23:10:33.982292+00:00
dag_ingest_ressarcimento_sus | manual__2026-05-11T22:41:08+00:00    | failed | 2026-05-11T22:41:08+00:00 | 2026-05-11T22:46:31.010482+00:00 | 2026-05-11T22:46:49.642137+00:00
dag_ingest_ressarcimento_sus | scheduled__2026-04-01T00:00:00+00:00 | failed | 2026-04-01T00:00:00+00:00 | 2026-05-11T22:46:31.007299+00:00 | 2026-05-11T22:46:49.610335+00:00


```

## Últimas execuções: dag_ingest_precificacao_ntrp
```
dag_id                       | run_id                               | state  | execution_date            | start_date                       | end_date

=============================+======================================+========+===========================+==================================+=================================
dag_ingest_precificacao_ntrp | manual__2026-05-12T00:33:20+00:00    | failed | 2026-05-12T00:33:20+00:00 | 2026-05-12T00:33:21.473211+00:00 | 2026-05-12T00:33:28.855048+00:00
dag_ingest_precificacao_ntrp | manual__2026-05-11T23:10:36+00:00    | failed | 2026-05-11T23:10:36+00:00 | 2026-05-11T23:10:37.290394+00:00 | 2026-05-11T23:10:42.458023+00:00
dag_ingest_precificacao_ntrp | manual__2026-05-11T22:41:15+00:00    | failed | 2026-05-11T22:41:15+00:00 | 2026-05-11T22:46:49.534506+00:00 | 2026-05-11T22:47:03.747345+00:00
dag_ingest_precificacao_ntrp | scheduled__2026-04-01T00:00:00+00:00 | failed | 2026-04-01T00:00:00+00:00 | 2026-05-11T22:46:49.533959+00:00 | 2026-05-11T22:47:03.731799+00:00


```

## Últimas execuções: dag_ingest_rede_prestadores
```
dag_id                      | run_id                               | state  | execution_date            | start_date                       | end_date

============================+======================================+========+===========================+==================================+=================================
dag_ingest_rede_prestadores | manual__2026-05-12T00:33:30+00:00    | failed | 2026-05-12T00:33:30+00:00 | 2026-05-12T00:33:31.330305+00:00 | 2026-05-12T00:33:38.732742+00:00
dag_ingest_rede_prestadores | manual__2026-05-11T23:10:44+00:00    | failed | 2026-05-11T23:10:44+00:00 | 2026-05-11T23:10:45.776949+00:00 | 2026-05-11T23:10:52.905031+00:00
dag_ingest_rede_prestadores | manual__2026-05-11T22:41:24+00:00    | failed | 2026-05-11T22:41:24+00:00 | 2026-05-11T22:47:05.083501+00:00 | 2026-05-11T22:47:18.762949+00:00
dag_ingest_rede_prestadores | scheduled__2026-04-01T00:00:00+00:00 | failed | 2026-04-01T00:00:00+00:00 | 2026-05-11T22:47:05.083184+00:00 | 2026-05-11T22:47:17.174065+00:00


```

## Últimas execuções: dag_ingest_regulatorios_complementares
```
dag_id                                 | run_id                               | state  | execution_date            | start_date                       | end_date

=======================================+======================================+========+===========================+==================================+=================================
dag_ingest_regulatorios_complementares | manual__2026-05-12T00:33:40+00:00    | failed | 2026-05-12T00:33:40+00:00 | 2026-05-12T00:33:40.429836+00:00 | 2026-05-12T00:34:05.308218+00:00
dag_ingest_regulatorios_complementares | manual__2026-05-11T23:10:54+00:00    | failed | 2026-05-11T23:10:54+00:00 | 2026-05-11T23:10:55.232515+00:00 | 2026-05-11T23:11:01.925361+00:00
dag_ingest_regulatorios_complementares | manual__2026-05-11T22:41:32+00:00    | failed | 2026-05-11T22:41:32+00:00 | 2026-05-11T22:47:22.362391+00:00 | 2026-05-11T22:47:59.968518+00:00
dag_ingest_regulatorios_complementares | scheduled__2026-04-01T00:00:00+00:00 | failed | 2026-04-01T00:00:00+00:00 | 2026-05-11T22:47:22.361966+00:00 | 2026-05-11T22:47:59.945171+00:00


```

## Últimas execuções: dag_ingest_beneficiarios_cobertura
```
dag_id                             | run_id                               | state  | execution_date            | start_date                       | end_date

===================================+======================================+========+===========================+==================================+=================================
dag_ingest_beneficiarios_cobertura | manual__2026-05-12T00:33:50+00:00    | failed | 2026-05-12T00:33:50+00:00 | 2026-05-12T00:33:50.890540+00:00 | 2026-05-12T00:33:59.581163+00:00
dag_ingest_beneficiarios_cobertura | manual__2026-05-11T23:11:04+00:00    | failed | 2026-05-11T23:11:04+00:00 | 2026-05-11T23:11:05.309655+00:00 | 2026-05-11T23:11:10.270335+00:00
dag_ingest_beneficiarios_cobertura | manual__2026-05-11T22:41:40+00:00    | failed | 2026-05-11T22:41:40+00:00 | 2026-05-11T22:47:43.919098+00:00 | 2026-05-11T22:47:51.880399+00:00
dag_ingest_beneficiarios_cobertura | scheduled__2026-04-01T00:00:00+00:00 | failed | 2026-04-01T00:00:00+00:00 | 2026-05-11T22:47:44.215665+00:00 | 2026-05-11T22:47:53.693873+00:00


```

