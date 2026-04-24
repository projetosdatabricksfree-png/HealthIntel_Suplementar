# Sprint 20 — Comercialização e Enterprise Final

**Status:** Concluída
**Objetivo:** formalizar os 5 tiers comerciais com SLAs por camada; atualizar rate limiting e billing; criar catálogo comercial; executar suite de regressão completa Fase 3; congelar baseline `v2.0.0`.
**Critério de saída:** 5 tiers operacionais com `camadas_permitidas` e `sla_*` configurados; regressão Fase 3 zero falhas; tag `v2.0.0` criada e documentada.

## Histórias

### HIS-20.1 — Tiers Comerciais Formais

- [x] Criar migration `infra/postgres/init/020_plano_tiers_fase3.sql` adicionando colunas em `plataforma.plano`:
  - `camadas_permitidas TEXT[]` — valores: `['bronze', 'prata', 'ouro']`
  - `sla_latencia_p95_ms INTEGER`
  - `sla_disponibilidade_mensal NUMERIC(5,2)` — ex: `99.90`
  - `rate_limit_por_hora INTEGER`
  - `descricao_comercial TEXT`
- [x] Inserir/atualizar os 5 planos:

  | plano | camadas_permitidas | rate_limit_por_hora | sla_latencia_p95_ms | sla_disponibilidade |
  |-------|-------------------|---------------------|---------------------|---------------------|
  | `piloto` | `['ouro']` | 100 | 500 | 99.00 |
  | `essencial` | `['ouro']` | 1000 | 200 | 99.00 |
  | `plus` | `['ouro', 'prata']` | 5000 | 200 | 99.50 |
  | `enterprise` | `['ouro', 'prata', 'bronze']` | 20000 | 150 | 99.90 |
  | `enterprise_tecnico` | `['ouro', 'prata', 'bronze']` | 0 (sem limite) | 150 | 99.90 |

- [x] Validar que `plataforma.chave_api` tem FK válida para o plano correto de cada cliente demo.

### HIS-20.2 — Rate Limiting por Tier e Camada

- [x] Atualizar `api/app/middleware/rate_limit.py`:
  - Ler `rate_limit_por_hora` de `plataforma.plano` (via cache Redis TTL 300s).
  - Plano `enterprise_tecnico` com `rate_limit_por_hora = 0` → sem limite.
  - Rate limit separado por prefixo de rota: `/v1/bronze` consome 3x; `/v1/prata` consome 2x; `/v1` (ouro) consome 1x do bucket.
- [x] Header de resposta `X-RateLimit-Remaining` e `X-RateLimit-Reset` em todas as respostas.
- [x] Teste unitário `api/tests/unit/test_rate_limit.py` validando multiplicadores por prefixo.

### HIS-20.3 — Billing por Camada

- [x] Atualizar `plataforma.log_uso`: adicionar coluna `camada TEXT` com valores `'ouro'`, `'prata'`, `'bronze'`.
- [x] Atualizar `api/app/middleware/log_requisicao.py`: inferir camada pelo prefixo da rota e registrar em `log_uso`.
- [x] Atualizar script `scripts/billing_close.py`: calcular consumo desagregado por camada para fatura.
- [x] Criar view `plataforma.vw_consumo_por_camada` agrupando `log_uso` por cliente, camada e mês.

### HIS-20.4 — Catálogo Comercial

- [x] Criar `docs/comercial/matriz_planos.md` com:
  - Tabela de planos: tier | camadas | rate limit | SLA latência | SLA disponibilidade | preço-âncora (placeholder)
  - Tabela de endpoints por tier: endpoint | plano mínimo | camada | dataset
  - Comparativo v1.0 → v2.0 (novos endpoints por tier)
- [x] Criar `docs/comercial/onboarding_enterprise.md`: guia de provisionamento de chave, configuração de plano, teste de integração.
- [x] Atualizar `GET /v1/meta/endpoints` para incluir campo `camada` (bronze/prata/ouro) e `plano_minimo` por endpoint.

### HIS-20.5 — Suite de Regressão Fase 3

- [x] Criar `testes/regressao/test_endpoints_fase3.py` cobrindo:
  - Bronze API: todos os 11 endpoints `/v1/bronze/*` com plano `enterprise_tecnico`
  - Bronze API bloqueio: HTTP 403 para plano `piloto` em `/v1/bronze/*`
  - Prata API: todos os 14 endpoints `/v1/prata/*` com plano `analitico`
  - Prata API bloqueio: HTTP 403 para plano `piloto` em `/v1/prata/*`
  - Quarentena: `/v1/prata/quarentena/resumo` com plano `analitico`
  - Score v3: `/v1/operadoras/{id}/score-v3` com plano `essencial`
  - Ranking composto: `/v1/rankings/composto` com plano `essencial`
  - Rate limit: resposta com headers `X-RateLimit-Remaining`
  - Billing: `plataforma.log_uso` com coluna `camada` preenchida
- [x] Executar `pytest testes/regressao/ -v` — zero falhas (hard gate obrigatório para aceite da sprint).

### HIS-20.6 — Baseline v2.0.0

- [x] Executar `dbt docs generate` e salvar como `docs/dbt_docs_v2.0.0.html` e `docs/dbt_catalog_v2.0.0.json`.
- [x] Atualizar `docs/CHANGELOG.md`:
  - Novos endpoints Fase 3: Bronze API (11), Prata API (14), Score v3 (2), Ranking composto (1)
  - Novos tiers: `plus`, `enterprise`, `enterprise_tecnico` com SLAs
  - Versão metodologia: `v3.0` com pesos definidos
  - Datasets adicionados: QUALISS, IEPRS (se viáveis), CNES (Sprint 13), TISS (Sprint 14)
  - Mudanças arquiteturais: quarentena real, hash bronze, `camadas_permitidas`, rate limit por camada
- [x] Criar tag git `v2.0.0-baseline` após todos os critérios de saída passarem.
- [x] Atualizar `docs/sprints/README.md` e `docs/sprints/fase3/README.md` marcando todas as sprints como Concluída.

## Entregas esperadas

- [x] DDL `infra/postgres/init/020_plano_tiers_fase3.sql`
- [x] `api/app/middleware/rate_limit.py` atualizado com multiplicadores por camada
- [x] `plataforma.log_uso` com coluna `camada`
- [x] View `plataforma.vw_consumo_por_camada`
- [x] `docs/comercial/matriz_planos.md`
- [x] `docs/comercial/onboarding_enterprise.md`
- [x] `testes/regressao/test_endpoints_fase3.py`
- [x] `docs/dbt_catalog_v2.0.0.json`
- [x] `docs/CHANGELOG.md` atualizado
- [x] Tag git `v2.0.0-baseline`

## Validação esperada

- [x] `ruff check api ingestao scripts`
- [x] `pytest testes/regressao/ -v` — zero falhas (hard gate)
- [x] `pytest api/tests/unit/test_rate_limit.py -v`
- [x] `dbt docs generate` sem erros
- [x] `plataforma.plano` contém 5 tiers com `sla_*` e `camadas_permitidas` preenchidos
- [x] Plano `piloto` não acessa `/v1/bronze/*` nem `/v1/prata/*` (HTTP 403)
- [x] Plano `enterprise_tecnico` acessa todas as camadas sem rate limit
- [x] `plataforma.log_uso` registra coluna `camada` para todas as requisições
- [x] `docs/CHANGELOG.md` contém entrada `v2.0.0` com lista completa de entregáveis
