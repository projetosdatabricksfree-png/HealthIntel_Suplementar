#!/usr/bin/env bash
# Sprint 39 / HIS-39.6 — Monitor de saúde do backup pgBackRest
#
# VERIFICAÇÕES (executadas a cada 5 minutos via pgbackrest-monitor.timer):
#
#   CHECK 1 — WAL archive:
#     Consulta pg_stat_archiver.last_archived_time.
#     Alerta se o último WAL arquivado foi há mais de WAL_MAX_AGE_S (padrão: 3600s / 1h).
#     Registra uma linha tipo='wal' em plataforma.backup_execucao por execução —
#     esse registro é a evidência auditável de saúde do archive_command.
#     O archive_command em si é chamado pelo PostgreSQL (postgresql.fase7.conf),
#     não por este script; este script apenas observa e registra o resultado.
#
#   CHECK 2 — Tamanho do diretório pg_wal:
#     Alerta se o diretório PG_WAL_DIR exceder PG_WAL_LIMIT_GB (padrão: 5 GB).
#     Hard gate da sprint: alerta deve disparar em até 5 minutos após exceder o limite.
#
#   CHECK 3 — Frescor do backup full:
#     Consulta MAX(iniciado_em) em backup_execucao onde tipo='full' e status='sucesso'.
#     Alerta se o último full foi há mais de FULL_MAX_AGE_S (padrão: 93600s / 26h).
#
#   CHECK 4 — Frescor do backup diff:
#     Consulta MAX(iniciado_em) em backup_execucao onde tipo='diff' e status='sucesso'.
#     Alerta se o último diff foi há mais de DIFF_MAX_AGE_S (padrão: 25200s / 7h).
#
# INTEGRAÇÃO:
#   Padrão: registra falhas em plataforma.backup_alerta (035_fase7_backup_alerta.sql).
#   Prometheus: se PROMETHEUS_PUSHGATEWAY_URL estiver definido, envia métricas via curl.
#     Métricas: pgbackrest_wal_age_seconds, pgbackrest_full_age_seconds,
#               pgbackrest_diff_age_seconds, pgbackrest_wal_archiver_healthy.
#
# PRÉ-REQUISITOS NA VPS:
#   1. plataforma.backup_execucao criada (034_fase7_backup_execucao.sql aplicado).
#   2. plataforma.backup_alerta criada (035_fase7_backup_alerta.sql aplicado).
#   3. Usuário postgres com acesso ao banco e ao diretório PG_WAL_DIR.
#   4. curl disponível se PROMETHEUS_PUSHGATEWAY_URL estiver configurado.
#
# USO:
#   sudo -u postgres bash scripts/backup/pgbackrest_monitor.sh
#   # Personalizar thresholds:
#   PG_WAL_LIMIT_GB=3 PG_WAL_DIR=/var/lib/postgresql/16/main/pg_wal \
#     sudo -u postgres bash scripts/backup/pgbackrest_monitor.sh
#
# CHAMADO POR:
#   infra/systemd/pgbackrest-monitor.timer (a cada 5 minutos)
#
# SAÍDA:
#   Exit 0 — todas as verificações passaram
#   Exit 1 — uma ou mais verificações falharam; alertas em plataforma.backup_alerta
#   Exit 3 — falha de conexão com o banco de dados; nenhum alerta registrado

set -euo pipefail

STANZA="${STANZA:-healthintel}"
PGHOST="${PGHOST:-/var/run/postgresql}"
PGPORT="${PGPORT:-5432}"
PGDATABASE="${PGDATABASE:-healthintel}"
PGUSER="${PGUSER:-postgres}"
PG_WAL_DIR="${PG_WAL_DIR:-/var/lib/postgresql/16/main/pg_wal}"
PG_WAL_LIMIT_GB="${PG_WAL_LIMIT_GB:-5}"
PROMETHEUS_PUSHGATEWAY_URL="${PROMETHEUS_PUSHGATEWAY_URL:-}"

# Thresholds em segundos
WAL_MAX_AGE_S=3600    # 1h  — alinhado ao archive_timeout=3600 de postgresql.fase7.conf
FULL_MAX_AGE_S=93600  # 26h — full diário às 03:00 + 2h de folga operacional
DIFF_MAX_AGE_S=25200  # 7h  — diffs a cada 6h + 1h de folga operacional

# ─── Helpers SQL ──────────────────────────────────────────────────────────────
_psql() {
    psql -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d "${PGDATABASE}" \
         -v ON_ERROR_STOP=1 -t -A -c "$1"
}

_escape() {
    printf '%s' "${1}" | sed "s/'/''/g"
}

_insert_alerta() {
    local tipo="$1" severidade="$2" mensagem="$3"
    _psql "INSERT INTO plataforma.backup_alerta (check_tipo, severidade, mensagem)
           VALUES ('${tipo}', '${severidade}', '$(_escape "${mensagem}")');" > /dev/null
}

_insert_wal_execucao() {
    local status="$1" log_resumo="$2" erro="$3"
    _psql "INSERT INTO plataforma.backup_execucao
               (stanza, tipo, repositorio, iniciado_em, finalizado_em, status, log_resumo, erro)
           VALUES ('${STANZA}', 'wal', 'repo1_local', now(), now(), '${status}',
                   '$(_escape "${log_resumo}")',
                   NULLIF('$(_escape "${erro}")', ''));" > /dev/null
}

# ─── Conectividade com o banco ────────────────────────────────────────────────
if ! _psql "SELECT 1;" > /dev/null 2>&1; then
    echo "[pgbackrest_monitor] ERRO: sem conexão com ${PGDATABASE}@${PGHOST}:${PGPORT}" >&2
    exit 3
fi

echo "[pgbackrest_monitor] início=$(date --iso-8601=seconds)"
FALHAS=0

# ─── CHECK 1: WAL archive via pg_stat_archiver ────────────────────────────────
WAL_INFO="" RC_WAL=0
WAL_INFO=$(_psql "SELECT
    COALESCE(EXTRACT(EPOCH FROM (now() - last_archived_time))::int, -1)::text
    || ' ' || COALESCE(last_failed_wal, '')
    || ' ' || COALESCE(EXTRACT(EPOCH FROM (now() - last_failed_time))::int, -1)::text
    FROM pg_stat_archiver;") || RC_WAL=$?

WAL_AGE_S="-1" WAL_FAIL_WAL="" WAL_FAIL_AGE_S="-1"
if [[ ${RC_WAL} -eq 0 ]] && [[ -n "${WAL_INFO}" ]]; then
    read -r WAL_AGE_S WAL_FAIL_WAL WAL_FAIL_AGE_S <<< "${WAL_INFO}"
fi

if ! [[ "${WAL_AGE_S}" =~ ^[0-9]+$ ]]; then
    MSG="pg_stat_archiver: nenhum WAL arquivado ainda (stanza=${STANZA})"
    echo "[pgbackrest_monitor] ALERTA wal_atraso: ${MSG}" >&2
    _insert_alerta "wal_atraso" "aviso" "${MSG}"
    _insert_wal_execucao "falha" "pg_stat_archiver: last_archived_time=NULL" "${MSG}"
    FALHAS=$((FALHAS + 1))
elif [[ ${WAL_AGE_S} -gt ${WAL_MAX_AGE_S} ]]; then
    MSG="Último WAL arquivado há ${WAL_AGE_S}s (limite: ${WAL_MAX_AGE_S}s / 1h)"
    echo "[pgbackrest_monitor] ALERTA wal_atraso: ${MSG}" >&2
    _insert_alerta "wal_atraso" "critico" "${MSG}"
    _insert_wal_execucao "falha" "pg_stat_archiver: last_archived_time age=${WAL_AGE_S}s" "${MSG}"
    FALHAS=$((FALHAS + 1))
else
    LOG="pg_stat_archiver: last_archived_time age=${WAL_AGE_S}s — dentro do limite de ${WAL_MAX_AGE_S}s"
    echo "[pgbackrest_monitor] WAL OK (${WAL_AGE_S}s atrás)"
    _insert_wal_execucao "sucesso" "${LOG}" ""
fi

# ─── CHECK 2: Tamanho do diretório pg_wal ─────────────────────────────────────
WAL_LIMIT_BYTES=$(( PG_WAL_LIMIT_GB * 1024 * 1024 * 1024 ))
if [[ -d "${PG_WAL_DIR}" ]]; then
    WAL_SIZE_BYTES=0 RC_DU=0
    WAL_SIZE_BYTES=$(du -sb "${PG_WAL_DIR}" 2>/dev/null | awk '{print $1}') || RC_DU=$?
    if [[ ${RC_DU} -ne 0 ]]; then
        echo "[pgbackrest_monitor] AVISO: du falhou em '${PG_WAL_DIR}'; pulando check de tamanho" >&2
    else
        WAL_SIZE_MB=$(( WAL_SIZE_BYTES / 1048576 ))
        WAL_LIMIT_MB=$(( PG_WAL_LIMIT_GB * 1024 ))
        if [[ ${WAL_SIZE_BYTES} -gt ${WAL_LIMIT_BYTES} ]]; then
            MSG="pg_wal ocupa ${WAL_SIZE_MB} MB (limite: ${WAL_LIMIT_MB} MB / ${PG_WAL_LIMIT_GB} GB) em ${PG_WAL_DIR}"
            echo "[pgbackrest_monitor] ALERTA pg_wal_tamanho: ${MSG}" >&2
            _insert_alerta "pg_wal_tamanho" "critico" "${MSG}"
            FALHAS=$((FALHAS + 1))
        else
            echo "[pgbackrest_monitor] pg_wal OK (${WAL_SIZE_MB} MB < ${WAL_LIMIT_MB} MB)"
        fi
    fi
else
    echo "[pgbackrest_monitor] AVISO: PG_WAL_DIR='${PG_WAL_DIR}' não encontrado; pulando check de tamanho" >&2
fi

# ─── CHECK 3: Frescor do backup full ─────────────────────────────────────────
FULL_AGE_S="" RC_FULL=0
FULL_AGE_S=$(_psql "SELECT EXTRACT(EPOCH FROM (now() - MAX(iniciado_em)))::int
                    FROM plataforma.backup_execucao
                    WHERE tipo = 'full' AND status = 'sucesso';") || RC_FULL=$?

if [[ ${RC_FULL} -ne 0 ]] || ! [[ "${FULL_AGE_S}" =~ ^[0-9]+$ ]]; then
    MSG="Nenhum backup full com sucesso registrado em backup_execucao"
    echo "[pgbackrest_monitor] ALERTA full_atraso: ${MSG}" >&2
    _insert_alerta "full_atraso" "critico" "${MSG}"
    FALHAS=$((FALHAS + 1))
elif [[ ${FULL_AGE_S} -gt ${FULL_MAX_AGE_S} ]]; then
    MSG="Último full há ${FULL_AGE_S}s (limite: ${FULL_MAX_AGE_S}s / 26h)"
    echo "[pgbackrest_monitor] ALERTA full_atraso: ${MSG}" >&2
    _insert_alerta "full_atraso" "critico" "${MSG}"
    FALHAS=$((FALHAS + 1))
else
    echo "[pgbackrest_monitor] full OK (${FULL_AGE_S}s atrás)"
fi

# ─── CHECK 4: Frescor do backup diff ─────────────────────────────────────────
DIFF_AGE_S="" RC_DIFF=0
DIFF_AGE_S=$(_psql "SELECT EXTRACT(EPOCH FROM (now() - MAX(iniciado_em)))::int
                    FROM plataforma.backup_execucao
                    WHERE tipo = 'diff' AND status = 'sucesso';") || RC_DIFF=$?

if [[ ${RC_DIFF} -ne 0 ]] || ! [[ "${DIFF_AGE_S}" =~ ^[0-9]+$ ]]; then
    MSG="Nenhum backup diff com sucesso registrado em backup_execucao"
    echo "[pgbackrest_monitor] ALERTA diff_atraso: ${MSG}" >&2
    _insert_alerta "diff_atraso" "aviso" "${MSG}"
    FALHAS=$((FALHAS + 1))
elif [[ ${DIFF_AGE_S} -gt ${DIFF_MAX_AGE_S} ]]; then
    MSG="Último diff há ${DIFF_AGE_S}s (limite: ${DIFF_MAX_AGE_S}s / 7h)"
    echo "[pgbackrest_monitor] ALERTA diff_atraso: ${MSG}" >&2
    _insert_alerta "diff_atraso" "aviso" "${MSG}"
    FALHAS=$((FALHAS + 1))
else
    echo "[pgbackrest_monitor] diff OK (${DIFF_AGE_S}s atrás)"
fi

# ─── Prometheus Pushgateway (opcional) ───────────────────────────────────────
if [[ -n "${PROMETHEUS_PUSHGATEWAY_URL}" ]]; then
    WAL_HEALTHY=$(( FALHAS == 0 ? 1 : 0 ))
    PAYLOAD="# HELP pgbackrest_wal_archiver_healthy 1 se WAL archive OK nos últimos ${WAL_MAX_AGE_S}s, 0 se atrasado
# TYPE pgbackrest_wal_archiver_healthy gauge
pgbackrest_wal_archiver_healthy{stanza=\"${STANZA}\"} ${WAL_HEALTHY}
# HELP pgbackrest_wal_age_seconds Segundos desde o último WAL arquivado (pg_stat_archiver)
# TYPE pgbackrest_wal_age_seconds gauge
pgbackrest_wal_age_seconds{stanza=\"${STANZA}\"} ${WAL_AGE_S:-0}
# HELP pgbackrest_full_age_seconds Segundos desde o último full backup com sucesso
# TYPE pgbackrest_full_age_seconds gauge
pgbackrest_full_age_seconds{stanza=\"${STANZA}\"} ${FULL_AGE_S:-0}
# HELP pgbackrest_diff_age_seconds Segundos desde o último diff backup com sucesso
# TYPE pgbackrest_diff_age_seconds gauge
pgbackrest_diff_age_seconds{stanza=\"${STANZA}\"} ${DIFF_AGE_S:-0}
"
    RC_PUSH=0
    printf '%s' "${PAYLOAD}" | curl -s --max-time 10 --data-binary @- \
        "${PROMETHEUS_PUSHGATEWAY_URL}/metrics/job/pgbackrest_monitor/instance/${STANZA}" \
        > /dev/null || RC_PUSH=$?
    if [[ ${RC_PUSH} -eq 0 ]]; then
        echo "[pgbackrest_monitor] métricas enviadas ao Prometheus Pushgateway"
    else
        echo "[pgbackrest_monitor] AVISO: push Prometheus falhou (exit=${RC_PUSH})" >&2
    fi
fi

# ─── Resultado ────────────────────────────────────────────────────────────────
echo "[pgbackrest_monitor] concluído: ${FALHAS} falha(s) em $(date --iso-8601=seconds)"
[[ ${FALHAS} -eq 0 ]] || exit 1
