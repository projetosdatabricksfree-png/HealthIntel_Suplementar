#!/usr/bin/env bash
set -Eeuo pipefail

ENV_FILE="${ENV_FILE:-.env.hml}"
if [ -f "$ENV_FILE" ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      ''|'#'*) continue ;;
    esac
    key="${line%%=*}"
    value="${line#*=}"
    case "$key" in
      HML_IP|HML_DEV_API_KEY)
        export "$key=$value"
        ;;
    esac
  done < "$ENV_FILE"
fi

HML_IP="${HML_IP:-5.189.160.27}"
API_BASE_URL="${API_BASE_URL:-http://$HML_IP:8080}"
FRONTEND_URL="${FRONTEND_URL:-http://$HML_IP}"
DEV_KEY="${HML_DEV_API_KEY:-hi_local_dev_2026_api_key}"
ORIGIN="${ORIGIN:-http://$HML_IP}"
FAILURES=0

ok() {
  printf 'OK   %s\n' "$*"
}

fail() {
  printf 'FAIL %s\n' "$*" >&2
  FAILURES=$((FAILURES + 1))
}

status_code() {
  local url="$1"
  shift
  curl -sS -o /tmp/healthintel_public_check_body.txt -w '%{http_code}' "$@" "$url" || printf '000'
}

expect_status() {
  local label="$1"
  local expected="$2"
  local url="$3"
  shift 3
  local status
  status="$(status_code "$url" "$@")"
  if [ "$status" = "$expected" ]; then
    ok "$label retornou $status"
  else
    fail "$label esperava $expected e retornou $status: $(head -c 300 /tmp/healthintel_public_check_body.txt 2>/dev/null || true)"
  fi
}

check_cors() {
  local headers
  headers="$(curl -sS -i -X OPTIONS "$API_BASE_URL/v1/meta/endpoints" \
    -H "Origin: $ORIGIN" \
    -H "Access-Control-Request-Method: GET" \
    -H "Access-Control-Request-Headers: X-API-Key" || true)"

  if printf '%s\n' "$headers" | tr -d '\r' | grep -qi "^access-control-allow-origin: $ORIGIN$"; then
    ok "CORS publico aceita Origin $ORIGIN"
  else
    fail "CORS publico nao retornou access-control-allow-origin para $ORIGIN"
  fi
}

expect_status "Frontend publico" "200" "$FRONTEND_URL" -I
expect_status "API publica /saude" "200" "$API_BASE_URL/saude"
expect_status "API publica /prontidao" "200" "$API_BASE_URL/prontidao"
expect_status "API publica /v1/operadoras dev" "200" "$API_BASE_URL/v1/operadoras?pagina=1&por_pagina=10" -H "X-API-Key: $DEV_KEY"
check_cors

rm -f /tmp/healthintel_public_check_body.txt

if [ "$FAILURES" -gt 0 ]; then
  printf '\nResultado: %s falha(s).\n' "$FAILURES" >&2
  exit 1
fi

printf '\nResultado: todos os checks publicos passaram.\n'
