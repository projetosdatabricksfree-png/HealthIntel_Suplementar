# Evidência — DDL Idempotente Delta ANS na VPS (Sprint 42 Fase 2)

**Timestamp:** 2026-05-11T22:32:00Z
**Fase:** 2 — Aplicação DDL

## Schemas pré-DDL

Todos os 6 schemas já existiam:
- api_ans, bruto_ans, consumo_ans, consumo_premium_ans, plataforma, stg_ans

## Aplicação dos SQLs

| Arquivo | Resultado |
|---|---|
| 041_delta_ans_produtos_planos.sql | ✅ OK — 5 tabelas + índices |
| 042_delta_ans_tuss_oficial.sql | ✅ OK — 1 tabela + 3 índices |
| 043_delta_ans_tiss_subfamilias.sql | ✅ OK — 3 tabelas particionadas + índices |
| 044_delta_ans_sip.sql | ✅ OK — 1 tabela + 3 índices |
| 045_delta_ans_ressarcimento_sus.sql | ✅ OK — 5 tabelas + índices |
| 046_delta_ans_precificacao_ntrp.sql | ✅ OK — 6 tabelas + índices |
| 047_delta_ans_rede_prestadores.sql | ✅ OK — 6 tabelas + índices |
| 048_delta_ans_regulatorios_complementares.sql | ✅ OK — 8 tabelas + índices |
| 049_delta_ans_beneficiarios_cobertura.sql | ✅ OK — 3 tabelas + índices |
| 050_delta_ans_grants.sql | ✅ OK — GRANT + ALTER DEFAULT PRIVILEGES |

## Output completo

```
>>> aplicando infra/postgres/init/041_delta_ans_produtos_planos.sql
CREATE TABLE / CREATE INDEX (×5 tabelas, múltiplos índices) — OK

>>> aplicando infra/postgres/init/042_delta_ans_tuss_oficial.sql
CREATE TABLE / CREATE INDEX (×3) — OK

>>> aplicando infra/postgres/init/043_delta_ans_tiss_subfamilias.sql
CREATE TABLE / CREATE TABLE (particionadas) / CREATE INDEX — OK

>>> aplicando infra/postgres/init/044_delta_ans_sip.sql
CREATE TABLE / CREATE INDEX (×3) — OK

>>> aplicando infra/postgres/init/045_delta_ans_ressarcimento_sus.sql
CREATE TABLE (×5) / CREATE INDEX — OK

>>> aplicando infra/postgres/init/046_delta_ans_precificacao_ntrp.sql
CREATE TABLE (×6) / CREATE INDEX — OK

>>> aplicando infra/postgres/init/047_delta_ans_rede_prestadores.sql
CREATE TABLE (×6) / CREATE INDEX — OK

>>> aplicando infra/postgres/init/048_delta_ans_regulatorios_complementares.sql
CREATE TABLE (×8) / CREATE INDEX — OK

>>> aplicando infra/postgres/init/049_delta_ans_beneficiarios_cobertura.sql
CREATE TABLE (×3) / CREATE INDEX — OK

>>> aplicando infra/postgres/init/050_delta_ans_grants.sql
GRANT / GRANT / ALTER DEFAULT PRIVILEGES (×2) — OK
```

## Conclusão

✅ 10/10 SQLs aplicados com sucesso.
✅ Todas as tabelas bruto_ans delta criadas (idempotente — CREATE TABLE IF NOT EXISTS).
✅ Grants confirmados para consumo_ans e consumo_premium_ans.
✅ Safe para prosseguir com bootstrap layouts Mongo.
