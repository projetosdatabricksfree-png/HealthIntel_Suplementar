#!/usr/bin/env bash
# Executa carga SIB tipado por UF na VPS, dispara rebuild dbt dos modelos Core/API
# dependentes de SIB e limpa registros genéricos.
#
# USO:
#   bash scripts/vps/run_sib_tipado_vps.sh
#   UFS=AC,AL,AM COMPETENCIA=202503 bash scripts/vps/run_sib_tipado_vps.sh
#
# VARIÁVEIS:
#   UFS          - lista de UFs separada por vírgula (default: SP)
#   COMPETENCIA  - YYYYMM (default: mês atual)
#   PROJECT_DIR  - raiz do projeto na VPS (default: /opt/healthintel)
#   ENV_FILE     - arquivo .env a usar (default: .env.hml)
#   DRY_RUN      - se "1", apenas valida sem executar (default: 0)

set -Eeuo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/healthintel}"
ENV_FILE="${ENV_FILE:-.env.hml}"
LOG_DIR="${LOG_DIR:-logs/fase13}"
UFS="${UFS:-SP}"
COMPETENCIA="${COMPETENCIA:-$(date +%Y%m)}"
DRY_RUN="${DRY_RUN:-0}"

# UFs válidas Brasil
_UFS_VALIDAS="AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO"

cd "$PROJECT_DIR"
mkdir -p "$LOG_DIR"

timestamp="$(date +%Y%m%d_%H%M%S)"
log_file="$LOG_DIR/run_sib_tipado_${timestamp}.log"
exec > >(tee -a "$log_file") 2>&1

printf '[run_sib_tipado] inicio=%s UFS=%s COMPETENCIA=%s DRY_RUN=%s\n' \
  "$(date --iso-8601=seconds)" "$UFS" "$COMPETENCIA" "$DRY_RUN"

# Validar COMPETENCIA
if ! [[ "$COMPETENCIA" =~ ^[0-9]{6}$ ]]; then
  printf 'FAIL COMPETENCIA invalida: %s (esperado YYYYMM)\n' "$COMPETENCIA" >&2
  exit 1
fi

# Validar UFs
IFS=',' read -ra _UFS_ARRAY <<< "$UFS"
for uf in "${_UFS_ARRAY[@]}"; do
  uf_upper="${uf^^}"
  if ! grep -qw "$uf_upper" <<< "$_UFS_VALIDAS"; then
    printf 'FAIL UF invalida: %s. Valores aceitos: %s\n' "$uf_upper" "$_UFS_VALIDAS" >&2
    exit 1
  fi
done

# Verificar disco (> 80% bloqueia)
disco_pct=$(df "$PROJECT_DIR" | awk 'NR==2 {print $5}' | tr -d '%')
if [ "${disco_pct:-0}" -gt 80 ]; then
  printf 'FAIL disco acima de 80%% (%s%%). Abortar para evitar particao cheia.\n' "$disco_pct" >&2
  exit 1
fi
printf '[run_sib_tipado] disco OK (%s%%)\n' "$disco_pct"

if [ "$DRY_RUN" = "1" ]; then
  printf '[run_sib_tipado] DRY_RUN ativo — validacoes passaram, abortando antes da execucao.\n'
  exit 0
fi

# Helper: executa Python na ingestao via docker compose ou .venv ou PATH.
# O uso de -T preserva stdin em execucoes remotas nao interativas.
run_python() {
  if docker compose --env-file "$ENV_FILE" -f infra/docker-compose.yml \
      -f infra/docker-compose.hml.yml ps --services --filter status=running 2>/dev/null | grep -qx 'api'; then
    docker compose --env-file "$ENV_FILE" \
      -f infra/docker-compose.yml -f infra/docker-compose.hml.yml \
      exec -T -e PYTHONPATH=/workspace api python "$@"
    return
  fi
  if docker compose --env-file "$ENV_FILE" -f infra/docker-compose.yml \
      -f infra/docker-compose.hml.yml config --services 2>/dev/null | grep -qx 'api'; then
    docker compose --env-file "$ENV_FILE" \
      -f infra/docker-compose.yml -f infra/docker-compose.hml.yml \
      run --rm -T -e PYTHONPATH=/workspace api python "$@"
    return
  fi
  if [ -x ".venv/bin/python" ]; then
    PYTHONPATH="$PROJECT_DIR" .venv/bin/python "$@"
    return
  fi
  PYTHONPATH="$PROJECT_DIR" python3 "$@"
}

# Helper: executa dbt via compose ou .venv ou PATH
run_dbt() {
  if docker compose --env-file "$ENV_FILE" -f infra/docker-compose.yml \
      -f infra/docker-compose.hml.yml ps --services --filter status=running 2>/dev/null | grep -qx 'dbt'; then
    docker compose --env-file "$ENV_FILE" \
      -f infra/docker-compose.yml -f infra/docker-compose.hml.yml \
      exec -T dbt "$@"
    return
  fi
  if docker compose --env-file "$ENV_FILE" -f infra/docker-compose.yml \
      -f infra/docker-compose.hml.yml config --services 2>/dev/null | grep -qx 'dbt'; then
    docker compose --env-file "$ENV_FILE" \
      -f infra/docker-compose.yml -f infra/docker-compose.hml.yml \
      run --rm -T dbt "$@"
    return
  fi
  if [ -x ".venv/bin/dbt" ]; then
    (cd healthintel_dbt && \
      DBT_LOG_PATH=/tmp/healthintel_dbt_logs \
      DBT_TARGET_PATH=/tmp/healthintel_dbt_target \
      ../.venv/bin/dbt "$@")
    return
  fi
  (cd healthintel_dbt && \
    DBT_LOG_PATH=/tmp/healthintel_dbt_logs \
    DBT_TARGET_PATH=/tmp/healthintel_dbt_target \
    dbt "$@")
}

# --- ETAPA 1: ingestao SIB tipado por UF ---
printf '\n[run_sib_tipado] ETAPA 1 — ingestao SIB tipado (UFS=%s COMPETENCIA=%s)\n' "$UFS" "$COMPETENCIA"

run_python - <<EOF
import asyncio
from ingestao.app.ingestao_real import executar_ingestao_sib_uf_streaming

ufs = [uf.strip().upper() for uf in "${UFS}".split(",") if uf.strip()]
competencia = "${COMPETENCIA}"

async def main():
    for uf in ufs:
        print(f"[run_sib_tipado] ingerindo SIB UF={uf} competencia={competencia}")
        resultado = await executar_ingestao_sib_uf_streaming(competencia, uf)
        print(f"[run_sib_tipado] resultado UF={uf}: {resultado}")

asyncio.run(main())
EOF

# --- ETAPA 2: validar contagem bruto_ans ---
printf '\n[run_sib_tipado] ETAPA 2 — validando bruto_ans.sib_beneficiario_operadora\n'
docker exec -i healthintel_postgres psql -v ON_ERROR_STOP=1 \
  -U healthintel -d healthintel -c "
  SELECT
    'sib_beneficiario_operadora' AS tabela,
    competencia,
    COUNT(*) AS registros
  FROM bruto_ans.sib_beneficiario_operadora
  WHERE _arquivo_origem LIKE 'sib_ativo_%'
  GROUP BY competencia
  UNION ALL
  SELECT
    'sib_beneficiario_municipio',
    competencia,
    COUNT(*)
  FROM bruto_ans.sib_beneficiario_municipio
  WHERE _arquivo_origem LIKE 'sib_ativo_%'
  GROUP BY competencia
  ORDER BY tabela, competencia;
"
op_count=$(docker exec -i healthintel_postgres psql -v ON_ERROR_STOP=1 -U healthintel -d healthintel -Atc "
  SELECT COUNT(*)
  FROM bruto_ans.sib_beneficiario_operadora
  WHERE _arquivo_origem LIKE 'sib_ativo_%';
")
mun_count=$(docker exec -i healthintel_postgres psql -v ON_ERROR_STOP=1 -U healthintel -d healthintel -Atc "
  SELECT COUNT(*)
  FROM bruto_ans.sib_beneficiario_municipio
  WHERE _arquivo_origem LIKE 'sib_ativo_%';
")
if [ "${op_count:-0}" -le 0 ] || [ "${mun_count:-0}" -le 0 ]; then
  printf 'FAIL SIB tipado sem linhas: operadora=%s municipio=%s\n' "$op_count" "$mun_count" >&2
  exit 1
fi

# --- ETAPA 3: limpar genéricos SIB ---
printf '\n[run_sib_tipado] ETAPA 3 — limpando bruto_ans.ans_linha_generica para SIB\n'
docker exec -i healthintel_postgres psql -v ON_ERROR_STOP=1 \
  -U healthintel -d healthintel -c "
  DELETE FROM bruto_ans.ans_linha_generica
  WHERE dataset_codigo LIKE 'sib%';
  SELECT 'genericos removidos' AS status;
"

# --- ETAPA 4: rebuild dbt modelos SIB/serving ---
printf '\n[run_sib_tipado] ETAPA 4 — dbt run modelos Core dependentes de SIB\n'
run_dbt run \
  --select "+api_ranking_score +api_market_share_mensal +api_score_operadora_mensal +api_ranking_crescimento +api_ranking_oportunidade" \
  --exclude "tag:tiss tag:premium tag:consumo_premium"

# --- ETAPA 5: flush Redis ---
printf '\n[run_sib_tipado] ETAPA 5 — flush cache Redis Core\n'
if docker exec healthintel_redis redis-cli ping >/dev/null 2>&1; then
  for pattern in 'cache:ranking:*' 'cache:mercado:*' 'cache:operadora:*'; do
    docker exec healthintel_redis redis-cli --scan --pattern "$pattern" | \
      xargs -r docker exec -i healthintel_redis redis-cli del || true
  done
  printf '[run_sib_tipado] Redis flush OK\n'
else
  printf '[run_sib_tipado] WARN Redis indisponivel para flush\n'
fi

# --- ETAPA 6: contagem final ---
printf '\n[run_sib_tipado] ETAPA 6 — contagens finais api_ans\n'
docker exec -i healthintel_postgres psql -v ON_ERROR_STOP=1 \
  -U healthintel -d healthintel -c "
  SELECT 'api_ranking_score' AS tabela, COUNT(*) AS registros FROM api_ans.api_ranking_score
  UNION ALL
  SELECT 'api_market_share_mensal', COUNT(*) FROM api_ans.api_market_share_mensal
  UNION ALL
  SELECT 'api_score_operadora_mensal', COUNT(*) FROM api_ans.api_score_operadora_mensal
  UNION ALL
  SELECT 'api_ranking_crescimento', COUNT(*) FROM api_ans.api_ranking_crescimento
  UNION ALL
  SELECT 'api_ranking_oportunidade', COUNT(*) FROM api_ans.api_ranking_oportunidade
  ORDER BY tabela;
"
api_min_count=$(docker exec -i healthintel_postgres psql -v ON_ERROR_STOP=1 -U healthintel -d healthintel -Atc "
  WITH contagens AS (
    SELECT COUNT(*) AS total FROM api_ans.api_ranking_score
    UNION ALL
    SELECT COUNT(*) FROM api_ans.api_market_share_mensal
    UNION ALL
    SELECT COUNT(*) FROM api_ans.api_score_operadora_mensal
  )
  SELECT MIN(total) FROM contagens;
")
if [ "${api_min_count:-0}" -le 0 ]; then
  printf 'FAIL api_ans Core SIB ainda possui tabela principal vazia (min=%s)\n' "$api_min_count" >&2
  exit 1
fi

printf '\n[run_sib_tipado] concluido. Log: %s\n' "$log_file"
