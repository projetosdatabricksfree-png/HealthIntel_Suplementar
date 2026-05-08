#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

OUT_DIR="${OUT_DIR:-$ROOT_DIR/tmp/auditoria}"
AUDIT_TIMESTAMP="${AUDIT_TIMESTAMP:-$(date +%Y%m%d_%H%M%S%z)}"
ENV_NAME="${ENV_NAME:-unknown}"
STRICT="${STRICT:-0}"

DBT_PROJECT_DIR="${DBT_PROJECT_DIR:-$ROOT_DIR/healthintel_dbt}"
DBT_PROFILES_DIR="${DBT_PROFILES_DIR:-$DBT_PROJECT_DIR}"
DBT_TARGET_PATH="${DBT_TARGET_PATH:-/tmp/healthintel_dbt_auditoria_target}"
DBT_LOG_PATH="${DBT_LOG_PATH:-/tmp/healthintel_dbt_auditoria_logs}"
DBT_TARGET="${DBT_TARGET:-}"

EXPECTED_SCHEMAS="bruto_ans,stg_ans,int_ans,nucleo_ans,api_ans,consumo_ans,consumo_premium_ans,ref_ans,plataforma"

if [ -z "${DATABASE_URL:-}" ]; then
    printf 'ERRO: defina DATABASE_URL para executar a auditoria.\n' >&2
    exit 2
fi

if [ "$STRICT" != "0" ] && [ "$STRICT" != "1" ]; then
    printf 'ERRO: STRICT deve ser 0 ou 1.\n' >&2
    exit 2
fi

if [ -x "${DBT_BIN:-}" ]; then
    DBT_BIN="$DBT_BIN"
elif [ -x "$ROOT_DIR/.venv/bin/dbt" ]; then
    DBT_BIN="$ROOT_DIR/.venv/bin/dbt"
elif command -v dbt >/dev/null 2>&1; then
    DBT_BIN="$(command -v dbt)"
else
    printf 'ERRO: dbt nao encontrado. Defina DBT_BIN ou instale dbt no ambiente.\n' >&2
    exit 2
fi

if [ -x "${PYTHON:-}" ]; then
    PYTHON_BIN="$PYTHON"
elif [ -x "$ROOT_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
else
    printf 'ERRO: python3 nao encontrado.\n' >&2
    exit 2
fi

if ! command -v psql >/dev/null 2>&1; then
    printf 'ERRO: psql nao encontrado no PATH.\n' >&2
    exit 2
fi

mkdir -p "$OUT_DIR" "$DBT_TARGET_PATH" "$DBT_LOG_PATH"

export DBT_PROFILES_DIR
export DBT_TARGET_PATH
export DBT_LOG_PATH

printf 'Executando dbt parse em %s...\n' "$DBT_PROJECT_DIR"
parse_args=(parse --profiles-dir "$DBT_PROFILES_DIR")
if [ -n "$DBT_TARGET" ]; then
    parse_args+=(--target "$DBT_TARGET")
fi

(
    cd "$DBT_PROJECT_DIR"
    "$DBT_BIN" "${parse_args[@]}"
)

manifest_source="$DBT_TARGET_PATH/manifest.json"
if [ ! -f "$manifest_source" ]; then
    printf 'ERRO: manifest dbt nao encontrado em %s apos dbt parse.\n' "$manifest_source" >&2
    exit 2
fi

manifest_copy="$OUT_DIR/manifest_dbt_${AUDIT_TIMESTAMP}.json"
cp -f "$manifest_source" "$manifest_copy"
cp -f "$manifest_copy" "$OUT_DIR/manifest_dbt_latest.json"

expected_csv="$OUT_DIR/objetos_dbt_esperados_${AUDIT_TIMESTAMP}.csv"
manifest_summary_json="$OUT_DIR/manifest_dbt_summary_${AUDIT_TIMESTAMP}.json"
out_of_scope_csv="$OUT_DIR/manifest_schemas_fora_escopo_${AUDIT_TIMESTAMP}.csv"

"$PYTHON_BIN" "$SCRIPT_DIR/extrair_manifest_dbt.py" \
    --manifest "$manifest_copy" \
    --expected-out "$expected_csv" \
    --summary-out "$manifest_summary_json" \
    --out-of-scope-out "$out_of_scope_csv" \
    --schemas "$EXPECTED_SCHEMAS" \
    --target-name "$DBT_TARGET"

printf 'Exportando catalogos do banco auditado...\n'
AUDIT_TIMESTAMP="$AUDIT_TIMESTAMP" OUT_DIR="$OUT_DIR" DATABASE_URL="$DATABASE_URL" \
    bash "$SCRIPT_DIR/exportar_catalogo_schema.sh" >/dev/null

catalogo_schema_csv="$OUT_DIR/catalogo_schema_${AUDIT_TIMESTAMP}.csv"

schemas_status_csv="$OUT_DIR/validacao_schemas_${AUDIT_TIMESTAMP}.csv"
seeds_status_csv="$OUT_DIR/validacao_seeds_${AUDIT_TIMESTAMP}.csv"
missing_dbt_csv="$OUT_DIR/objetos_dbt_faltantes_${AUDIT_TIMESTAMP}.csv"
baseline_diff_csv="$OUT_DIR/diferencas_baseline_${AUDIT_TIMESTAMP}.csv"
grants_status_csv="$OUT_DIR/validacao_grants_${AUDIT_TIMESTAMP}.csv"
roles_db_file="$OUT_DIR/roles_banco_${AUDIT_TIMESTAMP}.txt"
roles_project_file="$OUT_DIR/roles_mencionadas_projeto_${AUDIT_TIMESTAMP}.txt"
report_file="$OUT_DIR/relatorio_paridade_${AUDIT_TIMESTAMP}.md"

psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -Atc "
    select rolname
    from pg_catalog.pg_roles
    where rolname !~ '^pg_'
    order by rolname;
" > "$roles_db_file"
cp -f "$roles_db_file" "$OUT_DIR/roles_banco_latest.txt"

if command -v rg >/dev/null 2>&1; then
    rg --no-filename -o "healthintel_[A-Za-z0-9_]*reader|role_[A-Za-z0-9_]*reader" \
        "$ROOT_DIR/infra" "$ROOT_DIR/healthintel_dbt" "$ROOT_DIR/scripts" "$ROOT_DIR/docs" 2>/dev/null \
        | sort -u > "$roles_project_file" || true
else
    grep -RhoE "healthintel_[A-Za-z0-9_]*reader|role_[A-Za-z0-9_]*reader" \
        "$ROOT_DIR/infra" "$ROOT_DIR/healthintel_dbt" "$ROOT_DIR/scripts" "$ROOT_DIR/docs" 2>/dev/null \
        | sort -u > "$roles_project_file" || true
fi
cp -f "$roles_project_file" "$OUT_DIR/roles_mencionadas_projeto_latest.txt"

baseline_schema_csv="${BASELINE_SCHEMA_CSV:-}"
if [ -z "$baseline_schema_csv" ] && [ -n "${BASELINE_DIR:-}" ]; then
    baseline_schema_csv="$BASELINE_DIR/catalogo_schema_latest.csv"
fi

baseline_enabled="0"
if [ -n "$baseline_schema_csv" ]; then
    if [ ! -f "$baseline_schema_csv" ]; then
        printf 'ERRO: baseline de schema nao encontrado em %s.\n' "$baseline_schema_csv" >&2
        exit 2
    fi
    baseline_enabled="1"
fi

tmp_psql="$(mktemp)"
trap 'rm -f "$tmp_psql"' EXIT

cat > "$tmp_psql" <<SQL
\\set ON_ERROR_STOP on

create temp table auditoria_objetos_dbt_esperados (
    database_name text,
    schema_name text,
    object_name text,
    resource_type text,
    materialized text,
    original_file_path text,
    tags text,
    enabled text,
    target_name text,
    unique_id text,
    schema_in_scope text
);
\\copy auditoria_objetos_dbt_esperados from '$expected_csv' with (format csv, header true)

\\set output_file '$schemas_status_csv'
\\i '$SCRIPT_DIR/validar_schemas_principais.sql'

\\set output_file '$seeds_status_csv'
\\i '$SCRIPT_DIR/validar_seeds_obrigatorias.sql'

\\set output_file '$missing_dbt_csv'
\\i '$SCRIPT_DIR/listar_objetos_dbt_faltantes.sql'

\\set output_file '$grants_status_csv'
\\i '$SCRIPT_DIR/validar_grants_minimos.sql'
SQL

if [ "$baseline_enabled" = "1" ]; then
    cat >> "$tmp_psql" <<SQL

create temp table auditoria_baseline_schema (
    table_schema text,
    table_name text,
    column_name text,
    data_type text,
    udt_name text,
    is_nullable text,
    column_default text,
    ordinal_position text
);
create temp table auditoria_catalogo_schema_atual (
    table_schema text,
    table_name text,
    column_name text,
    data_type text,
    udt_name text,
    is_nullable text,
    column_default text,
    ordinal_position text
);
\\copy auditoria_baseline_schema from '$baseline_schema_csv' with (format csv, header true)
\\copy auditoria_catalogo_schema_atual from '$catalogo_schema_csv' with (format csv, header true)

\\set output_file '$baseline_diff_csv'
\\i '$SCRIPT_DIR/comparar_catalogo_baseline.sql'
SQL
else
    printf '%s\n' 'severity,check_type,table_schema,table_name,column_name,expected_data_type,actual_data_type,expected_udt_name,actual_udt_name,expected_is_nullable,actual_is_nullable,expected_column_default,actual_column_default,expected_ordinal_position,actual_ordinal_position,message' > "$baseline_diff_csv"
fi

psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$tmp_psql"

git_branch="$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || printf 'unknown')"
git_commit="$(git -C "$ROOT_DIR" rev-parse HEAD 2>/dev/null || printf 'unknown')"
dbt_version="$("$DBT_BIN" --version 2>&1 | sed ':a;N;$!ba;s/\n/; /g' || true)"
python_version="$("$PYTHON_BIN" --version 2>&1 || true)"
psql_version="$(psql --version 2>&1 || true)"

export AUDIT_REPORT_FILE="$report_file"
export AUDIT_STRICT="$STRICT"
export AUDIT_ENV_NAME="$ENV_NAME"
export AUDIT_TIMESTAMP="$AUDIT_TIMESTAMP"
export AUDIT_GIT_BRANCH="$git_branch"
export AUDIT_GIT_COMMIT="$git_commit"
export AUDIT_DBT_VERSION="$dbt_version"
export AUDIT_PYTHON_VERSION="$python_version"
export AUDIT_PSQL_VERSION="$psql_version"
export AUDIT_DBT_PROJECT_DIR="$DBT_PROJECT_DIR"
export AUDIT_DBT_PROFILES_DIR="$DBT_PROFILES_DIR"
export AUDIT_DBT_TARGET="$DBT_TARGET"
export AUDIT_DBT_TARGET_PATH="$DBT_TARGET_PATH"
export AUDIT_DBT_LOG_PATH="$DBT_LOG_PATH"
export AUDIT_DATABASE_URL="$DATABASE_URL"
export AUDIT_MANIFEST_COPY="$manifest_copy"
export AUDIT_MANIFEST_SUMMARY_JSON="$manifest_summary_json"
export AUDIT_EXPECTED_CSV="$expected_csv"
export AUDIT_OUT_OF_SCOPE_CSV="$out_of_scope_csv"
export AUDIT_SCHEMAS_STATUS_CSV="$schemas_status_csv"
export AUDIT_SEEDS_STATUS_CSV="$seeds_status_csv"
export AUDIT_MISSING_DBT_CSV="$missing_dbt_csv"
export AUDIT_BASELINE_DIFF_CSV="$baseline_diff_csv"
export AUDIT_GRANTS_STATUS_CSV="$grants_status_csv"
export AUDIT_ROLES_DB_FILE="$roles_db_file"
export AUDIT_ROLES_PROJECT_FILE="$roles_project_file"
export AUDIT_BASELINE_ENABLED="$baseline_enabled"
export AUDIT_BASELINE_SCHEMA_CSV="$baseline_schema_csv"
export AUDIT_OUT_DIR="$OUT_DIR"

blocking_failures="$("$PYTHON_BIN" - <<'PY'
from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


def read_csv(path: str) -> list[dict[str, str]]:
    if not path or not Path(path).exists():
        return []
    with open(path, newline="", encoding="utf-8") as fp:
        return list(csv.DictReader(fp))


def read_lines(path: str) -> list[str]:
    if not path or not Path(path).exists():
        return []
    with open(path, encoding="utf-8") as fp:
        return [line.strip() for line in fp if line.strip()]


def mask_database_url(url: str) -> str:
    if not url:
        return ""
    try:
        parsed = urlsplit(url)
    except ValueError:
        return "***"
    if parsed.password is None:
        return urlunsplit(parsed)
    username = parsed.username or ""
    host = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    userinfo = f"{username}:***@" if username else "***@"
    return urlunsplit((parsed.scheme, f"{userinfo}{host}{port}", parsed.path, parsed.query, parsed.fragment))


def count_by_severity(rows: list[dict[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        severity = row.get("severity", "UNKNOWN") or "UNKNOWN"
        counts[severity] = counts.get(severity, 0) + 1
    return counts


def append_table(lines: list[str], rows: list[dict[str, str]], columns: list[str], limit: int = 30) -> None:
    if not rows:
        lines.append("Nenhum registro.")
        return
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join("---" for _ in columns) + " |")
    for row in rows[:limit]:
        values = [str(row.get(col, "")).replace("\n", " ") for col in columns]
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > limit:
        lines.append(f"\nExibindo {limit} de {len(rows)} registros.")


summary_path = os.environ["AUDIT_MANIFEST_SUMMARY_JSON"]
with open(summary_path, encoding="utf-8") as fp:
    manifest_summary = json.load(fp)

schemas_rows = read_csv(os.environ["AUDIT_SCHEMAS_STATUS_CSV"])
seeds_rows = read_csv(os.environ["AUDIT_SEEDS_STATUS_CSV"])
missing_dbt_rows = read_csv(os.environ["AUDIT_MISSING_DBT_CSV"])
baseline_rows = read_csv(os.environ["AUDIT_BASELINE_DIFF_CSV"])
grants_rows = read_csv(os.environ["AUDIT_GRANTS_STATUS_CSV"])
out_of_scope_rows = read_csv(os.environ["AUDIT_OUT_OF_SCOPE_CSV"])
roles_db = read_lines(os.environ["AUDIT_ROLES_DB_FILE"])
roles_project = read_lines(os.environ["AUDIT_ROLES_PROJECT_FILE"])

fail_rows = []
for source_name, rows in [
    ("schemas", schemas_rows),
    ("seeds", seeds_rows),
    ("objetos_dbt", missing_dbt_rows),
    ("baseline", baseline_rows),
    ("grants", grants_rows),
]:
    for row in rows:
        if row.get("severity") == "FAIL":
            fail_rows.append((source_name, row))

warn_rows = []
for source_name, rows in [
    ("objetos_dbt", missing_dbt_rows),
    ("baseline", baseline_rows),
    ("grants", grants_rows),
]:
    for row in rows:
        if row.get("severity") == "WARN":
            warn_rows.append((source_name, row))

status = "PASS" if not fail_rows else "FAIL"

lines: list[str] = []
lines.append("# Auditoria de Paridade dbt/PostgreSQL")
lines.append("")
lines.append("## Contexto")
lines.append("")
lines.append(f"- Ambiente: `{os.environ.get('AUDIT_ENV_NAME', '')}`")
lines.append(f"- Timestamp: `{os.environ.get('AUDIT_TIMESTAMP', '')}`")
lines.append(f"- STRICT: `{os.environ.get('AUDIT_STRICT', '')}`")
lines.append(f"- Status: `{status}`")
lines.append(f"- Git branch: `{os.environ.get('AUDIT_GIT_BRANCH', '')}`")
lines.append(f"- Git commit: `{os.environ.get('AUDIT_GIT_COMMIT', '')}`")
lines.append(f"- dbt version: `{os.environ.get('AUDIT_DBT_VERSION', '')}`")
lines.append(f"- Python version: `{os.environ.get('AUDIT_PYTHON_VERSION', '')}`")
lines.append(f"- psql version: `{os.environ.get('AUDIT_PSQL_VERSION', '')}`")
lines.append(f"- DBT_PROJECT_DIR: `{os.environ.get('AUDIT_DBT_PROJECT_DIR', '')}`")
lines.append(f"- DBT_PROFILES_DIR: `{os.environ.get('AUDIT_DBT_PROFILES_DIR', '')}`")
lines.append(f"- DBT_TARGET: `{os.environ.get('AUDIT_DBT_TARGET', '')}`")
lines.append(f"- DBT_TARGET_PATH: `{os.environ.get('AUDIT_DBT_TARGET_PATH', '')}`")
lines.append(f"- DBT_LOG_PATH: `{os.environ.get('AUDIT_DBT_LOG_PATH', '')}`")
lines.append(f"- DATABASE_URL: `{mask_database_url(os.environ.get('AUDIT_DATABASE_URL', ''))}`")
lines.append(f"- Manifest usado: `{os.environ.get('AUDIT_MANIFEST_COPY', '')}`")
lines.append(f"- Baseline local: `{os.environ.get('AUDIT_BASELINE_SCHEMA_CSV', '') if os.environ.get('AUDIT_BASELINE_ENABLED') == '1' else 'nao informado'}`")
lines.append("")

lines.append("## Recursos dbt")
lines.append("")
lines.append(f"- Objetos considerados: `{manifest_summary.get('considered_count', 0)}`")
for key, value in (manifest_summary.get("expected_by_resource_type") or {}).items():
    lines.append(f"- Considerados `{key}`: `{value}`")
ignored = manifest_summary.get("ignored_counts") or {}
for key in ["ephemeral", "disabled", "tests", "sources", "exposures", "macros", "docs"]:
    lines.append(f"- Ignorados `{key}`: `{ignored.get(key, 0)}`")
lines.append(f"- Objetos em schemas fora do escopo principal: `{manifest_summary.get('out_of_scope_objects_count', 0)}`")
out_schemas = manifest_summary.get("out_of_scope_schemas") or []
if out_schemas:
    lines.append(f"- Schemas fora do escopo principal: `{', '.join(out_schemas)}`")
lines.append("")

lines.append("## Resumo de severidades")
lines.append("")
summary_rows = [
    ("schemas", count_by_severity(schemas_rows)),
    ("seeds", count_by_severity(seeds_rows)),
    ("objetos_dbt", count_by_severity(missing_dbt_rows)),
    ("baseline", count_by_severity(baseline_rows)),
    ("grants", count_by_severity(grants_rows)),
]
lines.append("| Grupo | PASS | FAIL | WARN | INFO |")
lines.append("| --- | ---: | ---: | ---: | ---: |")
for group, counts in summary_rows:
    lines.append(f"| {group} | {counts.get('PASS', 0)} | {counts.get('FAIL', 0)} | {counts.get('WARN', 0)} | {counts.get('INFO', 0)} |")
lines.append("")

lines.append("## Roles detectadas")
lines.append("")
lines.append("### Banco")
append_table(lines, [{"role": role} for role in roles_db], ["role"], limit=50)
lines.append("")
lines.append("### Projeto")
append_table(lines, [{"role": role} for role in roles_project], ["role"], limit=50)
lines.append("")

lines.append("## Schemas obrigatorios")
lines.append("")
append_table(lines, schemas_rows, ["severity", "schema_name", "exists", "message"])
lines.append("")

lines.append("## Seeds obrigatorias")
lines.append("")
append_table(lines, seeds_rows, ["severity", "seed_schema", "seed_name", "exists", "row_count", "message"])
lines.append("")

lines.append("## Objetos dbt faltantes")
lines.append("")
append_table(lines, missing_dbt_rows, ["severity", "schema_name", "object_name", "resource_type", "materialized", "original_file_path", "message"])
lines.append("")

lines.append("## Schemas fora do escopo principal no manifest")
lines.append("")
append_table(lines, out_of_scope_rows, ["schema_name", "object_name", "resource_type", "materialized", "original_file_path"], limit=50)
lines.append("")

lines.append("## Diferencas contra baseline local")
lines.append("")
append_table(lines, baseline_rows, ["severity", "check_type", "table_schema", "table_name", "column_name", "expected_data_type", "actual_data_type", "message"])
lines.append("")

lines.append("## Grants e permissoes")
lines.append("")
append_table(lines, grants_rows, ["severity", "check_type", "role_name", "object_schema", "object_name", "privilege_type", "message"], limit=80)
lines.append("")

lines.append("## Arquivos gerados")
lines.append("")
for env_key in [
    "AUDIT_EXPECTED_CSV",
    "AUDIT_SCHEMAS_STATUS_CSV",
    "AUDIT_SEEDS_STATUS_CSV",
    "AUDIT_MISSING_DBT_CSV",
    "AUDIT_BASELINE_DIFF_CSV",
    "AUDIT_GRANTS_STATUS_CSV",
]:
    lines.append(f"- `{os.environ.get(env_key, '')}`")
lines.append("")

lines.append("## Proximo passo seguro")
lines.append("")
if fail_rows:
    lines.append("Corrigir primeiro as falhas listadas acima. Nao execute `dbt build --select +tag:mart` enquanto seeds obrigatorias estiverem ausentes ou vazias.")
else:
    lines.append("Auditoria sem falhas bloqueantes. Se as seeds obrigatorias estao presentes e populadas, o proximo passo seguro e executar `dbt build --select +tag:mart`.")
lines.append("")

report_file = Path(os.environ["AUDIT_REPORT_FILE"])
report_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(len(fail_rows))
PY
)"

cp -f "$report_file" "$OUT_DIR/relatorio_paridade_latest.md"
cp -f "$manifest_summary_json" "$OUT_DIR/manifest_dbt_summary_latest.json"
cp -f "$out_of_scope_csv" "$OUT_DIR/manifest_schemas_fora_escopo_latest.csv"

printf 'Relatorio gerado em: %s\n' "$report_file"

if [ "$STRICT" = "1" ] && [ "$blocking_failures" -gt 0 ]; then
    printf 'Auditoria STRICT falhou com %s divergencia(s) bloqueante(s).\n' "$blocking_failures" >&2
    exit 1
fi

exit 0
