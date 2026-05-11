# Evidência — TUSS Oficial

**Timestamp:** 2026-05-11T22:07:46Z  
**Commit:** e665fbf  

## Contagem TUSS vigente
```
ERROR:  relation "api_ans.api_tuss_procedimento_vigente" does not exist
LINE 1: select count(*) as total_tuss_vigente from api_ans.api_tuss_...
                                                   ^
ERRO: query falhou
```

## Duplicidade por codigo_tuss + versao_tuss
```
ERROR:  relation "api_ans.api_tuss_procedimento_vigente" does not exist
LINE 1: ... codigo_tuss, versao_tuss, count(*) as total from api_ans.ap...
                                                             ^
ERRO: query falhou
```

## Amostra por código
```
ERROR:  relation "api_ans.api_tuss_procedimento_vigente" does not exist
LINE 1: ...gencia_inicio, vigencia_fim, is_tuss_vigente from api_ans.ap...
                                                             ^
ERRO: query falhou
```

## Busca por descrição (consulta)
```
ERROR:  relation "api_ans.api_tuss_procedimento_vigente" does not exist
LINE 1: ...uss, descricao, versao_tuss, is_tuss_vigente from api_ans.ap...
                                                             ^
ERRO: query falhou
```

## Contagem TUSS consumo
```
ERROR:  relation "consumo_ans.consumo_tuss_procedimento_vigente" does not exist
ERRO: query falhou
```

## Diagnóstico

**Status:** Não validável — `api_tuss_procedimento_vigente` e `consumo_tuss_procedimento_vigente` ausentes na VPS.  
**Root cause:** `dag_ingest_tuss_oficial` nunca foi executado → `bruto_ans` sem dados TUSS → `dbt build` não criou as tabelas.  
**Pendência:** Executar `dag_ingest_tuss_oficial` na VPS e depois `dbt build --select tag:delta_ans_100`.

