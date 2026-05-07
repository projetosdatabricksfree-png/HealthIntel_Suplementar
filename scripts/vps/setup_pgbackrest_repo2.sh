#!/usr/bin/env bash
# Sprint 40 / HIS-40.2 — Ativa repo2 S3-compatible no pgBackRest
#
# Valida variáveis de ambiente, materializa pgbackrest.conf com repo2,
# executa pgbackrest check e dispara o primeiro backup full no repo2.
#
# USO:
#   # 1. Preencher /etc/healthintel/pgbackrest.env com as vars reais (fora do git)
#   set -a; source /etc/healthintel/pgbackrest.env; set +a
#   sudo bash scripts/vps/setup_pgbackrest_repo2.sh
#
#   # Modo dry-run: valida vars sem alterar nada
#   DRY_RUN=1 bash scripts/vps/setup_pgbackrest_repo2.sh
#
# VARIÁVEIS NECESSÁRIAS (em /etc/healthintel/pgbackrest.env):
#   PGBACKREST_REPO2_ENDPOINT    — endpoint S3 (ex: s3.us-east-1.amazonaws.com)
#   PGBACKREST_REPO2_BUCKET      — nome do bucket
#   PGBACKREST_REPO2_REGION      — região (auto para Cloudflare R2)
#   PGBACKREST_REPO2_KEY         — Access Key ID
#   PGBACKREST_REPO2_KEY_SECRET  — Secret Access Key
#   PGBACKREST_REPO2_CIPHER_PASS — senha AES-256 (mínimo 32 chars aleatórios)
#   POSTGRES_DATA_DIR            — diretório de dados PostgreSQL
#
# PROVEDOR RECOMENDADO (MVP):
#   Cloudflare R2 — sem custo de egress, S3-compatible, bucket criado em:
#   https://dash.cloudflare.com -> R2 Object Storage
#   Region: use "auto" em PGBACKREST_REPO2_REGION para R2.

set -Eeuo pipefail

STANZA="${STANZA:-healthintel}"
CONF_TEMPLATE="${CONF_TEMPLATE:-infra/pgbackrest/pgbackrest.conf}"
CONF_DEST="${CONF_DEST:-/etc/pgbackrest/pgbackrest.conf}"
ENV_FILE_VPS="${ENV_FILE_VPS:-/etc/healthintel/pgbackrest.env}"
DRY_RUN="${DRY_RUN:-0}"

printf '[setup_pgbackrest_repo2] inicio=%s stanza=%s\n' "$(date --iso-8601=seconds)" "$STANZA"

# --- Validar variáveis obrigatórias ---
VARS_OBRIGATORIAS=(
  PGBACKREST_REPO2_ENDPOINT
  PGBACKREST_REPO2_BUCKET
  PGBACKREST_REPO2_REGION
  PGBACKREST_REPO2_KEY
  PGBACKREST_REPO2_KEY_SECRET
  PGBACKREST_REPO2_CIPHER_PASS
  POSTGRES_DATA_DIR
)

falhas=0
for var in "${VARS_OBRIGATORIAS[@]}"; do
  val="${!var:-}"
  if [[ -z "$val" ]]; then
    printf 'ERRO: variavel obrigatoria nao definida: %s\n' "$var" >&2
    falhas=$((falhas + 1))
  elif [[ "$val" == *"<"* ]]; then
    printf 'ERRO: variavel %s ainda tem placeholder: %s\n' "$var" "$val" >&2
    falhas=$((falhas + 1))
  fi
done

# Validar tamanho mínimo da cipher pass
if [[ -n "${PGBACKREST_REPO2_CIPHER_PASS:-}" ]]; then
  if [[ "${#PGBACKREST_REPO2_CIPHER_PASS}" -lt 32 ]]; then
    printf 'ERRO: PGBACKREST_REPO2_CIPHER_PASS deve ter >= 32 caracteres\n' >&2
    falhas=$((falhas + 1))
  fi
fi

if (( falhas > 0 )); then
  printf '\n%s variavel(is) invalida(s). Preencher %s e re-exportar:\n' "$falhas" "$ENV_FILE_VPS"
  printf '  set -a; source %s; set +a\n' "$ENV_FILE_VPS"
  printf '\nPara gerar PGBACKREST_REPO2_CIPHER_PASS segura:\n'
  printf '  python3 -c "import secrets; print(secrets.token_urlsafe(48))"\n'
  exit 1
fi

printf '[setup_pgbackrest_repo2] OK: todas as variáveis presentes\n'

if [[ "$DRY_RUN" == "1" ]]; then
  printf '[setup_pgbackrest_repo2] DRY_RUN=1 — validacoes passaram, encerrando sem alterar nada.\n'
  exit 0
fi

# --- Materializar pgbackrest.conf ---
if [[ ! -f "$CONF_TEMPLATE" ]]; then
  printf 'ERRO: template nao encontrado: %s\n' "$CONF_TEMPLATE" >&2
  exit 1
fi

printf '[setup_pgbackrest_repo2] materializando %s -> %s\n' "$CONF_TEMPLATE" "$CONF_DEST"
mkdir -p "$(dirname "$CONF_DEST")"
envsubst < "$CONF_TEMPLATE" > "${CONF_DEST}.tmp"

# Verificar que nao ha variaveis nao expandidas
if grep -q '\${' "${CONF_DEST}.tmp"; then
  printf 'ERRO: conf materializado ainda contem variaveis nao expandidas:\n' >&2
  grep '\${' "${CONF_DEST}.tmp" >&2
  rm -f "${CONF_DEST}.tmp"
  exit 1
fi

mv "${CONF_DEST}.tmp" "$CONF_DEST"
chmod 640 "$CONF_DEST"
chown postgres:postgres "$CONF_DEST" 2>/dev/null || true
printf '[setup_pgbackrest_repo2] OK: %s materializado\n' "$CONF_DEST"

# --- pgbackrest check para validar repo2 ---
printf '\n[setup_pgbackrest_repo2] executando pgbackrest check...\n'
if ! sudo -u postgres pgbackrest --stanza="$STANZA" check; then
  printf 'ERRO: pgbackrest check falhou. Verificar conectividade S3 e credenciais.\n' >&2
  printf 'Dicas:\n'
  printf '  - PGBACKREST_REPO2_ENDPOINT deve incluir o host sem "https://"\n'
  printf '  - Para Cloudflare R2: endpoint = <account_id>.r2.cloudflarestorage.com\n'
  printf '  - Verificar permissoes do bucket (ListBucket, GetObject, PutObject, DeleteObject)\n'
  exit 1
fi
printf '[setup_pgbackrest_repo2] OK: pgbackrest check passou\n'

# --- Primeiro backup full no repo2 ---
printf '\n[setup_pgbackrest_repo2] executando primeiro backup full no repo2...\n'
printf 'Este processo pode levar vários minutos dependendo do tamanho do banco.\n'
sudo -u postgres pgbackrest --stanza="$STANZA" --repo=2 backup --type=full

printf '\n[setup_pgbackrest_repo2] verificando repo2 em pgbackrest info...\n'
sudo -u postgres pgbackrest --stanza="$STANZA" info

printf '\n[setup_pgbackrest_repo2] concluido em %s\n' "$(date --iso-8601=seconds)"
printf '\nPROXIMOS PASSOS:\n'
printf '  1. Executar smoke: STANZA=%s make smoke-pgbackrest\n' "$STANZA"
printf '  2. Agendar backup diff repo2 no systemd ou crontab:\n'
printf '     sudo -u postgres pgbackrest --stanza=%s --repo=2 backup --type=diff\n' "$STANZA"
printf '  3. Registrar evidencia em docs/operacao/baseline_capacidade.md\n'
printf '  4. Testar restore a partir do repo2:\n'
printf '     sudo -u postgres bash scripts/backup/pgbackrest_restore.sh --type=latest --repo=2 --confirm\n'
