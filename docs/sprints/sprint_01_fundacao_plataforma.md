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
