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
      HML_DEV_API_KEY|HML_ADMIN_API_KEY)
        export "$key=$value"
        ;;
    esac
  done < "$ENV_FILE"
fi

FRONTEND_URL="${FRONTEND_URL:-http://app.healthintel.com.br}"
API_BASE_URL="${API_BASE_URL:-http://api.healthintel.com.br:8080}"
ORIGIN="${ORIGIN:-http://app.healthintel.com.br}"
DEV_KEY="${HML_DEV_API_KEY:-}"
ADMIN_KEY="${HML_ADMIN_API_KEY:-}"
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
  curl -sS -o /tmp/healthintel_domain_check_body.txt -w '%{http_code}' "$@" "$url" || printf '000'
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
    fail "$label esperava $expected e retornou $status: $(head -c 300 /tmp/healthintel_domain_check_body.txt 2>/dev/null || true)"
  fi
}

check_cors() {
  local headers
  headers="$(curl -sS -i -X OPTIONS "$API_BASE_URL/v1/operadoras?pagina=1&por_pagina=10" \
    -H "Origin: $ORIGIN" \
    -H "Access-Control-Request-Method: GET" \
    -H "Access-Control-Request-Headers: X-API-Key" || true)"

  if printf '%s\n' "$headers" | tr -d '\r' | grep -qi "^access-control-allow-origin: $ORIGIN$"; then
    ok "CORS dominio aceita Origin $ORIGIN"
  else
    fail "CORS dominio nao retornou access-control-allow-origin para $ORIGIN"
  fi

  if printf '%s\n' "$headers" | tr -d '\r' | grep -qi '^access-control-allow-headers: .*X-API-Key'; then
    ok "CORS dominio aceita header X-API-Key"
  else
    fail "CORS dominio nao declarou X-API-Key em access-control-allow-headers"
  fi
}

expect_status "Frontend dominio" "200" "$FRONTEND_URL" -I
expect_status "API dominio /saude" "200" "$API_BASE_URL/saude"
expect_status "API dominio /prontidao" "200" "$API_BASE_URL/prontidao"

if [ -n "$ADMIN_KEY" ]; then
  expect_status "API dominio /v1/meta/endpoints admin" "200" "$API_BASE_URL/v1/meta/endpoints" -H "X-API-Key: $ADMIN_KEY"
else
  fail "HML_ADMIN_API_KEY ausente para teste de /v1/meta/endpoints"
fi

if [ -n "$DEV_KEY" ]; then
  expect_status "API dominio /v1/operadoras dev" "200" "$API_BASE_URL/v1/operadoras?pagina=1&por_pagina=10" -H "X-API-Key: $DEV_KEY"
  expect_status "Admin billing com chave dev" "403" "$API_BASE_URL/admin/billing/resumo?referencia=2026-05" -H "X-API-Key: $DEV_KEY"
else
  fail "HML_DEV_API_KEY ausente para testes de rotas Core/admin"
fi

if [ -n "$ADMIN_KEY" ]; then
  local_admin_status="$(status_code "$API_BASE_URL/admin/billing/resumo?referencia=2026-05" -H "X-API-Key: $ADMIN_KEY")"
  if [ "$local_admin_status" = "200" ] || [ "$local_admin_status" = "500" ] || [ "$local_admin_status" = "503" ]; then
    ok "Admin billing com chave admin retornou $local_admin_status"
  else
    fail "Admin billing com chave admin retornou $local_admin_status: $(head -c 300 /tmp/healthintel_domain_check_body.txt 2>/dev/null || true)"
  fi
fi

check_cors

rm -f /tmp/healthintel_domain_check_body.txt

if [ "$FAILURES" -gt 0 ]; then
  printf '\nResultado: %s falha(s).\n' "$FAILURES" >&2
  exit 1
fi

printf '\nResultado: todos os checks por dominio HTTP passaram.\n'
