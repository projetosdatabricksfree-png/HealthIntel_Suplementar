#!/usr/bin/env bash
# Executar a cada 5 min via cron na VPS:
#   */5 * * * * root bash /opt/healthintel/scripts/alertas/cron_alertas.sh >> /var/log/healthintel/alertas.log 2>&1
#
# Requer /etc/healthintel/alertas.env com:
#   POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
#   SLACK_WEBHOOK_URL (ou ALERTAS_EMAIL_DEST + ALERTAS_SMTP_*)
#   ALERTAS_JANELA_MIN (default: 15)

set -euo pipefail

ENV_FILE="${ALERTAS_ENV_FILE:-/etc/healthintel/alertas.env}"
if [[ -f "${ENV_FILE}" ]]; then
    set -a
    # shellcheck source=/dev/null
    source "${ENV_FILE}"
    set +a
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec python3 "${SCRIPT_DIR}/alertas_criticos_bridge.py"
