#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/healthintel}"
ENV_FILE="${ENV_FILE:-.env.hml}"
LOG_DIR="${LOG_DIR:-logs/fase13}"
DBT_PROJECT_DIR="${DBT_PROJECT_DIR:-healthintel_dbt}"
DBT_SELECTORS="${DBT_SELECTORS:-+api_operadora +api_ranking_score +api_market_share_mensal +api_score_operadora_mensal +api_ranking_crescimento +api_ranking_oportunidade}"
DBT_EXCLUDE="${DBT_EXCLUDE:-tag:tiss tag:premium tag:consumo_premium api_tiss_operadora_trimestral api_sinistralidade_procedimento}"

cd "$PROJECT_DIR"
mkdir -p "$LOG_DIR"

timestamp="$(date +%Y%m%d_%H%M%S)"
log_file="$LOG_DIR/build_serving_core_$timestamp.log"
exec > >(tee -a "$log_file") 2>&1

run_dbt() {
  if docker compose --env-file "$ENV_FILE" -f infra/docker-compose.yml -f infra/docker-compose.hml.yml config --services | grep -qx 'dbt'; then
    docker compose --env-file "$ENV_FILE" -f infra/docker-compose.yml -f infra/docker-compose.hml.yml run --rm dbt "$@"
    return
  fi

  if [ -x ".venv/bin/dbt" ]; then
    (cd "$DBT_PROJECT_DIR" && DBT_LOG_PATH=/tmp/healthintel_dbt_logs DBT_TARGET_PATH=/tmp/healthintel_dbt_target ../.venv/bin/dbt "$@")
    return
  fi

  if command -v dbt >/dev/null 2>&1; then
    (cd "$DBT_PROJECT_DIR" && DBT_LOG_PATH=/tmp/healthintel_dbt_logs DBT_TARGET_PATH=/tmp/healthintel_dbt_target dbt "$@")
    return
  fi

  printf 'FAIL dbt nao encontrado via compose, .venv/bin/dbt ou PATH.\n' >&2
  exit 1
}

printf 'Listando modelos Core/API candidatos...\n'
if ! run_dbt ls --select $DBT_SELECTORS --exclude $DBT_EXCLUDE; then
  printf 'WARN selectors Core falharam. Listando modelos api disponiveis para diagnostico.\n'
  run_dbt ls --select path:models/api || true
  exit 1
fi

printf 'Executando dbt build (run + test) Core/API sem TISS e sem premium pesado.\n'
run_dbt build --select $DBT_SELECTORS --exclude $DBT_EXCLUDE

printf 'Invalidando cache Redis para chaves Core (ranking, mercado, operadoras).\n'
if docker exec healthintel_redis redis-cli ping >/dev/null 2>&1; then
  for pattern in 'cache:ranking:*' 'cache:mercado:*' 'cache:operadora:*'; do
    chaves=$(docker exec healthintel_redis redis-cli --scan --pattern "$pattern" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$chaves" -gt 0 ]; then
      docker exec healthintel_redis redis-cli --scan --pattern "$pattern" | \
        xargs -r docker exec -i healthintel_redis redis-cli del
      printf 'Cache limpo: %s (%s chaves)\n' "$pattern" "$chaves"
    fi
  done
else
  printf 'WARN Redis nao disponivel para flush de cache. Chaves expiram pelo TTL natural.\n'
fi

printf 'Validando existencia das tabelas Core API no Postgres.\n'
docker exec -i healthintel_postgres psql -v ON_ERROR_STOP=1 -U healthintel -d healthintel -c "
  select
    relname as tabela,
    n_live_tup::bigint as linhas_estimadas
  from pg_stat_user_tables
  where schemaname = 'api_ans'
    and relname in (
      'api_operadora',
      'api_ranking_score',
      'api_market_share_mensal',
      'api_score_operadora_mensal',
      'api_ranking_crescimento',
      'api_ranking_oportunidade'
    )
  order by relname;
"

printf 'Build serving Core concluido. Log: %s\n' "$log_file"
