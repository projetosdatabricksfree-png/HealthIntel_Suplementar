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

API_BASE_URL="${API_BASE_URL:-https://api.healthintel.com.br}"
DEV_KEY="${HML_DEV_API_KEY:-}"
ADMIN_KEY="${HML_ADMIN_API_KEY:-}"
FAILURES=0

ok() {
  printf 'OK_COM_DADOS %s\n' "$*"
}

warn() {
  printf 'OK_VAZIO %s\n' "$*"
}

fail() {
  printf 'FAIL %s\n' "$*" >&2
  FAILURES=$((FAILURES + 1))
}

status_code() {
  local url="$1"
  shift
  local code
  code="$(curl -sS -o /tmp/healthintel_api_core_check_body.json -w '%{http_code}' "$@" "$url" 2>/tmp/healthintel_api_core_check_error.log || true)"
  if [ -z "$code" ]; then
    printf '000'
    return
  fi
  printf '%s' "$code"
}

json_data_len() {
  python3 - <<'PY'
import json
from pathlib import Path

path = Path("/tmp/healthintel_api_core_check_body.json")
if not path.exists():
    print(0)
    raise SystemExit

try:
    payload = json.loads(path.read_text())
except Exception:
    print(0)
    raise SystemExit

dados = payload.get("dados")
if isinstance(dados, list):
    print(len(dados))
else:
    print(0)
PY
}

json_first_record_summary() {
  python3 - <<'PY'
import json
from pathlib import Path

path = Path("/tmp/healthintel_api_core_check_body.json")
if not path.exists():
    print("{}")
    raise SystemExit

try:
    payload = json.loads(path.read_text())
except Exception:
    print("{}")
    raise SystemExit

dados = payload.get("dados")
if not isinstance(dados, list) or not dados:
    print("{}")
    raise SystemExit

row = dados[0]
if not isinstance(row, dict):
    print("{}")
    raise SystemExit

selected = {
    "registro_ans": row.get("registro_ans"),
    "nome": row.get("nome"),
    "razao_social": row.get("razao_social"),
    "modalidade": row.get("modalidade"),
    "uf_sede": row.get("uf_sede"),
    "competencia_referencia": row.get("competencia_referencia"),
}
print(json.dumps(selected, ensure_ascii=True))
PY
}

classify_result() {
  local label="$1"
  local code="$2"
  local require_data="${3:-false}"
  local data_len

  case "$code" in
    200)
      data_len="$(json_data_len)"
      if [ "$require_data" = "true" ] && [ "$data_len" -eq 0 ]; then
        warn "$label retornou 200 com dados vazios"
        FAILURES=$((FAILURES + 1))
        return
      fi
      if [ "$data_len" -gt 0 ]; then
        ok "$label retornou 200 com $data_len registro(s)"
      else
        warn "$label retornou 200 sem lista de dados ou com lista vazia"
      fi
      ;;
    401|403)
      fail "$label ERRO_AUTH $code: $(head -c 240 /tmp/healthintel_api_core_check_body.json 2>/dev/null || true)"
      ;;
    500|503)
      fail "$label ERRO_BACKEND $code: $(head -c 240 /tmp/healthintel_api_core_check_body.json 2>/dev/null || true)"
      ;;
    404)
      fail "$label FORA_DO_MVP $code"
      ;;
    000)
      fail "$label indisponivel: $(head -c 240 /tmp/healthintel_api_core_check_error.log 2>/dev/null || true)"
      ;;
    *)
      fail "$label status inesperado $code: $(head -c 240 /tmp/healthintel_api_core_check_body.json 2>/dev/null || true)"
      ;;
  esac
}

if [ -z "$DEV_KEY" ]; then
  fail "HML_DEV_API_KEY ausente"
fi

if [ -z "$ADMIN_KEY" ]; then
  fail "HML_ADMIN_API_KEY ausente"
fi

code="$(status_code "$API_BASE_URL/saude")"
if [ "$code" = "200" ]; then
  ok "/saude retornou 200"
else
  fail "/saude retornou $code"
fi

code="$(status_code "$API_BASE_URL/prontidao")"
if [ "$code" = "200" ]; then
  ok "/prontidao retornou 200"
else
  fail "/prontidao retornou $code"
fi

code="$(status_code "$API_BASE_URL/v1/meta/endpoints" -H "X-API-Key: $ADMIN_KEY")"
classify_result "/v1/meta/endpoints" "$code" false

code="$(status_code "$API_BASE_URL/v1/operadoras?pagina=1&por_pagina=10" -H "X-API-Key: $DEV_KEY")"
classify_result "/v1/operadoras" "$code" true
if [ "$code" = "200" ]; then
  printf 'PAYLOAD /v1/operadoras %s\n' "$(json_first_record_summary)"
fi

code="$(status_code "$API_BASE_URL/v1/rankings/operadora/score?pagina=1&por_pagina=10" -H "X-API-Key: $DEV_KEY")"
classify_result "/v1/rankings/operadora/score" "$code" false

code="$(status_code "$API_BASE_URL/v1/mercado/municipio?pagina=1&por_pagina=10" -H "X-API-Key: $DEV_KEY")"
classify_result "/v1/mercado/municipio" "$code" false

rm -f /tmp/healthintel_api_core_check_body.json /tmp/healthintel_api_core_check_error.log

if [ "$FAILURES" -gt 0 ]; then
  printf '\nResultado: %s falha(s) na homologacao comercial Core.\n' "$FAILURES" >&2
  exit 1
fi

printf '\nResultado: checks Core passaram com dados comerciais minimos.\n'
