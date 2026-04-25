# Arquitetura Operacional de Produção — Fase 6

Define onde cada peça do HealthIntel Suplementar roda em produção, como é separada de dev/staging, como secrets são protegidos e como uma nova versão é publicada sem quebrar cliente.

## 1. Visão geral (topologia alvo)

```
                          INTERNET
                              │
                              │ HTTPS 443
                              ▼
                  ┌───────────────────────┐
                  │   NGINX (TLS + WAF)   │  ← Let's Encrypt ou cert corporativo
                  │  /v1/*  /openapi.json │  rate-limit borda, security headers
                  │  /portal/*            │
                  │  /docs (ReDoc)        │
                  └──────────┬────────────┘
                             │ HTTP interno
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │  API #1  │   │  API #2  │   │  API #N  │   uvicorn workers
        │ FastAPI  │   │ FastAPI  │   │ FastAPI  │   (image vX.Y.Z)
        └────┬─────┘   └────┬─────┘   └────┬─────┘
             │              │              │
             ├──────────────┼──────────────┤
             ▼              ▼              ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │  REDIS   │   │ PgBouncer│   │  MONGO   │
        │  cache   │   │  pool    │   │ layouts  │
        │ rate-lim │   └────┬─────┘   └──────────┘
        └──────────┘        │
                            ▼
                      ┌──────────┐
                      │POSTGRES16│  ← PRIMARY (read+write)
                      │  prod    │
                      └────┬─────┘
                           │ wal-shipping/pgBackRest
                           ▼
                    ┌─────────────┐
                    │ Backup S3/  │
                    │  storage    │
                    │  off-host   │
                    └─────────────┘

PIPE OFFLINE (Airflow + dbt) ────► escreve em bruto_ans, stg, int, nucleo
PIPE PUBLICACAO (DAG controlada) ─► promove para api_ans + consumo_ans
                                    SOMENTE após hardgate passar
```

## 2. Onde cada peça roda

| Peça | Onde roda | Tipo | Acesso externo |
|------|-----------|------|----------------|
| API REST | Container `healthintel_api` | stateless, N réplicas | via Nginx (HTTPS) |
| Layout Service | Container `healthintel_layout` | stateless, 1–2 réplicas | só interno |
| PostgreSQL | Container `healthintel_postgres` | stateful, 1 primário | só interno via PgBouncer |
| MongoDB | Container `healthintel_mongo` | stateful, 1 nó | só interno |
| Redis | Container `healthintel_redis` | stateful, 1 nó com AOF | só interno |
| PgBouncer | Container `healthintel_pgbouncer` | stateless | só interno |
| Nginx | Container `healthintel_nginx` | stateless | borda 443 |
| Airflow scheduler/webserver/worker | Containers `healthintel_airflow_*` | parcialmente stateful (db meta no Postgres) | webserver atrás de auth/SSO |
| dbt | Executa dentro do container Airflow worker (Cosmos) | stateless | n/a |
| Jobs ELT (`elt_*`) | Container Airflow worker via DAG | stateless | n/a |
| Frontend portal (SPA) | Container Nginx servindo build estático | stateless | borda 443 (host separado opcional) |

## 3. Onde ficam os arquivos brutos ANS

- **Storage primário**: bucket S3-compatible (MinIO self-hosted ou AWS S3) `s3://healthintel-bruto/{dataset}/{competencia}/{arquivo}`.
- **Cache local**: volume `./infra/data/bruto_cache/` no host do worker, limpo automaticamente após carga + checksum.
- **Não armazenar bruto em Postgres**; só hash, layout-id, lote-id e linhas estruturadas.
- **Retenção**: 36 meses no S3, depois arquivar em `glacier`/`cold storage`.

## 4. Onde ficam logs e métricas

| Tipo | Destino | Retenção |
|------|---------|----------|
| Logs estruturados (API/Airflow/Layout) | `stdout` JSON → **Loki** ou **journald → Vector → S3** | 30d quente, 1 ano frio |
| Métricas Prometheus | `/metrics` em cada serviço → **Prometheus** | 15d local, agrupados em VictoriaMetrics ou Mimir |
| Dashboards | **Grafana** | indefinido (versionado em `infra/grafana/dashboards/`) |
| Alertas | Alertmanager → Slack/email/webhook | 90d histórico |
| Tracing | **Tempo** (opcional, fase futura) | 7d |
| Error tracking | **Glitchtip** ou **Sentry self-hosted** | 90d |
| Audit log de acesso | Tabela `plataforma.audit_log` no Postgres | 12 meses |

## 5. Onde ficam backups

| Item | Origem | Frequência | Retenção | Destino |
|------|--------|-----------|----------|---------|
| Postgres `healthintel` | pgBackRest full+incremental | diário full + horário incremental | 30 dias quente, 90 dias frio | S3 off-host |
| Postgres WAL | streaming | contínuo | 7 dias | S3 |
| Mongo `healthintel_layout` | `mongodump` | diário | 30 dias | S3 |
| Configurações Airflow (DB meta) | snapshot | diário | 14 dias | S3 |
| Imagens Docker | registry | a cada release | indefinido | container registry privado |
| Manifests dbt (`docs/dbt_*`) | tag git | a cada release | indefinido | git + S3 |

## 6. Separação de ambientes

| Ambiente | Host | Banco | Domínio | Dado real |
|----------|------|-------|---------|-----------|
| **Local** | máquina do dev | `healthintel_local` (volume) | `localhost` | seeds demo |
| **Dev integrado** | VM/host de dev | `healthintel_dev` | `dev.healthintel.internal` | seeds + amostra ANS |
| **Staging** | host idêntico ao prod | `healthintel_staging` | `staging.healthintel.com.br` | dado real reduzido (1 UF, 6 competências) |
| **Produção** | host de prod | `healthintel_prod` | `api.healthintel.com.br` | dado real completo |
| **Sandbox cliente** | host de prod (banco separado) | `healthintel_sandbox` | `sandbox.healthintel.com.br` | dado sintético determinístico |

Regras:
- Cada ambiente tem container registry tag distinto: `:dev`, `:staging`, `:vX.Y.Z`.
- Cada ambiente tem `.env` próprio em `infra/env/{ambiente}.env`, **fora do git**.
- Promoção: `dev` → `staging` (manual após CI verde) → `prod` (manual após smoke staging).
- Sandbox espelha contrato de produção, mas com seeds; tem reset semanal.

## 7. Como proteger secrets

- **Não-objetivo**: rodar Vault na Fase 6. Solução enxuta primeiro.
- **`.env` de produção**: fora do git, chmod 0600, dono `healthintel`, montado read-only em containers.
- **Secrets sensíveis** (`POSTGRES_PASSWORD`, `MONGO_PASSWORD`, `API_JWT_ADMIN_SECRET`, `LAYOUT_SERVICE_TOKEN`, `AIRFLOW_FERNET_KEY`): preferir **Docker secrets** (`docker compose --secrets` ou `compose-spec` v3.7+).
- **API keys de cliente**: já estão hash em `plataforma.api_key.chave_hash`. Manter assim.
- **Rotação**: scripts `scripts/admin/rotacionar_secret.py` para Postgres, Mongo, Redis. Executar a cada 90 dias.
- **Auditoria**: registro de quem rotacionou em `docs/runbooks/log_rotacao_secrets.md`.

## 8. Como publicar nova versão sem quebrar cliente

### 8.1 Pipeline de release

1. Merge para `main` com PR aprovado.
2. CI roda: `ruff`, `sqlfluff`, `pytest`, `dbt compile`, `dbt test`.
3. Tag git `vX.Y.Z` dispara build de imagens.
4. Imagens publicadas no registry com tags `:vX.Y.Z` e `:staging`.
5. Deploy automatizado em staging.
6. **Smoke staging** roda: `make smoke`, `make smoke-prata`, `make smoke-consumo`, `pytest testes/regressao/`.
7. Aprovação manual no console de release.
8. Imagens recebem tag `:vX.Y.Z` e `:prod`.
9. **Deploy blue-green em prod**: nova versão sobe em paralelo (`api_blue`/`api_green`), Nginx aponta gradualmente.
10. **Smoke prod** com chave sintética.
11. Promote: Nginx aponta 100% para nova versão; antiga fica de standby por 24h.
12. Tag versionada no OpenAPI: `docs/api/openapi-vX.Y.Z.json` commitado.

### 8.2 Rollback

- Se métricas regredirem (5xx > 1% por 5 min, latência p95 > 800ms por 10 min), Nginx aponta de volta em < 30s.
- `make rollback VERSION=vX.Y.Z-1` aplica imagens anteriores.
- Postgres não rola back automaticamente; migrations devem ser **forward-compatible** (additive only durante Fase 6).

### 8.3 Migrations de banco

- **Regra de ouro**: nenhuma migration destrutiva (DROP COLUMN, RENAME) em release direto.
- Migration destrutiva é dividida em 2 releases: (1) deprecate + parar uso; (2) drop após 30 dias.
- Migrations rodam em transação; falha = abort + alerta.
- Histórico em `infra/postgres/migrations/V{n}__descricao.sql` ou `alembic`.

### 8.4 Versionamento de endpoint

- Endpoints atuais permanecem em `/v1/*` byte-idênticos.
- Quebra contratual exige `/v2/*` novo.
- `Sunset` header anuncia data de deprecação ≥ 180 dias antes.
- Histórico de versões em `docs/produto/versionamento_api.md`.

## 9. Recursos críticos por persona

| Persona | Recurso técnico crítico em prod |
|---------|---------------------------------|
| Hospital | `mart_operadora_360`, `score_v3`, `tiss`, `regulatorio_v2` em `api_ans` com freshness D+1 |
| Agência regulatória | `regulatorio_v2`, `mercado`, `ranking` com série histórica completa |
| Analista / BI engineer | Acesso direto a `consumo_ans` via Postgres + API completa com OpenAPI estável |
| Corretora pequena | `cnes`, `mercado`, `ranking` (Starter) |
| Corretora média | + `mart_score_operadora`, `mart_mercado_municipio` (Professional) |
| Corretora grande | + `/v1/premium/*`, MDM público + privado, contrato/subfatura por tenant (Enterprise) |

## 10. Resumo de portas em produção

| Porta | Serviço | Exposição |
|-------|---------|-----------|
| 443 | Nginx (TLS) | Internet |
| 80 | Nginx (redirect 443) | Internet |
| 8000 | API | só rede interna |
| 8001 | Layout Service | só rede interna |
| 8088 | Airflow webserver | só rede interna ou via VPN |
| 5432 | Postgres | só rede interna |
| 6432 | PgBouncer | só rede interna |
| 27017 | MongoDB | só rede interna |
| 6379 | Redis | só rede interna |
| 9090 | Prometheus | só rede interna |
| 3000 | Grafana | só rede interna ou via VPN |

## 11. Decisões adiadas (futuro pós-`v4.0.0`)

- Multi-AZ Postgres com replica.
- Kubernetes (hoje docker-compose é suficiente para MVP comercial).
- HashiCorp Vault para secrets.
- WAF dedicado (Cloudflare/Imperva).
- Read-replica para BI engineers heavy users.
- Federação de identidade SSO (SAML/OIDC) para portal.
