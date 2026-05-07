#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/healthintel}"
ENV_FILE="${ENV_FILE:-.env.hml}"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-healthintel_postgres}"
POSTGRES_USER="${POSTGRES_USER:-healthintel}"
POSTGRES_DB="${POSTGRES_DB:-healthintel}"
BACKUP_DIR="${BACKUP_DIR:-backups/pre_fase13}"
LOG_DIR="${LOG_DIR:-logs/fase13}"
RECENT_BACKUP_MINUTES="${RECENT_BACKUP_MINUTES:-120}"

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

CORE_API_TABLES=(
  api_operadora
  api_ranking_score
  api_market_share_mensal
  api_score_operadora_mensal
)

if [ "${CONFIRM_SYNC_SCHEMA:-}" != "SIM" ]; then
  printf 'Defina CONFIRM_SYNC_SCHEMA=SIM para sincronizar estrutura na VPS.\n' >&2
  exit 2
fi

cd "$PROJECT_DIR"
mkdir -p "$BACKUP_DIR" "$LOG_DIR"

timestamp="$(date +%Y%m%d_%H%M%S)"
log_file="$LOG_DIR/sync_schema_vps_$timestamp.log"
exec > >(tee -a "$log_file") 2>&1

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

psql_exec() {
  docker exec -i "$POSTGRES_CONTAINER" psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" "$@"
}

table_counts() {
  psql_exec -c "
    select table_schema, count(*) as tabelas
    from information_schema.tables
    where table_schema in ($(schema_csv))
      and table_type in ('BASE TABLE', 'VIEW')
    group by table_schema
    order by table_schema;
  "
}

recent_backup_exists() {
  find "$BACKUP_DIR" -maxdepth 1 -type f -name 'healthintel_pre_fase13_*.sql.gz' -mmin "-$RECENT_BACKUP_MINUTES" | grep -q .
}

create_backup() {
  local backup_file="$BACKUP_DIR/healthintel_pre_fase13_$timestamp.sql"
  printf 'Criando backup logico completo em %s.gz...\n' "$backup_file"
  docker exec -t "$POSTGRES_CONTAINER" pg_dump \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    --no-owner \
    --no-privileges \
    > "$backup_file"
  gzip -f "$backup_file"
  test -s "$backup_file.gz"
}

printf '=== Contagem antes ===\n'
table_counts

if recent_backup_exists; then
  printf 'Backup recente encontrado em %s. Novo backup nao sera criado.\n' "$BACKUP_DIR"
else
  create_backup
fi

printf '=== Preparando schemas e roles auxiliares ===\n'
psql_exec -c "
  create schema if not exists plataforma;
  create schema if not exists bruto_ans;
  create schema if not exists stg_ans;
  create schema if not exists int_ans;
  create schema if not exists nucleo_ans;
  create schema if not exists consumo_ans;
  create schema if not exists consumo_premium_ans;
  create schema if not exists api_ans;
  create schema if not exists ref_ans;
  create schema if not exists mdm_privado;
  create schema if not exists bruto_cliente;
  create schema if not exists stg_cliente;
  create schema if not exists quality_ans;
  create schema if not exists mdm_ans;
  do \$\$
  begin
    if not exists (select 1 from pg_roles where rolname = 'healthintel_cliente_reader') then
      create role healthintel_cliente_reader;
    end if;
    if not exists (select 1 from pg_roles where rolname = 'healthintel_premium_reader') then
      create role healthintel_premium_reader;
    end if;
  end
  \$\$;
"

printf '=== Garantindo tabelas plataforma sem seeds locais ===\n'
psql_exec -c "
  create table if not exists plataforma.plano (
      id uuid primary key,
      nome text not null unique,
      limite_rpm integer not null,
      endpoint_permitido text[] not null,
      status text not null,
      criado_em timestamptz not null default now()
  );

  create table if not exists plataforma.cliente (
      id uuid primary key,
      nome text not null,
      email text not null unique,
      status text not null,
      plano_id uuid not null references plataforma.plano(id),
      criado_em timestamptz not null default now()
  );

  create table if not exists plataforma.chave_api (
      id uuid primary key,
      cliente_id uuid not null references plataforma.cliente(id),
      plano_id uuid not null references plataforma.plano(id),
      hash_chave char(64) not null unique,
      prefixo_chave char(10) not null,
      status text not null,
      criado_em timestamptz not null default now(),
      ultimo_uso_em timestamptz
  );

  create table if not exists plataforma.log_uso (
      id bigserial,
      chave_id uuid not null references plataforma.chave_api(id),
      cliente_id uuid not null references plataforma.cliente(id),
      plano_id uuid not null references plataforma.plano(id),
      endpoint text not null,
      rota text,
      metodo text not null,
      codigo_status integer not null,
      latencia_ms integer not null,
      cache_hit boolean not null default false,
      timestamp_req timestamptz not null,
      hash_ip text,
      primary key (id, timestamp_req)
  ) partition by range (timestamp_req);

  create table if not exists plataforma.log_uso_default
      partition of plataforma.log_uso default;

  create index if not exists ix_chave_api_hash on plataforma.chave_api (hash_chave);
  create index if not exists ix_chave_api_cliente on plataforma.chave_api (cliente_id, status);
  create index if not exists ix_log_uso_chave_tempo on plataforma.log_uso (chave_id, timestamp_req desc);
  create index if not exists ix_log_uso_endpoint_tempo on plataforma.log_uso (endpoint, timestamp_req desc);
"

printf '=== Aplicando init SQL idempotente sem TISS e sem seed de chave local ===\n'
while IFS= read -r sql_file; do
  base_name="$(basename "$sql_file")"
  case "$base_name" in
    003_api_comercial.sql)
      printf 'SKIP %s: DDL sensivel aplicado sem inserts locais.\n' "$base_name"
      continue
      ;;
    012_tiss.sql)
      printf 'SKIP %s: TISS fora do escopo da Fase 13B.\n' "$base_name"
      continue
      ;;
  esac
  printf 'Aplicando %s...\n' "$base_name"
  psql_exec < "$sql_file"
done < <(find infra/postgres/init -maxdepth 1 -type f -name '*.sql' | sort)

printf '=== Contagem depois ===\n'
table_counts

printf '=== Validando tabelas Core API ===\n'
for table_name in "${CORE_API_TABLES[@]}"; do
  exists="$(psql_exec -Atc "select to_regclass('api_ans.$table_name') is not null;")"
  if [ "$exists" != "t" ]; then
    printf 'WARN api_ans.%s ainda nao existe. Ela deve ser criada pelo dbt/serving Core.\n' "$table_name"
  else
    printf 'OK api_ans.%s existe.\n' "$table_name"
  fi
done

api_table_count="$(psql_exec -Atc "select count(*) from information_schema.tables where table_schema = 'api_ans' and table_type in ('BASE TABLE', 'VIEW');")"
if [ "$api_table_count" -le 1 ]; then
  printf 'WARN api_ans continua reduzido a %s tabela(s). Proximo passo obrigatorio: build_serving_core.sh.\n' "$api_table_count" >&2
  if [ "${REQUIRE_API_ANS_EXPANDED:-NAO}" = "SIM" ]; then
    printf 'FAIL REQUIRE_API_ANS_EXPANDED=SIM e api_ans ainda nao foi expandido.\n' >&2
    exit 1
  fi
fi

printf 'Sincronizacao de estrutura concluida. Log: %s\n' "$log_file"
