#!/usr/bin/env bash
# Sprint 39 / HIS-39.4 — Inicialização e verificação do pgBackRest
#
# COMANDOS DOCUMENTADOS:
#
#   stanza-create:
#     pgbackrest --stanza=healthintel stanza-create
#     Cria a estrutura do repositório em repo1 (local: /var/lib/pgbackrest) e
#     repo2 (S3-compatible). Deve ser executado UMA VEZ após instalar o pgBackRest
#     e materializar /etc/pgbackrest/pgbackrest.conf na VPS.
#     Idempotente: re-execução segura quando a stanza já existe.
#     Requer: PostgreSQL rodando; repo1 e repo2 acessíveis.
#
#   check (hardgate):
#     pgbackrest --stanza=healthintel check
#     Valida end-to-end: conectividade com PostgreSQL, acessibilidade de repo1 e
#     repo2, e confirmação de que o WAL archive funciona (PostgreSQL deve estar
#     rodando com archive_mode=on e archive_command=pgbackrest archive-push).
#     Executar SEMPRE após stanza-create e antes de aceitar o backup como
#     operacional. Falha aqui significa que o backup NÃO está protegendo os dados.
#
# PRÉ-REQUISITOS NA VPS:
#   1. pgBackRest instalado:
#        pgbackrest --version
#   2. Segredos carregados e configuração materializada:
#        set -a; source /etc/healthintel/pgbackrest.env; set +a
#        envsubst < /repo/infra/pgbackrest/pgbackrest.conf > /etc/pgbackrest/pgbackrest.conf
#        chmod 640 /etc/pgbackrest/pgbackrest.conf
#        chown postgres:postgres /etc/pgbackrest/pgbackrest.conf
#   3. PostgreSQL rodando com os parâmetros WAL do Fase 7:
#        # Adicionar ao postgresql.conf:
#        #   include = '/etc/postgresql/conf.d/postgresql.fase7.conf'
#        systemctl restart postgresql
#   4. Repositório local criado e com permissão para o usuário postgres:
#        mkdir -p /var/lib/pgbackrest && chown postgres:postgres /var/lib/pgbackrest
#   5. Variável POSTGRES_DATA_DIR presente em /etc/healthintel/pgbackrest.env.
#
# USO:
#   sudo -u postgres bash scripts/backup/pgbackrest_init.sh
#   # Com banco em socket/porta alternativa:
#   PGHOST=/var/run/postgresql PGDATABASE=healthintel \
#     sudo -u postgres bash scripts/backup/pgbackrest_init.sh
#
# ROLLBACK:
#   stanza-create falhou: verificar acesso a repo1 e repo2; reexecutar.
#   check falhou: reiniciar PostgreSQL após aplicar postgresql.fase7.conf; reexecutar.
#   Desfazer stanza (DESTRUTIVO — apaga todos os backups no repositório):
#     pgbackrest --stanza=healthintel stanza-delete --force
#   plataforma.backup_execucao preserva o histórico de todas as tentativas.
#
# SAÍDA:
#   Exit 0 — stanza-create e check concluídos com sucesso; backup operacional.
#   Exit 1 — stanza-create falhou.
#   Exit 2 — check falhou (stanza pode ter sido criada; avaliar antes de re-executar).
#   Exit 3 — falha de conexão com o banco de dados.

set -euo pipefail

STANZA="${STANZA:-healthintel}"
PGHOST="${PGHOST:-/var/run/postgresql}"
PGPORT="${PGPORT:-5432}"
PGDATABASE="${PGDATABASE:-healthintel}"
PGUSER="${PGUSER:-postgres}"

_psql() {
    psql -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d "${PGDATABASE}" \
         -v ON_ERROR_STOP=1 -t -A -c "$1"
}

_escape() {
    # Duplica aspas simples para strings SQL (entrada interna — sem dados de usuário)
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
    local id="$1" status="$2" resumo="$3" erro="$4"
    _psql "UPDATE plataforma.backup_execucao SET
               finalizado_em = now(),
               status        = '${status}',
               log_resumo    = '$(_escape "${resumo}")',
               erro          = NULLIF('$(_escape "${erro}")', '')
           WHERE id = ${id};"
}

# Verificar conectividade com o banco antes de prosseguir
if ! _psql "SELECT 1;" > /dev/null 2>&1; then
    echo "[pgbackrest_init] ERRO: sem conexão com ${PGDATABASE}@${PGHOST}:${PGPORT}" >&2
    exit 3
fi

echo "[pgbackrest_init] stanza=${STANZA}  início=$(date --iso-8601=seconds)"

# ─── FASE 1: stanza-create ────────────────────────────────────────────────────
# Inicializa a estrutura do repositório em repo1 (local) e repo2 (S3-compatible).
# tipo='info' — operação de setup, não um backup nem um check de integridade.
echo "[pgbackrest_init] 1/2 — stanza-create"
ID_CREATE=$(_insert_execucao "info" "repo1_local" \
    "stanza-create: inicializando repo1 (local /var/lib/pgbackrest) e repo2 (S3)")
[[ "${ID_CREATE}" =~ ^[0-9]+$ ]] || { echo "[pgbackrest_init] ERRO: id inválido '${ID_CREATE}'" >&2; exit 3; }

OUTPUT_CREATE="" RC_CREATE=0
OUTPUT_CREATE=$(pgbackrest --stanza="${STANZA}" stanza-create 2>&1) || RC_CREATE=$?

if [[ ${RC_CREATE} -eq 0 ]]; then
    _update_execucao "${ID_CREATE}" "sucesso" "${OUTPUT_CREATE}" ""
    echo "[pgbackrest_init] stanza-create: sucesso (backup_execucao.id=${ID_CREATE})"
else
    _update_execucao "${ID_CREATE}" "falha" "" "${OUTPUT_CREATE}"
    echo "[pgbackrest_init] stanza-create: FALHOU exit=${RC_CREATE} (id=${ID_CREATE})" >&2
    printf '%s\n' "${OUTPUT_CREATE}" >&2
    exit 1
fi

# ─── FASE 2: check ────────────────────────────────────────────────────────────
# Hardgate: valida conectividade com PostgreSQL, acessibilidade de repo1 e repo2,
# e confirma que WAL archive funciona end-to-end.
echo "[pgbackrest_init] 2/2 — check (hardgate: conectividade + WAL archive)"
ID_CHECK=$(_insert_execucao "check" "repo1_local" \
    "check pos-stanza-create: validando repo1, repo2 e WAL archive end-to-end")
[[ "${ID_CHECK}" =~ ^[0-9]+$ ]] || { echo "[pgbackrest_init] ERRO: id inválido '${ID_CHECK}'" >&2; exit 3; }

OUTPUT_CHECK="" RC_CHECK=0
OUTPUT_CHECK=$(pgbackrest --stanza="${STANZA}" check 2>&1) || RC_CHECK=$?

if [[ ${RC_CHECK} -eq 0 ]]; then
    _update_execucao "${ID_CHECK}" "sucesso" "${OUTPUT_CHECK}" ""
    echo "[pgbackrest_init] check: sucesso — backup operacional (backup_execucao.id=${ID_CHECK})"
else
    _update_execucao "${ID_CHECK}" "falha" "" "${OUTPUT_CHECK}"
    echo "[pgbackrest_init] check: FALHOU exit=${RC_CHECK} (id=${ID_CHECK})" >&2
    printf '%s\n' "${OUTPUT_CHECK}" >&2
    exit 2
fi

echo "[pgbackrest_init] concluído $(date --iso-8601=seconds)"
echo "[pgbackrest_init] registros: stanza-create id=${ID_CREATE}  check id=${ID_CHECK}"
