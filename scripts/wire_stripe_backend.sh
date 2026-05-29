#!/usr/bin/env bash
# Wire backend Stripe config into /opt/healthintel/.env (Caminho A — checkout via API).
# Prompts for the two live secrets interactively so they are NOT stored in the script
# nor in shell history. Price IDs are not secret and are baked in below.
#
# Run:  bash /opt/healthintel/scripts/wire_stripe_backend.sh
set -euo pipefail

ENV_FILE="/opt/healthintel/.env"

# Price IDs (BRL, mensal) — confirmados contra a Pricing page
PRICE_STARTER="price_1TYvBbHOIEIF4PLbGiZ3RhnC"
PRICE_PRO="price_1TYvBnHOIEIF4PLbsqWJzQij"
PRICE_MAX="price_1TYvBnHOIEIF4PLb6afYNzSE"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERRO: $ENV_FILE não encontrado." >&2
  exit 1
fi

# Aborta se já existir STRIPE_SECRET_KEY para não duplicar
if grep -qE '^STRIPE_SECRET_KEY=' "$ENV_FILE"; then
  echo "AVISO: STRIPE_SECRET_KEY já existe em $ENV_FILE — nada a fazer."
  echo "Chaves STRIPE atuais:"
  grep -oE '^STRIPE[A-Z_]*=' "$ENV_FILE" || true
  exit 0
fi

# Lê os segredos sem ecoar na tela / sem ir pro history
read -r -s -p "Cole a STRIPE_SECRET_KEY (sk_live_...): " SK; echo
read -r -s -p "Cole o STRIPE_WEBHOOK_SECRET (whsec_...): " WH; echo

if [[ -z "$SK" || -z "$WH" ]]; then
  echo "ERRO: secret key e webhook secret são obrigatórios." >&2
  exit 1
fi
if [[ "$SK" != sk_live_* && "$SK" != sk_test_* ]]; then
  echo "ERRO: a secret key deve começar com sk_live_ ou sk_test_." >&2
  exit 1
fi
if [[ "$WH" != whsec_* ]]; then
  echo "ERRO: o webhook secret deve começar com whsec_." >&2
  exit 1
fi

# Backup
BACKUP="${ENV_FILE}.bak.$(date +%s)"
cp "$ENV_FILE" "$BACKUP"
echo "Backup criado: $BACKUP"

# Append (sem ecoar os segredos)
{
  printf '\n# Stripe backend (funil pago via API) — rotacionar secret + webhook após validar\n'
  printf 'STRIPE_SECRET_KEY=%s\n' "$SK"
  printf 'STRIPE_WEBHOOK_SECRET=%s\n' "$WH"
  printf 'STRIPE_PRICE_STARTER=%s\n' "$PRICE_STARTER"
  printf 'STRIPE_PRICE_PRO=%s\n' "$PRICE_PRO"
  printf 'STRIPE_PRICE_MAX=%s\n' "$PRICE_MAX"
} >> "$ENV_FILE"

unset SK WH

echo "OK — STRIPE no .env (nomes, sem valores):"
grep -oE '^STRIPE[A-Z_]*=' "$ENV_FILE"
