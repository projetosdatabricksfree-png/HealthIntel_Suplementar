---
name: healthintel-observability-billing-ops
description: Operação, observabilidade, métricas de uso, billing e alertas — observabilidade como proteção comercial do DaaS.
---

# HealthIntel — Observabilidade, Billing e Operação

## Quando usar esta skill

- Ao mexer em logging estruturado (structlog), métricas, dashboards operacionais ou alertas.
- Ao trabalhar em billing (`api/app/services/billing.py`, `make billing-close REF=YYYYMM`, router `admin_billing`).
- Ao definir o que entra em `plataforma.log_uso` e como é consumido por auditoria, suporte e cobrança.
- Ao definir SLOs/SLAs de freshness, ingestão, latência ou qualidade.

## Regras obrigatórias

1. Registrar **uso por cliente, endpoint, volume, plano e janela de tempo** em `plataforma.log_uso`. Sem isso, billing e proteção comercial ficam cegos.
2. **Billing deve refletir o contrato**: planos, requests, queries, volume retornado, camada acessada (Bronze/Prata/Ouro/Consumo/Premium), janela do ciclo (`REF=YYYYMM`).
3. Logs estruturados (structlog) alimentam **auditoria, suporte e cobrança** simultaneamente. Não logar payload integral; logar identificadores, contagens, latência, plano, status.
4. Métricas mínimas a manter visíveis:
   - **requests por cliente** (volume e ritmo),
   - **linhas retornadas** (proxy de volume entregue, base de billing por volume),
   - **latência** (p50/p95/p99 por endpoint),
   - **erros** (4xx/5xx por endpoint e por cliente),
   - **consumo por plano** (Standard / Analítico / Enterprise / Premium),
   - **jobs executados** (DAGs Airflow, status `plataforma.job`, lote),
   - **freshness dos dados** (último `_carregado_em` por dataset; SLO por fonte).
5. Observabilidade **não é dashboard bonito**. É:
   - **proteção comercial** (detecta abuso, scraping, dump tentado),
   - **operação do DaaS** (ingestão saudável, qualidade no contrato, freshness no SLO),
   - **base contábil** (billing reproduzível e auditável a partir de logs).
6. Alertas devem priorizar, em ordem:
   - **indisponibilidade** (API/Postgres/Redis/Mongo down),
   - **abuso** (sinais de scraping, padrão de dump, picos anômalos por chave),
   - **falha de ingestão** (`plataforma.job` em erro; lote travado; quarentena explodiu),
   - **quebra de qualidade** (testes dbt críticos falhando; `taxa_aprovacao` despencando),
   - **freshness vencido** (dataset além do SLO declarado em `_sources.yml`).
7. Billing fecha por ciclo (`REF=YYYYMM`). O fechamento precisa ser **idempotente** e **reproduzível** a partir de `plataforma.log_uso` + planos vigentes — não a partir de cálculo ad-hoc.
8. Toda mudança em billing ou em log de uso é mudança sensível: **rastrear migration, versão, e impacto em ciclos abertos**.

## Anti-padrões

- Logar payload completo (vazamento de dado e custo de armazenamento).
- Métrica que existe só no dashboard e não em log persistido (não dá para reauditar depois).
- Alerta para tudo (cansaço operacional) ou alerta para nada (ninguém é avisado quando freshness estoura).
- Billing calculado a partir de “o que o cliente disse que consumiu” em vez de `plataforma.log_uso`.
- Fechar ciclo `REF=YYYYMM` antes de garantir que todos os logs daquele período foram persistidos.
- Tratar observabilidade como “feature visual” em vez de mecanismo de defesa do produto.
- Mascarar erros (engolir 500 com 200 + `dados: []`) para “limpar o painel”.
- Acoplar billing a uma métrica volátil (ex.: latência) em vez de a contadores estáveis (requests, linhas, plano, camada).

## Checklist antes de concluir

- [ ] `plataforma.log_uso` recebe cliente, endpoint, plano/camada, timestamp, volume e latência?
- [ ] Métricas-chave (requests, linhas, latência, erros, plano, jobs, freshness) estão sendo coletadas?
- [ ] Há alerta acionável (não só log) para indisponibilidade, abuso, falha de ingestão, qualidade e freshness?
- [ ] Billing do ciclo é reproduzível a partir de `plataforma.log_uso` + planos?
- [ ] `make billing-close REF=YYYYMM` é idempotente e auditável?
- [ ] Logs não vazam payload sensível?
- [ ] Erros são reportados como erros (não mascarados em respostas “verdes”)?
- [ ] Sinais de abuso conectam-se à skill `healthintel-commercial-protection-security` (throttle/bloqueio/alerta)?

## Exemplo de prompt de uso

> “Vou implementar fechamento de ciclo `REF=202604` e auditoria por cliente/camada.
> Aplique a skill `healthintel-observability-billing-ops` e me oriente:
> (1) que campos `plataforma.log_uso` deve ter para sustentar billing por camada (Bronze 3×/Prata 2×/Ouro 1×/Consumo/Premium),
> (2) como garantir idempotência do `make billing-close`,
> (3) que alertas precisam estar armados antes do fechamento (freshness, qualidade, abuso, falha de job),
> (4) o que **não** logar para evitar vazamento.”
