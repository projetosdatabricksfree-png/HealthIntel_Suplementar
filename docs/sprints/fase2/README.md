# Fase 2 — Expansão da Plataforma HealthIntel

Fase de expansão pós-MVP cobrindo datasets ausentes e camada analítica de procedimentos.

## Sprints

| Sprint | Título | Status |
|--------|--------|--------|
| [Sprint 13](sprint_13_cnes_estabelecimentos.md) | CNES Estabelecimentos | Em andamento |
| [Sprint 14](sprint_14_tiss_cruzamentos.md) | D-TISS, TUSS, Rol e Cruzamentos | Não iniciada |

## Progresso Sprint 13 — CNES

- [x] DDL bronze + particionamento
- [x] Layout registry MongoDB
- [x] DAG ingestão
- [x] Loader Python
- [x] Partição automática (dag_criar_particao_mensal)
- [x] Source freshness (_sources.yml)
- [x] dbt staging + intermediates + marts + API
- [x] FastAPI endpoints + schemas + service
- [x] Seed demo + smoke test + Makefile targets

## Progresso Sprint 14 — D-TISS

- [x] DDL bronze + particionamento
- [x] Layout registry MongoDB
- [x] DAG ingestão
- [x] Loader Python
- [x] Seeds ref_tuss + ref_rol_procedimento
- [x] dbt staging + intermediates + marts + API
- [x] FastAPI endpoints TISS
- [x] Seed demo + Makefile targets
