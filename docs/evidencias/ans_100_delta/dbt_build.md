# Evidência — dbt build --select tag:delta_ans_100

Data: 2026-05-11
Comando: `DBT_LOG_PATH=/tmp/healthintel_dbt_logs DBT_TARGET_PATH=/tmp/healthintel_dbt_target .venv/bin/dbt build --select tag:delta_ans_100`

## Resultado

```
Finished running 48 table models, 76 data tests, 38 view models in 22.01s.

Completed successfully

Done. PASS=162 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=162
```

## Modelos incluídos (tag:delta_ans_100)

- 38 view models (stg_*)
- 48 table models (api_* + consumo_*)
- 76 data tests (not_null, unique, relationships, accepted_values)

## Pré-requisito aplicado

DDL files 041-050 aplicados no postgres local antes do build:
- `041_delta_ans_produtos_planos.sql`
- `042_delta_ans_tuss_oficial.sql`
- `043_delta_ans_tiss_subfamilias.sql`
- `044_delta_ans_sip.sql`
- `045_delta_ans_ressarcimento_sus.sql`
- `046_delta_ans_precificacao_ntrp.sql`
- `047_delta_ans_rede_prestadores.sql`
- `048_delta_ans_regulatorios_complementares.sql`
- `049_delta_ans_beneficiarios_cobertura.sql`
- `050_delta_ans_grants.sql`
