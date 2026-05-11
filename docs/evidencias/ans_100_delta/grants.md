# Evidência — Grants

Data: 2026-05-11

## Query executada

```sql
SELECT grantee, table_schema, count(*) as tabelas_com_grant
FROM information_schema.role_table_grants
WHERE table_schema IN ('api_ans', 'consumo_ans', 'consumo_premium_ans')
GROUP BY grantee, table_schema
ORDER BY grantee, table_schema;
```

## Resultado

```
          grantee           |    table_schema     | tabelas_com_grant 
----------------------------+---------------------+-------------------
 healthintel                | api_ans             |               679
 healthintel                | consumo_ans         |               133
 healthintel                | consumo_premium_ans |                77
 healthintel_cliente_reader | consumo_ans         |                19
 healthintel_premium_reader | consumo_premium_ans |                11
(5 rows)
```

## Interpretação

- `healthintel_cliente_reader` → 19 tabelas em `consumo_ans` (inclui novas tabelas delta: consumo_historico_plano, consumo_plano_servico_opcional, consumo_tuss_procedimento_vigente, consumo_tiss_utilizacao_operadora_mes, consumo_sip_assistencial_operadora, consumo_ressarcimento_sus_operadora, etc.)
- `healthintel_premium_reader` → 11 tabelas em `consumo_premium_ans`
- API acessa `api_ans` via usuário principal `healthintel` (sem role separada)

Arquivo de grants: `infra/postgres/init/050_delta_ans_grants.sql`
