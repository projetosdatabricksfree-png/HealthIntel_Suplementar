#!/usr/bin/env bash
# §18.4 — Verifica validade do certificado TLS e alerta se expira em < DIAS_ALERTA dias.
# Instalar em cron diario na VPS:
#   0 7 * * * root bash /opt/healthintel/scripts/vps/check_tls_expiracao.sh >> /var/log/healthintel/tls_check.log 2>&1

set -euo pipefail

HOSTS="${TLS_HOSTS:-api.healthintel.com.br app.healthintel.com.br}"
DIAS_ALERTA="${TLS_DIAS_ALERTA:-30}"
SLACK_WEBHOOK="${SLACK_WEBHOOK_URL:-}"
EMAIL_DESTINO="${TLS_ALERT_EMAIL:-}"

falhas=0

_alerta() {
  local host="$1" dias_restantes="$2" validade="$3"
  local msg="[TLS] ALERTA: ${host} expira em ${dias_restantes} dia(s) (${validade}). Caddy pode estar com problema de renovacao."

  echo "$msg"

  if [[ -n "$SLACK_WEBHOOK" ]]; then
    curl -s -X POST "$SLACK_WEBHOOK" \
      -H 'Content-type: application/json' \
      --data "{\"text\":\"$msg\"}" >/dev/null || true
  fi

  if [[ -n "$EMAIL_DESTINO" ]]; then
    echo "$msg" | mail -s "[HealthIntel] Alerta TLS: $host" "$EMAIL_DESTINO" 2>/dev/null || true
  fi

  falhas=$((falhas + 1))
}

for host in $HOSTS; do
  validade=$(openssl s_client -connect "${host}:443" -servername "${host}" \
    </dev/null 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)

  if [[ -z "$validade" ]]; then
    echo "[TLS] ERRO: nao foi possivel obter certificado de ${host}"
    falhas=$((falhas + 1))
    continue
  fi

  expira_ts=$(date -d "$validade" +%s 2>/dev/null || date -jf "%b %d %T %Y %Z" "$validade" +%s 2>/dev/null || echo 0)
  agora_ts=$(date +%s)
  dias_restantes=$(( (expira_ts - agora_ts) / 86400 ))

  if (( dias_restantes < 0 )); then
    _alerta "$host" "$dias_restantes" "$validade"
    echo "[TLS] CRITICO: ${host} JA EXPIROU em ${validade}"
  elif (( dias_restantes < DIAS_ALERTA )); then
    _alerta "$host" "$dias_restantes" "$validade"
  else
    echo "[TLS] OK: ${host} expira em ${dias_restantes} dia(s) (${validade})"
  fi
done

exit $falhas
