#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/healthintel}"
LOG_DIR="${LOG_DIR:-logs/fase13}"
ELT_ESCOPO="${ELT_ESCOPO:-sector_core}"
ELT_FAMILIAS="${ELT_FAMILIAS:-cadop,sib,idss,igr,nip}"
ELT_LIMITE="${ELT_LIMITE:-100}"
ELT_MAX_DEPTH="${ELT_MAX_DEPTH:-5}"
MAX_DISK_USE_PCT="${MAX_DISK_USE_PCT:-80}"

cd "$PROJECT_DIR"
mkdir -p "$LOG_DIR"

timestamp="$(date +%Y%m%d_%H%M%S)"
log_file="$LOG_DIR/carga_core_sem_tiss_$timestamp.log"
exec > >(tee -a "$log_file") 2>&1

disk_pct="$(df -P . | awk 'NR==2 {gsub("%", "", $5); print $5}')"
if [ "$disk_pct" -gt "$MAX_DISK_USE_PCT" ]; then
  printf 'FAIL uso de disco em %s%%, limite %s%%.\n' "$disk_pct" "$MAX_DISK_USE_PCT" >&2
  exit 1
fi

if [ "$ELT_ESCOPO" = "all_ftp" ]; then
  printf 'FAIL ELT_ESCOPO=all_ftp e proibido nesta fase.\n' >&2
  exit 1
fi

familias_lower="$(printf '%s' "$ELT_FAMILIAS" | tr '[:upper:]' '[:lower:]')"
case ",$familias_lower," in
  *",tiss,"*|*",cnes,"*|*",cnes_completo,"*|*",all_ftp,"*)
    printf 'FAIL familias proibidas nesta fase: %s\n' "$ELT_FAMILIAS" >&2
    exit 1
    ;;
esac

if ! grep -qE '^elt-all:' Makefile; then
  printf 'FAIL alvo make elt-all nao existe no Makefile.\n' >&2
  exit 1
fi

if [ -x ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
else
  PYTHON_BIN="${PYTHON_BIN:-python3}"
fi

compose_cmd=(docker compose --env-file .env.hml -f infra/docker-compose.yml -f infra/docker-compose.hml.yml)

printf 'Executando carga controlada Core sem TISS.\n'
printf 'ELT_ESCOPO=%s\n' "$ELT_ESCOPO"
printf 'ELT_FAMILIAS=%s\n' "$ELT_FAMILIAS"
printf 'ELT_LIMITE=%s\n' "$ELT_LIMITE"
printf 'ELT_MAX_DEPTH=%s\n' "$ELT_MAX_DEPTH"
printf 'Uso de disco=%s%%\n' "$disk_pct"

if command -v make >/dev/null 2>&1; then
  make elt-all \
    ELT_ESCOPO="$ELT_ESCOPO" \
    ELT_FAMILIAS="$ELT_FAMILIAS" \
    ELT_LIMITE="$ELT_LIMITE" \
    ELT_MAX_DEPTH="$ELT_MAX_DEPTH"
elif "${compose_cmd[@]}" ps -q api >/dev/null 2>&1; then
  printf 'make nao encontrado; executando comando equivalente no container api.\n'
  "${compose_cmd[@]}" exec -T \
    -e PYTHONPATH=/workspace \
    api python scripts/elt_all_ans.py \
      --escopo "$ELT_ESCOPO" \
      --familias "$ELT_FAMILIAS" \
      --limite "$ELT_LIMITE" \
      --max-depth "$ELT_MAX_DEPTH"
else
  printf 'make nao encontrado; executando comando equivalente diretamente com %s.\n' "$PYTHON_BIN"
  PYTHONPATH="$PWD" "$PYTHON_BIN" scripts/elt_all_ans.py \
    --escopo "$ELT_ESCOPO" \
    --familias "$ELT_FAMILIAS" \
    --limite "$ELT_LIMITE" \
    --max-depth "$ELT_MAX_DEPTH"
fi

printf 'Carga controlada concluida. Log: %s\n' "$log_file"
