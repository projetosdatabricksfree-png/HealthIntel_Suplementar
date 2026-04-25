# Matriz de Gaps — Entrega ao Cliente (Fase 6)

Cada gap mapeado para área, severidade, dependência, sprint sugerida, critério de aceite e risco caso não seja endereçado.
**Severidade**: `BLOQUEANTE` (impede go-live), `ALTA` (impede plano Enterprise), `MÉDIA` (limita escala/qualidade), `BAIXA` (evolução).

| # | Gap | Área | Impacto | Severidade | Dependência | Sprint | Critério de aceite | Risco se não fizer |
|---|-----|------|---------|------------|-------------|--------|---------------------|---------------------|
| G01 | Sem ambiente staging idêntico ao de prod | Infra | Releases sem rede de proteção | BLOQUEANTE | infra Docker/host | 15 | `make deploy-staging` cria ambiente espelhado, com dados sintéticos | Bug em prod sem como reproduzir |
| G02 | Sem Dockerfile de produção da API | Infra | Imagem inflada e build em runtime | BLOQUEANTE | – | 15 | `Dockerfile.api` multi-stage, image final < 250 MB, healthcheck embutido | Deploy lento, superfície de ataque ampla |
| G03 | Sem Dockerfile de produção do Layout Service | Infra | Mesmo de G02 | ALTA | G02 | 15 | `Dockerfile.layout`, image < 250 MB | Idem |
| G04 | Secrets em `.env` versionado | Segurança | Risco de vazamento | BLOQUEANTE | – | 15/19 | `.env.production` fora do git, secrets em arquivo `.env` em volume restrito ou Docker secrets | Vazamento de credencial = incidente LGPD |
| G05 | Sem TLS/HTTPS na borda | Segurança | Cliente Enterprise não aceita | BLOQUEANTE | nginx | 15 | Nginx serve `https://` com cert válido (Let's Encrypt ou corporativo) | Bloqueio de venda Enterprise |
| G06 | Sem rate limit distribuído | API | Abuso multi-instância | ALTA | redis | 16 | `slowapi` com storage Redis ou implementação custom no middleware | DoS acidental ou intencional |
| G07 | Endpoint `/v1/catalogo` ausente | API | Cliente não descobre datasets | ALTA | – | 16 | `GET /v1/catalogo` retorna lista de datasets, esquemas, freshness, plano necessário | Onboarding lento, suporte sobrecarregado |
| G08 | Endpoint `/v1/freshness` ausente | API | Cliente não confia em dado | ALTA | freshness gate | 16 | `GET /v1/freshness` por dataset retorna `_carregado_em`, `versao_dataset`, `status` | Cliente reclama de dado stale sem aviso |
| G09 | Endpoint `/v1/qualidade` ausente | API | Cliente não vê taxa_aprovacao | ALTA | macro existente | 16 | `GET /v1/qualidade?dataset=X` retorna taxa, registros em quarentena, último lote | Falta de transparência sobre qualidade |
| G10 | Erros não padronizados (sem RFC 9457) | API | Cliente não trata erro | ALTA | – | 16 | Toda resposta 4xx/5xx em formato `application/problem+json` com `type/title/status/detail/instance` | Integração frágil, suporte caro |
| G11 | Paginação não obrigatória | API | Endpoint pesado pode derrubar | ALTA | – | 16 | Lista sempre retorna `meta.pagina`, `meta.tamanho_pagina`, `meta.total`, default 100, max 1000 | OOM em endpoint sem filtro |
| G12 | Filtros e ordenação não padronizados | API | UX pobre | MÉDIA | – | 16 | `?ordenar_por=`, `?direcao=`, `?filtro_chave=valor` documentados no OpenAPI | Cliente confuso |
| G13 | OpenAPI não publicado externamente | API | BI engineer não autogera client | ALTA | – | 16/20 | OpenAPI 3.1 versionado em `https://api.healthintel.com.br/openapi.json` + ReDoc/Swagger UI público | Integração demorada |
| G14 | Sem exemplos cURL/Python/Postman | Docs | Onboarding lento | MÉDIA | – | 20 | Cada endpoint tem 3 exemplos (cURL, Python `requests`, Postman collection) | Suporte vira gargalo |
| G15 | Sem freshness gate hard de publicação | Orquestração | Dado stale chega no cliente | BLOQUEANTE | – | 17 | DAG `dag_publicacao_controlada` só promove se `taxa_aprovacao ≥ 95%` e `freshness ok` | Crise de confiança |
| G16 | Sem tabela `plataforma.publicacao` | Orquestração | Sem rastro de release | ALTA | – | 17 | DDL + DAG insere registro de cada release de dataset | Sem auditoria de publicação |
| G17 | Sem alerta de falha de ingestão | Observabilidade | Equipe descobre tarde | ALTA | – | 17/18 | Webhook Slack/email em falha de qualquer DAG | Incidente sem comunicação |
| G18 | Logs sem `request_id`/`tenant_id` estruturado | Observabilidade | Debug caro | ALTA | – | 18 | Todo log JSON com `request_id`, `tenant_id`, `endpoint`, `latencia_ms` | Suporte gasta horas em incidente |
| G19 | Sem métricas Prometheus | Observabilidade | Sem dashboard | ALTA | – | 18 | `/metrics` Prometheus expõe RPS, latência p50/p95/p99, 4xx/5xx | Sem visibilidade técnica |
| G20 | Sem dashboard Grafana | Observabilidade | Métrica sem visualização | MÉDIA | G19 | 18 | Dashboard `healthintel_api` com 8 painéis | Time fica reativo |
| G21 | Sem alertas de SLO | Observabilidade | Fora do SLA sem aviso | ALTA | G19 | 18 | Alerta `latencia_p95 > 800ms 5min` e `5xx > 1% 5min` | Cliente avisa antes da equipe |
| G22 | Sem error tracking (Sentry-like) | Observabilidade | Erros perdidos | MÉDIA | – | 18 | Stack traces enviados a Sentry self-hosted ou Glitchtip | Bug latente em prod |
| G23 | Sem uptime externo | Observabilidade | Detecção tardia de outage | ALTA | – | 18 | Probe externo a `/saude` a cada 60s | SLA furado sem registro |
| G24 | Sem backup automatizado de Postgres | Infra | Perda total em incidente | BLOQUEANTE | – | 15/19 | Job diário pgBackRest ou `pg_basebackup` em storage off-host com retenção 30d | Game over |
| G25 | Sem teste de restore | Infra | Backup que não restaura | BLOQUEANTE | G24 | 15/19 | Runbook executado mensalmente em staging | Backup virtual |
| G26 | Sem rotação de secrets | Segurança | Credencial vaza fica eterna | ALTA | – | 19 | Runbook + DAG mensal de rotação | LGPD/SOC2 reprovam |
| G27 | Sem mascaramento de CPF/CNPJ em log | Segurança | LGPD | BLOQUEANTE | – | 19 | Filtro de log `mascara_documento` aplicado em handler de erro | Multa LGPD |
| G28 | Sem auditoria de acesso por chave | Segurança | Sem rastro forense | ALTA | logs estruturados | 19 | Tabela `plataforma.audit_log` com (api_key_id, endpoint, ip, hora, status) | Sem resposta a incidente |
| G29 | Sem bloqueio por inadimplência | Billing | Cliente devedor consome | ALTA | billing existente | 19 | `validar_chave` checa `cliente.status='ativo'` | Receita perdida |
| G30 | Sem aviso de aproximação de quota | Billing | Surpresa de bloqueio | MÉDIA | quota | 19 | Webhook a 80%/90%/100% | Atrito comercial |
| G31 | Sem `/v1/portal/usage` | Portal | Cliente não acompanha | ALTA | – | 19/20 | Endpoint retorna consumo por dia/endpoint/competência | Suporte recebe pergunta diária |
| G32 | Sem `/v1/portal/me` | Portal | Cliente não vê plano | MÉDIA | – | 19/20 | Endpoint retorna plano, camadas, limite, vencimento | UX pobre |
| G33 | Sem rotação self-service de API key | Portal | Suporte manual em cada cliente | MÉDIA | – | 19/20 | `POST /v1/portal/api-keys/rotate` | Esforço manual desnecessário |
| G34 | Sem sandbox com dados sintéticos | Onboarding | Cliente testa em prod | ALTA | – | 20 | Banco separado `healthintel_sandbox` com seeds determinísticos + chaves sandbox `_sbx_` | Métricas de prod poluídas |
| G35 | Sem checklist de homologação | Onboarding | Cliente sobe sem validar | MÉDIA | – | 20 | Doc + script `verificar_homologacao_cliente.py` que executa 8 chamadas-chave | Cliente quebra em prod |
| G36 | Sem termo de aceite técnico digital | Onboarding | Sem registro de SLA aceito | ALTA | – | 20 | Tabela `plataforma.aceite_tecnico` + DAG/endpoint para registro | Disputa contratual |
| G37 | Sem FAQ técnica pública | Onboarding | Suporte vira FAQ | BAIXA | – | 20 | `docs/produto/faq.md` + publicação | Suporte caro |
| G38 | Sem catálogo de datasets em JSON | Docs | BI engineer pula docs | MÉDIA | catálogo existe | 20 | `docs/produto/catalogo_datasets.json` machine-readable | Auto-discovery falha |
| G39 | Sem dicionário de campos por endpoint | Docs | Cliente interpreta errado | ALTA | OpenAPI | 20 | `docs/produto/dicionario_campos.md` com nome, tipo, unidade, exemplo, valores possíveis | Interpretação errada de KPI |
| G40 | Sem guia por persona (hospital/broker/analista) | Docs | Onboarding genérico | MÉDIA | – | 20 | 4 guias separados em `docs/produto/guia_*.md` | Vendas perde foco |
| G41 | API single-instance | Escala | Falha total se cair | ALTA | docker compose | 15 | 2+ réplicas atrás de Nginx, com health-check | Outage = downtime total |
| G42 | Sem PgBouncer | Escala | Pool exhaustion | MÉDIA | – | 15 | PgBouncer em transaction pooling, 200 client → 25 server | API trava sob carga |
| G43 | Sem read replica de Postgres | Escala | Read crítico em master | BAIXA | – | futuro | Doc + sizing previsto | Latência alta em pico |
| G44 | Cache Redis sem persistência | Escala | Perde TTL no restart | BAIXA | – | 15 | Redis com `appendonly yes` ou snapshot 5min | Picos pós-restart |
| G45 | Sem retenção de `bruto_ans` | Escala | Banco infla | MÉDIA | – | 17 | Política: arquiva partição > 36 meses para storage frio | Custo de disco cresce |
| G46 | Sem rollback de release documentado | Operação | Bug em prod fica até hotfix | BLOQUEANTE | imagens versionadas | 15/21 | Runbook `rollback_api.md` + tag git anterior + script `make rollback VERSION=` | MTTR alto |
| G47 | Sem versionamento de OpenAPI por release | API | Cliente não sabe se mudou | ALTA | – | 16 | `openapi.json` salvo em `docs/api/openapi-vX.Y.Z.json` por tag | Quebra silenciosa |
| G48 | Sem teste de carga em CI | Qualidade | Performance regride | MÉDIA | locust | 18 | `make load-test-baseline` rodado a cada release | Regressão silenciosa |
| G49 | Sem suite de regressão de endpoints Fase 1–5 | Qualidade | Mudança quebra contrato | ALTA | testes existentes | 21 | `pytest testes/regressao/test_endpoints_fase1_a_5.py` zero falhas | Quebra de contrato |
| G50 | Sem runbooks operacionais consolidados | Operação | Sem playbook em incidente | ALTA | runbooks existentes | 18/21 | 8 runbooks: deploy, rollback, restore, freshness incident, rate-limit incident, leak suspect, novo cliente, billing close | Pessoa-chave fica gargalo |

## Resumo por severidade

- **BLOQUEANTES** (8): G01, G02, G04, G05, G15, G24, G25, G27, G46.
- **ALTA** (24).
- **MÉDIA** (12).
- **BAIXA** (3).

## Resumo por sprint

- **Sprint 14** — diagnóstico, mapa, congelamento de baseline (apoia este documento, sem gaps próprios).
- **Sprint 15** — G01, G02, G03, G04, G05, G24, G25, G41, G42, G44, G46.
- **Sprint 16** — G06, G07, G08, G09, G10, G11, G12, G13, G47.
- **Sprint 17** — G15, G16, G17, G45.
- **Sprint 18** — G18, G19, G20, G21, G22, G23, G48, G50 (parcial).
- **Sprint 19** — G04 (final), G24/G25 (validação), G26, G27, G28, G29, G30, G31, G32, G33.
- **Sprint 20** — G14, G31/G32/G33 (UI), G34, G35, G36, G37, G38, G39, G40.
- **Sprint 21** — G46 (executar), G49, G50 (consolidar) + hardgate completo.
