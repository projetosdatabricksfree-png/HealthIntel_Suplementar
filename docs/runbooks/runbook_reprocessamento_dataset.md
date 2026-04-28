# Runbook — Reprocessamento de dataset

## Objetivo

Reexecutar um dataset sem quebrar histórico nem contrato de API.

## Passos

1. Identificar dataset e competência afetados.
2. Conferir impacto em `api_ans` e `nucleo_ans`.
3. Rodar `dbt build` apenas para a tag afetada.
4. Validar `dbt test` singular e `pytest` de regressão.
5. Atualizar `plataforma.versao_dataset` para logs per-carga legados; para datasets de `referencia_versionada` ou `snapshot_atual`, atualizar o manifesto `plataforma.versao_dataset_vigente`.

## Critério de encerramento

- dados reprocessados;
- API estável;
- sem duplicidade de versão;
- sem quebra de contratos.
