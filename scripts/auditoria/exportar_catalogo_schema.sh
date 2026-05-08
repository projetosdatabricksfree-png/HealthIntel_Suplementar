#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUT_DIR="${OUT_DIR:-$ROOT_DIR/tmp/auditoria}"
AUDIT_TIMESTAMP="${AUDIT_TIMESTAMP:-$(date +%Y%m%d_%H%M%S%z)}"

if [ -z "${DATABASE_URL:-}" ]; then
    printf 'ERRO: defina DATABASE_URL para exportar o catalogo do banco.\n' >&2
    exit 2
fi

if ! command -v psql >/dev/null 2>&1; then
    printf 'ERRO: psql nao encontrado no PATH.\n' >&2
    exit 2
fi

mkdir -p "$OUT_DIR"

export_csv() {
    local sql_file="$1"
    local output_file="$2"

    psql "$DATABASE_URL" \
        -v ON_ERROR_STOP=1 \
        -v output_file="$output_file" \
        -f "$sql_file"
}

schema_file="$OUT_DIR/catalogo_schema_${AUDIT_TIMESTAMP}.csv"
objetos_file="$OUT_DIR/catalogo_objetos_${AUDIT_TIMESTAMP}.csv"
grants_file="$OUT_DIR/catalogo_grants_${AUDIT_TIMESTAMP}.csv"
constraints_file="$OUT_DIR/catalogo_constraints_${AUDIT_TIMESTAMP}.csv"
indexes_file="$OUT_DIR/catalogo_indexes_${AUDIT_TIMESTAMP}.csv"

export_csv "$SCRIPT_DIR/exportar_catalogo_schema.sql" "$schema_file"
export_csv "$SCRIPT_DIR/exportar_catalogo_objetos.sql" "$objetos_file"
export_csv "$SCRIPT_DIR/exportar_catalogo_grants.sql" "$grants_file"
export_csv "$SCRIPT_DIR/exportar_catalogo_constraints.sql" "$constraints_file"
export_csv "$SCRIPT_DIR/exportar_catalogo_indexes.sql" "$indexes_file"

cp -f "$schema_file" "$OUT_DIR/catalogo_schema_latest.csv"
cp -f "$objetos_file" "$OUT_DIR/catalogo_objetos_latest.csv"
cp -f "$grants_file" "$OUT_DIR/catalogo_grants_latest.csv"
cp -f "$constraints_file" "$OUT_DIR/catalogo_constraints_latest.csv"
cp -f "$indexes_file" "$OUT_DIR/catalogo_indexes_latest.csv"

cat <<EOF
Catalogos exportados em: $OUT_DIR
- $schema_file
- $objetos_file
- $grants_file
- $constraints_file
- $indexes_file
EOF
