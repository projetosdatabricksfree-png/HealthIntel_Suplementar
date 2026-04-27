# Changelog

## `v3.8.0-gov` — Sprint 33: Governança Documental, Catálogos e Padrões Normativos

Data de referência: `2026-04-27`

### Entregas consolidadas

- 13 documentos raiz de governança em `docs/governanca/` cobrindo: camadas oficiais, catálogo de tabelas, dicionário de colunas, padrões de tipagem, nomenclatura, índices/chaves/constraints, competência/datas, qualidade/validação, MDM, data products, API, segurança/LGPD e hard gates normativos.
- 12 templates oficiais em `docs/governanca/templates/` para documentação padronizada de tabelas, colunas, índices, constraints, funções, triggers, relacionamentos, data products, MDM, regras de qualidade, exceções e endpoints.
- Corpo normativo permanente — toda nova implementação deve passar pelos hard gates documentais antes dos hard gates físicos.
- Anti-escopo formalizado: enrichment não é camada ativa; Serpro, Receita online e BrasilAPI não são dependências obrigatórias.
- CNPJ, CPF, CNES e Registro ANS formalmente governados como `varchar`, nunca tipos numéricos.

### Status

- **Release documental/normativo** — entrega em ambiente de desenvolvimento/homologação.
- Nenhum artefato técnico (dbt, API, infra, scripts) foi alterado por esta sprint.
- Sem presumir clientes ativos em produção.

### Evidências

- `docs/governanca/README.md`
- `docs/governanca/catalogo_tabelas.md`
- `docs/governanca/dicionario_colunas.md`
- `docs/governanca/padroes_tipagem.md`
- `docs/governanca/padroes_nomenclatura.md`
- `docs/governanca/padroes_indices_chaves_constraints.md`
- `docs/governanca/padroes_competencia_datas.md`
- `docs/governanca/padroes_qualidade_validacao.md`
- `docs/governanca/mdm_governanca.md`
- `docs/governanca/data_products_governanca.md`
- `docs/governanca/api_governanca.md`
- `docs/governanca/seguranca_lgpd_governanca.md`
- `docs/governanca/hardgate_governanca.md`
- `docs/governanca/templates/` (12 templates)
- `docs/sprints/fase5/sprint_33_governanca_documental.md`

## `v3.7.0` — Sprint 32: Endpoints Premium, Smoke Tests e Release Técnico

Data de referência: `2026-04-27`

### Entregas consolidadas

- 9 rotas `/v1/premium/*` expostas via FastAPI, consultando exclusivamente `api_ans.api_premium_*`.
- Service centralizado de datasets premium com mapeamento declarativo, filtros parametrizados e ordenação controlada.
- Schemas Pydantic v2 completos para todos os 9 datasets (operadora 360, CNES, TISS, TUSS, MDM operadora, MDM prestador, contrato, subfatura, quality).
- Tenant obrigatório em rotas privadas (`/v1/premium/contratos`, `/v1/premium/subfaturas`) — HTTP 403 sem tenant autenticado.
- Plano não-premium bloqueado com HTTP 403 em toda rota `/v1/premium/*`.
- Paginação obrigatória (1–100 linhas por request) em todas as rotas premium.
- Smoke premium com 14 cenários de validação.
- Testes de integração com 12 cenários.
- Regressão Fase 5 com 6 cenários de contrato.
- Makefile com targets `smoke-premium`, `dbt-build-premium`, `dbt-test-premium`.
- Documentação de catálogo premium, quality scores, MDM contrato/subfatura e validação CNPJ offline.

### Status

- **Entrega técnica/homologação** — ainda não há cliente ativo em produção.
- Nenhum endpoint legado foi alterado ou quebrado.
- Nenhuma dependência externa (Serpro, Receita online, BrasilAPI, enrichment).
- FastAPI premium lê somente `api_ans.api_premium_*`.

### Evidências

- `docs/produto/catalogo_premium.md`
- `docs/produto/quality_scores.md`
- `docs/produto/mdm_contrato_subfatura.md`
- `docs/produto/validacao_cnpj_offline.md`
- `docs/produto/tiss_tuss_premium.md`
- `docs/sprints/fase5/sprint_32_endpoints_smoke_hardgate_fase5.md`

## `v2.0.0`

Data de referência: `2026-04-23`

### Entregas consolidadas

- Bronze API técnica com 11 endpoints e contrato de auditoria.
- Prata API analítica com 14 endpoints e quarentena visível.
- Score v3 composto com fallback técnico e ranking composto.
- Governança de camadas com `camadas_permitidas`, hash por arquivo e hash por linha.
- Billing e rate limit desagregados por camada.
- Catálogo comercial e documentação de contratos por camada.

### Metodologia

- `score_v3`
- `ranking_composto_v3`

### Evidências

- `docs/arquitetura/contratos_por_camada.md`
- `docs/arquitetura/contrato_bronze_api.md`
- `docs/arquitetura/contrato_prata_api.md`
- `docs/arquitetura/score_v3_metodologia.md`
- `docs/catalogo_endpoints.md`
- `docs/catalogo_datasets.md`

## `v1.0.0-baseline`

Data de referência: `2026-04-22`

### Entregas consolidadas

- Sprint 12 concluída com vazios assistenciais, oportunidade v2 e catálogo de rollout.
- Catálogo de endpoints publicado e alinhado ao runtime.
- Catálogo de datasets consolidado por schema e modelo dbt.
- Runbooks finais publicados para operação e suporte.

### Metodologia

- `score_v1`
- `score_regulatorio_v2`
- `score_v2`
- `oportunidade_v2`

### Evidências

- `docs/catalogo_endpoints.md`
- `docs/catalogo_datasets.md`
- `docs/dbt_catalog_v1.0.0.json`
