# Evidência — Smokes SQL

Data: 2026-05-11

## Contagem de registros nas tabelas API delta

```
                 tabela                  | count 
-----------------------------------------+-------
 api_produto_plano                       |     0
 api_historico_plano                     |     0
 api_plano_servico_opcional              |     0
 api_quadro_auxiliar_corresponsabilidade |     0
 api_tuss_procedimento_vigente           |     0
 api_sip_assistencial_operadora          |     0
 api_ressarcimento_sus_operadora_plano   |     0
 api_painel_precificacao                 |     0
 api_valor_comercial_medio_municipio     |     0
 api_prestador_acreditado                |     0
 api_penalidade_operadora                |     0
 api_rpc_operadora_mes                   |     0
(12 rows)
```

**Nota**: Contagem 0 é esperada no ambiente local — as tabelas bronze existem mas não foram carregadas com dados reais. Os smokes de volume real são executados na VPS após a primeira carga via DAG Airflow.

## Estrutura das tabelas (schemas corretos)

Todas as 12 tabelas acima existem em `api_ans` e foram criadas pelo `dbt build` com sucesso (SELECT 0 rows = tabela criada, sem dados).
