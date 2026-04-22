# Runbook — Reprocessamento e tratamento de erro

## Cenários atendidos

- arquivo enviado para `plataforma.arquivo_quarentena`;
- layout inativo ou incompatível;
- reprocessamento manual após correção de alias/layout.

## Passos

1. Consultar quarentena:

```sql
select *
from plataforma.arquivo_quarentena
order by criado_em desc
limit 20;
```

2. Validar incompatibilidade no layout registry:

```bash
curl -H "X-API-Key: hi_local_admin_2026_api_key" \
  http://localhost:8080/admin/layouts/incompativeis
```

3. Corrigir layout ou alias conforme o caso.

4. Disparar reprocessamento:

```bash
curl -X POST http://localhost:8080/admin/layouts/reprocessar \
  -H "Content-Type: application/json" \
  -H "X-API-Key: hi_local_admin_2026_api_key" \
  -d '{
    "layout_id": "layout_cadop_csv",
    "layout_versao_id": "layout_cadop_csv:v1",
    "motivo": "Correcao de alias competencia",
    "arquivo_origem": "cadop_202604.csv",
    "lote_ids": []
  }'
```

5. Reexecutar a DAG ou o pipeline local correspondente.

## Critério de encerramento

- arquivo sai do estado de quarentena;
- novo `lote_id` é gerado;
- `plataforma.execucao_layout` e `evento_layout` registram o reprocessamento;
- `dbt build` posterior não apresenta regressão.
