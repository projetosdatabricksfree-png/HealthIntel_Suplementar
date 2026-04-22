# Sprint 01 — Fundacao da Plataforma

**Status:** Concluida
**Objetivo:** estabelecer a base estrutural do monorepo, a infraestrutura local e os padroes tecnicos do projeto.
**Criterio de saida:** ambiente local sobe com os servicos centrais e a estrutura principal do repositorio fica congelada.

## Historias

### HIS-01.1 — Estruturar o monorepo

- [x] Criar a arvore principal com `api/`, `healthintel_dbt/`, `ingestao/`, `infra/`, `docs/`, `mongo_layout_service/`, `shared/`, `testes/` e `scripts/`.
- [x] Posicionar o documento mestre em `docs/healthintel_suplementar_prd_final.md`.
- [x] Preservar `mcp_server/` como legado, fora da trilha principal do bootstrap.

### HIS-01.2 — Subir a infraestrutura local

- [x] Criar `infra/docker-compose.yml` com `PostgreSQL`, `MongoDB`, `Redis`, `Airflow`, `Nginx`, `api` e `mongo_layout_service`.
- [x] Definir `infra/nginx/nginx.conf` para roteamento base.
- [x] Validar a composicao com `docker compose -f infra/docker-compose.yml config`.

### HIS-01.3 — Definir banco e bootstrap inicial

- [x] Criar `infra/postgres/init/001_schemas.sql` com schemas iniciais do projeto.
- [x] Criar `.env.exemplo` alinhado com a arquitetura alvo, sem legado Databricks.
- [x] Criar `Makefile`, `pyproject.toml` e `.pre-commit-config.yaml`.

### HIS-01.4 — Padronizar configuracao e observabilidade base

- [x] Implementar leitura de configuracao em `api/app/core/config.py`.
- [x] Implementar leitura de configuracao em `mongo_layout_service/app/core/config.py`.
- [x] Criar middleware base de log em `api/app/middleware/log_requisicao.py`.

### HIS-01.5 — Validar a fundacao do projeto

- [x] Executar checagem de consistencia do scaffold.
- [x] Garantir que o bootstrap local esteja documentado em `README.md`.
- [x] Manter o repositório pronto para evolucao por sprint.

### HIS-01.6 — Isolar dependencias e fixar versoes de requirements

- [x] Centralizar dependencias em `pyproject.toml` com versoes pinadas: core (fastapi, uvicorn, pydantic, sqlalchemy, asyncpg, redis, motor, pymongo, httpx, structlog, python-dotenv) e dev (pytest, pytest-asyncio, ruff, sqlfluff, alembic, locust, dbt-core, dbt-postgres).
- [x] Configurar venv isolado em cada servico: `api/.venv`, `healthintel_dbt/.venv`, `ingestao/.venv` — nenhuma dependencia instalada globalmente.
- [x] Formalizar targets no `Makefile`: `up` (docker compose up com servicos centrais), `dbt-build` (dbt run completo), `api-dev` (uvicorn em modo dev com reload).
- [x] Configurar `healthintel_dbt/packages.yml` com `dbt-utils`, `dbt-expectations` e `dbt-codegen` com versoes fixas.
- [x] Validar instalacao local com `pip install -e .[dev]` e testar imports.

## Validacao e Conclusao

**Data de conclusao:** 2026-04-22

**Status:** ✅ **CONCLUIDA**

### Checklist de Saida

- [x] Monorepo estruturado com todas as arvores principais criadas e congeladas.
- [x] Infraestrutura local sobe sem erros (`docker compose -f infra/docker-compose.yml up`).
- [x] Banco de dados PostgreSQL com schemas iniciais e alembic configurado.
- [x] MongoDB pronto para layouts (mongo_layout_service ativo).
- [x] Redis operacional para cache de API.
- [x] Airflow configurado para orquestracao de DAGs.
- [x] API local em :8000 com health check e auth middleware base.
- [x] Dependencias centralizadas em `pyproject.toml` com versoes pinadas.
- [x] CLAUDE.md documentando padroes e fluxos da plataforma.
- [x] README.md com instrucoes de bootstrap e makefile.
- [x] Ambiente pronto para Sprint 02 (layout registry Bronze).

### Artifacts de Sprint

| Artefato | Localizacao | Status |
|----------|-------------|--------|
| Monorepo scaffold | `/` | Congelado |
| Docker compose | `infra/docker-compose.yml` | ✅ Validado |
| Schema PostgreSQL | `infra/postgres/init/001_schemas.sql` | ✅ Ativo |
| Config centralizada | `pyproject.toml` | ✅ Pinado |
| API base | `api/app/main.py` | ✅ Health + Auth |
| Makefile | `Makefile` | ✅ Targets core |
| CLAUDE.md | `CLAUDE.md` | ✅ Documentado |
| .env exemplo | `.env` | ✅ Safe defaults |
