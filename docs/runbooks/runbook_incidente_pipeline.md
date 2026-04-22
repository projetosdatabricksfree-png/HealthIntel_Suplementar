# Runbook — Incidente de pipeline

## Objetivo

Diagnosticar falha em DAG, ingestão, dbt ou API sem interromper o restante da plataforma.

## Passos

1. Verificar `GET /prontidao` e `GET /saude`.
2. Conferir último evento em `plataforma.job` e `plataforma.execucao_layout`.
3. Identificar o ponto de quebra:
   - download;
   - layout;
   - parse;
   - bronze;
   - dbt;
   - API.
4. Se houver quarentena, manter arquivo isolado até correção de layout/alias.
5. Reexecutar apenas a tag afetada:

```bash
dbt build --select tag:vazio
dbt build --select tag:oportunidade_v2
```

## Critério de encerramento

- DAG volta a concluir com sucesso;
- `plataforma.job.status = sucesso`;
- nenhuma regressão em `pytest` ou `dbt build`.

