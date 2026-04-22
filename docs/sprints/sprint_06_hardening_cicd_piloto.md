# Sprint 06 — Hardening, CI/CD e Piloto

**Status:** Concluida
**Objetivo:** preparar o produto para operacao controlada com qualidade, carga e governanca de deploy.
**Criterio de saida:** staging repetivel, carga validada e runbooks operacionais prontos.

## Historias

### HIS-06.1 — Automatizar validacao do repositorio

- [x] Criar pipeline CI para lint, testes e validacoes dbt.
- [x] Adicionar verificacao de `docker compose config`.
- [x] Publicar criterios de bloqueio de merge.

### HIS-06.2 — Medir capacidade e performance

- [x] Criar cenarios Locust para endpoints MVP.
- [x] Medir latencia `p95` da API com e sem cache.
- [x] Registrar baseline de capacidade por plano.

### HIS-06.3 — Endurecer operacao

- [x] Formalizar `SLO` e `SLA`.
- [x] Revisar limites operacionais de upload e parse.
- [x] Fechar padroes de seguranca de segredos e ambientes.

### HIS-06.4 — Publicar runbooks

- [x] Criar runbook de subida de ambiente.
- [x] Criar runbook de cadastro e aprovacao de layout.
- [x] Criar runbook de reprocessamento e tratamento de erro.

### HIS-06.5 — Executar piloto controlado

- [x] Preparar ambiente de staging.
- [x] Rodar smoke test fim a fim.
- [x] Fechar checklist de readiness para design partners.

## Entregas implementadas

- [x] Criar `.github/workflows/ci.yml`.
- [x] Criar `.github/workflows/load-test.yml`.
- [x] Criar `.sqlfluff` com `templater = dbt`.
- [x] Implementar `GET /prontidao` na API publica.
- [x] Implementar `GET /prontidao` no `mongo_layout_service`.
- [x] Proteger o layout registry com `X-Service-Token`.
- [x] Endurecer `infra/nginx/nginx.conf` com headers e limites.
- [x] Criar `scripts/run_load_test.sh`.
- [x] Criar `scripts/smoke_piloto.py`.
- [x] Publicar runbooks em `docs/runbooks/`.
- [x] Publicar baseline e readiness em `docs/operacao/`.

### HIS-06.6 — Completar hardening de autenticacao e contrato de seguranca

- [ ] Verificar que `api/app/middleware/autenticacao.py` implementa cache Redis com TTL 60s para hash de chave antes de consultar `plataforma.chave_api` — evitar query PostgreSQL por request (PRD secao 9.2).
- [ ] Verificar que `dependencia.py` implementa `verificar_plano()` validando `endpoint_permitido` do plano do cliente em cada request autenticado (PRD secao 9.2).
- [ ] Documentar SLO dos endpoints MVP em `docs/operacao/slo_mvp.md`: latencia p95 < 200ms, disponibilidade 99,5%/mes por endpoint (PRD secao 9.3).
- [ ] Garantir que CI em `.github/workflows/ci.yml` inclui passo `dbt compile` e validacao de `sqlfluff` nos modelos alterados (PRD secao 14.1 criterios de pronto).
