#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
HML_IP="${HML_IP:-5.189.160.27}"
ENV_FILE="${ENV_FILE:-$PROJECT_DIR/.env.hml}"
APP_ENV_FILE="$PROJECT_DIR/frontend/healthintel_frontend_fase9/.env.production"
COMPOSE_FILES=(-f "$PROJECT_DIR/infra/docker-compose.yml" -f "$PROJECT_DIR/infra/docker-compose.hml.yml")
SERVICES=(postgres mongo redis api mongo_layout_service nginx frontend)

read_env_value() {
  local key="$1"
  awk -F= -v target="$key" '$1 == target {sub(/^[^=]*=/, "", $0); print $0; exit}' "$ENV_FILE"
}

log() {
  printf '\n[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

if [ ! -d "$PROJECT_DIR/infra" ] || [ ! -d "$PROJECT_DIR/frontend/healthintel_frontend_fase9" ]; then
  echo "FAIL: PROJECT_DIR invalido: $PROJECT_DIR" >&2
  echo "Use: PROJECT_DIR=/opt/healthintel $0" >&2
  exit 1
fi

if [ "$PROJECT_DIR" != "/opt/healthintel" ]; then
  log "Aviso: PROJECT_DIR atual e $PROJECT_DIR. Em VPS, o caminho recomendado e /opt/healthintel."
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "FAIL: arquivo de ambiente nao encontrado: $ENV_FILE" >&2
  echo "Crie com: cp .env.hml.example .env.hml" >&2
  exit 1
fi

if grep -q '<trocar' "$ENV_FILE"; then
  echo "FAIL: $ENV_FILE ainda contem placeholders <trocar...>. Preencha valores fortes antes do deploy." >&2
  exit 1
fi

API_PUBLIC_URL_VALUE="${API_PUBLIC_URL:-$(read_env_value API_PUBLIC_URL || true)}"
FRONTEND_API_BASE_URL="${API_PUBLIC_URL_VALUE:-http://$HML_IP:8080}"

log "Gravando env de build do frontend para homologacao"
cat > "$APP_ENV_FILE" <<EOF
VITE_API_BASE_URL=$FRONTEND_API_BASE_URL
VITE_ENABLE_DEMO_FALLBACK=false
VITE_APP_NAME=HealthIntel Core ANS
EOF

log "Validando docker compose"
docker compose --env-file "$ENV_FILE" "${COMPOSE_FILES[@]}" config >/tmp/healthintel_hml_compose_rendered.yml

log "Subindo somente servicos de homologacao"
docker compose --env-file "$ENV_FILE" "${COMPOSE_FILES[@]}" up -d --build "${SERVICES[@]}"

log "Status dos containers"
docker compose --env-file "$ENV_FILE" "${COMPOSE_FILES[@]}" ps "${SERVICES[@]}"

cat <<EOF

Deploy iniciado.

Logs uteis:
docker compose --env-file "$ENV_FILE" -f "$PROJECT_DIR/infra/docker-compose.yml" -f "$PROJECT_DIR/infra/docker-compose.hml.yml" logs -f api nginx frontend

Healthcheck local na VPS:
$PROJECT_DIR/scripts/vps/check_hml_ip.sh

Rollback simples da camada exposta:
docker compose --env-file "$ENV_FILE" -f "$PROJECT_DIR/infra/docker-compose.yml" -f "$PROJECT_DIR/infra/docker-compose.hml.yml" stop frontend nginx api mongo_layout_service
EOF
