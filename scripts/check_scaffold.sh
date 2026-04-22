#!/usr/bin/env bash
set -euo pipefail

test -f README.md
test -f docs/healthintel_suplementar_prd_final.md
test -f infra/docker-compose.yml
test -f api/app/main.py
test -f mongo_layout_service/app/main.py
test -f healthintel_dbt/dbt_project.yml
test -f .github/workflows/ci.yml
test -f docs/runbooks/subida_ambiente.md
test -f docs/operacao/slo_sla.md

echo "Scaffold HealthIntel verificado com sucesso."
