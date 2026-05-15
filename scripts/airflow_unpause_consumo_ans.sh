#!/usr/bin/env bash
set -euo pipefail

DAGS=(
  dag_anual_idss
  dag_backfill_consumo_ans_36m
  dag_dbt_consumo_refresh
  dag_ingest_cnes
  dag_ingest_diops
  dag_ingest_fip
  dag_ingest_glosa
  dag_ingest_igr
  dag_ingest_nip
  dag_ingest_portabilidade
  dag_ingest_precificacao_ntrp
  dag_ingest_produto_plano
  dag_ingest_prudencial
  dag_ingest_regime_especial
  dag_ingest_ressarcimento_sus
  dag_ingest_rn623
  dag_ingest_sip_delta
  dag_ingest_taxa_resolutividade
  dag_ingest_tuss_oficial
  dag_ingest_vda
)

for dag_id in "${DAGS[@]}"; do
  airflow dags unpause "${dag_id}"
done
