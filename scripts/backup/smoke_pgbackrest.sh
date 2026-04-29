#!/usr/bin/env bash
# Sprint 39 / HIS-39.8 — Smoke operacional pgBackRest
#
# Valida backup PostgreSQL com pgBackRest sem simular sucesso:
#   - pgbackrest check
#   - repo2 S3-compatible presente e com full recente
#   - auditoria em plataforma.backup_execucao por tipo
#   - alertas críticos recentes em plataforma.backup_alerta
#
# Uso esperado na VPS:
#   STANZA=healthintel PGDATABASE=healthintel PGUSER=postgres make smoke-pgbackrest

set -euo pipefail

STANZA="${STANZA:-healthintel}"
PGHOST="${PGHOST:-/var/run/postgresql}"
PGPORT="${PGPORT:-5432}"
PGDATABASE="${PGDATABASE:-healthintel}"
PGUSER="${PGUSER:-postgres}"
WAL_MAX_AGE_S="${WAL_MAX_AGE_S:-3600}"
FULL_WINDOW="${FULL_WINDOW:-26 hours}"
DIFF_WINDOW="${DIFF_WINDOW:-24 hours}"
REPO2_FULL_WINDOW_DAYS="${REPO2_FULL_WINDOW_DAYS:-35}"
ALERT_WINDOW="${ALERT_WINDOW:-2 hours}"

FALHAS=0

_erro() {
    echo "[smoke_pgbackrest] ERRO: $*" >&2
    FALHAS=$((FALHAS + 1))
}

_require_cmd() {
    local cmd="$1"
    if ! command -v "${cmd}" > /dev/null 2>&1; then
        _erro "comando obrigatório indisponível: ${cmd}"
    fi
}

_psql() {
    psql -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d "${PGDATABASE}" \
         -v ON_ERROR_STOP=1 -t -A -c "$1"
}

_escape() {
    printf '%s' "${1}" | sed "s/'/''/g"
}

_insert_check_execucao() {
    local resumo="$1"
    _psql "INSERT INTO plataforma.backup_execucao
               (stanza, tipo, repositorio, iniciado_em, status, log_resumo, executado_por)
           VALUES ('${STANZA}', 'check', 'repo1_local', now(), 'em_execucao',
                   '$(_escape "${resumo}")', current_user)
           RETURNING id;"
}

_update_check_execucao() {
    local id="$1" status="$2" resumo="$3" erro="$4"
    _psql "UPDATE plataforma.backup_execucao SET
               finalizado_em = now(),
               status        = '${status}',
               log_resumo    = '$(_escape "${resumo}")',
               erro          = NULLIF('$(_escape "${erro}")', '')
           WHERE id = ${id};"
}

_assert_numeric_ge() {
    local valor="$1" esperado="$2" nome="$3"
    if ! [[ "${valor}" =~ ^[0-9]+$ ]]; then
        _erro "${nome}: valor não numérico ou ausente (${valor:-vazio})"
    elif (( valor < esperado )); then
        _erro "${nome}: ${valor} < ${esperado}"
    else
        echo "[smoke_pgbackrest] OK: ${nome}=${valor}"
    fi
}

_assert_last_status() {
    local tipo="$1"
    local linha status iniciado erro
    linha="$(_psql "SELECT status || '|' || iniciado_em::text || '|' || COALESCE(erro, '')
                   FROM plataforma.backup_execucao
                   WHERE tipo = '${tipo}'
                   ORDER BY iniciado_em DESC
                   LIMIT 1;")" || {
        _erro "falha ao consultar última execução tipo=${tipo}"
        return
    }

    if [[ -z "${linha}" ]]; then
        _erro "sem evidência em plataforma.backup_execucao para tipo=${tipo}"
        return
    fi

    IFS='|' read -r status iniciado erro <<< "${linha}"
    if [[ "${status}" != "sucesso" ]]; then
        _erro "última execução tipo=${tipo} status=${status} iniciado_em=${iniciado} erro=${erro}"
    else
        echo "[smoke_pgbackrest] OK: última execução tipo=${tipo} status=sucesso iniciado_em=${iniciado}"
    fi
}

_validate_repo2_info() {
    local info_json="$1"
    INFO_JSON_PAYLOAD="${info_json}" python3 - "${REPO2_FULL_WINDOW_DAYS}" <<'PY'
import datetime as dt
import json
import os
import sys

window_days = int(sys.argv[1])
payload = json.loads(os.environ.get("INFO_JSON_PAYLOAD", ""))
now = dt.datetime.now(dt.timezone.utc)

repo2_ok = False
full_recent = False
diagnostics = []

for stanza in payload if isinstance(payload, list) else [payload]:
    for repo in stanza.get("repo", []):
        key = repo.get("key") or repo.get("repo-key")
        status = repo.get("status") or {}
        if str(key) == "2" and int(status.get("code", 1)) == 0:
            repo2_ok = True

    for backup in stanza.get("backup", []):
        if backup.get("type") != "full":
            continue

        repo_key = (
            backup.get("repo-key")
            or backup.get("repository-key")
            or (backup.get("database") or {}).get("repo-key")
            or (backup.get("repository") or {}).get("key")
        )
        label = backup.get("label", "<sem label>")
        if str(repo_key) != "2":
            diagnostics.append(f"full ignorado label={label} repo_key={repo_key}")
            continue

        ts = backup.get("timestamp") or {}
        stop = ts.get("stop") or ts.get("start")
        if stop is None:
            diagnostics.append(f"full repo2 sem timestamp label={label}")
            continue
        try:
            stop_dt = dt.datetime.fromtimestamp(int(stop), tz=dt.timezone.utc)
        except (TypeError, ValueError):
            diagnostics.append(f"full repo2 timestamp inválido label={label} stop={stop}")
            continue
        age_days = (now - stop_dt).total_seconds() / 86400
        if age_days <= window_days:
            full_recent = True

if not repo2_ok:
    print("repo2 ausente ou sem status ok em pgbackrest info --output=json", file=sys.stderr)
if not full_recent:
    print(
        f"repo2 sem backup full dentro de {window_days} dias; detalhes: "
        + "; ".join(diagnostics[-5:]),
        file=sys.stderr,
    )

sys.exit(0 if repo2_ok and full_recent else 1)
PY
}

echo "[smoke_pgbackrest] início=$(date --iso-8601=seconds) stanza=${STANZA}"

_require_cmd pgbackrest
_require_cmd psql
_require_cmd python3
if (( FALHAS > 0 )); then
    exit 1
fi

if ! _psql "SELECT 1;" > /dev/null 2>&1; then
    echo "[smoke_pgbackrest] ERRO: sem conexão com ${PGDATABASE}@${PGHOST}:${PGPORT}" >&2
    exit 3
fi

ID_CHECK="$(_insert_check_execucao "smoke-pgbackrest: pgbackrest check")"
if ! [[ "${ID_CHECK}" =~ ^[0-9]+$ ]]; then
    echo "[smoke_pgbackrest] ERRO: id inválido para execução check: ${ID_CHECK}" >&2
    exit 3
fi

CHECK_OUTPUT="" CHECK_RC=0
CHECK_OUTPUT="$(pgbackrest --stanza="${STANZA}" check 2>&1)" || CHECK_RC=$?
if (( CHECK_RC == 0 )); then
    _update_check_execucao "${ID_CHECK}" "sucesso" "${CHECK_OUTPUT}" ""
    echo "[smoke_pgbackrest] OK: pgbackrest check"
else
    _update_check_execucao "${ID_CHECK}" "falha" "" "${CHECK_OUTPUT}" || true
    echo "[smoke_pgbackrest] ERRO: pgbackrest check falhou exit=${CHECK_RC}" >&2
    printf '%s\n' "${CHECK_OUTPUT}" >&2
    exit 1
fi

INFO_JSON="" INFO_RC=0
INFO_JSON="$(pgbackrest --stanza="${STANZA}" info --output=json 2>&1)" || INFO_RC=$?
if (( INFO_RC != 0 )); then
    _erro "pgbackrest info --output=json falhou exit=${INFO_RC}: ${INFO_JSON}"
elif _validate_repo2_info "${INFO_JSON}"; then
    echo "[smoke_pgbackrest] OK: repo2 com full válido dentro de ${REPO2_FULL_WINDOW_DAYS} dias"
else
    _erro "repo2 não atende ao critério de full válido"
fi

WAL_AGE="$(_psql "SELECT COALESCE(EXTRACT(EPOCH FROM (now() - MAX(iniciado_em)))::int, -1)
                  FROM plataforma.backup_execucao
                  WHERE tipo = 'wal' AND status = 'sucesso';")" || {
    _erro "falha ao consultar frescor WAL em backup_execucao"
    WAL_AGE="-1"
}
if ! [[ "${WAL_AGE}" =~ ^[0-9]+$ ]]; then
    _erro "WAL sem execução recente com sucesso"
elif (( WAL_AGE > WAL_MAX_AGE_S )); then
    _erro "WAL atrasado: ${WAL_AGE}s > ${WAL_MAX_AGE_S}s"
else
    echo "[smoke_pgbackrest] OK: WAL age=${WAL_AGE}s"
fi

FULL_COUNT="$(_psql "SELECT COUNT(*)
                    FROM plataforma.backup_execucao
                    WHERE tipo = 'full'
                      AND status = 'sucesso'
                      AND iniciado_em > now() - interval '${FULL_WINDOW}';")" || {
    _erro "falha ao consultar backups full recentes"
    FULL_COUNT=""
}
_assert_numeric_ge "${FULL_COUNT}" 1 "full_sucesso_${FULL_WINDOW// /_}"

DIFF_COUNT="$(_psql "SELECT COUNT(*)
                    FROM plataforma.backup_execucao
                    WHERE tipo = 'diff'
                      AND status = 'sucesso'
                      AND iniciado_em > now() - interval '${DIFF_WINDOW}';")" || {
    _erro "falha ao consultar backups diff recentes"
    DIFF_COUNT=""
}
_assert_numeric_ge "${DIFF_COUNT}" 4 "diff_sucesso_${DIFF_WINDOW// /_}"

for tipo in full diff wal check; do
    _assert_last_status "${tipo}"
done

ALERTAS_CRITICOS="$(_psql "SELECT COUNT(*)
                          FROM plataforma.backup_alerta
                          WHERE severidade = 'critico'
                            AND verificado_em > now() - interval '${ALERT_WINDOW}';")" || {
    _erro "falha ao consultar plataforma.backup_alerta"
    ALERTAS_CRITICOS=""
}
if ! [[ "${ALERTAS_CRITICOS}" =~ ^[0-9]+$ ]]; then
    _erro "alertas críticos: valor não numérico"
elif (( ALERTAS_CRITICOS > 0 )); then
    _erro "existem ${ALERTAS_CRITICOS} alerta(s) crítico(s) nas últimas ${ALERT_WINDOW}"
else
    echo "[smoke_pgbackrest] OK: sem alertas críticos nas últimas ${ALERT_WINDOW}"
fi

echo "[smoke_pgbackrest] concluído: ${FALHAS} falha(s) em $(date --iso-8601=seconds)"
[[ ${FALHAS} -eq 0 ]] || exit 1
