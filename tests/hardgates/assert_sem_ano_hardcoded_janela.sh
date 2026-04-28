#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

arquivos=(
  "ingestao/app/janela_carga.py"
  "ingestao/app/carregar_postgres.py"
  "ingestao/app/ingestao_real.py"
  "ingestao/app/pipeline_bronze.py"
)

falhas=()

for arquivo in "${arquivos[@]}"; do
  [[ -f "$arquivo" ]] || continue

  while IFS=: read -r numero_linha conteudo; do
    [[ -n "${numero_linha:-}" ]] || continue
    falhas+=("${arquivo}:${numero_linha}: comparacao direta de competencia com ano fixo: ${conteudo}")
  done < <(
    grep -nE "competencia[^#]*(<=|>=|<|>|==|!=)[[:space:]]*20[0-9]{4}" "$arquivo" || true
  )

  while IFS=: read -r numero_linha conteudo; do
    [[ -n "${numero_linha:-}" ]] || continue
    falhas+=("${arquivo}:${numero_linha}: regra de janela com current_year - 1: ${conteudo}")
  done < <(
    grep -nE "current_year[[:space:]]*-[[:space:]]*1|ano_atual[[:space:]]*-[[:space:]]*1|ano_vigente[[:space:]]*-[[:space:]]*1" "$arquivo" || true
  )
done

if (( ${#falhas[@]} > 0 )); then
  printf 'Hardgate falhou: ano hardcoded em logica produtiva de janela.\n' >&2
  printf '%s\n' "${falhas[@]}" >&2
  exit 1
fi

printf 'Hardgate OK: sem ano hardcoded em logica produtiva de janela.\n'
