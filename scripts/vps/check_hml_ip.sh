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
      HML_IP|API_EXTERNAL_PORT|FRONTEND_EXTERNAL_PORT|HML_DEV_API_KEY|HML_ADMIN_API_KEY)
        export "$key=$value"
        ;;
    esac
  done < "$ENV_FILE"
fi

HML_IP="${HML_IP:-5.189.160.27}"
API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:${API_EXTERNAL_PORT:-8080}}"
FRONTEND_URL="${FRONTEND_URL:-http://127.0.0.1:${FRONTEND_EXTERNAL_PORT:-80}}"
DEV_KEY="${HML_DEV_API_KEY:-hi_local_dev_2026_api_key}"
ADMIN_KEY="${HML_ADMIN_API_KEY:-hi_local_admin_2026_api_key}"
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
  curl -sS -o /tmp/healthintel_check_body.txt -w '%{http_code}' "$@" "$url" || printf '000'
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
    fail "$label esperava $expected e retornou $status: $(head -c 300 /tmp/healthintel_check_body.txt 2>/dev/null || true)"
  fi
}

expect_admin_real_status() {
  local label="$1"
  local url="$2"
  local status
  status="$(status_code "$url" -H "X-API-Key: $ADMIN_KEY")"
  if [ "$status" = "200" ]; then
    ok "$label retornou 200"
  elif [ "$status" != "000" ] && [ "$status" != "401" ] && [ "$status" != "403" ]; then
    ok "$label retornou erro real nao-auth $status"
  else
    fail "$label retornou status auth/indisponivel $status: $(head -c 300 /tmp/healthintel_check_body.txt 2>/dev/null || true)"
  fi
}

check_cors() {
  local headers
  headers="$(curl -sS -i -X OPTIONS "$API_BASE_URL/v1/meta/endpoints" \
    -H "Origin: $ORIGIN" \
    -H "Access-Control-Request-Method: GET" \
    -H "Access-Control-Request-Headers: X-API-Key" || true)"

  if printf '%s\n' "$headers" | tr -d '\r' | grep -qi "^access-control-allow-origin: $ORIGIN$"; then
    ok "CORS aceita Origin $ORIGIN"
  else
    fail "CORS nao retornou access-control-allow-origin para $ORIGIN"
  fi
}

expect_status "API /saude" "200" "$API_BASE_URL/saude"
expect_status "API /prontidao" "200" "$API_BASE_URL/prontidao"
expect_status "API /v1/meta/endpoints admin" "200" "$API_BASE_URL/v1/meta/endpoints" -H "X-API-Key: $ADMIN_KEY"
expect_status "API /v1/operadoras dev" "200" "$API_BASE_URL/v1/operadoras?pagina=1&por_pagina=10" -H "X-API-Key: $DEV_KEY"
expect_status "Admin billing com chave dev" "403" "$API_BASE_URL/admin/billing/resumo?referencia=2026-05" -H "X-API-Key: $DEV_KEY"
expect_admin_real_status "Admin billing com chave admin" "$API_BASE_URL/admin/billing/resumo?referencia=2026-05"
check_cors
expect_status "Frontend local" "200" "$FRONTEND_URL" -I

rm -f /tmp/healthintel_check_body.txt

if [ "$FAILURES" -gt 0 ]; then
  printf '\nResultado: %s falha(s).\n' "$FAILURES" >&2
  exit 1
fi

printf '\nResultado: todos os checks passaram.\n'
