# Evidência — TISS/RPC Janela 24 Meses

**Timestamp:** 2026-05-11T22:07:46Z  
**Commit:** e665fbf  

## TISS e RPC api_ans
```
ERROR:  relation "api_ans.api_tiss_ambulatorial_operadora_mes" does not exist
LINE 1: ...cia) as qtd_competencias, count(*) as linhas from api_ans.ap...
                                                             ^
ERRO: query falhou
```

## TISS consumo_ans
```
ERROR:  relation "consumo_ans.consumo_tiss_utilizacao_operadora_mes" does not exist
ERRO: query falhou
```

## Diagnóstico

**Status:** Não validável — tabelas TISS e RPC ausentes na VPS (dbt build não executado).  
**Pendência:** Executar `dbt build --select tag:delta_ans_100` na VPS após DAGs de ingestão rodarem.  
**Critério de 24 meses:** Será verificado na próxima rodada de validação pós-ingestão real.

