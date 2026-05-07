#!/usr/bin/env bash
# §18.2 — Backup lógico PostgreSQL (Docker) → Cloudflare R2
#
# Usa pg_dumpall via docker exec + rclone para upload off-site.
# Registra início e resultado em plataforma.backup_execucao.
#
# REQUISITOS NA VPS:
#   - rclone instalado (curl https://rclone.org/install.sh | bash)
#   - /etc/healthintel/r2_backup.env criado e chmod 600 com as vars abaixo
#
# VARS EM /etc/healthintel/r2_backup.env:
#   RCLONE_CONFIG_R2_TYPE=s3
#   RCLONE_CONFIG_R2_PROVIDER=Cloudflare
#   RCLONE_CONFIG_R2_ACCESS_KEY_ID=<access_key_id>
#   RCLONE_CONFIG_R2_SECRET_ACCESS_KEY=<secret_access_key>
#   RCLONE_CONFIG_R2_ENDPOINT=https://<account_id>.r2.cloudflarestorage.com
#   R2_BUCKET=pgbackrest-vps
#   POSTGRES_USER=healthintel
#   POSTGRES_DB=healthintel
#
# USO:
#   bash scripts/backup/backup_r2.sh
#
# AGENDAMENTO (instalar na VPS):
#   /etc/cron.d/healthintel-backup-r2:
#     0 2 * * * root bash /opt/healthintel/scripts/backup/backup_r2.sh >> /var/log/healthintel/backup_r2.log 2>&1

set -euo pipefail

ENV_FILE="${BACKUP_ENV_FILE:-/etc/healthintel/r2_backup.env}"
if [[ -f "${ENV_FILE}" ]]; then
    set -a
    # shellcheck source=/dev/null
    source "${ENV_FILE}"
    set +a
fi

STANZA="${STANZA:-healthintel}"
CONTAINER="${POSTGRES_CONTAINER:-healthintel_postgres}"
PGUSER="${POSTGRES_USER:-healthintel}"
PGDB="${POSTGRES_DB:-healthintel}"
R2_BUCKET="${R2_BUCKET:-pgbackrest-vps}"
RCLONE_REMOTE="${RCLONE_REMOTE:-r2}"
TMP_DIR="${TMP_DIR:-/tmp}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DUMP_FILE="${TMP_DIR}/healthintel_${TIMESTAMP}.sql.gz"
REMOTE_NAME="healthintel_${TIMESTAMP}.sql.gz"

_psql() {
    docker exec "${CONTAINER}" psql -U "${PGUSER}" -d "${PGDB}" \
        -v ON_ERROR_STOP=1 -t -A -c "$1" 2>/dev/null
}

_psql_id() {
    _psql "$1" | grep -E '^[0-9]+$' | head -1
}

_escape() {
    printf '%s' "${1}" | sed "s/'/''/g"
}

echo "[backup_r2] inicio=$(date --iso-8601=seconds) stanza=${STANZA}"

# Registro de início em plataforma.backup_execucao
ID=$(_psql_id "INSERT INTO plataforma.backup_execucao
        (stanza, tipo, repositorio, iniciado_em, status, log_resumo)
    VALUES ('${STANZA}', 'full', 'repo2_externo', now(), 'em_execucao',
            'pg_dumpall → ${RCLONE_REMOTE}:${R2_BUCKET}/backups/${REMOTE_NAME}')
    RETURNING id;")
[[ "${ID}" =~ ^[0-9]+$ ]] || { echo "[backup_r2] ERRO: id inválido '${ID}'" >&2; exit 3; }
echo "[backup_r2] backup_execucao.id=${ID}"

RC=0

# Dump via docker exec
echo "[backup_r2] pg_dumpall inicio"
if ! docker exec "${CONTAINER}" pg_dumpall -U "${PGUSER}" 2>/dev/null | gzip > "${DUMP_FILE}"; then
    RC=$?
fi

BYTES=""
if [[ ${RC} -eq 0 ]]; then
    BYTES=$(stat -c%s "${DUMP_FILE}" 2>/dev/null || echo "")
    echo "[backup_r2] dump ok bytes=${BYTES:-?}; upload iniciando"

    if ! rclone copy "${DUMP_FILE}" "${RCLONE_REMOTE}:${R2_BUCKET}/backups/" \
        --retries 3 \
        --contimeout 60s \
        --timeout 300s; then
        RC=$?
    fi
fi

# Remover dump local
rm -f "${DUMP_FILE}"

if [[ ${RC} -eq 0 ]]; then
    # Remove backups R2 mais antigos que RETENTION_DAYS
    rclone delete --min-age "${RETENTION_DAYS}d" \
        "${RCLONE_REMOTE}:${R2_BUCKET}/backups/" 2>/dev/null || true

    _psql "UPDATE plataforma.backup_execucao SET
        finalizado_em=now(), status='sucesso',
        bytes_armazenados=${BYTES:-NULL},
        log_resumo='$(_escape "${RCLONE_REMOTE}:${R2_BUCKET}/backups/${REMOTE_NAME}")'
    WHERE id=${ID};"

    echo "[backup_r2] sucesso id=${ID} remote=${RCLONE_REMOTE}:${R2_BUCKET}/backups/${REMOTE_NAME}"
else
    _psql "UPDATE plataforma.backup_execucao SET
        finalizado_em=now(), status='falha',
        erro='exit=${RC}'
    WHERE id=${ID};"
    echo "[backup_r2] FALHOU exit=${RC} id=${ID}" >&2
    exit 1
fi

echo "[backup_r2] concluido=$(date --iso-8601=seconds)"
