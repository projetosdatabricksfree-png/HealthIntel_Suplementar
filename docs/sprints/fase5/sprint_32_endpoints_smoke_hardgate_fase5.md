# Sprint 32 — Endpoints Novos, Smoke Tests e Hardgate Fase 5

**Status:** Backlog
**Fase:** Fase 5 — Enriquecimento, Qualidade e MDM sem quebrar o hardgate
**Tag de saída prevista:** `v3.7.0` (release final da Fase 5)
**Objetivo:** expor somente os novos produtos validados, sem quebrar endpoints atuais.
**Fim esperado:** produto comercial fechado com API premium, qualidade e rastreabilidade; baseline `v3.7.0` taggeada.
**Critério de saída:** rotas `/v1/premium/*` operacionais; hardgate `make smoke-premium` zero falhas; `make dbt-build-premium` zero erros; documentação comercial publicada; rotas atuais permanecem com mesmo contrato.

## Regra-mãe

- [ ] Nenhuma rota existente em `/v1/*` é alterada.
- [ ] Toda rota nova vive sob `/v1/premium/*`.
- [ ] Plano comercial novo `premium` controla acesso via `verificar_camada('premium')` ou `verificar_plano('premium')`.
- [ ] Endpoints premium consomem APENAS modelos `api_ans.api_premium_*` (Sprint 31).
- [ ] A FastAPI não consulta `consumo_premium_ans`, `mdm`, `mdm_privado`, `enrichment` ou `quality_ans` diretamente.

## Histórias

### HIS-12.1 — Criar endpoints premium sem alterar endpoints atuais

- [ ] Criar `api/app/routers/premium.py`.
- [ ] Criar `api/app/services/premium.py`.
- [ ] Criar `api/app/schemas/premium.py`.
- [ ] Implementar queries somente contra `api_ans.api_premium_*`, preservando a regra existente de FastAPI ler `api_ans`.
- [ ] Criar rota `GET /v1/premium/operadoras`.
- [ ] Criar rota `GET /v1/premium/cnes/estabelecimentos`.
- [ ] Criar rota `GET /v1/premium/tiss/procedimentos`.
- [ ] Criar rota `GET /v1/premium/tuss/procedimentos`.
- [ ] Criar rota `GET /v1/premium/mdm/operadoras`.
- [ ] Criar rota `GET /v1/premium/mdm/prestadores`.
- [ ] Criar rota `GET /v1/premium/contratos` (autenticada por `tenant_id`).
- [ ] Criar rota `GET /v1/premium/subfaturas` (autenticada por `tenant_id`).
- [ ] Criar rota `GET /v1/premium/quality/datasets`.
- [ ] Não alterar rotas atuais (`/v1/operadoras`, `/v1/bronze/*`, `/v1/prata/*`, etc.).
- [ ] Criar plano `premium` em `plataforma.plano` com `camadas_permitidas = ['bronze', 'prata', 'gold', 'premium']`.
- [ ] Criar dependência `verificar_camada('premium')` reutilizando padrão existente.
- [ ] Adicionar testes integração em `api/tests/integration/test_premium.py`.

### HIS-12.2 — Criar hardgate de publicação premium

- [ ] Criar teste: produto premium não pode conter CNPJ tecnicamente inválido (`assert_premium_sem_cnpj_invalido.sql`).
- [ ] Criar teste: produto premium não pode conter operadora sem MDM (`assert_premium_operadora_tem_mdm.sql`).
- [ ] Criar teste: produto premium CNES não pode conter CNES inválido (`assert_premium_cnes_valido.sql`).
- [ ] Criar teste: produto premium contrato não pode conter contrato divergente bloqueante (`assert_premium_contrato_sem_excecao_bloqueante.sql`).
- [ ] Criar teste: produto premium subfatura não pode conter subfatura órfã (`assert_premium_subfatura_com_contrato.sql`).
- [ ] Criar teste: endpoint premium não pode apontar para tabela fora de `api_ans.api_premium_*` (verificação documental + smoke).
- [ ] Criar `make smoke-premium` (script `scripts/smoke_premium.py`).
- [ ] Criar `make dbt-build-premium` (`dbt build --select tag:quality tag:enrichment tag:mdm tag:mdm_privado tag:consumo_premium tag:premium`).
- [ ] Criar `make dbt-test-premium` (`dbt test --select tag:quality tag:enrichment tag:mdm tag:mdm_privado tag:consumo_premium tag:premium`).
- [ ] Adicionar suite de regressão `testes/regressao/test_endpoints_fase5.py`.

### HIS-12.3 — Criar documentação comercial de qualidade

- [ ] Criar `docs/produto/catalogo_premium.md`.
- [ ] Criar `docs/produto/quality_scores.md` (definição de cada `quality_score_*`).
- [ ] Criar `docs/produto/mdm_contrato_subfatura.md`.
- [ ] Criar `docs/produto/validacao_cnpj_receita.md`.
- [ ] Criar `docs/produto/tiss_tuss_premium.md`.
- [ ] Criar exemplos de request/response (curl + Python) para cada rota `/v1/premium/*`.
- [ ] Documentar separação entre consumo SQL direto (`consumo_premium_ans`) e API premium (`api_ans.api_premium_*`).
- [ ] Criar descrição de valor para operadoras.
- [ ] Criar descrição de valor para hospitais.
- [ ] Criar descrição de valor para consultorias e grandes empresas.
- [ ] Atualizar `docs/CHANGELOG.md` com entrada `v3.7.0` (Sprints 26–32).
- [ ] Atualizar `docs/sprints/fase5/README.md` consolidando o status final da Fase 5.
- [ ] Atualizar `CLAUDE.md`: novo plano `premium`, novos schemas (`enrichment`, `mdm_privado`), novos comandos `make` (`smoke-premium`, `dbt-build-premium`, `enrich-cnpj`).

## Entregas esperadas

- [ ] Router/service/schema premium em `api/app/`
- [ ] 9 rotas `/v1/premium/*`
- [ ] Plano comercial `premium` em `plataforma.plano`
- [ ] 6 testes singulares de hardgate premium
- [ ] `make smoke-premium`, `make dbt-build-premium`, `make dbt-test-premium`
- [ ] `testes/regressao/test_endpoints_fase5.py`
- [ ] 5 documentos comerciais em `docs/produto/`
- [ ] `docs/CHANGELOG.md` atualizado (`v3.7.0`)
- [ ] `CLAUDE.md` atualizado
- [ ] Tag git `v3.7.0`

## Validação esperada (hard gates)

- [ ] `ruff check api ingestao scripts shared testes` zero erros.
- [ ] `dbt build --select tag:quality tag:enrichment tag:mdm tag:mdm_privado tag:consumo_premium tag:premium` zero erros.
- [ ] `dbt test` zero falhas em toda a stack.
- [ ] `make smoke-premium` zero falhas.
- [ ] `pytest api/tests/integration/test_premium.py -v` zero falhas.
- [ ] `pytest testes/regressao/test_endpoints_fase5.py -v` zero falhas.
- [ ] Suite de regressão das Fases 1–4 (`testes/regressao/test_endpoints_fase4.py`) continua zero falhas.
- [ ] Verificação documental: zero alterações em rotas `/v1/{operadoras,bronze,prata,…}`.
- [ ] Verificação documental/código: nenhum serviço premium referencia `consumo_premium_ans` diretamente.
- [ ] Tag `v3.7.0` criada apontando para commit pós-aprovação.

## Resultado Esperado

Sprint 32 fecha a Fase 5 e a entrega comercial. A plataforma passa a expor um portfólio premium completo (operadoras, CNES, TISS/TUSS, MDM, contrato e subfatura) com qualidade explícita, validação documental e Serpro como fonte de verdade para CNPJ. Todos os endpoints, modelos e contratos das Fases 1–4 permanecem byte-idênticos: o cliente legado não percebe mudança; o cliente premium ganha um produto de outra ordem de grandeza.
