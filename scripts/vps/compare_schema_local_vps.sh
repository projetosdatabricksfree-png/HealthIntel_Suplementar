#!/usr/bin/env bash
set -Eeuo pipefail

VPS_SSH="${VPS_SSH:-root@5.189.160.27}"
VPS_PROJECT_DIR="${VPS_PROJECT_DIR:-/opt/healthintel}"
LOCAL_POSTGRES_CONTAINER="${LOCAL_POSTGRES_CONTAINER:-healthintel_postgres}"
POSTGRES_USER="${POSTGRES_USER:-healthintel}"
POSTGRES_DB="${POSTGRES_DB:-healthintel}"
OUT_DIR="${OUT_DIR:-tmp/schema_compare}"

SCHEMAS=(
  plataforma
  bruto_ans
  stg_ans
  int_ans
  nucleo_ans
  consumo_ans
  consumo_premium_ans
  api_ans
  ref_ans
  mdm_privado
  bruto_cliente
)

schema_csv() {
  local joined=""
  local schema
  for schema in "${SCHEMAS[@]}"; do
    if [ -n "$joined" ]; then
      joined="$joined,"
    fi
    joined="$joined'$schema'"
  done
  printf '%s' "$joined"
}

SQL_TABLES="
select table_schema || '.' || table_name
from information_schema.tables
where table_schema in ($(schema_csv))
  and table_type in ('BASE TABLE', 'VIEW')
order by 1;
"

SQL_COUNTS="
select table_schema, count(*) as total
from information_schema.tables
where table_schema in ($(schema_csv))
  and table_type in ('BASE TABLE', 'VIEW')
group by table_schema
order by table_schema;
"

mkdir -p "$OUT_DIR"

printf 'Coletando estrutura local em %s...\n' "$LOCAL_POSTGRES_CONTAINER"
docker exec -i "$LOCAL_POSTGRES_CONTAINER" psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "$SQL_TABLES" \
  | sort -u > "$OUT_DIR/local_tables.txt"

printf 'Coletando estrutura da VPS via %s...\n' "$VPS_SSH"
ssh "$VPS_SSH" "cd '$VPS_PROJECT_DIR' && docker exec -i healthintel_postgres psql -v ON_ERROR_STOP=1 -U '$POSTGRES_USER' -d '$POSTGRES_DB' -Atc \"$SQL_TABLES\"" \
  | sort -u > "$OUT_DIR/vps_tables.txt"

comm -23 "$OUT_DIR/local_tables.txt" "$OUT_DIR/vps_tables.txt" > "$OUT_DIR/missing_on_vps.txt"
comm -13 "$OUT_DIR/local_tables.txt" "$OUT_DIR/vps_tables.txt" > "$OUT_DIR/extra_on_vps.txt"

LOCAL_COUNTS="$(docker exec -i "$LOCAL_POSTGRES_CONTAINER" psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "$SQL_COUNTS")"
VPS_COUNTS="$(ssh "$VPS_SSH" "cd '$VPS_PROJECT_DIR' && docker exec -i healthintel_postgres psql -v ON_ERROR_STOP=1 -U '$POSTGRES_USER' -d '$POSTGRES_DB' -Atc \"$SQL_COUNTS\"")"

cat > "$OUT_DIR/summary.md" <<EOF
# Comparacao de Schema Local x VPS

Gerado em: $(date -Is)

## Escopo

Schemas comparados:

$(printf -- '- %s\n' "${SCHEMAS[@]}")

## Totais

- tabelas/views locais: $(wc -l < "$OUT_DIR/local_tables.txt")
- tabelas/views na VPS: $(wc -l < "$OUT_DIR/vps_tables.txt")
- ausentes na VPS: $(wc -l < "$OUT_DIR/missing_on_vps.txt")
- extras na VPS: $(wc -l < "$OUT_DIR/extra_on_vps.txt")

## Contagem por schema - local

\`\`\`text
$LOCAL_COUNTS
\`\`\`

## Contagem por schema - VPS

\`\`\`text
$VPS_COUNTS
\`\`\`

## Arquivos gerados

- tmp/schema_compare/local_tables.txt
- tmp/schema_compare/vps_tables.txt
- tmp/schema_compare/missing_on_vps.txt
- tmp/schema_compare/extra_on_vps.txt
- tmp/schema_compare/summary.md
EOF

printf '\nResumo salvo em %s/summary.md\n' "$OUT_DIR"
