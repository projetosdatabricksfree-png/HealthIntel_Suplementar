#!/usr/bin/env bash
# Smoke test para endpoints comerciais HealthIntel.
# Uso: HEALTHINTEL_API_KEY=<key> bash scripts/smoke/smoke_api_endpoints_comerciais.sh [BASE_URL]
set -euo pipefail

BASE_URL="${1:-http://5.189.160.27:8080}"
KEY="${HEALTHINTEL_API_KEY:-}"

PASS=0
FAIL=0

check() {
    local label="$1"
    local path="$2"

    # Sem chave → 401
    local code_no_key
    code_no_key=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}${path}?page=1&per_page=5")
    if [ "$code_no_key" = "401" ]; then
        echo "[PASS] $label — sem chave retorna 401"
        PASS=$((PASS + 1))
    else
        echo "[FAIL] $label — sem chave retornou $code_no_key (esperado 401)"
        FAIL=$((FAIL + 1))
    fi

    if [ -z "$KEY" ]; then
        echo "[SKIP] $label — HEALTHINTEL_API_KEY não definida, pulando teste com chave"
        return
    fi

    # Com chave → 200 + envelope
    local body
    body=$(curl -s -w "\n%{http_code}" -H "X-API-Key: ${KEY}" "${BASE_URL}${path}?page=1&per_page=5")
    local code
    code=$(echo "$body" | tail -1)
    local json
    json=$(echo "$body" | head -n -1)

    if [ "$code" != "200" ]; then
        echo "[FAIL] $label — com chave retornou $code (esperado 200)"
        FAIL=$((FAIL + 1))
        return
    fi

    # Valida estrutura do envelope
    local has_dados has_meta has_total
    has_dados=$(echo "$json" | python3 -c "import sys,json; d=json.load(sys.stdin); print('yes' if 'dados' in d else 'no')" 2>/dev/null || echo "no")
    has_meta=$(echo "$json" | python3 -c "import sys,json; d=json.load(sys.stdin); print('yes' if 'meta' in d else 'no')" 2>/dev/null || echo "no")
    has_total=$(echo "$json" | python3 -c "import sys,json; d=json.load(sys.stdin); print('yes' if d.get('meta',{}).get('total') is not None else 'no')" 2>/dev/null || echo "no")

    if [ "$has_dados" = "yes" ] && [ "$has_meta" = "yes" ] && [ "$has_total" = "yes" ]; then
        local total
        total=$(echo "$json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['meta']['total'])" 2>/dev/null || echo "?")
        echo "[PASS] $label — 200, envelope ok, total=$total"
        PASS=$((PASS + 1))
    else
        echo "[FAIL] $label — 200 mas envelope inválido (dados=$has_dados meta=$has_meta total=$has_total)"
        echo "       Resposta: $(echo "$json" | head -c 200)"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== Smoke: Endpoints HealthIntel Comerciais ==="
echo "    BASE_URL: $BASE_URL"
echo "    KEY: ${KEY:0:12}..."
echo ""

# Endpoints existentes (validação de regressão)
check "operadoras"        "/v1/operadoras"
check "meta/dataset"      "/v1/meta/dataset"
check "meta/versao"       "/v1/meta/versao"
check "tuss/procedimentos" "/v1/tuss/procedimentos"

# Novos endpoints comerciais
check "produtos-planos"   "/v1/produtos-planos"
check "historico-planos"  "/v1/historico-planos"
check "regulatorio"       "/v1/regulatorio"
check "igr"               "/v1/igr"
check "nip"               "/v1/nip"
check "idss"              "/v1/idss"
check "financeiro"        "/v1/financeiro"
check "prudencial"        "/v1/prudencial"
check "regime-especial"   "/v1/regime-especial"
check "glosa"             "/v1/glosa"

echo ""
echo "=== Resultado: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
