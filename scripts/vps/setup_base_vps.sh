#!/usr/bin/env bash
set -Eeuo pipefail

log() {
  printf '\n[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

if [ "$(id -u)" -eq 0 ]; then
  SUDO=""
else
  SUDO="sudo"
fi

log "Atualizando pacotes base"
$SUDO apt-get update
$SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y \
  ca-certificates \
  curl \
  dnsutils \
  git \
  gnupg \
  htop \
  jq \
  nano \
  rsync \
  ufw \
  unzip

if ! command -v docker >/dev/null 2>&1; then
  log "Instalando Docker via repositorio do Ubuntu"
  $SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y docker.io
else
  log "Docker ja instalado"
fi

log "Habilitando servico Docker"
$SUDO systemctl enable docker
$SUDO systemctl start docker

if docker compose version >/dev/null 2>&1; then
  log "Docker Compose plugin ja instalado"
else
  log "Instalando Docker Compose plugin oficial"
  ARCH="$(uname -m)"
  case "$ARCH" in
    x86_64) COMPOSE_ARCH="x86_64" ;;
    aarch64|arm64) COMPOSE_ARCH="aarch64" ;;
    *)
      echo "Arquitetura nao suportada automaticamente para Docker Compose: $ARCH" >&2
      exit 1
      ;;
  esac
  $SUDO mkdir -p /usr/local/lib/docker/cli-plugins
  $SUDO curl -fsSL \
    "https://github.com/docker/compose/releases/download/v2.29.7/docker-compose-linux-${COMPOSE_ARCH}" \
    -o /usr/local/lib/docker/cli-plugins/docker-compose
  $SUDO chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
  docker compose version
fi

if [ -n "${SUDO_USER:-}" ] && [ "$SUDO_USER" != "root" ]; then
  log "Adicionando usuario $SUDO_USER ao grupo docker"
  $SUDO usermod -aG docker "$SUDO_USER" || true
fi

if swapon --show | awk 'NR > 1 { found=1 } END { exit found ? 0 : 1 }'; then
  log "Swap ja existe"
else
  log "Criando swap de 8G em /swapfile"
  $SUDO fallocate -l 8G /swapfile || $SUDO dd if=/dev/zero of=/swapfile bs=1M count=8192
  $SUDO chmod 600 /swapfile
  $SUDO mkswap /swapfile
  $SUDO swapon /swapfile
  if ! grep -qE '^/swapfile\s+' /etc/fstab; then
    echo '/swapfile none swap sw 0 0' | $SUDO tee -a /etc/fstab >/dev/null
  fi
fi

log "Configurando firewall UFW: liberar somente 22, 80 e 8080"
$SUDO ufw allow 22/tcp
$SUDO ufw allow 80/tcp
$SUDO ufw allow 8080/tcp
$SUDO ufw default deny incoming
$SUDO ufw default allow outgoing
$SUDO ufw --force enable
$SUDO ufw status verbose

log "Setup base concluido"
cat <<'EOF'

Proximos passos:
1. Copiar o projeto para /opt/healthintel.
2. Criar /opt/healthintel/.env.hml a partir de .env.hml.example.
3. Trocar placeholders por valores fortes na VPS.
4. Rodar scripts/vps/deploy_hml_ip.sh dentro do projeto.

Observacao: se voce usa usuario nao-root, saia e entre novamente para aplicar o grupo docker.
EOF
