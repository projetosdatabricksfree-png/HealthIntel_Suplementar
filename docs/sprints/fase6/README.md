# Fase 6 — Entrega ao Cliente / Operação Comercial

A Fase 6 fecha o ciclo do produto: pega tudo que já passou no hardgate (`v3.0.0` da Fase 4 e `v3.7.0` da Fase 5) e transforma em **plataforma operada** que cliente real consome em produção sem erro, com previsibilidade comercial, segurança, suporte e SLA.

## Contexto

- **Fase 1–4**: medallion completa, ingestão real SIB/CADOP, Gold marts BI, `consumo_ans` (`v3.0.0`).
- **Fase 5**: enriquecimento documental, MDM público/privado, produtos premium e governança (`v3.7.0` + `v3.8.0-gov`).
- **Fase 6**: ambiente de produção, runtime estável, API comercializável, billing, onboarding, observabilidade, segurança LGPD, suporte e go-live (`v4.0.0`).

A Fase 6 é **100% aditiva e operacional**: não altera lógica de modelos, não renomeia tabelas, não muda contratos de endpoints existentes. O que muda é **como** o sistema é entregue, executado, monitorado e cobrado.

## Público alvo (decisões comerciais embutidas)

| Persona | Necessidade-chave | Plano sugerido | Endpoints prioritários |
|---------|-------------------|----------------|------------------------|
| Hospitais | Solvência financeira/regulatória de operadoras pagadoras, glosas, sinistralidade, rede | Professional / Enterprise | `financeiro_v2`, `regulatorio_v2`, `tiss`, `mart_operadora_360`, `score_v3` |
| Agências/consultorias regulatórias | Série histórica IDSS, NIP, RN623, ranking, IGR | Professional | `regulatorio_v2`, `mercado`, `ranking`, `mart_score_operadora` |
| Analistas / BI engineers | Pull massivo, schema estável, paginação, freshness explícito, OpenAPI sólido, acesso direto a `consumo_ans` | Professional | API + `consumo_ans` direto (Power BI / Metabase / psql) |
| Corretoras pequenas | Rede assistencial básica, ranking de operadoras por modalidade | Starter | `cnes`, `mercado`, `ranking` |
| Corretoras médias | + portabilidade, score, mercado por município | Professional | `mart_mercado_municipio`, `mart_score_operadora`, `cnes` |
| Corretoras grandes / brokers nacionais | + contrato/subfatura privado por tenant, MDM, validação Receita, dado curado | Enterprise / Premium | `/v1/premium/*`, `mdm_*`, contrato/subfatura privado |

## Sprints

| Sprint | Título | Status | Tag prevista |
|--------|--------|--------|--------------|
| [Sprint 14](sprint_14_diagnostico_operacional.md) | Diagnóstico Operacional e Mapa de Entrega ao Cliente | Backlog | `v3.9.0-diag` |
| [Sprint 15](sprint_15_infra_runtime_deploy.md) | Infraestrutura, Runtime e Deploy | Backlog | `v3.9.1-infra` |
| [Sprint 16](sprint_16_api_producao_consumo_cliente.md) | API de Produção e Consumo do Cliente | Backlog | `v3.9.2-api` |
| [Sprint 17](sprint_17_orquestracao_cargas_freshness.md) | Orquestração, Freshness e Publicação Controlada | Backlog | `v3.9.3-orquestracao` |
| [Sprint 18](sprint_18_observabilidade_sla_slo.md) | Observabilidade, SLA e SLO | Backlog | `v3.9.4-obs` |
| [Sprint 19](sprint_19_seguranca_lgpd_tenant_billing.md) | Segurança, LGPD, Tenant e Billing | Backlog | `v3.9.5-seg` |
| [Sprint 20](sprint_20_onboarding_cliente_documentacao.md) | Onboarding, Documentação e Sandbox do Cliente | Backlog | `v3.9.6-onboarding` |
| [Sprint 21](sprint_21_go_live_hardgate_comercial.md) | Go-live, Hardgate Comercial e Operação Assistida | Backlog | `v4.0.0` |

## Regra-mãe da Fase 6

- Não alterar modelos `stg_*`, `int_*`, `fat_*`, `mart_*`, `api_*`, `consumo_*`, `consumo_premium_*`, `mdm_*`.
- Não renomear endpoint nem mudar contrato de resposta existente.
- Não reescrever DAGs aprovadas; apenas adicionar DAGs/operadores de operação (freshness gate, publicação, alerta).
- Toda quebra contratual exige novo endpoint versionado (`/v2/...`), nunca alteração in-place.
- Toda task como `[ ]`. Nunca `[x]` no backlog.
- Português-Brasil em toda documentação.

## Documentos de apoio

- [diagnostico_sistema_atual.md](diagnostico_sistema_atual.md) — estado do sistema, riscos, gaps de produção
- [matriz_gaps_entrega_cliente.md](matriz_gaps_entrega_cliente.md) — gap × área × severidade × sprint
- [arquitetura_operacional_producao.md](arquitetura_operacional_producao.md) — onde cada peça roda em prod
- [sizing_maquinas_ambientes.md](sizing_maquinas_ambientes.md) — 4 cenários (dev, MVP, prod inicial, prod escala)
- [backlog_entrega_cliente.md](backlog_entrega_cliente.md) — backlog consolidado por área
- [hardgate_fase6_entrega_cliente.md](hardgate_fase6_entrega_cliente.md) — checklist de release `v4.0.0`

Documento comercial de saída: `docs/produto/entrega_cliente.md`.

## Critério de saída da Fase 6 (`v4.0.0`)

A Fase 6 só fecha quando:

- [ ] Pelo menos 1 cliente piloto consumindo a API em ambiente de produção sem erro durante 14 dias corridos.
- [ ] Hardgate `hardgate_fase6_entrega_cliente.md` 100% verde.
- [ ] Suite de regressão das Fases 1–5 zero falhas.
- [ ] Backup + restore testados em ambiente staging idêntico ao de produção.
- [ ] Documentação OpenAPI publicada e validada externamente.
- [ ] Tag git `v4.0.0` apontando para o commit do go-live.
