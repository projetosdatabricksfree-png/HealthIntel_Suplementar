# Evidência — Contagens api_ans

**Timestamp:** 2026-05-11T22:07:46Z  
**Commit:** e665fbf  

## Contagens api_ans (20 tabelas)
```
ERROR:  relation "api_ans.api_produto_plano" does not exist
ERRO: query falhou — nenhuma das 20 tabelas delta existe na VPS
```

## Diagnóstico — tabelas delta ausentes (validação manual)

```sql
-- Executado: select count(*) from information_schema.tables where table_schema = 'api_ans';
-- Resultado: 60 tabelas (pré-Sprint 41)
-- Resultado: 0 tabelas delta (api_produto_plano, api_tuss_procedimento_vigente, etc.)
```

**Root cause:** `dbt build --select tag:delta_ans_100` não foi executado na VPS após o deploy da Sprint 41.

| Tabela | Existe na VPS |
|---|---|
| api_produto_plano | ❌ ausente |
| api_historico_plano | ❌ ausente |
| api_plano_servico_opcional | ❌ ausente |
| api_quadro_auxiliar_corresponsabilidade | ❌ ausente |
| api_tuss_procedimento_vigente | ❌ ausente |
| api_tiss_ambulatorial_operadora_mes | ❌ ausente |
| api_tiss_hospitalar_operadora_mes | ❌ ausente |
| api_tiss_plano_mes | ❌ ausente |
| api_sip_assistencial_operadora | ❌ ausente |
| api_ressarcimento_beneficiario_abi | ❌ ausente |
| api_ressarcimento_sus_operadora_plano | ❌ ausente |
| api_ressarcimento_hc | ❌ ausente |
| api_ressarcimento_cobranca_arrecadacao | ❌ ausente |
| api_ressarcimento_indice_pagamento | ❌ ausente |
| api_painel_precificacao | ❌ ausente |
| api_valor_comercial_medio_municipio | ❌ ausente |
| api_prestador_acreditado | ❌ ausente |
| api_alteracao_rede_hospitalar | ❌ ausente |
| api_penalidade_operadora | ❌ ausente |
| api_rpc_operadora_mes | ❌ ausente |

**Pendência:** Executar os DAGs de ingestão + `dbt build --select tag:delta_ans_100` na VPS.

