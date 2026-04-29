#!/usr/bin/env bash
# Sprint 39 / HIS-39.5 — Wrapper de execução de backup pgBackRest
#
# COMANDOS COBERTOS:
#
#   backup --type=full:
#     pgbackrest --stanza=healthintel backup --type=full
#     Captura snapshot completo do cluster PostgreSQL em repo1 (local) e repo2 (S3).
#     Deve ser executado via pgbackrest-full.timer (03:00 diário).
#     Duração: variável conforme tamanho do banco; pode levar até 4h.
#
#   backup --type=diff:
#     pgbackrest --stanza=healthintel backup --type=diff
#     Captura apenas os blocos modificados desde o último full. Mais rápido e menor.
#     Deve ser executado via pgbackrest-diff.timer (00:00, 06:00, 12:00, 18:00).
#
# NOTA SOBRE WAL E archive-push:
#   Este script NÃO executa pgbackrest archive-push.
#   O archive-push é chamado pelo PostgreSQL diretamente via archive_command:
#     archive_command = 'pgbackrest --stanza=healthintel archive-push %p'
#   (configurado em infra/postgres/conf/postgresql.fase7.conf)
#   O registro de tipo='wal' em plataforma.backup_execucao é feito pelo
#   script de monitoramento (HIS-39.6), não por este wrapper.
#
# PRÉ-REQUISITOS NA VPS:
#   1. pgBackRest instalado e stanza inicializada (pgbackrest_init.sh executado).
#   2. python3 disponível (extração de bytes de pgbackrest info --output=json).
#   3. Usuário postgres com acesso à stanza e ao banco healthintel.
#   4. plataforma.backup_execucao existente (034_fase7_backup_execucao.sql aplicado).
#
# USO:
#   sudo -u postgres bash scripts/backup/pgbackrest_run.sh --type=full
#   sudo -u postgres bash scripts/backup/pgbackrest_run.sh --type=diff
#   # Com banco em socket/porta alternativa:
#   PGHOST=/var/run/postgresql PGDATABASE=healthintel \
#     sudo -u postgres bash scripts/backup/pgbackrest_run.sh --type=diff
#
# CHAMADO POR:
#   infra/systemd/pgbackrest-full.timer  → --type=full
#   infra/systemd/pgbackrest-diff.timer  → --type=diff
#
# ROLLBACK:
#   Falha de backup: verificar journalctl -u pgbackrest-full.service; reexecutar.
#   Falha de conectividade DB: verificar PGHOST/PGDATABASE/PGUSER; reexecutar.
#   Desativar schedule: systemctl disable --now pgbackrest-full.timer pgbackrest-diff.timer
#   plataforma.backup_execucao preserva o histórico de todas as tentativas.
#
# SAÍDA:
#   Exit 0 — backup concluído com sucesso; backup_execucao atualizado.
#   Exit 1 — backup falhou; backup_execucao atualizado com status='falha' + erro.
#   Exit 3 — falha de conexão com o banco de dados; nenhum registro criado.
#   Exit 4 — argumento --type inválido; nenhum registro criado.

set -euo pipefail

STANZA="${STANZA:-healthintel}"
PGHOST="${PGHOST:-/var/run/postgresql}"
PGPORT="${PGPORT:-5432}"
PGDATABASE="${PGDATABASE:-healthintel}"
PGUSER="${PGUSER:-postgres}"

# ─── Parse argumentos ─────────────────────────────────────────────────────────
TIPO=""
for arg in "$@"; do
    case "${arg}" in
        --type=full|--type=diff) TIPO="${arg#--type=}" ;;
        *) echo "[pgbackrest_run] ERRO: argumento desconhecido '${arg}'" >&2; exit 4 ;;
    esac
done

if [[ -z "${TIPO}" ]]; then
    echo "[pgbackrest_run] ERRO: --type=<full|diff> é obrigatório" >&2
    exit 4
fi

# ─── Helpers SQL ──────────────────────────────────────────────────────────────
_psql() {
    psql -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d "${PGDATABASE}" \
         -v ON_ERROR_STOP=1 -t -A -c "$1"
}

_escape() {
    printf '%s' "${1}" | sed "s/'/''/g"
}

_insert_execucao() {
    local tipo="$1" repositorio="$2" resumo="$3"
    _psql "INSERT INTO plataforma.backup_execucao
               (stanza, tipo, repositorio, iniciado_em, status, log_resumo, executado_por)
           VALUES ('${STANZA}', '${tipo}', '${repositorio}', now(), 'em_execucao',
                   '$(_escape "${resumo}")', current_user)
           RETURNING id;"
}

_update_execucao() {
    local id="$1" status="$2" resumo="$3" erro="$4" bytes_arm="$5" bytes_del="$6"
    _psql "UPDATE plataforma.backup_execucao SET
               finalizado_em      = now(),
               status             = '${status}',
               log_resumo         = '$(_escape "${resumo}")',
               erro               = NULLIF('$(_escape "${erro}")', ''),
               bytes_armazenados  = NULLIF('${bytes_arm}', '')::bigint,
               bytes_delta        = NULLIF('${bytes_del}', '')::bigint
           WHERE id = ${id};"
}

# ─── Conectividade com o banco ────────────────────────────────────────────────
if ! _psql "SELECT 1;" > /dev/null 2>&1; then
    echo "[pgbackrest_run] ERRO: sem conexão com ${PGDATABASE}@${PGHOST}:${PGPORT}" >&2
    exit 3
fi

echo "[pgbackrest_run] tipo=${TIPO}  stanza=${STANZA}  início=$(date --iso-8601=seconds)"

# ─── INSERT: início do backup ─────────────────────────────────────────────────
RESUMO_INICIO="backup --type=${TIPO}: repo1 (local /var/lib/pgbackrest) e repo2 (S3) cobertos"
ID=$(_insert_execucao "${TIPO}" "repo1_local" "${RESUMO_INICIO}")
[[ "${ID}" =~ ^[0-9]+$ ]] || { echo "[pgbackrest_run] ERRO: id inválido '${ID}'" >&2; exit 3; }
echo "[pgbackrest_run] backup_execucao.id=${ID} criado (status=em_execucao)"

# ─── EXECUÇÃO DO BACKUP ───────────────────────────────────────────────────────
OUTPUT_BACKUP="" RC_BACKUP=0
OUTPUT_BACKUP=$(pgbackrest --stanza="${STANZA}" backup --type="${TIPO}" 2>&1) || RC_BACKUP=$?

# ─── EXTRAÇÃO DE BYTES (via pgbackrest info --output=json + python3) ──────────
BYTES_ARM="" BYTES_DEL=""
if [[ ${RC_BACKUP} -eq 0 ]]; then
    INFO_JSON="" RC_INFO=0
    INFO_JSON=$(pgbackrest --stanza="${STANZA}" info --output=json 2>&1) || RC_INFO=$?

    if [[ ${RC_INFO} -eq 0 ]] && command -v python3 > /dev/null 2>&1; then
        read -r BYTES_ARM BYTES_DEL < <(
            printf '%s' "${INFO_JSON}" | python3 -c "
import json, sys
try:
    data = json.loads(sys.stdin.read())
    backups = data[0]['backup']
    if backups:
        repo = backups[-1]['info']['repository']
        print(repo.get('size', ''), repo.get('delta', ''))
    else:
        print('', '')
except Exception as e:
    sys.stderr.write('[pgbackrest_run] AVISO: falha ao extrair bytes: ' + str(e) + '\n')
    print('', '')
"
        ) || true
    else
        [[ ${RC_INFO} -ne 0 ]] && \
            echo "[pgbackrest_run] AVISO: pgbackrest info falhou (exit=${RC_INFO}); bytes_* serão NULL" >&2
        command -v python3 > /dev/null 2>&1 || \
            echo "[pgbackrest_run] AVISO: python3 não encontrado; bytes_* serão NULL" >&2
    fi
fi

# ─── UPDATE: resultado ────────────────────────────────────────────────────────
if [[ ${RC_BACKUP} -eq 0 ]]; then
    _update_execucao "${ID}" "sucesso" "${OUTPUT_BACKUP}" "" "${BYTES_ARM}" "${BYTES_DEL}"
    echo "[pgbackrest_run] backup --type=${TIPO}: sucesso" \
         " bytes_armazenados=${BYTES_ARM:-NULL} bytes_delta=${BYTES_DEL:-NULL}" \
         " (backup_execucao.id=${ID})"
else
    _update_execucao "${ID}" "falha" "" "${OUTPUT_BACKUP}" "" ""
    echo "[pgbackrest_run] backup --type=${TIPO}: FALHOU exit=${RC_BACKUP} (id=${ID})" >&2
    printf '%s\n' "${OUTPUT_BACKUP}" >&2
    exit 1
fi

echo "[pgbackrest_run] concluído $(date --iso-8601=seconds)"
