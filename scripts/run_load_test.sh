#!/usr/bin/env bash
set -euo pipefail

mkdir -p testes/load/resultados

HOST="${HOST:-http://localhost:8080}"
API_KEY="${API_KEY:-hi_local_dev_2026_api_key}"
CACHE_MODE="${CACHE_MODE:-mixed}"
OUT_PREFIX="${OUT_PREFIX:-testes/load/resultados/locust_$(date +%Y%m%d_%H%M%S)}"

# PLANO define perfis de carga pré-configurados:
#   growth_local  — carga moderada local (default), ~10 RPS
#   growth_cloud  — carga moderada VPS, ~30 RPS
#   stress        — carga alta, ~50 RPS
#   spike         — pico curtíssimo, ~100 RPS
PLANO="${PLANO:-growth_local}"

case "${PLANO}" in
    growth_local)
        USERS_DEFAULT=20
        SPAWN_RATE_DEFAULT=2
        DURACAO_DEFAULT=300
        ;;
    growth_cloud)
        USERS_DEFAULT=40
        SPAWN_RATE_DEFAULT=5
        DURACAO_DEFAULT=300
        ;;
    stress)
        USERS_DEFAULT=80
        SPAWN_RATE_DEFAULT=10
        DURACAO_DEFAULT=120
        ;;
    spike)
        USERS_DEFAULT=150
        SPAWN_RATE_DEFAULT=50
        DURACAO_DEFAULT=30
        ;;
    *)
        echo "PLANO desconhecido: ${PLANO}. Usando growth_local." >&2
        USERS_DEFAULT=20
        SPAWN_RATE_DEFAULT=2
        DURACAO_DEFAULT=300
        ;;
esac

# RPS aceito como alias de USERS (com wait_time=between(0.5,1.5) avg~1s: users ≈ RPS)
USERS="${RPS:-${USERS:-${USERS_DEFAULT}}}"
SPAWN_RATE="${SPAWN_RATE:-${SPAWN_RATE_DEFAULT}}"
DURACAO="${DURACAO:-${DURACAO_DEFAULT}}"

echo "Executando Locust — PLANO=${PLANO} HOST=${HOST} USERS=${USERS} DURACAO=${DURACAO}s CACHE_MODE=${CACHE_MODE}"

LOCUST_API_KEY="${API_KEY}" \
LOCUST_CACHE_MODE="${CACHE_MODE}" \
locust \
  -f testes/load/locustfile.py \
  --headless \
  --host "${HOST}" \
  --users "${USERS}" \
  --spawn-rate "${SPAWN_RATE}" \
  --run-time "${DURACAO}s" \
  --csv "${OUT_PREFIX}" \
  --only-summary

echo "Relatorios gerados em ${OUT_PREFIX}_*.csv"
