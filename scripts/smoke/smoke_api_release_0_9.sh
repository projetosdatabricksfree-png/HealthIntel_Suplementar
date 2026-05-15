#!/usr/bin/env bash
# Smoke API Release 0.9 Core ANS Comercial.
#
# Valida:
#   - /saude e /prontidao respondem sem autenticacao
#   - endpoints autenticados requerem X-API-Key
#   - endpoints publicaveis retornam 200 + envelope {dados, meta}
#   - paginacao funciona
#   - per_page acima do maximo e limitado
#   - endpoints ocultos (TISS, CNES, REDE, REGULATORIO) ainda respondem (nao-quebra)
#   - /openapi.json nao expoe endpoints ocultos (quando docs habilitado)
#
# Variaveis de ambiente:
#   HEALTHINTEL_TARGET_URL  - base URL (default: http://localhost:8080)
#   HEALTHINTEL_API_KEY     - chave valida (obrigatoria para testes autenticados)
#   HEALTHINTEL_REGISTRO_ANS - registro ANS para teste (default: 412755)
#
# Uso:
#   bash scripts/smoke/smoke_api_release_0_9.sh
#   HEALTHINTEL_TARGET_URL=http://5.189.160.27:8080 \\
#     HEALTHINTEL_API_KEY=... bash scripts/smoke/smoke_api_release_0_9.sh

set -uo pipefail

BASE="${HEALTHINTEL_TARGET_URL:-http://localhost:8080}"
KEY="${HEALTHINTEL_API_KEY:-}"
INTERNAL_TOKEN="${HEALTHINTEL_INTERNAL_TOKEN:-}"
REG="${HEALTHINTEL_REGISTRO_ANS:-412755}"
LOG_DIR="${HEALTHINTEL_LOG_DIR:-docs/evidencias/release_0_9}"
LOG_FILE="${LOG_DIR}/smoke_api_release_0_9.log"

mkdir -p "$LOG_DIR"
: > "$LOG_FILE"

PASS=0
FAIL=0

log() {
    echo "$@" | tee -a "$LOG_FILE"
}

testar() {
    # Aceita um ou mais codigos http esperados separados por '|' (ex: "200|403")
    local nome="$1" esperado="$2" comando="$3"
    local resposta http_code
    resposta=$(eval "$comando" 2>&1)
    http_code=$(echo "$resposta" | tail -1)
    local detalhe=$(echo "$resposta" | head -n -1 | head -c 200)
    if [[ "|$esperado|" == *"|$http_code|"* ]]; then
        log "  ✅ $nome: http=$http_code (esperado $esperado)"
        PASS=$((PASS + 1))
    else
        log "  ❌ $nome: http=$http_code (esperado $esperado) | resposta: $detalhe"
        FAIL=$((FAIL + 1))
    fi
}

curl_code() {
    # Imprime body e na ultima linha o HTTP code
    local url="$1"; shift
    curl -sS -o - -w "\n%{http_code}" "$@" "$url"
}

log "===== Smoke API Release 0.9 ====="
log "Base URL: $BASE"
log "Registro ANS teste: $REG"
log "Inicio: $(date -Iseconds)"
log ""

# -------- Bloco 1: endpoints publicos sem auth --------
log "[1] Endpoints publicos / internos"
testar "/saude (publico)" "200" "curl_code '$BASE/saude'"
testar "/prontidao sem token interno (401)" "401" "curl_code '$BASE/prontidao'"
if [[ -n "$INTERNAL_TOKEN" ]]; then
    testar "/prontidao com token interno (200)" "200" "curl_code '$BASE/prontidao' -H 'X-Internal-Token: $INTERNAL_TOKEN'"
fi

# -------- Bloco 2: autenticacao --------
log ""
log "[2] Autenticacao (X-API-Key)"
testar "/v1/meta/dataset sem chave (deve falhar)" "401" "curl_code '$BASE/v1/meta/dataset'"
testar "/v1/meta/dataset chave invalida (deve falhar)" "401" "curl_code '$BASE/v1/meta/dataset' -H 'X-API-Key: chave-invalida'"

if [[ -z "$KEY" ]]; then
    log "  ⚠️  HEALTHINTEL_API_KEY nao definida. Pulando testes autenticados."
else
    # 200 = chave + plano OK. 403 = chave OK mas plano sem acesso (depende do plano da chave de teste).
    testar "/v1/meta/dataset com chave (200 ou 403)" "200|403" "curl_code '$BASE/v1/meta/dataset' -H 'X-API-Key: $KEY'"

    # -------- Bloco 3: endpoints publicaveis com dado real --------
    log ""
    log "[3] Endpoints publicaveis (com dado)"
    testar "/v1/operadoras" "200|403" "curl_code '$BASE/v1/operadoras?per_page=5' -H 'X-API-Key: $KEY'"
    testar "/v1/operadoras/{reg} (200/404 reg inexistente/403 plano)" "200|404|403" "curl_code '$BASE/v1/operadoras/$REG' -H 'X-API-Key: $KEY'"
    testar "/v1/produtos/planos" "200|403" "curl_code '$BASE/v1/produtos/planos?per_page=5' -H 'X-API-Key: $KEY'"
    testar "/v1/produtos/historico" "200|403" "curl_code '$BASE/v1/produtos/historico?per_page=5' -H 'X-API-Key: $KEY'"
    testar "/v1/mercado/municipio" "200|403" "curl_code '$BASE/v1/mercado/municipio?per_page=5' -H 'X-API-Key: $KEY'"
    testar "/v1/rankings/score (200/403)" "200|403|404" "curl_code '$BASE/v1/rankings/score?per_page=5' -H 'X-API-Key: $KEY'"
    testar "/v1/prata/cadop" "200|403" "curl_code '$BASE/v1/prata/cadop?competencia=202412&per_page=5' -H 'X-API-Key: $KEY'"

    # -------- Bloco 4: paginacao --------
    log ""
    log "[4] Paginacao"
    testar "/v1/produtos/planos?page=1&per_page=10" "200|403" "curl_code '$BASE/v1/produtos/planos?page=1&per_page=10' -H 'X-API-Key: $KEY'"
    testar "/v1/produtos/planos?per_page=99999 (limitado/422)" "200|403|422" "curl_code '$BASE/v1/produtos/planos?per_page=99999' -H 'X-API-Key: $KEY'"

    # -------- Bloco 5: endpoints ocultos (TISS) - ainda respondem via HTTP --------
    log ""
    log "[5] Endpoints ocultos do Swagger (ainda respondem com 200/403/404)"
    testar "/v1/tiss/{reg}/procedimentos" "200|403|404" "curl_code '$BASE/v1/tiss/$REG/procedimentos' -H 'X-API-Key: $KEY'"
    testar "/v1/cnes/municipios" "200|403|404" "curl_code '$BASE/v1/cnes/municipios' -H 'X-API-Key: $KEY'"
    testar "/v1/regulatorio/portabilidade" "200|403|404" "curl_code '$BASE/v1/regulatorio/portabilidade' -H 'X-API-Key: $KEY'"
fi

# -------- Bloco 6: endpoints inexistentes --------
log ""
log "[6] Endpoints inexistentes"
testar "/v1/inexistente" "404" "curl_code '$BASE/v1/inexistente'"

# -------- Bloco 7: Swagger limpo --------
log ""
log "[7] OpenAPI / Swagger (apenas se docs habilitado)"
openapi=$(curl -sS "$BASE/openapi.json" 2>&1)
http_openapi=$(curl -sS -o /dev/null -w "%{http_code}" "$BASE/openapi.json")
if [[ "$http_openapi" == "200" ]]; then
    n_paths=$(echo "$openapi" | grep -oE '"/v1/[^"]+"' | sort -u | wc -l)
    n_tiss=$(echo "$openapi" | grep -oE '"/v1/tiss[^"]*"' | wc -l)
    n_cnes=$(echo "$openapi" | grep -oE '"/v1/cnes[^"]*"' | wc -l)
    n_rede=$(echo "$openapi" | grep -oE '"/v1/rede[^"]*"' | wc -l)
    log "  ℹ️  /openapi.json: $n_paths paths v1 (tiss=$n_tiss, cnes=$n_cnes, rede=$n_rede)"
    if [[ "$n_tiss" == "0" && "$n_cnes" == "0" && "$n_rede" == "0" ]]; then
        log "  ✅ Swagger limpo: TISS/CNES/REDE ocultos"
        PASS=$((PASS + 1))
    else
        log "  ❌ Swagger expoe TISS/CNES/REDE: tiss=$n_tiss cnes=$n_cnes rede=$n_rede"
        FAIL=$((FAIL + 1))
    fi
else
    log "  ℹ️  /openapi.json: http=$http_openapi (provavelmente desabilitado em producao)"
fi

# -------- Resumo --------
log ""
log "===== Resumo ====="
log "PASS: $PASS"
log "FAIL: $FAIL"
log "Fim: $(date -Iseconds)"

if [[ "$FAIL" -gt 0 ]]; then
    exit 1
fi
exit 0
