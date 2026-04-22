#!/usr/bin/env bash
set -euo pipefail

mkdir -p testes/load/resultados

HOST="${HOST:-http://localhost:8080}"
USERS="${USERS:-10}"
SPAWN_RATE="${SPAWN_RATE:-2}"
DURATION="${DURATION:-30s}"
API_KEY="${API_KEY:-hi_local_dev_2026_api_key}"
CACHE_MODE="${CACHE_MODE:-mixed}"
OUT_PREFIX="${OUT_PREFIX:-testes/load/resultados/locust_$(date +%Y%m%d_%H%M%S)}"

echo "Executando Locust contra ${HOST} com CACHE_MODE=${CACHE_MODE}, USERS=${USERS}, DURATION=${DURATION}"

LOCUST_API_KEY="${API_KEY}" \
LOCUST_CACHE_MODE="${CACHE_MODE}" \
locust \
  -f testes/load/locustfile.py \
  --headless \
  --host "${HOST}" \
  --users "${USERS}" \
  --spawn-rate "${SPAWN_RATE}" \
  --run-time "${DURATION}" \
  --csv "${OUT_PREFIX}" \
  --only-summary

echo "Relatorios gerados em ${OUT_PREFIX}_*.csv"
