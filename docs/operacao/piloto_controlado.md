# Piloto controlado — Readiness

## Objetivo

Conduzir o primeiro piloto com design partners sem reabrir a arquitetura da plataforma.

## Checklist de readiness

- [x] CI com `ruff`, `pytest`, `sqlfluff` e `dbt compile`.
- [x] `docker compose config` validado.
- [x] smoke script fim a fim disponível.
- [x] teste de carga Locust versionado.
- [x] runbooks operacionais publicados.
- [x] SLO/SLA formalizados.
- [x] hardening mínimo aplicado em API, layout service e Nginx.
- [x] limite de payload documentado e configurável por ambiente.
- [x] acesso interno ao layout registry protegido por `X-Service-Token`.
- [x] endpoints de prontidão disponíveis para API e layout service.

## Fluxo para staging

1. Publicar imagem/commit da release candidata.
2. Aplicar `docker compose config` com variáveis do ambiente.
3. Subir dependências e aplicar scripts SQL.
4. Rodar `dbt deps && dbt build`.
5. Rodar `python scripts/smoke_piloto.py`.
6. Executar `bash scripts/run_load_test.sh` com `CACHE_MODE=mixed`.
7. Registrar resultado em `plataforma.job` ou ferramenta externa do deploy.

## Critério de go/no-go

- `smoke_piloto.py` sem falhas;
- `sqlfluff`, `ruff` e `pytest` sem erro;
- `p95` dentro do SLO definido;
- nenhuma dependência crítica indisponível em `/prontidao`.
