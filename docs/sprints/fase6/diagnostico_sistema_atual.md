# Diagnóstico do Sistema Atual — Fase 6

Estado do HealthIntel Suplementar antes da Fase 6, separado por área.
Origem: leitura de `README.md`, `CLAUDE.md`, `infra/docker-compose.yml`, `Makefile`, `api/app/`, `healthintel_dbt/models/`, `ingestao/dags/`, `docs/sprints/fase{1..5}/`, `docs/comercial/`, `docs/runbooks/`, `pyproject.toml`.

## 1. O que já existe e está pronto

### 1.1 Camada de dados (medallion)
- `bruto_ans` com tabelas particionadas RANGE por competência/trimestre para CADOP, SIB, IGR, NIP, RN623, IDSS, TISS, CNES, DIOPS, FIP, Glosa, VDA, Rede Assistencial, Regime Especial, Portabilidade, Prudencial, Taxa de Resolutividade.
- `stg_ans`: views de normalização e cast.
- `int_ans`: ephemerals para enrich/derivação.
- `nucleo_ans`: dimensions (`dim_*`) e facts (`fat_*`) consolidados.
- `nucleo_ans` Gold marts BI: `mart_operadora_360`, `mart_mercado_municipio`, `mart_score_operadora`, `mart_rede_assistencial`, `mart_regulatorio_operadora`, `mart_tiss_procedimento`.
- `api_ans`: 11 modelos Bronze API + 17 modelos Prata API.
- `consumo_ans`: 8 modelos desnormalizados para entrega direta a BI/analista (role `healthintel_cliente_reader`).
- `plataforma`: clientes, planos, API keys, billing, jobs, dataset_versao, lote_ingestao, log_uso.

### 1.2 API REST
- FastAPI, Pydantic v2, envelope `{dados, meta}`.
- Rotas: `operadora`, `mercado`, `ranking`, `regulatorio`, `regulatorio_v2`, `financeiro`, `financeiro_v2`, `rede`, `cnes`, `tiss`, `meta`, `admin_billing`, `admin_layout`, `bronze`, `prata`.
- Middlewares: `autenticacao` (X-API-Key + Redis cache TTL 60s), `rate_limit` (SlowAPI), `hardening` (security headers), `log_requisicao`.
- Dependências: `validar_chave`, `verificar_plano`, `verificar_camada('bronze'|'prata')`.
- Score v3 implementado (`fat_score_v3_operadora_mensal` + endpoint).
- 5 planos comerciais com `camadas_permitidas TEXT[]`.

### 1.3 Ingestão
- Airflow 2.9 + astronomer-cosmos.
- DAG mestre mensal + DAGs individuais por dataset.
- Ingestão real para SIB e CADOP.
- Quarentena semântica por dataset.
- Hash bronze, freshness via `_sources.yml`, macro `taxa_aprovacao_dataset`.
- Scripts ELT genéricos (`elt_discover`, `elt_extract`, `elt_load`).

### 1.4 Governança
- Versionamento de layout em MongoDB.
- DAG `dag_registrar_versao` para registro de versão.
- DAG `dag_dbt_freshness` para freshness check.
- DAG `dag_dbt_consumo_refresh` para refresh do schema `consumo_ans`.

### 1.5 Cliente / monetização (existente)
- `plataforma.cliente`, `plataforma.api_key`, `plataforma.plano`, `plataforma.contrato`, `plataforma.fatura`.
- Script `provisionar_cliente_postgres.py` para criar role de cliente em `consumo_ans`.
- Pipeline de billing mensal (`make billing-close REF=YYYYMM`).

### 1.6 Frontend portal (em construção)
- React 19 + Vite 7 SPA em `frontend/healthintel_frontend_portal/`.
- Login via X-API-Key + playground de endpoints.
- Não está em deploy de produção.

## 2. O que está pronto, mas só para ambiente local

- `infra/docker-compose.yml` levanta Postgres 16, Mongo 7, Redis 7, Airflow, Nginx, API, Layout Service.
- Faltam imagens próprias de produção (atualmente usa `python:3.12-slim` cru com `pip install -e .` em runtime).
- Sem Dockerfile dedicado para API e Layout Service.
- Sem proxy reverso configurado para HTTPS externo (Nginx só serve frontend interno).
- Secrets em `.env` checkado no git (valores default safe-for-local).

## 3. O que ainda é risco para go-live

- **Sem ambiente staging** equivalente ao de produção; teste de release acontece no mesmo ambiente.
- **Sem pipeline CI/CD** que faça deploy automatizado por tag (somente `make ci-local`).
- **Sem plano de rollback documentado** para deploy quebrado.
- **Sem backup automatizado de Postgres em produção**; só dump manual em dev.
- **Sem teste de restore** validado.
- **Sem rotação de secrets** documentada; credenciais Mongo/Postgres/Airflow vivem em `.env`.
- **Sem TLS/HTTPS ativo**; Nginx hoje serve HTTP local.
- **Sem WAF / proteção DDoS** na borda.
- **Rate limit** por chave em SlowAPI in-memory (não compartilhado entre réplicas).
- **Cache Redis** sem persistência configurada (perde TTL no restart).

## 4. O que falta para cliente consumir sem erro

| Lacuna | Impacto |
|--------|---------|
| Endpoint `/v1/catalogo` que liste datasets, esquemas e freshness | Cliente não descobre o que pode consumir |
| Endpoint `/v1/qualidade` que exponha `taxa_aprovacao` por dataset/lote | Cliente não confia no dado sem visibilidade |
| Endpoint `/v1/freshness` por dataset | Cliente não sabe se dado está atualizado |
| Erros padronizados (problem+json RFC 9457) | Cliente não consegue tratar erro programaticamente |
| Paginação obrigatória em todos endpoints com lista | Endpoint pesado pode derrubar API |
| Filtros padronizados (operadora, competência, UF, modalidade) | Cliente faz pull massivo desnecessário |
| OpenAPI 3.1 publicado e versionado | Sem doc machine-readable, integração lenta |
| Exemplos cURL/Python/Postman por endpoint | Onboarding do BI engineer trava |
| Sandbox com dados sintéticos | Cliente novo testa em prod, polui métricas |
| Rate limit distribuído (Redis) | Réplica de API ignora limite imposto na outra |

## 5. O que falta para operação recorrente

- Job de freshness com **bloqueio de publicação** se dataset estiver stale (quality gate hard).
- Job de **publicação controlada**: dbt build → testes → smoke → promote para `api_ans`/`consumo_ans` em transação.
- Tabela `plataforma.publicacao` com histórico de releases de dado.
- Alertas quando ingestão falha (Slack/email/webhook).
- Reprocessamento idempotente com `lote_ingestao_id`.
- Retenção configurada para `bruto_ans` (hoje cresce indefinidamente).

## 6. O que falta para suporte comercial

- Endpoint `/v1/portal/me` (cliente consulta seu próprio plano e consumo).
- Endpoint `/v1/portal/usage` (consumo por dia, por endpoint).
- Endpoint `/v1/portal/api-keys` (rotação self-service).
- Bloqueio automático por inadimplência (faturamento integrado a status de cliente).
- Aviso de aproximação de limite via webhook.
- Sandbox com dados sintéticos em conta separada.
- Contratos de SLA assinados.
- Termo de uso e LGPD assinados (registro de aceite).

## 7. O que falta para segurança

- TLS/HTTPS em toda camada externa (Nginx + Let's Encrypt ou certificado corporativo).
- Mascaramento de CPF/CNPJ em logs (hoje pode vazar em log de erro).
- Rotação automática de API keys e secrets.
- Auditoria estruturada de acesso por chave.
- Política de retenção de logs alinhada à LGPD.
- Hardening de Postgres: `pg_hba.conf` restrito, `ssl=on`, `password_encryption=scram-sha-256`.
- Hardening de Mongo: TLS, RBAC restrito, `bind_ip` restrito.
- Hardening de Redis: ACL + senha + `bind` restrito + TLS interno.

## 8. O que falta para escala

- API hoje roda em uma instância única (sem horizontal scaling).
- Sem load balancer com health-check ativo.
- Sem connection pool (PgBouncer) na frente do Postgres.
- Cache Redis sem cluster nem failover.
- Sem CDN para respostas estáticas (catálogo, OpenAPI).
- Sem rate limit distribuído (multi-instância).
- Postgres single-node, sem read replica.
- Airflow single-node com `LocalExecutor`.

## 9. O que falta para monitoramento

- **Logs estruturados** estão parciais (`shared/logging`); falta padronizar `request_id`, `tenant_id`, `latência`.
- **Métricas Prometheus** ausentes.
- **Dashboard Grafana** não existe.
- **Alertas** não existem (sem PagerDuty/Slack/email).
- **Tracing distribuído** ausente.
- Sem **error tracking** (Sentry/equivalente).
- Sem **uptime check externo** (StatusCake, UptimeRobot, Datadog Synthetics).

## 10. O que falta para billing/rate limit

- Rate limit hoje é por chave individual em memória; sem **quota mensal**.
- Sem **bloqueio por excedente**.
- Sem aviso a 80%/90%/100% do limite.
- Faturamento mensal não bloqueia chave inadimplente.
- Sem registro de billing exportável (CSV/PDF).
- Sem endpoint para cliente baixar a própria fatura.

## 11. O que falta para documentação de API

- OpenAPI gerado pelo FastAPI mas não publicado externamente.
- Sem versionamento explícito do schema (sem `info.version` por release).
- Sem dicionário de campos por endpoint formalizado.
- Sem catálogo de datasets em formato consumível (JSON e Markdown).
- Sem exemplos curados por persona (hospital × analista × corretora).

## 12. O que falta para onboarding

- Sem fluxo automatizado: criar cliente → gerar key → enviar e-mail → registrar aceite → liberar.
- Sem ambiente sandbox com dados sintéticos.
- Sem checklist de homologação (5 endpoints, OK/erro, plano correto, freshness ok).
- Sem termo técnico de aceite digital.
- Sem FAQ pública.
- Sem guia de integração por persona.

## 13. Riscos críticos consolidados

1. **Cliente em produção sem backup testado** = perda de dados em incidente.
2. **API exposta sem TLS** = bloqueio de auditoria de cliente Enterprise.
3. **Sem staging** = release publica direto em prod sem rede de proteção.
4. **Sem rate limit distribuído** = abuso multi-instância passa.
5. **Sem freshness gate hard** = cliente recebe dado stale acreditando estar fresco.
6. **Logs com CPF/CNPJ** = não-conformidade LGPD.
7. **Secrets em `.env` versionado** = vazamento se repo virar público.
8. **Sem rollback** = bug em release fica em prod até hotfix manual.

## 14. Premissas para Fase 6

- A Fase 6 **não escreve novo modelo de dado**: só operacionaliza a entrega.
- Toda mudança de runtime deve ser reversível em ≤ 30 minutos.
- Cliente piloto roda 14 dias antes do `v4.0.0` ser taggeado.
- Sandbox e produção são banco/instância separados (zero contaminação).
