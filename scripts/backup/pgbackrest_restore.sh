#!/usr/bin/env bash
# Sprint 40 / HIS-40.1 — Restore pgBackRest (full, diff e PITR)
#
# Executa restore de cluster PostgreSQL a partir de repo1 (local) ou repo2 (S3).
# Registra evento em plataforma.backup_execucao APÓS o restore, via cluster restaurado.
#
# MODOS:
#   --type=latest  : restaura até o WAL mais recente disponível (default)
#   --type=pitr    : restaura até timestamp exato (requer --target)
#   --type=full    : restaura apenas do último backup full (sem WAL replay)
#
# USO:
#   sudo -u postgres bash scripts/backup/pgbackrest_restore.sh --type=latest
#   sudo -u postgres bash scripts/backup/pgbackrest_restore.sh --type=pitr \
#       --target='2026-05-06 12:00:00-03'
#   sudo -u postgres bash scripts/backup/pgbackrest_restore.sh \
#       --type=latest --repo=2
#
# VARIÁVEIS:
#   STANZA           — stanza pgBackRest (default: healthintel)
#   PGDATA           — diretório de dados do cluster restaurado (default: /var/lib/postgresql/16/main)
#   PGHOST           — socket/host para conexão pós-restore (default: /var/run/postgresql)
#   PGDATABASE       — banco de dados (default: healthintel)
#   PGUSER           — usuário PostgreSQL (default: postgres)
#   RESTORE_LOG_DIR  — diretório de log (default: /var/log/healthintel/restore)
#
# HARDGATES:
#   1. Nunca executar sobre cluster de produção ativo.
#   2. Requer que o PostgreSQL esteja parado antes do restore.
#   3. PGDATA precisa ser um diretório vazio ou o comando falha explicitamente.
#   4. Registrar resultado em plataforma.backup_execucao via cluster restaurado.
#
# SAÍDA:
#   Exit 0 — restore concluído; plataforma.backup_execucao atualizado.
#   Exit 1 — restore ou validação falhou.
#   Exit 2 — pré-condição violada (PostgreSQL ativo, PGDATA ocupado).
#   Exit 4 — argumento inválido.

set -euo pipefail

STANZA="${STANZA:-healthintel}"
PGDATA="${PGDATA:-/var/lib/postgresql/16/main}"
PGHOST="${PGHOST:-/var/run/postgresql}"
PGPORT="${PGPORT:-5432}"
PGDATABASE="${PGDATABASE:-healthintel}"
PGUSER="${PGUSER:-postgres}"
RESTORE_LOG_DIR="${RESTORE_LOG_DIR:-/var/log/healthintel/restore}"
REPO="${REPO:-1}"

TIPO_RESTORE="latest"
TARGET_PITR=""
CONFIRM=""

for arg in "$@"; do
  case "${arg}" in
    --type=latest|--type=full) TIPO_RESTORE="${arg#--type=}" ;;
    --type=pitr)                TIPO_RESTORE="pitr" ;;
    --target=*)                 TARGET_PITR="${arg#--target=}" ;;
    --repo=*)                   REPO="${arg#--repo=}" ;;
    --confirm)                  CONFIRM="sim" ;;
    *) printf 'ERRO: argumento desconhecido: %s\n' "${arg}" >&2; exit 4 ;;
  esac
done

if [[ "${TIPO_RESTORE}" == "pitr" && -z "${TARGET_PITR}" ]]; then
  printf 'ERRO: --type=pitr requer --target="YYYY-MM-DD HH:MM:SS±HH"\n' >&2
  exit 4
fi

mkdir -p "${RESTORE_LOG_DIR}"
log_file="${RESTORE_LOG_DIR}/restore_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "${log_file}") 2>&1

printf '[pgbackrest_restore] inicio=%s tipo=%s repo=%s target="%s"\n' \
  "$(date --iso-8601=seconds)" "${TIPO_RESTORE}" "${REPO}" "${TARGET_PITR}"

# --- Hardgate 1: confirmar execucao explicita ---
if [[ "${CONFIRM}" != "sim" ]]; then
  printf '\nATENCAO: este script restaura um cluster PostgreSQL.\n'
  printf 'Execute com --confirm para prosseguir.\n'
  printf 'Exemplo: bash %s --type=latest --repo=%s --confirm\n' "$0" "${REPO}"
  exit 2
fi

# --- Hardgate 2: PostgreSQL deve estar parado ---
if pg_isready -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" >/dev/null 2>&1; then
  printf 'ERRO: PostgreSQL esta ativo em %s:%s. Parar antes de restaurar.\n' \
    "${PGHOST}" "${PGPORT}" >&2
  printf 'Dica: sudo systemctl stop postgresql\n' >&2
  exit 2
fi
printf '[pgbackrest_restore] OK: PostgreSQL parado\n'

# --- Hardgate 3: verificar integridade do backup antes do restore ---
printf '[pgbackrest_restore] verificando stanza...\n'
if ! pgbackrest --stanza="${STANZA}" check; then
  printf 'ERRO: pgbackrest check falhou — nao restaurar de repositorio invalido.\n' >&2
  exit 1
fi
printf '[pgbackrest_restore] OK: pgbackrest check passou\n'

# --- Hardgate 4: PGDATA deve estar vazio ou inexistente ---
if [[ -d "${PGDATA}" ]] && [[ -n "$(ls -A "${PGDATA}" 2>/dev/null)" ]]; then
  printf 'ERRO: PGDATA=%s nao esta vazio. Apagar manualmente antes de restaurar.\n' \
    "${PGDATA}" >&2
  printf 'Dica: sudo rm -rf %s && sudo mkdir -p %s && sudo chown postgres:postgres %s\n' \
    "${PGDATA}" "${PGDATA}" "${PGDATA}" >&2
  exit 2
fi

# --- Construir comando de restore ---
RESTORE_ARGS=(
  --stanza="${STANZA}"
  "--repo=${REPO}"
  restore
)

case "${TIPO_RESTORE}" in
  latest)
    RESTORE_ARGS+=(--type=default)
    ;;
  pitr)
    RESTORE_ARGS+=(--type=time "--target=${TARGET_PITR}" --target-action=promote)
    ;;
  full)
    RESTORE_ARGS+=(--type=immediate --target-action=promote)
    ;;
esac

printf '[pgbackrest_restore] executando: pgbackrest %s\n' "${RESTORE_ARGS[*]}"
RESTORE_RC=0
pgbackrest "${RESTORE_ARGS[@]}" || RESTORE_RC=$?

if (( RESTORE_RC != 0 )); then
  printf '[pgbackrest_restore] ERRO: restore falhou exit=%s\n' "${RESTORE_RC}" >&2
  exit 1
fi
printf '[pgbackrest_restore] OK: restore concluido. Iniciando PostgreSQL para validacao...\n'

# --- Iniciar PostgreSQL restaurado para validacao ---
if command -v pg_ctlcluster >/dev/null 2>&1; then
  pg_ctlcluster 16 main start || true
elif command -v pg_ctl >/dev/null 2>&1; then
  pg_ctl -D "${PGDATA}" start -l "${RESTORE_LOG_DIR}/postgres_start.log" || true
else
  printf 'AVISO: nao foi possivel iniciar PostgreSQL automaticamente. Inicie manualmente.\n' >&2
fi

# Aguardar disponibilidade (ate 120s)
printf '[pgbackrest_restore] aguardando PostgreSQL ficar pronto...\n'
tentativa=0
while ! pg_isready -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" >/dev/null 2>&1; do
  tentativa=$((tentativa + 1))
  if (( tentativa > 24 )); then
    printf '[pgbackrest_restore] ERRO: PostgreSQL nao ficou pronto em 120s\n' >&2
    exit 1
  fi
  sleep 5
done
printf '[pgbackrest_restore] OK: PostgreSQL pronto apos %ss\n' "$((tentativa * 5))"

# --- Registrar resultado em plataforma.backup_execucao ---
RESUMO="restore tipo=${TIPO_RESTORE} repo=${REPO} target='${TARGET_PITR}' log=${log_file}"
psql -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d "${PGDATABASE}" \
  -v ON_ERROR_STOP=1 -c "
  INSERT INTO plataforma.backup_execucao
    (stanza, tipo, repositorio, iniciado_em, finalizado_em, status, log_resumo, executado_por)
  VALUES (
    '${STANZA}',
    'restore_test',
    'repo${REPO}_$([ "${REPO}" = "1" ] && echo "local" || echo "s3")',
    now() - interval '1 second',
    now(),
    'sucesso',
    '$( printf '%s' "${RESUMO}" | sed "s/'/''/g" )',
    current_user
  );
  SELECT 'restore_test registrado em plataforma.backup_execucao' AS status;
" || printf 'AVISO: falha ao registrar em plataforma.backup_execucao\n' >&2

# --- Smoke basico sobre cluster restaurado ---
printf '\n[pgbackrest_restore] smoke basico no cluster restaurado...\n'
psql -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d "${PGDATABASE}" \
  -v ON_ERROR_STOP=1 -c "
  SELECT
    table_schema,
    COUNT(*) AS tabelas
  FROM information_schema.tables
  WHERE table_schema IN ('api_ans', 'bruto_ans', 'plataforma')
  GROUP BY table_schema
  ORDER BY table_schema;
" || {
  printf '[pgbackrest_restore] ERRO: smoke SQL falhou no cluster restaurado\n' >&2
  exit 1
}

printf '\n[pgbackrest_restore] concluido. RTO observe: verifique timestamps no log.\n'
printf '[pgbackrest_restore] Log completo: %s\n' "${log_file}"
printf '\nPROXIMOS PASSOS:\n'
printf '  1. Validar smoke da API: SMOKE_BASE_URL=http://localhost:8080 python scripts/smoke_core.py\n'
printf '  2. Verificar contagem de tabelas Core: make smoke-core\n'
printf '  3. Registrar RTO em docs/operacao/baseline_capacidade.md\n'
printf '  4. Nao promover este cluster para producao sem validacao explicita.\n'
