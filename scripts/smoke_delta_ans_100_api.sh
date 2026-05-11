#!/usr/bin/env bash
# Sprint 42 — smoke API: saúde, readiness e frontend
set -euo pipefail

API_BASE="https://api.healthintel.com.br"
APP_BASE="https://app.healthintel.com.br"

echo "=== Smoke API Delta ANS 100% ==="
echo "Timestamp: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo ""

check_endpoint() {
    local label="$1"
    local url="$2"
    local expected_status="${3:-200}"

    http_status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "$url" || echo "ERRO_CURL")

    if [ "$http_status" = "$expected_status" ]; then
        echo "OK    [$http_status] $label — $url"
    else
        echo "FALHA [$http_status] $label — $url (esperado: $expected_status)"
    fi
}

echo "--- Endpoints API ---"
check_endpoint "/saude"  "${API_BASE}/saude"  "200"
check_endpoint "/ready"  "${API_BASE}/ready"  "200"

echo ""
echo "--- Frontend ---"
check_endpoint "app.healthintel.com.br" "${APP_BASE}" "200"

echo ""
echo "--- Headers /saude (raw) ---"
curl -si --max-time 15 "${API_BASE}/saude" | head -20

echo ""
echo "=== Fim smoke API ==="
